"""Check a CI diff, auditing all of HEAD when a push's old head is unavailable."""

import os
import re
import subprocess
import sys


def git_output(*args, input=None):
    return subprocess.check_output(["git", *args], input=input, text=True).strip()


def main():
    git_output("rev-parse", "--verify", "HEAD^{commit}")
    base = os.environ.get("BASE_SHA", "")
    if base and not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", base):
        raise ValueError("BASE_SHA must be a full Git object ID")
    if base and set(base) != {"0"}:
        object_type = git_output("cat-file", "--batch-check=%(objecttype)", input=f"{base}\n")
        if object_type == f"{base} missing" and os.environ.get("GITHUB_EVENT_NAME") == "push":
            print("Push base is unavailable; checking all files in HEAD.", flush=True)
            base = ""
        elif object_type != "commit":
            raise ValueError(f"Comparison base {base} is not an available commit")
    else:
        base = ""
    if not base:
        base = git_output("hash-object", "-t", "tree", "--stdin", input="")
    return subprocess.run(["git", "diff", "--check", base, "HEAD"]).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
