"""Check required skill fields, source entries, and local Markdown targets.

Markdown fragments support ATX/Setext headings and explicit HTML id/name
anchors. Generated anchors use rendered inline text (including image alt text),
lowercase Unicode letters/numbers/marks, retain underscores and hyphens, remove
punctuation/symbols, replace spaces with hyphens, and suffix duplicates with -1,
-2, etc. Custom anchors do not affect heading numbering. Code examples and YAML
frontmatter do not declare anchors. Fragments on non-Markdown files are unchecked.
GitHub's heading rules:
https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links
"""

from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
import yaml


class RenderedHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.anchors = set()

    def handle_data(self, data):
        self.text.append(data)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.anchors.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.anchors.add(attrs["name"])
        if tag == "img":
            self.text.append(attrs.get("alt", ""))


def markdown_anchors(tokens, markdown):
    html = RenderedHTML()
    html.feed(markdown.renderer.render(tokens, markdown.options, {}))
    headings = set()
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        heading = RenderedHTML()
        heading.feed(markdown.renderer.renderInline(
            tokens[index + 1].children or [], markdown.options, {},
        ))
        text = "".join(heading.text).lower()
        slug = "".join(character for character in text if character in " _-"
                       or unicodedata.category(character)[0] in "LNM").replace(" ", "-")
        anchor = slug
        suffix = 0
        while anchor in headings:
            suffix += 1
            anchor = f"{slug}-{suffix}"
        headings.add(anchor)
    return headings | html.anchors


ROOT = Path(__file__).resolve().parents[1]
errors = []
files = [ROOT / p for p in subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
    cwd=ROOT, text=True,
).splitlines()]
files = [path for path in files if path.is_file()]
sources = (ROOT / "SOURCES.md").read_text()
skills = sorted({ROOT / "skills" / p.relative_to(ROOT).parts[1]
                 for p in files if p.relative_to(ROOT).parts[0] == "skills"})
for folder in skills:
    if not folder.is_dir():
        errors.append(f"skills/{folder.name}: expected a skill folder")
        continue
    skill = folder / "SKILL.md"
    if not skill.is_file():
        errors.append(f"skills/{folder.name}: missing SKILL.md")
        continue
    text = skill.read_text()
    source_name = folder.name
    frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not frontmatter:
        errors.append(f"{skill.relative_to(ROOT)}: missing frontmatter")
    else:
        try:
            metadata = yaml.safe_load(frontmatter[1])
        except yaml.YAMLError as error:
            errors.append(f"{skill.relative_to(ROOT)}: invalid YAML: {error}")
            continue
        for field in ("name", "description"):
            value = metadata.get(field) if isinstance(metadata, dict) else None
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{skill.relative_to(ROOT)}: missing or empty {field}")
        name = metadata.get("name") if isinstance(metadata, dict) else None
        if isinstance(name, str) and name.strip():
            source_name = name.strip()
            if source_name != folder.name:
                errors.append(
                    f"{skill.relative_to(ROOT)}: name {source_name!r} "
                    f"does not match folder {folder.name!r}"
                )
        agent_file = folder / "agents" / "openai.yaml"
        try:
            agent_settings = yaml.safe_load(agent_file.read_text()) if agent_file.is_file() else {}
        except yaml.YAMLError as error:
            errors.append(f"{agent_file.relative_to(ROOT)}: invalid YAML: {error}")
            continue
        policy = agent_settings.get("policy", {}) if isinstance(agent_settings, dict) else {}
        claude_manual = isinstance(metadata, dict) and metadata.get("disable-model-invocation") is True
        codex_manual = isinstance(policy, dict) and policy.get("allow_implicit_invocation") is False
        if claude_manual != codex_manual:
            errors.append(f"skills/{folder.name}: invocation policy differs between SKILL.md and agents/openai.yaml")
    if f"\n## {source_name}\n" not in sources:
        errors.append(
            f"skills/{folder.name}: missing SOURCES.md entry for {source_name}"
        )

markdown = MarkdownIt().enable("strikethrough")
documents = {}


def document(path):
    path = path.resolve()
    if path not in documents:
        text = re.sub(r"\A---\n.*?\n---(?:\n|$)", "", path.read_text(), count=1, flags=re.S)
        tokens = markdown.parse(text)
        documents[path] = (tokens, markdown_anchors(tokens, markdown))
    return documents[path]


for path in files:
    if path.suffix.lower() != ".md":
        continue
    tokens, _ = document(path)
    targets = []
    for token in tokens:
        for child in token.children or []:
            if child.type == "link_open":
                targets.append(child.attrGet("href"))
            elif child.type == "image":
                targets.append(child.attrGet("src"))
    for target in targets:
        if target is None:
            continue
        link = urlsplit(target)
        if link.scheme or link.netloc or link.path.startswith("/"):
            continue
        destination = path.parent / unquote(link.path) if link.path else path
        if not destination.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target {target}")
        elif link.fragment and destination.is_file() and destination.suffix.lower() == ".md":
            _, anchors = document(destination)
            if unquote(link.fragment) not in anchors:
                errors.append(f"{path.relative_to(ROOT)}: missing Markdown anchor {target}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Checked {len(skills)} skills and local Markdown paths/anchors.")
