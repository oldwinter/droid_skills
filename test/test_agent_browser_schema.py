#!/usr/bin/env python3
"""Keep the agent-browser tool input boundary strict."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "tools" / "agent_browser.schema.json"


def parameters_schema() -> dict:
    document = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return document["function"]["parameters"]


def accepts(payload: dict) -> bool:
    schema = parameters_schema()
    required = set(schema["required"])
    properties = schema["properties"]
    if not required.issubset(payload):
        return False
    if schema.get("additionalProperties") is False and not set(payload).issubset(properties):
        return False
    command = payload.get("command")
    command_schema = properties["command"]
    return isinstance(command, str) and len(command) >= command_schema["minLength"]


class AgentBrowserSchemaTests(unittest.TestCase):
    def test_schema_rejects_unknown_properties(self):
        self.assertIs(parameters_schema()["additionalProperties"], False)
        self.assertFalse(accepts({"command": "agent-browser snapshot -i", "commmand": "typo"}))

    def test_schema_rejects_empty_command(self):
        self.assertEqual(parameters_schema()["properties"]["command"]["minLength"], 1)
        self.assertFalse(accepts({"command": ""}))

    def test_schema_accepts_documented_command(self):
        self.assertTrue(accepts({"command": "agent-browser snapshot -i"}))


if __name__ == "__main__":
    unittest.main()
