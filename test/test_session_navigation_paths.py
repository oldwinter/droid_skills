#!/usr/bin/env python3
"""Keep session-navigation examples copyable on a local machine."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAV = (ROOT / "session" / "session-navigation.md").read_text(encoding="utf-8")


def section(heading: str, next_heading: str) -> str:
    start = NAV.split(heading, 1)[1]
    return start.split(next_heading, 1)[0]


class SessionNavigationPathTests(unittest.TestCase):
    def test_examples_do_not_hardcode_upstream_home(self):
        self.assertNotIn("enoreyes", NAV)
        self.assertNotIn("-Users-enoreyes-", NAV)

    def test_tree_uses_placeholder_not_a_real_user(self):
        tree = section("## 会话存放位置", "## 查找会话")
        self.assertIn("-Users-<you>-", tree)
        self.assertNotIn("-Users-enoreyes-", tree)

    def test_recent_sessions_list_then_grep_folder(self):
        recent = section("### 查看项目的最近会话", "### 按内容搜索")
        self.assertIn("ls ~/.factory/sessions/", recent)
        self.assertIn('grep "myapp"', recent)
        self.assertIn('"$project"', recent)
        self.assertNotIn("-Users-enoreyes-code-work-myapp", recent)

    def test_search_and_read_use_local_folder_names(self):
        search = section("### 按内容搜索", "## 阅读会话")
        read = section("## 阅读会话", "## 常见情况")
        for block in (search, read):
            self.assertIn("ls ~/.factory/sessions/", block)
            self.assertIn('"$project"', block)
            self.assertNotIn("-Users-enoreyes-", block)


if __name__ == "__main__":
    unittest.main()
