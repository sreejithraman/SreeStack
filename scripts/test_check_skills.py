"""Exercise the checker CLI against small Git repositories."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(__file__).with_name("check_skills.py")


class MarkdownLinkChecks(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "scripts").mkdir()
        shutil.copyfile(CHECKER, self.root / "scripts/check_skills.py")
        (self.root / "SOURCES.md").write_text("")
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

    def check(self, files, succeeds=True):
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/check_skills.py")],
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0 if succeeds else 1, result.stderr)
        return result

    def test_relative_and_same_document_headings(self):
        self.check({
            "README.md": "[same](#local-heading) [other](docs/guide.md#setup)\n\n# Local heading\n",
            "docs/guide.md": "Setup\n=====\n",
        })

    def test_missing_and_renamed_heading_fail(self):
        self.check({"README.md": "# Before\n\n[section](#before)\n"})
        result = self.check({"README.md": "# After\n\n[section](#before)\n"}, succeeds=False)
        self.assertIn("README.md: missing Markdown anchor #before", result.stderr)

    def test_rendered_heading_text_and_unicode(self):
        self.check({
            "README.md": "[guide](guide.md#thisll-be-a-helpful-section-about-the-greek-letter-θ)\n"
                         "[formatting](guide.md#api-code-label--image)\n",
            "guide.md": "# This'll be a _Helpful_ Section About the Greek Letter Θ!\n"
                        "# **API** `Code` [Label](https://example.com) &amp; ![Image](image.png)\n",
            "image.png": "dummy",
        })

    def test_duplicates_and_existing_suffixes_remain_unique(self):
        self.check({
            "README.md": "# Setup\n# Setup-1\n# Setup\n# Setup\n\n"
                         "[one](#setup) [two](#setup-1) [three](#setup-2) [four](#setup-3)\n",
        })
        result = self.check({
            "README.md": "# Setup\n# Setup\n\n[missing](#setup-2)\n",
        }, succeeds=False)
        self.assertIn("missing Markdown anchor #setup-2", result.stderr)

    def test_percent_encoded_paths_and_fragments(self):
        self.check({
            "README.md": "[guide](docs/space%20name.md#caf%C3%A9)\n",
            "docs/space name.md": "# Café\n",
        })

    def test_explicit_anchors_and_heading_numbering(self):
        self.check({
            "README.md": '<a name="legacy"></a>\n<div id="custom"></div>\n'
                         '<a name="setup"></a>\n\n# Setup\n# Setup\n\n'
                         '[legacy](#legacy) [custom](#custom) [duplicate](#setup-1)\n',
        })

    def test_code_examples_and_frontmatter_do_not_declare_anchors(self):
        result = self.check({
            "README.md": '---\nname: hidden\n---\n\n'
                         '```md\n# Example\n<a id="fake"></a>\n```\n\n'
                         '[code](#example) [html](#fake) [metadata](#name-hidden)\n',
        }, succeeds=False)
        self.assertIn("missing Markdown anchor #example", result.stderr)
        self.assertIn("missing Markdown anchor #fake", result.stderr)
        self.assertIn("missing Markdown anchor #name-hidden", result.stderr)

    def test_existing_path_checks_and_ignored_link_types(self):
        self.check({
            "README.md": "[web](https://example.com/#anything) [root](/elsewhere.md#anything)\n"
                         "[asset](asset.txt#anything) [directory](docs/) [empty](#)\n",
            "asset.txt": "text",
            "docs/guide.md": "# Guide\n",
        })
        result = self.check({"README.md": "[missing](absent.md#heading)\n"}, succeeds=False)
        self.assertIn("missing link target absent.md#heading", result.stderr)

    def test_reference_links_are_checked(self):
        result = self.check({
            "README.md": "[guide][target]\n\n[target]: guide.md#missing\n",
            "guide.md": "# Existing\n",
        }, succeeds=False)
        self.assertIn("missing Markdown anchor guide.md#missing", result.stderr)

    def test_skill_rejects_same_file_anchor_jump_links(self):
        result = self.check({
            "SOURCES.md": "\n## demo\n",
            "skills/demo/SKILL.md": (
                "---\nname: demo\ndescription: Demo skill.\n---\n\n"
                "# Demo\n\nSee [details](#details) and [self](SKILL.md#details).\n\n"
                "## Details\n"
            ),
        }, succeeds=False)
        self.assertIn("same-file link #details", result.stderr)
        self.assertIn("same-file link SKILL.md#details", result.stderr)

    def test_skill_rejects_back_links_to_own_skill_md_but_allows_other_skills(self):
        self.check({
            "SOURCES.md": "\n## alpha\n\n## beta\n",
            "skills/alpha/SKILL.md": (
                "---\nname: alpha\ndescription: Alpha.\n---\n\n"
                "See [guide](references/guide.md).\n"
            ),
            "skills/alpha/references/guide.md": "Use [beta](../../beta/SKILL.md).\n",
            "skills/beta/SKILL.md": "---\nname: beta\ndescription: Beta.\n---\n\n# Beta\n",
        })
        result = self.check({
            "skills/alpha/references/guide.md": "See [main](../SKILL.md) and [top](../SKILL.md#alpha).\n",
            "skills/alpha/ADR.md": "Apply [rules](SKILL.md#alpha).\n",
            "skills/alpha/SKILL.md": "---\nname: alpha\ndescription: Alpha.\n---\n\n# Alpha\n",
        }, succeeds=False)
        self.assertIn("back-link to SKILL.md: ../SKILL.md", result.stderr)
        self.assertIn("back-link to SKILL.md: ../SKILL.md#alpha", result.stderr)
        self.assertIn("back-link to SKILL.md: SKILL.md#alpha", result.stderr)

    def test_skill_rejects_duplicate_local_links_but_allows_distinct_section_anchors(self):
        self.check({
            "SOURCES.md": "\n## demo\n",
            "skills/demo/SKILL.md": (
                "---\nname: demo\ndescription: Demo.\n---\n\n"
                "Read [guide](references/guide.md), [part a](references/guide.md#part-a), "
                "and [part b](references/guide.md#part-b).\n"
            ),
            "skills/demo/references/guide.md": "# Guide\n\n## Part A\n\n## Part B\n",
        })
        result = self.check({
            "skills/demo/SKILL.md": (
                "---\nname: demo\ndescription: Demo.\n---\n\n"
                "Read [one](references/guide.md) and [two](./references/guide.md).\n"
            ),
        }, succeeds=False)
        self.assertIn("duplicate link target ./references/guide.md", result.stderr)

    def test_duplicate_and_same_file_rules_do_not_restrict_root_docs(self):
        self.check({
            "README.md": (
                "# Top\n\n[top](#top) [a](docs/guide.md) [b](docs/guide.md)\n"
            ),
            "docs/guide.md": "# Guide\n",
        })


if __name__ == "__main__":
    unittest.main()
