#!/usr/bin/env python3
"""Read one PR completely from GitHub and report whether it can land."""

import argparse
import json
import re
import subprocess
import sys

READ_ATTEMPTS = 3
EXIT_CODES = {"ready": 0, "merged": 0, "blocked": 2, "pending": 3}
PASSING_CONCLUSIONS = {"SUCCESS", "NEUTRAL", "SKIPPED"}
PENDING_STATUS_STATES = {"PENDING", "EXPECTED"}
PR_URL = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")
PROVISIONAL_HEADING = "## Provisional"
PROVISIONAL_BLOCKER = (f"the body has an open '{PROVISIONAL_HEADING}' section; "
                       "it must not merge until that section is removed")
REVIEW_CONTEXT = "review-fix-loop"
REVIEW_BLOCKER = f"no passing '{REVIEW_CONTEXT}' status on this head; run Review Fix Loop on it"

# baseRefOid stops at the PR's last sync with its base, so read the branch's live tip instead.
SUMMARY_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      number url state isDraft isInMergeQueue mergeable mergeStateStatus reviewDecision body
      headRefName headRefOid baseRefName
      baseRef { target { oid } }
      autoMergeRequest { enabledAt }
      mergeCommit { oid }
      comments { totalCount }
      reviews { totalCount }
      reviewThreads { totalCount }
      reviewRequests(first: 100) {
        nodes {
          requestedReviewer {
            ... on User { login }
            ... on Team { slug }
            ... on Bot { login }
            ... on Mannequin { login }
          }
        }
      }
    }
  }
}
"""

WORKFLOWS_QUERY = """
query($owner: String!, $name: String!, $expression: String!) {
  repository(owner: $owner, name: $name) {
    object(expression: $expression) { id }
  }
}
"""

# `gh --paginate` follows the first pageInfo in each response, so it precedes `nodes`.
THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      page: reviewThreads(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line
          comments(first: 100) {
            pageInfo { hasNextPage }
            nodes { databaseId author { login } body url createdAt }
          }
        }
      }
    }
  }
}
"""

THREAD_COMMENTS_QUERY = """
query($id: ID!, $endCursor: String) {
  node(id: $id) {
    ... on PullRequestReviewThread {
      comments(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes { databaseId author { login } body url createdAt }
      }
    }
  }
}
"""

COMMENTS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      page: comments(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes { databaseId author { login } body url createdAt isMinimized }
      }
    }
  }
}
"""

REVIEWS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      page: reviews(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes { databaseId author { login } state body url submittedAt commit { oid } }
      }
    }
  }
}
"""

CHECKS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      commits(last: 1) {
        nodes {
          commit {
            statusCheckRollup {
              page: contexts(first: 100, after: $endCursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  __typename
                  ... on CheckRun {
                    name status conclusion detailsUrl
                    isRequired(pullRequestNumber: $number)
                  }
                  ... on StatusContext {
                    context state targetUrl
                    isRequired(pullRequestNumber: $number)
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


class ReadError(Exception):
    pass


def run_gh(args):
    try:
        result = subprocess.run(["gh", *args], text=True, capture_output=True)
    except OSError as error:
        raise ReadError(f"could not run gh: {error}") from error
    if result.returncode != 0:
        raise ReadError(result.stderr.strip() or f"gh {args[0]} failed")
    return result.stdout


def graphql_pages(gh, query, **variables):
    args = ["api", "graphql", "--paginate", "--slurp", "-f", f"query={query}"]
    for key, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
    return [page["data"] for page in json.loads(gh(args))]


def pull_request_pages(gh, query, pr):
    return [page["repository"]["pullRequest"] for page in graphql_pages(gh, query, **pr)]


def read_summary(gh, pr):
    return pull_request_pages(gh, SUMMARY_QUERY, pr)[0]


def is_provisional(body):
    """Match the marker on any line, code examples included, so no layout can hide it."""
    return any(line.rstrip() == PROVISIONAL_HEADING for line in (body or "").splitlines())


def checks_page(pull_request):
    rollup = pull_request["commits"]["nodes"][0]["commit"]["statusCheckRollup"]
    return rollup["page"] if rollup else {"nodes": []}


def all_nodes(gh, query, pr, page_of=lambda pull_request: pull_request["page"]):
    return [node for page in pull_request_pages(gh, query, pr) for node in page_of(page)["nodes"]]


def with_every_comment(gh, thread):
    if thread["comments"]["pageInfo"]["hasNextPage"]:
        pages = graphql_pages(gh, THREAD_COMMENTS_QUERY, id=thread["id"])
        thread["comments"]["nodes"] = [
            comment for page in pages for comment in page["node"]["comments"]["nodes"]]
    return thread


def check_result(node):
    if node["__typename"] == "CheckRun":
        name, url = node["name"], node["detailsUrl"]
        if node["status"] != "COMPLETED":
            state = "pending"
        else:
            state = "pass" if node["conclusion"] in PASSING_CONCLUSIONS else "fail"
    else:
        name, url = node["context"], node["targetUrl"]
        if node["state"] == "SUCCESS":
            state = "pass"
        else:
            state = "pending" if node["state"] in PENDING_STATUS_STATES else "fail"
    return {"name": name, "state": state, "required": node["isRequired"], "url": url}


def is_review_record(node):
    return node["__typename"] == "StatusContext" and node["context"] == REVIEW_CONTEXT


def has_workflows(gh, pr, head):
    pages = graphql_pages(gh, WORKFLOWS_QUERY, owner=pr["owner"], name=pr["name"],
                          expression=f"{head}:.github/workflows")
    return pages[0]["repository"]["object"] is not None


def commits_behind_base(gh, pr, summary):
    if summary["state"] != "OPEN":
        return 0
    span = f"{summary['baseRef']['target']['oid']}...{summary['headRefOid']}"
    return json.loads(gh(["api", f"repos/{pr['owner']}/{pr['name']}/compare/{span}"]))["behind_by"]


def read_state(gh, pr):
    """Read until the PR holds still, so every part describes one state of it."""
    for _ in range(READ_ATTEMPTS):
        summary = read_summary(gh, pr)
        nodes = all_nodes(gh, CHECKS_QUERY, pr, checks_page)
        records = [check_result(node) for node in nodes if is_review_record(node)]
        checks = [check_result(node) for node in nodes if not is_review_record(node)]
        state = {
            "summary": summary,
            "behind_by": commits_behind_base(gh, pr, summary),
            "threads": [with_every_comment(gh, node)
                        for node in all_nodes(gh, THREADS_QUERY, pr)],
            "comments": all_nodes(gh, COMMENTS_QUERY, pr),
            "reviews": all_nodes(gh, REVIEWS_QUERY, pr),
            "checks": checks,
            "review_status": records[0] if records else None,
            "expects_checks": bool(checks) or has_workflows(gh, pr, summary["headRefOid"]),
        }
        if read_summary(gh, pr) == summary:
            state["provisional"] = is_provisional(summary.pop("body"))
            return state
    raise ReadError(f"#{pr['number']} kept changing during the read")


def assess_checks(state, blockers, pending, to_settle):
    checks = state["checks"]
    failed = [check for check in checks if check["state"] == "fail"]
    pending += [f"check running: {check['name']}" for check in checks
                if check["state"] == "pending"]
    if any(check["required"] for check in checks):
        blockers += [f"required check failed: {check['name']} {check['url']}"
                     for check in failed if check["required"]]
        to_settle += [f"optional check failed: {check['name']} {check['url']}"
                      for check in failed if not check["required"]]
    else:
        blockers += [f"check failed, and GitHub requires none here: {check['name']} {check['url']}"
                     for check in failed]
    if not checks and state["expects_checks"]:
        pending.append("no checks reported yet, and this head has workflows")
    elif not checks:
        to_settle.append("no checks reported on this head")


def assess_merge_state(state, blockers, pending):
    summary = state["summary"]
    mergeable, merge_state = summary["mergeable"], summary["mergeStateStatus"]
    if mergeable == "CONFLICTING" or merge_state == "DIRTY":
        blockers.append("the branch conflicts with its base")
    elif mergeable == "UNKNOWN" or merge_state == "UNKNOWN":
        pending.append("GitHub is still computing mergeability")
    elif merge_state == "BEHIND":
        blockers.append("the branch is behind its base")
    elif merge_state == "BLOCKED" and not (pending or blockers):
        blockers.append("GitHub reports an unmet merge requirement")
    elif merge_state == "UNSTABLE" and all(
            check["state"] == "pass" for check in [*state["checks"], state["review_status"]]
            if check):
        blockers.append("GitHub reports a failing status that no check here shows; "
                        "read the head and test-merge targets")


def assess(state, expected_head=None):
    summary = state["summary"]
    blockers, pending, to_settle = [], [], []
    head = summary["headRefOid"]
    if expected_head is not None and head != expected_head:
        blockers.append(f"the head moved: expected {expected_head}, found {head}")
    if summary["state"] != "OPEN":
        if summary["state"] == "CLOSED":
            blockers.append("the PR is closed")
        return {"status": "blocked" if blockers else "merged", "blockers": blockers,
                "pending": [], "to_settle": []}

    if state.get("provisional"):
        blockers.append(PROVISIONAL_BLOCKER)
    if (state["review_status"] or {}).get("state") != "pass":
        blockers.append(REVIEW_BLOCKER)
    if summary["isDraft"]:
        blockers.append("the PR is a draft")
    if summary["reviewDecision"] == "CHANGES_REQUESTED":
        blockers.append("a reviewer requested changes")
    elif summary["reviewDecision"] == "REVIEW_REQUIRED":
        blockers.append("a required approval is missing")
    if summary["isInMergeQueue"]:
        pending.append("the PR is in the merge queue")
    elif summary["autoMergeRequest"]:
        pending.append("auto-merge is enabled")

    for request in summary["reviewRequests"]["nodes"]:
        reviewer = request["requestedReviewer"] or {}
        name = reviewer.get("login") or reviewer.get("slug") or "a hidden reviewer"
        pending.append(f"review requested from {name}")

    assess_checks(state, blockers, pending, to_settle)
    if state["behind_by"]:
        to_settle.append(f"{state['behind_by']} commit(s) behind {summary['baseRefName']}")

    open_threads = [thread for thread in state["threads"] if not thread["isResolved"]]
    if open_threads:
        blockers.append(f"{len(open_threads)} review thread(s) still open")
    to_settle += [f"comment: {comment['url']}" for comment in state["comments"]
                  if not comment["isMinimized"]]
    to_settle += [f"review: {review['url']}" for review in state["reviews"] if review["body"]]

    assess_merge_state(state, blockers, pending)
    status = "blocked" if blockers else "pending" if pending else "ready"
    return {"status": status, "blockers": blockers, "pending": pending, "to_settle": to_settle}


def resolve_target(gh, target):
    url = json.loads(gh(["pr", "view", target, "--json", "url"]))["url"]
    owner, name, number = PR_URL.search(url).groups()
    return {"owner": owner, "name": name, "number": int(number)}


def main(argv=None, gh=run_gh):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", help="PR number or URL")
    parser.add_argument("--head", help="the commit you verified; a different head blocks")
    args = parser.parse_args(argv)
    try:
        state = read_state(gh, resolve_target(gh, args.target))
    except ReadError as error:
        print(f"pr_state: {error}", file=sys.stderr)
        return 1
    assessment = assess(state, args.head)
    print(json.dumps({**assessment, **state}, indent=2))
    return EXIT_CODES[assessment["status"]]


if __name__ == "__main__":
    sys.exit(main())
