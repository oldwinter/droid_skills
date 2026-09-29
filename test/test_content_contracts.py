#!/usr/bin/env python3
"""Validate user-facing documentation contracts not covered by the catalog."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_BROWSER = ROOT / "automation" / "agent-browser.md"
FENCE = chr(96) * 3


def outside_fences(text: str) -> str:
    visible = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith(FENCE):
            in_fence = not in_fence
            continue
        if not in_fence:
            visible.append(line)
    return chr(10).join(visible)


def markdown_link_targets(text: str):
    for suffix in text.split("](")[1:]:
        yield suffix.split(")", 1)[0]


class ContentContractTests(unittest.TestCase):
    def test_agent_browser_relative_links_resolve_in_checkout(self):
        visible = outside_fences(AGENT_BROWSER.read_text(encoding="utf-8"))
        missing = []
        for raw_target in markdown_link_targets(visible):
            target = raw_target.split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (AGENT_BROWSER.parent / target).resolve().is_file():
                missing.append(raw_target)
        self.assertEqual(missing, [])
        self.assertNotIn("](references/", visible)


if __name__ == "__main__":
    unittest.main()
