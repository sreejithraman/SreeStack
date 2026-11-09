import contextlib
import io
import json
import re
import unittest

import pr_state

HEAD = "a" * 40


def base_tip(character):
    return {"target": {"oid": character * 40}}


def summary(**changes):
    return {
        "number": 7, "url": "https://github.com/o/r/pull/7", "state": "OPEN", "isDraft": False,
        "isInMergeQueue": False, "autoMergeRequest": None, "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN", "reviewDecision": None, "headRefName": "agent/x",
        "headRefOid": HEAD, "baseRefName": "main", "baseRef": base_tip("b"), "mergeCommit": None,
        "comments": {"totalCount": 0}, "reviews": {"totalCount": 0},
        "reviewThreads": {"totalCount": 0}, "reviewRequests": {"nodes": []}, "body": "",
        **changes,
    }


def check_run(name="ci", status="COMPLETED", conclusion="SUCCESS", required=True):
    return {"__typename": "CheckRun", "name": name, "status": status, "conclusion": conclusion,
            "detailsUrl": f"https://ci/{name}", "isRequired": required}


def status_context(state="SUCCESS", required=True, context="legacy"):
    return {"__typename": "StatusContext", "context": context, "state": state,
            "targetUrl": f"https://ci/{context}", "isRequired": required}


def review_status(state="SUCCESS", required=False):
    return status_context(state, required, context="review-fix-loop")


def thread_comment(number=1):
    return {"databaseId": number, "author": {"login": "bot"}, "body": f"fix {number}",
            "url": f"https://c/{number}", "createdAt": "2026-11-06T09:00:00Z"}


def thread(resolved=False, more_comments=False):
    return {"id": "T1", "isResolved": resolved, "isOutdated": False, "path": "a.py", "line": 3,
            "comments": {"pageInfo": {"hasNextPage": more_comments}, "nodes": [thread_comment()]}}


def comment(created="2026-11-06T09:00:00Z", minimized=False):
    return {"databaseId": 2, "author": {"login": "sam"}, "body": "hm", "url": "https://c/2",
            "createdAt": created, "isMinimized": minimized}


def review(body="looks off"):
    return {"databaseId": 3, "author": {"login": "sam"}, "state": "COMMENTED", "body": body,
            "url": "https://c/3", "submittedAt": "2026-11-06T09:00:00Z", "commit": {"oid": HEAD}}


class FakeGitHub:
    """Answer gh calls by query, returning every page only when asked to paginate."""

    def __init__(self, summaries=None, threads=(), comments=(), reviews=(), checks=(check_run(),),
                 review=review_status(), page_size=100, behind_by=0, thread_comments=(),
                 workflows=False):
        self.summaries = list(summaries or [summary()])
        self.threads, self.comments, self.reviews = list(threads), list(comments), list(reviews)
        self.checks, self.page_size = [*checks, *([review] if review else [])], page_size
        self.behind_by, self.thread_comments = behind_by, list(thread_comments)
        self.workflows, self.compared = workflows, []

    def pages(self, nodes):
        starts = range(0, len(nodes), self.page_size)
        return [{"nodes": nodes[start:start + self.page_size]} for start in starts] or [
            {"nodes": []}]

    def __call__(self, args):
        if args[:2] == ["pr", "view"]:
            return json.dumps({"url": "https://github.com/o/r/pull/7"})
        if args[1].startswith("repos/"):
            self.compared.append(args[1])
            return json.dumps({"behind_by": self.behind_by})
        query = next(arg for arg in args if arg.startswith("query="))
        answers = self.answer(query)
        return json.dumps(answers if "--paginate" in args else answers[:1])

    def answer(self, query):
        if "object(expression" in query:
            found = {"id": "tree"} if self.workflows else None
            return [{"data": {"repository": {"object": found}}}]
        if "headRefOid" in query:
            current = self.summaries.pop(0) if len(self.summaries) > 1 else self.summaries[0]
            selected = set(re.findall(r"\w+", query))
            return self.wrap([{key: value for key, value in current.items() if key in selected}])
        if "node(id" in query:
            return [{"data": {"node": {"comments": page}}}
                    for page in self.pages(self.thread_comments)]
        if "reviewThreads" in query:
            return self.wrap({"page": page} for page in self.pages(self.threads))
        if "isMinimized" in query:
            return self.wrap({"page": page} for page in self.pages(self.comments))
        if "reviews(" in query:
            return self.wrap({"page": page} for page in self.pages(self.reviews))
        rollups = [{"page": page} for page in self.pages(self.checks)] if self.checks else [None]
        return self.wrap({"commits": {"nodes": [{"commit": {"statusCheckRollup": rollup}}]}}
                         for rollup in rollups)

    @staticmethod
    def wrap(pull_requests):
        return [{"data": {"repository": {"pullRequest": pull_request}}}
                for pull_request in pull_requests]


def run(github, *args):
    output, errors = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        code = pr_state.main(["7", *args], gh=github)
    return code, json.loads(output.getvalue()) if output.getvalue() else errors.getvalue()


class Readiness(unittest.TestCase):
    def test_clean_pr_is_ready(self):
        code, result = run(FakeGitHub())
        self.assertEqual((code, result["status"]), (0, "ready"))
        self.assertEqual(result["summary"]["headRefOid"], HEAD)

    def test_merged_pr_reports_its_commit(self):
        merged = summary(state="MERGED", mergeCommit={"oid": "c" * 40})
        code, result = run(FakeGitHub([merged], checks=[check_run(conclusion="FAILURE")]))
        self.assertEqual((code, result["status"], result["summary"]["mergeCommit"]["oid"]),
                         (0, "merged", "c" * 40))

    def test_merged_pr_with_another_head_blocks(self):
        merged = summary(state="MERGED", mergeCommit={"oid": "c" * 40}, headRefOid="e" * 40)
        code, result = run(FakeGitHub([merged]), "--head", HEAD)
        self.assertEqual((code, result["status"], result["summary"]["state"]),
                         (2, "blocked", "MERGED"))
        self.assertIn("the head moved", result["blockers"][0])

    def test_queued_pr_waits_instead_of_inviting_a_second_merge(self):
        for changes, message in (({"isInMergeQueue": True}, "the PR is in the merge queue"),
                                 ({"autoMergeRequest": {"enabledAt": "t"}}, "auto-merge is enabled"),
                                 ({"isInMergeQueue": True, "mergeStateStatus": "BLOCKED"},
                                  "the PR is in the merge queue")):
            with self.subTest(changes):
                code, result = run(FakeGitHub([summary(**changes)]))
                self.assertEqual((code, result["pending"], result["blockers"]),
                                 (3, [message], []))

    def test_closed_pr_blocks(self):
        code, result = run(FakeGitHub([summary(state="CLOSED")]))
        self.assertEqual((code, result["blockers"]), (2, ["the PR is closed"]))

    def test_each_failed_conclusion_blocks(self):
        for conclusion in ("FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED",
                           "STARTUP_FAILURE", "STALE"):
            with self.subTest(conclusion):
                code, result = run(FakeGitHub(checks=[check_run(conclusion=conclusion)]))
                self.assertEqual(code, 2)
                self.assertIn("required check failed: ci https://ci/ci", result["blockers"])

    def test_skipped_and_neutral_required_checks_pass(self):
        for conclusion in ("SKIPPED", "NEUTRAL"):
            with self.subTest(conclusion):
                self.assertEqual(run(FakeGitHub(checks=[check_run(conclusion=conclusion)]))[0], 0)

    def test_running_required_check_waits_even_when_github_says_blocked(self):
        code, result = run(FakeGitHub([summary(mergeStateStatus="BLOCKED")],
                                      checks=[check_run(status="IN_PROGRESS", conclusion=None)]))
        self.assertEqual((code, result["pending"], result["blockers"]),
                         (3, ["check running: ci"], []))

    def test_failure_outranks_pending(self):
        code, result = run(FakeGitHub(checks=[
            check_run("a", conclusion="FAILURE"),
            check_run("b", status="QUEUED", conclusion=None)]))
        self.assertEqual((code, result["status"]), (2, "blocked"))

    def test_status_contexts_count(self):
        self.assertEqual(run(FakeGitHub(checks=[status_context("FAILURE")]))[0], 2)
        self.assertEqual(run(FakeGitHub(checks=[status_context("ERROR")]))[0], 2)
        self.assertEqual(run(FakeGitHub(checks=[status_context("PENDING")]))[0], 3)
        self.assertEqual(run(FakeGitHub(checks=[status_context("SUCCESS")]))[0], 0)

    def test_optional_failure_needs_a_reader_not_a_block(self):
        code, result = run(FakeGitHub(checks=[check_run(), check_run(
            "lint", conclusion="FAILURE", required=False)]))
        self.assertEqual(code, 0)
        self.assertEqual(result["to_settle"], ["optional check failed: lint https://ci/lint"])

    def test_lone_optional_checks_hold_the_same_bar(self):
        code, result = run(FakeGitHub([summary(mergeStateStatus="UNSTABLE")],
                                      checks=[check_run(conclusion="FAILURE", required=False)]))
        self.assertEqual(code, 2)
        self.assertIn("GitHub requires none here: ci", result["blockers"][0])

    def test_any_running_check_waits(self):
        for checks in ([check_run(status="IN_PROGRESS", conclusion=None, required=False)],
                       [check_run("a"), check_run("b", status="QUEUED", conclusion=None,
                                                  required=False)]):
            with self.subTest(checks):
                self.assertEqual(run(FakeGitHub(checks=checks))[0], 3)

    def test_head_with_workflows_waits_for_its_checks(self):
        code, result = run(FakeGitHub(checks=(), workflows=True))
        self.assertEqual((code, result["status"]), (3, "pending"))
        self.assertIn("no checks reported yet", result["pending"][0])

    def test_requested_reviewers_are_waited_for(self):
        requests = [{"requestedReviewer": {"login": "sam"}},
                    {"requestedReviewer": {"slug": "core"}},
                    {"requestedReviewer": None}]
        code, result = run(FakeGitHub([summary(reviewRequests={"nodes": requests})]))
        self.assertEqual((code, result["pending"]),
                         (3, ["review requested from sam", "review requested from core",
                              "review requested from a hidden reviewer"]))

    def test_no_checks_on_the_head_is_flagged(self):
        code, result = run(FakeGitHub(checks=()))
        self.assertEqual(code, 0)
        self.assertEqual(result["to_settle"], ["no checks reported on this head"])

    def test_base_that_moved_without_a_strict_rule_is_flagged(self):
        code, result = run(FakeGitHub(behind_by=3))
        self.assertEqual((code, result["to_settle"]), (0, ["3 commit(s) behind main"]))

    def test_unseen_requirement_blocks_through_github_state(self):
        code, result = run(FakeGitHub([summary(mergeStateStatus="BLOCKED")]))
        self.assertEqual((code, result["blockers"]),
                         (2, ["GitHub reports an unmet merge requirement"]))

    def test_merge_states(self):
        cases = {
            "BEHIND": (2, "the branch is behind its base"),
            "DIRTY": (2, "the branch conflicts with its base"),
        }
        for merge_state, (code, blocker) in cases.items():
            with self.subTest(merge_state):
                result = run(FakeGitHub([summary(mergeStateStatus=merge_state)]))
                self.assertEqual((result[0], result[1]["blockers"]), (code, [blocker]))

    def test_unstable_with_nothing_to_show_for_it_blocks(self):
        code, result = run(FakeGitHub([summary(mergeStateStatus="UNSTABLE")]))
        self.assertEqual(code, 2)
        self.assertIn("test-merge", result["blockers"][0])

    def test_unstable_explained_by_an_optional_failure_is_for_the_reader(self):
        code, result = run(FakeGitHub([summary(mergeStateStatus="UNSTABLE")], checks=[
            check_run(), check_run("lint", conclusion="FAILURE", required=False)]))
        self.assertEqual((code, result["blockers"]), (0, []))

    def test_conflicting_blocks_and_unknown_waits(self):
        self.assertEqual(run(FakeGitHub([summary(mergeable="CONFLICTING")]))[0], 2)
        self.assertEqual(run(FakeGitHub([summary(mergeable="UNKNOWN")]))[0], 3)
        self.assertEqual(run(FakeGitHub([summary(mergeStateStatus="UNKNOWN")]))[0], 3)

    def test_draft_and_reviews_block(self):
        self.assertEqual(run(FakeGitHub([summary(isDraft=True)]))[0], 2)
        for decision, blocker in (("CHANGES_REQUESTED", "a reviewer requested changes"),
                                  ("REVIEW_REQUIRED", "a required approval is missing")):
            with self.subTest(decision):
                _, result = run(FakeGitHub([summary(reviewDecision=decision)]))
                self.assertEqual(result["blockers"], [blocker])

    def test_verified_head_must_match(self):
        self.assertEqual(run(FakeGitHub(), "--head", HEAD)[0], 0)
        for other in ("d" * 40, HEAD[:10], ""):
            with self.subTest(other):
                code, result = run(FakeGitHub(), "--head", other)
                self.assertEqual(code, 2)
                self.assertIn("the head moved", result["blockers"][0])


class ReviewGate(unittest.TestCase):
    def test_head_without_the_review_status_blocks(self):
        """The rollup covers only the last commit, so a status left on an older one is absent."""
        for checks in ([check_run()], []):
            with self.subTest(checks=checks):
                code, result = run(FakeGitHub(checks=checks, review=None))
                self.assertEqual((code, result["blockers"]), (2, [pr_state.REVIEW_BLOCKER]))

    def test_review_blocker_sends_every_head_to_the_loop(self):
        self.assertEqual(pr_state.REVIEW_BLOCKER, "no passing 'review-fix-loop' status on this "
                                                  "head; run Review Fix Loop on it")

    def test_passing_review_status_lets_the_head_land(self):
        code, result = run(FakeGitHub())
        self.assertEqual((code, result["status"], result["review_status"]["state"]),
                         (0, "ready", "pass"))

    def test_ci_rules_are_unchanged_beside_a_passing_review_status(self):
        cases = (([check_run(conclusion="FAILURE")], "required check failed: ci https://ci/ci"),
                 ([check_run(conclusion="FAILURE", required=False)],
                  "check failed, and GitHub requires none here: ci https://ci/ci"))
        for checks, blocker in cases:
            with self.subTest(blocker=blocker):
                code, result = run(FakeGitHub(checks=checks))
                self.assertEqual((code, result["blockers"]), (2, [blocker]))

    def test_closed_and_merged_prs_need_no_review_status(self):
        merged = summary(state="MERGED", mergeCommit={"oid": "c" * 40})
        self.assertEqual(run(FakeGitHub([merged], review=None))[1]["status"], "merged")
        code, result = run(FakeGitHub([summary(state="CLOSED")], review=None))
        self.assertEqual((code, result["blockers"]), (2, ["the PR is closed"]))

    def test_review_status_other_than_success_blocks(self):
        for state in ("PENDING", "EXPECTED", "FAILURE", "ERROR"):
            for merge_state in ("CLEAN", "UNSTABLE"):
                with self.subTest(state=state, merge_state=merge_state):
                    code, result = run(FakeGitHub([summary(mergeStateStatus=merge_state)],
                                                  review=review_status(state)))
                    self.assertEqual((code, result["blockers"], result["pending"]),
                                     (2, [pr_state.REVIEW_BLOCKER], []))

    def test_same_named_job_is_a_ci_check_not_the_record(self):
        code, result = run(FakeGitHub(checks=[check_run("review-fix-loop")], review=None))
        self.assertEqual((code, result["blockers"]), (2, [pr_state.REVIEW_BLOCKER]))
        self.assertIsNone(result["review_status"])
        self.assertEqual([check["name"] for check in result["checks"]], ["review-fix-loop"])

    def test_only_the_status_counts_in_any_order_across_pages(self):
        job, status = check_run("review-fix-loop"), review_status("FAILURE")
        for nodes in ([job, status], [status, job]):
            with self.subTest(first=nodes[0]["__typename"]):
                code, result = run(FakeGitHub(checks=nodes, review=None, page_size=1))
                self.assertEqual((code, result["blockers"]), (2, [pr_state.REVIEW_BLOCKER]))
                self.assertEqual(result["review_status"]["state"], "fail")
                self.assertEqual([check["state"] for check in result["checks"]], ["pass"])

    def test_failed_same_named_job_blocks_beside_a_passing_status(self):
        failed_job = check_run("review-fix-loop", conclusion="FAILURE")
        code, result = run(FakeGitHub(checks=[failed_job]))
        self.assertEqual((code, result["blockers"]),
                         (2, ["required check failed: review-fix-loop https://ci/review-fix-loop"]))

    def test_required_review_status_is_not_a_ci_check(self):
        _, result = run(FakeGitHub(review=review_status("ERROR", required=True)))
        self.assertEqual(result["blockers"], [pr_state.REVIEW_BLOCKER])
        self.assertEqual([check["name"] for check in result["checks"]], ["ci"])


PROVISIONAL_BODY = ("## Summary\nAdds the list.\n\n## Provisional\n"
                    "Rests on secret-plan #12; clears when it merges.\n")


class Provisional(unittest.TestCase):
    def test_ready_pr_with_the_heading_is_blocked_without_its_text(self):
        code, result = run(FakeGitHub([summary(body=PROVISIONAL_BODY)]))
        self.assertEqual((code, result["status"]), (2, "blocked"))
        self.assertEqual(result["blockers"], [pr_state.PROVISIONAL_BLOCKER])
        self.assertNotIn("secret-plan", json.dumps(result))

    def test_armed_or_queued_pr_with_the_heading_is_blocked_not_pending(self):
        for armed in ({"isInMergeQueue": True},
                      {"autoMergeRequest": {"enabledAt": "2026-11-08T09:00:00Z"}}):
            with self.subTest(armed=armed):
                code, result = run(FakeGitHub([summary(body=PROVISIONAL_BODY, **armed)]))
                self.assertEqual((code, result["status"]), (2, "blocked"))
                self.assertIn(pr_state.PROVISIONAL_BLOCKER, result["blockers"])

    def test_heading_blocks_wherever_it_appears(self):
        nested_fences = ("````markdown\n```python\nexample()\n````\n\n"
                         "## Provisional\nHeld until the dependency merges.\n")
        for body in ("```\n## Provisional\n```\n", nested_fences, "## Provisional \r\n"):
            with self.subTest(body=body):
                code, result = run(FakeGitHub([summary(body=body)]))
                self.assertEqual((code, result["blockers"]), (2, [pr_state.PROVISIONAL_BLOCKER]))

    def test_pr_without_the_heading_is_unaffected(self):
        for body in ("## Summary\nNo provisional work here.\n", "##Provisional\n",
                     "## Provisional notes\n", None):
            with self.subTest(body=body):
                code, result = run(FakeGitHub([summary(body=body)]))
                self.assertEqual((code, result["status"], result["blockers"]), (0, "ready", []))

    def test_body_edit_during_the_read_is_reread(self):
        github = FakeGitHub([summary(), summary(body=PROVISIONAL_BODY),
                             summary(body=PROVISIONAL_BODY)])
        self.assertEqual(run(github)[1]["status"], "blocked")


class Feedback(unittest.TestCase):
    def test_open_thread_blocks_and_carries_its_text(self):
        code, result = run(FakeGitHub(threads=[thread()]))
        self.assertEqual((code, result["blockers"]), (2, ["1 review thread(s) still open"]))
        self.assertEqual(result["threads"][0]["comments"]["nodes"][0]["body"], "fix 1")

    def test_resolved_thread_is_kept_but_does_not_block(self):
        code, result = run(FakeGitHub(threads=[thread(resolved=True)]))
        self.assertEqual((code, len(result["threads"])), (0, 1))

    def test_long_thread_is_read_to_its_last_comment(self):
        long_thread = [thread_comment(number) for number in range(1, 6)]
        code, result = run(FakeGitHub(threads=[thread(resolved=True, more_comments=True)],
                                      thread_comments=long_thread, page_size=2))
        self.assertEqual(code, 0)
        self.assertEqual(len(result["threads"][0]["comments"]["nodes"]), 5)

    def test_every_page_is_read(self):
        threads = [thread(resolved=True) for _ in range(5)]
        comments = [comment() for _ in range(5)]
        github = FakeGitHub(threads=threads, comments=comments, checks=[
            check_run(str(index)) for index in range(4)] + [
            check_run("last", conclusion="FAILURE")], page_size=2)
        code, result = run(github)
        self.assertEqual((len(result["threads"]), len(result["comments"])), (5, 5))
        self.assertEqual(code, 2)
        self.assertIn("required check failed: last https://ci/last", result["blockers"])

    def test_open_thread_on_a_later_page_blocks(self):
        threads = [thread(resolved=True) for _ in range(3)] + [thread()]
        self.assertEqual(run(FakeGitHub(threads=threads, page_size=1))[0], 2)

    def test_every_comment_needs_settling_even_after_a_later_push(self):
        code, result = run(FakeGitHub(comments=[comment("2026-01-01T00:00:00Z")]))
        self.assertEqual((code, result["to_settle"]), (0, ["comment: https://c/2"]))

    def test_hidden_comments_are_kept_but_not_flagged(self):
        _, result = run(FakeGitHub(comments=[comment(minimized=True)]))
        self.assertEqual((len(result["comments"]), result["to_settle"]), (1, []))

    def test_review_with_a_body_needs_settling(self):
        _, result = run(FakeGitHub(reviews=[review()]))
        self.assertEqual(result["to_settle"], ["review: https://c/3"])
        _, result = run(FakeGitHub(reviews=[review(body="")]))
        self.assertEqual(result["to_settle"], [])


class Reading(unittest.TestCase):
    def test_head_that_moves_once_is_reread(self):
        moved = summary(headRefOid="e" * 40)
        code, result = run(FakeGitHub([summary(), moved, moved, moved]))
        self.assertEqual((code, result["summary"]["headRefOid"]), (0, "e" * 40))

    def test_any_change_during_the_read_is_reread(self):
        for changes in ({"baseRefName": "release", "baseRef": base_tip("c")},
                        {"baseRef": base_tip("c")},
                        {"isDraft": True},
                        {"reviewDecision": "CHANGES_REQUESTED"},
                        {"comments": {"totalCount": 1}},
                        {"reviews": {"totalCount": 1}},
                        {"reviewThreads": {"totalCount": 1}},
                        {"mergeable": "CONFLICTING", "mergeStateStatus": "DIRTY"}):
            with self.subTest(changes):
                changed = summary(**changes)
                _, result = run(FakeGitHub([summary(), changed, changed, changed]))
                self.assertEqual({key: result["summary"][key] for key in changes}, changes)

    def test_changed_mergeability_is_not_reported_ready(self):
        dirty = summary(mergeable="CONFLICTING", mergeStateStatus="DIRTY")
        code, result = run(FakeGitHub([summary(), dirty, dirty, dirty]))
        self.assertEqual((code, result["blockers"]), (2, ["the branch conflicts with its base"]))

    def test_behind_count_measures_from_the_live_base_tip(self):
        github = FakeGitHub()
        run(github)
        self.assertEqual(github.compared[0], f"repos/o/r/compare/{'b' * 40}...{HEAD}")

    def test_a_pr_that_keeps_changing_is_an_error(self):
        heads = [summary(headRefOid=character * 40) for character in "abcdefg"]
        code, message = run(FakeGitHub(heads))
        self.assertEqual(code, 1)
        self.assertIn("kept changing", message)

    def test_failed_gh_is_an_error(self):
        def fails(_):
            raise pr_state.ReadError("gh: rate limit exceeded")

        code, message = run(fails)
        self.assertEqual(code, 1)
        self.assertIn("rate limit exceeded", message)

    def test_url_from_gh_gives_the_repository(self):
        self.assertEqual(pr_state.resolve_target(FakeGitHub(), "7"),
                         {"owner": "o", "name": "r", "number": 7})


if __name__ == "__main__":
    unittest.main()
