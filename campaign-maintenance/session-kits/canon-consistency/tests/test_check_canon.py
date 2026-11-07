import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import mock_open, patch


KIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_canon", KIT / "check_canon.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
EXAMPLE = json.loads((KIT / "canon.example.json").read_text(encoding="utf-8"))


class ValidationTests(unittest.TestCase):
    def test_example_accepts_unknown_and_draft_without_judging_narrative(self):
        self.assertEqual(checker.validate(EXAMPLE), [])

    def test_duplicate_and_unresolved_references(self):
        data = copy.deepcopy(EXAMPLE)
        data["facts"][1]["id"] = data["facts"][0]["id"]
        data["facts"][1]["references"] = ["missing", "missing"]
        errors = checker.validate(data)
        self.assertEqual([(e["code"], e["path"]) for e in errors], [
            ("duplicate_id", "/facts/1/id"),
            ("duplicate_reference", "/facts/1/references/1"),
            ("unresolved_reference", "/facts/1/references/0"),
        ])

    def test_types_missing_unknown_and_bad_values(self):
        data = {"schemaVersion": True, "rulesVersion": None,
                "facts": [{"id": "Bad ID", "status": "approved",
                           "text": " ", "references": [None], "extra/key": 1}]}
        errors = checker.validate(data)
        self.assertEqual([(e["code"], e["path"]) for e in errors], [
            ("version", "/schemaVersion"), ("rules_version", "/rulesVersion"),
            ("missing", "/facts/0/source"), ("unknown", "/facts/0/extra~1key"),
            ("id", "/facts/0/id"), ("status", "/facts/0/status"),
            ("text", "/facts/0/text"), ("reference", "/facts/0/references/0"),
        ])

    def test_non_object_and_non_array(self):
        self.assertEqual(checker.validate([])[0]["path"], "")
        data = copy.deepcopy(EXAMPLE)
        data["facts"] = {}
        self.assertEqual(checker.validate(data)[0]["path"], "/facts")

    def test_edition_options_and_forward_reference(self):
        data = copy.deepcopy(EXAMPLE)
        data["facts"].reverse()
        for edition in ("2014", "2024", "unknown"):
            data["rulesVersion"] = edition
            self.assertEqual(checker.validate(data), [])


class CommandTests(unittest.TestCase):
    def invoke(self, argv):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = checker.main(argv)
        return status, json.loads(output.getvalue())

    def test_valid_file_and_usage(self):
        status, result = self.invoke(["check_canon.py", str(KIT / "canon.example.json")])
        self.assertEqual((status, result), (0, {"ok": True, "diagnostics": []}))
        status, result = self.invoke(["check_canon.py"])
        self.assertEqual((status, result["diagnostics"][0]["code"]), (2, "usage"))

    def test_malformed_duplicate_keys_nonfinite_and_missing_file(self):
        for raw in ('{', '{"a":1,"a":2}', '{"value":NaN}'):
            with self.subTest(raw=raw), patch("pathlib.Path.open", mock_open(read_data=raw)):
                status, result = self.invoke(["check_canon.py", "test.json"])
                self.assertEqual((status, result["diagnostics"][0]["code"]), (2, "input"))
        status, result = self.invoke(["check_canon.py", str(KIT / "does-not-exist.json")])
        self.assertEqual((status, result["diagnostics"][0]["code"]), (2, "input"))

    def test_validation_exit_code(self):
        with patch("pathlib.Path.open", mock_open(read_data='{"schemaVersion":1,"rulesVersion":"unknown","facts":[{}]}')):
            status, result = self.invoke(["check_canon.py", "test.json"])
        self.assertEqual(status, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["diagnostics"][0]["code"], "missing")


if __name__ == "__main__":
    unittest.main()
