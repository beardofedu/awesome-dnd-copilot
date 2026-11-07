import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import run
from contracts import ROOT, SAMPLE_PATHS, check_state
from run import _fixture_results, _source_sample_results


class FixtureContractTests(unittest.TestCase):
    def test_every_fixture_matches_its_declared_expectation(self):
        mismatches = [
            (name, errors, expected)
            for name, passed, errors, expected in _fixture_results()
            if not passed
        ]
        self.assertEqual([], mismatches)

    def test_checked_in_state_examples_are_complete_and_referenced(self):
        mismatches = [
            (name, errors)
            for name, passed, errors, _ in _source_sample_results()
            if not passed
        ]
        self.assertEqual([], mismatches)

    def test_contract_rejects_non_object_schema_input(self):
        self.assertTrue(check_state([], {}))
        self.assertTrue(check_state({"kit": []}, {}))

    def test_record_fields_validate_types_and_known_facts(self):
        state = json.loads((ROOT / SAMPLE_PATHS["party-journal"]).read_text(encoding="utf-8"))
        state["quests"][0]["title"] = []
        errors = check_state(state, run.SAMPLE_REFS["party-journal"])
        self.assertIn("output.quests[0].title must be a non-empty string", errors)

        state = json.loads((ROOT / SAMPLE_PATHS["session-bridge"]).read_text(encoding="utf-8"))
        state["events"][0]["text"] = {}
        errors = check_state(state, run.SAMPLE_REFS["session-bridge"])
        self.assertIn("output.events[0].text must be a non-empty string", errors)

        state = json.loads((ROOT / SAMPLE_PATHS["dm-session-cockpit"]).read_text(encoding="utf-8"))
        state["scenes"][0]["done"] = "false"
        state["npcs"][0]["knownFacts"] = ["valid fact", {}]
        errors = check_state(state, run.SAMPLE_REFS["dm-session-cockpit"])
        self.assertIn("output.scenes[0].done must be boolean", errors)
        self.assertIn("output.npcs[0].knownFacts[1] must be a non-empty string", errors)

    def test_bridge_suggestions_may_cite_observations(self):
        state = json.loads((ROOT / SAMPLE_PATHS["session-bridge"]).read_text(encoding="utf-8"))
        state["suggestions"][0]["sourceRef"] = "fictional sample notes"
        self.assertEqual([], check_state(state, run.SAMPLE_REFS["session-bridge"]))

    def test_combatants_must_be_objects_and_ids_are_validated_safely(self):
        state = json.loads((ROOT / SAMPLE_PATHS["dm-session-cockpit"]).read_text(encoding="utf-8"))
        state["combat"]["combatants"] = [None]
        errors = check_state(state, run.SAMPLE_REFS["dm-session-cockpit"])
        self.assertIn("output.combat.combatants[0] must be an object", errors)

        state["combat"]["combatants"] = [{"id": []}]
        errors = check_state(state, run.SAMPLE_REFS["dm-session-cockpit"])
        self.assertTrue(any("output.combat.combatants[0].id" in error for error in errors))

    def test_sample_path_requires_its_assigned_kit(self):
        with patch.object(run, "ROOT", ROOT), patch.object(
            run, "SAMPLE_PATHS", {"session-bridge": SAMPLE_PATHS["party-journal"]}
        ):
            mismatches = {
                name: errors
                for name, passed, errors, _ in run._source_sample_results()
                if not passed
            }
        self.assertIn("source-state:session-bridge", mismatches)
        self.assertIn("output.kit must be 'session-bridge'", mismatches["source-state:session-bridge"][0])

    def test_fixture_reference_ids_are_normalized_in_both_runner_modes(self):
        fixture_path = HERE / "fixtures" / "accepted-party-journal.json"
        case = json.loads(fixture_path.read_text(encoding="utf-8"))
        case["references"]["approved-notes"]["id"] = "different-approved-id"
        case["output"]["quests"][0]["sourceRef"] = "different-approved-id"
        loaded_cases = {"accepted-party-journal": (fixture_path, case)}
        with patch.object(run, "_load_cases", return_value=loaded_cases):
            self.assertTrue(_fixture_results()[0][1])
            output = io.StringIO()
            with patch.object(sys, "argv", ["run.py", "--check-fixture", "accepted-party-journal.json"]):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(0, run.main())
        self.assertIn("PASS accepted-party-journal.json", output.getvalue())


if __name__ == "__main__":
    unittest.main()
