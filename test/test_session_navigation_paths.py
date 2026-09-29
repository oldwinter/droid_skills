#!/usr/bin/env python3
"""Keep session-navigation examples copyable on a local machine."""

import os
import subprocess
import tempfile
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

    def test_recent_sessions_select_exactly_one_folder(self):
        recent = section("### 查看项目的最近会话", "### 按内容搜索")
        self.assertIn('project_dir=$(select_project_dir "myapp") || exit 1', recent)
        self.assertIn('"$project_dir"', recent)
        self.assertNotIn("grep", recent)
        self.assertNotIn("head -1)", recent)
        self.assertNotIn("for f in $(ls", recent)
        self.assertIn("while IFS= read -r -d '' f", recent)
        self.assertNotIn("-Users-enoreyes-code-work-myapp", recent)

    def test_project_selector_preserves_spaces_and_rejects_ambiguity(self):
        recent = section("### 查看项目的最近会话", "### 按内容搜索")
        lines = recent.splitlines()
        start = lines.index('sessions_root="$HOME/.factory/sessions"')
        end = lines.index('project_dir=$(select_project_dir "myapp") || exit 1')
        selector = chr(10).join(lines[start : end + 1])
        selector += chr(10) + 'echo -n "$project_dir"'

        with tempfile.TemporaryDirectory() as temp_dir:
            sessions_root = Path(temp_dir) / ".factory" / "sessions"
            sessions_root.mkdir(parents=True)
            expected = sessions_root / "-home-user-My Project-myapp"
            expected.mkdir()
            env = {**os.environ, "HOME": temp_dir}
            one = subprocess.run(
                ["bash", "-c", selector],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            (sessions_root / "-home-user-other-myapp").mkdir()
            many = subprocess.run(
                ["bash", "-c", selector],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            for path in sessions_root.iterdir():
                path.rmdir()
            none = subprocess.run(
                ["bash", "-c", selector],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(one.returncode, 0, one.stderr)
        self.assertEqual(one.stdout, str(expected))
        self.assertNotEqual(many.returncode, 0)
        self.assertNotEqual(none.returncode, 0)

    def test_recent_session_sorter_preserves_spaces_and_limits_results(self):
        recent = section("### 查看项目的最近会话", "### 按内容搜索")
        lines = recent.splitlines()
        start = lines.index("""  python3 - "$project_dir" <<'PY'""")
        end = lines.index("PY", start + 1)
        script = chr(10).join(lines[start + 1 : end])
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "project with spaces"
            project_dir.mkdir()
            for index in range(12):
                path = project_dir / f"session-{index:02d}.jsonl"
                path.write_text("{}" + chr(10), encoding="utf-8")
                os.utime(path, (index, index))
            result = subprocess.run(
                ["python3", "-", str(project_dir)],
                input=script.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        paths = [Path(os.fsdecode(raw)) for raw in result.stdout.split(bytes([0])) if raw]
        self.assertEqual(len(paths), 10)
        self.assertEqual(paths[0].name, "session-11.jsonl")
        self.assertEqual(paths[-1].name, "session-02.jsonl")
        self.assertTrue(all("project with spaces" in str(path) for path in paths))

    def test_search_and_read_use_local_folder_names(self):
        search = section("### 按内容搜索", "## 阅读会话")
        read = section("## 阅读会话", "## 常见情况")
        self.assertIn('project_dir=$(select_project_dir "myapp") || exit 1', search)
        self.assertIn('api_dir=$(select_project_dir "api") || exit 1', search)
        self.assertNotIn("grep", search)
        self.assertIn('project_dir=$(select_project_dir "myapp") || exit 1', read)
        self.assertIn('"$project_dir"', read)
        for block in (search, read):
            self.assertNotIn("-Users-enoreyes-", block)

    def test_read_commands_select_and_quote_a_real_session_file(self):
        read = section("## 阅读会话", "## 常见情况")
        self.assertNotIn("<uuid>.jsonl", read)
        self.assertNotIn("<uuid>.settings.json", read)
        self.assertIn("session_file=$(find", read)
        self.assertIn('[[ -z "$session_file" ]]', read)
        self.assertIn('head -1 "$session_file"', read)
        self.assertIn('wc -l "$session_file"', read)

    def test_topic_search_derives_first_path_relative_to_sessions_root(self):
        topic = section("### 找到有关某个主题的项目会话", "## 阅读会话")
        self.assertNotIn("cut -d'/' -f1-5", topic)
        self.assertIn('relative=${file#"$sessions_root"/}', topic)
        self.assertIn('echo "${relative%%/*}"', topic)

        commands = [
            'relative=${file#"$sessions_root"/}',
            'echo "${relative%%/*}"',
        ]
        script = chr(10).join(
            ['sessions_root=$1', 'file=$2', *commands]
        )
        cases = (
            ("/Users/alice/.factory/sessions", "-Users-alice-code-app"),
            ("/home/alice/.factory/sessions", "-home-alice-code-app"),
        )
        for root, project in cases:
            result = subprocess.run(
                ["bash", "-c", script, "bash", root, f"{root}/{project}/id.jsonl"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), project)


if __name__ == "__main__":
    unittest.main()
