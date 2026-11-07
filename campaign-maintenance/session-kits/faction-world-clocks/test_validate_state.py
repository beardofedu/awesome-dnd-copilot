import copy
import json
import unittest
from pathlib import Path

from validate_state import validate


SAMPLE = json.loads(Path(__file__).with_name("state.example.json").read_text(encoding="utf-8"))


class ValidateFactionWorldClocksTests(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(validate(copy.deepcopy(SAMPLE)), [])

    def test_clock_thresholds_are_inclusive_and_out_of_range_is_rejected(self):
        for value in (0, 6):
            state = copy.deepcopy(SAMPLE)
            state["clocks"][0]["value"] = value
            change = state["proposals"][0]["changes"][0]
            change["delta"] = 1 if value == 0 else -1
            change["resultingValue"] = value + change["delta"]
            self.assertEqual(validate(state), [])
        state = copy.deepcopy(SAMPLE)
        state["clocks"][0]["value"] = 7
        self.assertTrue(any("inclusive range 0..6" in error for error in validate(state)))

    def test_proposed_deltas_must_stay_inside_clock_range_and_match_result(self):
        for delta, result in ((-1, 0), (5, 6)):
            state = copy.deepcopy(SAMPLE)
            change = state["proposals"][0]["changes"][0]
            state["clocks"][0]["value"] = 1 if delta == -1 else 1
            change["delta"] = delta
            change["resultingValue"] = result
            self.assertEqual(validate(state), [])
        for delta, result in ((-2, -1), (6, 7)):
            state = copy.deepcopy(SAMPLE)
            change = state["proposals"][0]["changes"][0]
            state["clocks"][0]["value"] = 1
            change["delta"] = delta
            change["resultingValue"] = result
            self.assertTrue(any("outside 0..6" in error for error in validate(state)))

    def test_integer_fields_reject_booleans_and_fractions(self):
        for invalid in (True, 1.5):
            state = copy.deepcopy(SAMPLE)
            state["clocks"][0]["value"] = invalid
            self.assertTrue(any("$.clocks[0].value" in error for error in validate(state)))

    def test_unknown_references_and_duplicate_ids_are_reported(self):
        state = copy.deepcopy(SAMPLE)
        state["clocks"][0]["factionId"] = "missing-faction"
        state["proposals"][0]["changes"][0]["clockId"] = "missing-clock"
        state["proposals"][0]["sourceRefs"] = ["missing-source"]
        state["factions"][1]["id"] = state["factions"][0]["id"]
        errors = validate(state)
        self.assertTrue(any("unknown faction" in error for error in errors))
        self.assertTrue(any("unknown clock" in error for error in errors))
        self.assertTrue(any("unknown source" in error for error in errors))
        self.assertTrue(any("duplicate ID" in error for error in errors))

    def test_stale_base_revision_is_rejected(self):
        state = copy.deepcopy(SAMPLE)
        state["proposals"][0]["baseRevision"] = "reedbridge-r6"
        self.assertTrue(any("stale proposal" in error for error in validate(state)))

    def test_zero_delta_is_rejected(self):
        state = copy.deepcopy(SAMPLE)
        state["proposals"][0]["changes"][0]["delta"] = 0
        self.assertTrue(any("nonzero integer" in error for error in validate(state)))


if __name__ == "__main__":
    unittest.main()
