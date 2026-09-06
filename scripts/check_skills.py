"""Check required skill fields, source entries, and inline local Markdown links."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []
files = [ROOT / p for p in subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
    cwd=ROOT, text=True,
).splitlines()]
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
    if f"\n## {folder.name}\n" not in sources:
        errors.append(f"skills/{folder.name}: missing SOURCES.md entry")

for path in files:
    if path.suffix.lower() != ".md" or not path.is_file():
        continue
    text = re.sub(r"```.*?```|~~~.*?~~~", "", path.read_text(), flags=re.S)
    text = re.sub(r"(`+).*?\1", "", text, flags=re.S)
    for target in re.findall(r"\]\(([^\s)]+)\)", text):
        link = urlsplit(target)
        if link.scheme or link.netloc or not link.path or link.path.startswith("/"):
            continue
        if not (path.parent / unquote(link.path)).exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target {target}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Checked {len(skills)} skills and inline local Markdown links.")
