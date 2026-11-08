"""Host adapters for compare.py: one isolated, non-interactive session per call.

Each adapter loads exactly the given skill tree, hides installed skills, plugins,
and user instructions, and keeps raw output, redacted, in the cell's evidence
folder. The runner never copies, replaces or deletes a real login. Flags were
checked against `claude --help` 2.1.318 and `codex exec --help` 0.166.0.
"""

from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

GRACE_SECONDS = 5
SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|AUTH", re.I)


class InvalidEvidence(Exception):
    pass


def secret_values() -> list:
    """Values of inherited variables whose names look secret, longest first. Short values would mangle text."""
    return sorted({v for k, v in os.environ.items() if SECRET_NAME.search(k) and len(v) >= 8}, key=len, reverse=True)


def redact(text: str) -> str:
    for value in secret_values():
        text = text.replace(value, "[REDACTED]")
    return text


def write_atomic(path: Path, text: str) -> None:
    draft = path.with_name(f".{path.name}.partial")
    draft.write_text(redact(text))
    os.replace(draft, path)


def redact_file(path: Path) -> None:
    write_atomic(path, path.read_text(errors="replace"))


def redact_in_place(path: Path) -> None:
    """Redact a text file, keeping its mode. Binary files are left as they are."""
    try:
        text = path.read_text()
    except (UnicodeDecodeError, OSError):
        return
    if redact(text) != text:
        path.write_text(redact(text))


def stop_group(process: subprocess.Popen) -> None:
    """End every process in the session's group: TERM, then KILL after a grace period."""
    def alive():
        process.poll()
        try:
            os.killpg(process.pid, 0)
            return True
        except (ProcessLookupError, PermissionError):  # macOS says EPERM once only zombies remain.
            return False
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except (ProcessLookupError, PermissionError):
            return
        deadline = time.monotonic() + GRACE_SECONDS
        while time.monotonic() < deadline:
            if not alive():
                return
            time.sleep(0.02)


def run_group(command, *, cwd, env, stdout, stderr, timeout):
    """Run in its own process group, which ends with it. Returns the exit code, or None on timeout."""
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=stdout,
                               stderr=stderr, start_new_session=True)
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    finally:  # Also on KeyboardInterrupt and other exceptions.
        stop_group(process)
        process.wait()


@dataclass
class RunResult:
    status: str = "ok"  # ok, error, or timeout
    error: str | None = None
    answer: str = ""
    calls: list | None = None  # [{"name", "path"?, "command"?, "skill"?}]
    tokens: dict | None = None
    cost_usd: float | None = None
    turns: int | None = None
    model: str | None = None
    loaded_skills: list | None = None
    wall_seconds: float = 0.0
    checks: list = field(default_factory=list)

    def read_skill(self, name: str) -> bool:
        marker = f"{name}/SKILL.md"
        return any(call.get("skill") == name or marker in (call.get("path") or "")
                   or marker in (call.get("command") or "") for call in self.calls or [])

    def save(self, out: Path, extra=None) -> None:
        write_atomic(out / "answer.txt", self.answer)
        write_atomic(out / "result.json", json.dumps({**(extra or {}), **asdict(self)}, indent=2))


def frontmatter(skill: Path) -> str:
    text = (skill / "SKILL.md").read_text()
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return match.group(1) if match else ""


def model_invocable(tree: Path) -> list:
    return sorted(skill.name for skill in tree.iterdir() if (skill / "SKILL.md").exists()
                  and not re.search(r"^disable-model-invocation:\s*true\s*$", frontmatter(skill), re.M))


def skill_names(*directories: Path) -> set:
    return {entry.name for directory in directories if directory.is_dir()
            for entry in directory.iterdir() if not entry.name.startswith(".")}


def execute(command, *, cwd, env, out: Path, timeout) -> tuple:
    """Run a host CLI, keeping its redacted stdout and stderr. Returns (exit code or None on timeout, stdout)."""
    with open(out / "raw.jsonl", "w") as stdout, open(out / "stderr.log", "w") as stderr:
        code = run_group(command, cwd=cwd, env=env, stdout=stdout, stderr=stderr, timeout=timeout)
    for name in ("raw.jsonl", "stderr.log"):
        redact_file(out / name)
    return code, (out / "raw.jsonl").read_text()


def events(raw: str):
    for line in raw.splitlines():
        try:
            yield json.loads(line)
        except ValueError:
            continue


class Claude:
    """`claude -p` with stream-json output, project settings only, and the tree as a project skill set."""

    # Claude Code bundles a skill under this installed name, so the leak probe can't tell them apart.
    bundled_names = {"verify"}
    telemetry_notes = ("cost_usd is total_cost_usd as Claude Code reports it. tokens.input excludes cache reads "
                       "and cache writes, which are listed separately; price each at its own rate, never summed.")

    def version(self) -> str:
        return subprocess.check_output(["claude", "--version"], text=True).strip()

    def installed_skill_names(self) -> set:
        return skill_names(Path.home() / ".claude/skills") - self.bundled_names

    def run(self, *, skills, prompt, work, out, settings, scratch, variant) -> RunResult:
        command = ["claude", "-p", "--output-format", "stream-json", "--verbose",
                   "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence",
                   "--model", settings["model"], "--permission-mode", settings.get("permission_mode", "acceptEdits"),
                   "--allowedTools", *settings.get("allowed_tools", ["Bash", "Read", "Skill"])]
        if settings.get("effort"):
            command += ["--effort", settings["effort"]]
        if settings.get("max_budget_usd"):
            command += ["--max-budget-usd", str(settings["max_budget_usd"])]
        if skills is not None:
            shutil.copytree(skills, work / ".claude/skills")
        code, raw = execute([*command, "--", prompt], cwd=work, env=dict(os.environ), out=out,
                            timeout=settings.get("timeout_seconds", 600))
        result = RunResult(calls=[])
        final = None
        for event in events(raw):
            if event.get("type") == "system" and event.get("subtype") == "init":
                result.loaded_skills, result.model = event.get("skills"), event.get("model")
            elif event.get("type") == "assistant":
                for block in event["message"].get("content", []):
                    if block.get("type") == "tool_use":
                        given = block.get("input") or {}
                        result.calls.append({"name": block["name"], "path": given.get("file_path"),
                                             "command": given.get("command"), "skill": given.get("skill"),
                                             "nested": bool(event.get("parent_tool_use_id"))})
            elif event.get("type") == "result":
                final = event
        if final:
            usage = final.get("usage") or {}
            result.answer = final.get("result") or ""
            result.cost_usd = final.get("total_cost_usd")
            result.turns = final.get("num_turns")
            result.tokens = {"input": usage.get("input_tokens"), "cache_read": usage.get("cache_read_input_tokens"),
                             "cache_write": usage.get("cache_creation_input_tokens"),
                             "output": usage.get("output_tokens")}
        if code is None:
            result.status, result.error = "timeout", "the session hit timeout_seconds"
        elif code != 0 or not final or final.get("is_error"):
            result.status = "error"
            result.error = f"claude exited {code}" + (f": {final.get('subtype')}" if final else "; no result event")
        return result


class Codex:
    """`codex exec --json` with a disposable HOME and CODEX_HOME that links only the login.

    A link, not a copy, so refresh-token rotation keeps working: Codex may refresh the
    real login through it, as it does in normal use. The runner itself never copies,
    replaces or deletes that file, and checks after each session that it is still a
    regular file.
    """

    telemetry_notes = ("Codex reports no cost. tokens.* sum turn.completed usage: input_tokens includes "
                       "cached_input_tokens and output_tokens includes reasoning_output_tokens, as in the "
                       "Responses API, so never add the parts; price cached input at its own rate.")

    def version(self) -> str:
        return subprocess.check_output(["codex", "--version"], text=True).strip()

    def codex_home(self) -> Path:
        return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))

    def installed_skill_names(self) -> set:
        return skill_names(Path.home() / ".agents/skills", self.codex_home() / "skills")

    @staticmethod
    def regular(path: Path) -> bool:
        return path.is_file() and not path.is_symlink()

    def run(self, *, skills, prompt, work, out, settings, scratch, variant) -> RunResult:
        home, codex_home = scratch / "home", scratch / "codex-home"
        codex_home.mkdir(parents=True)
        (home / ".agents/skills").mkdir(parents=True)
        login = self.codex_home() / "auth.json"
        if not self.regular(login):
            raise InvalidEvidence(f"{login} must be a regular file; log in with `codex login`")
        for name in ("auth.json", "auth.lock"):
            if (self.codex_home() / name).exists():
                (codex_home / name).symlink_to(self.codex_home() / name)
        if skills is not None:
            shutil.copytree(skills, home / ".agents/skills", dirs_exist_ok=True)
        command = ["codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--ignore-rules",
                   "--disable", "plugins", "--disable", "apps", "--disable", "hooks",
                   "-s", settings.get("sandbox", "workspace-write"), "-m", settings["model"], "-C", str(work)]
        if settings.get("effort"):
            command += ["-c", f'model_reasoning_effort="{settings["effort"]}"']
        env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(codex_home)}
        code, raw = execute([*command, "--", prompt], cwd=work, env=env, out=out,
                            timeout=settings.get("timeout_seconds", 600))
        result = RunResult(calls=[], model=settings["model"])
        usage, failure = {}, None
        for event in events(raw):
            item = event.get("item") or {}
            if event.get("type") == "item.completed":
                kind = item.get("type")
                if kind == "agent_message":
                    result.answer = item.get("text", "")
                elif kind == "command_execution":
                    result.calls.append({"name": "shell", "command": item.get("command")})
                elif kind == "file_change":
                    result.calls += [{"name": "file_change", "path": c.get("path")} for c in item.get("changes", [])]
                elif kind == "mcp_tool_call":
                    result.calls.append({"name": f"mcp:{item.get('server')}.{item.get('tool')}"})
                elif kind not in ("reasoning", "todo_list"):
                    result.calls.append({"name": kind})
            elif event.get("type") == "turn.completed":
                for key, value in (event.get("usage") or {}).items():
                    usage[key] = usage.get(key, 0) + value
            elif event.get("type") in ("turn.failed", "error"):
                failure = json.dumps(event)[:500]
        result.tokens = usage or None
        result.turns = None  # Codex exec reports no model-request count.
        if not self.regular(login):
            failure = (failure or "") + f" {login} is no longer a regular file; check it before the next run."
        elif not (codex_home / "auth.json").is_symlink():
            failure = (failure or "") + " Codex replaced the login link, so the real login may need `codex login`."
        if code is None:
            result.status, result.error = "timeout", "the session hit timeout_seconds"
        elif code != 0 or failure or not usage:
            result.status, result.error = "error", f"codex exited {code}" + (f": {failure}" if failure else "")
        return result


ADAPTERS = {"claude": Claude, "codex": Codex}
