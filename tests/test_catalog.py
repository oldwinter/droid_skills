#!/usr/bin/env python3
"""Keep the README catalog projection aligned with category directories."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CATEGORIES = (
    "automation",
    "documents",
    "incident",
    "installers",
    "missions",
    "qa",
    "review",
    "session",
    "wiki",
)
COUNT_RE = re.compile(r"\*\*(\d+) 个提取的 skill\*\*")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FRONTMATTER_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)


def skill_files() -> list[Path]:
    files: list[Path] = []
    for category in CATEGORIES:
        files.extend(sorted((ROOT / category).glob("*.md")))
    return files


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def claimed_skill_count(text: str) -> int:
    match = COUNT_RE.search(text)
    if match is None:
        raise AssertionError("README must state the extracted skill count")
    return int(match.group(1))


def markdown_link_targets(text: str) -> list[str]:
    targets = []
    for raw in MD_LINK_RE.findall(text):
        target = raw.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        targets.append(target)
    return targets


def frontmatter_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise AssertionError(f"{path} is missing YAML frontmatter")
    block = text.split("---", 2)[1]
    match = FRONTMATTER_NAME_RE.search(block)
    if match is None:
        raise AssertionError(f"{path} is missing name: frontmatter")
    return match.group(1).strip().strip("\"'")


class CatalogProjectionTests(unittest.TestCase):
    def test_category_markdown_count_matches_readme(self):
        files = skill_files()
        self.assertEqual(len(CATEGORIES), 9)
        self.assertEqual(len(files), claimed_skill_count(readme_text()))
        self.assertEqual(len(files), 23)

    def test_each_skill_is_linked_and_name_matches_filename(self):
        text = readme_text()
        missing = []
        mismatched = []
        for path in skill_files():
            rel = path.relative_to(ROOT).as_posix()
            if f"]({rel})" not in text and f"](./{rel})" not in text:
                missing.append(rel)
            name = frontmatter_name(path)
            if name != path.stem:
                mismatched.append(f"{rel}: name={name!r} stem={path.stem!r}")
        self.assertEqual(missing, [], f"README does not link skill files: {missing}")
        self.assertEqual(mismatched, [], f"name: does not match filename: {mismatched}")

    def test_relative_markdown_links_exist(self):
        missing = []
        found = []
        for target in markdown_link_targets(readme_text()):
            if not target.endswith(".md"):
                continue
            found.append(target)
            resolved = (README.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                missing.append(target)
                continue
            if not resolved.is_file():
                missing.append(target)
        self.assertTrue(found, "expected relative .md links in README")
        self.assertEqual(missing, [], f"README links to missing markdown: {missing}")

    def test_unextractable_names_are_not_repo_files(self):
        text = readme_text()
        section = text.split("## 不可提取", 1)[1]
        self.assertIn("不是本 checkout 里的文件", section)
        self.assertIn("没有 `droid-control.md`", section)
        self.assertNotIn("](droid-control.md)", text)
        for path in skill_files():
            self.assertTrue(path.is_file())


class BundleContaminationTests(unittest.TestCase):
    """Skill files must not retain minified JS from the extracted bundle."""

    BUNDLE_MARKERS = (
        re.compile(r"`,[A-Za-z0-9_$]{2,}="),
        re.compile(r"\bvar [A-Za-z0-9_$]{2,}="),
        re.compile(r"systemPrompt:"),
        re.compile(r"metadata:\{"),
    )

    def test_skill_files_have_no_bundle_fragments(self):
        hits = []
        for path in skill_files():
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                for pattern in self.BUNDLE_MARKERS:
                    if pattern.search(line):
                        hits.append(f"{path.relative_to(ROOT)}:{lineno} matches {pattern.pattern}")
        self.assertEqual(hits, [], f"bundle fragments left in skill files: {hits}")


if __name__ == "__main__":
    unittest.main()
