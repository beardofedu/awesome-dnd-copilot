import copy
import json
import unittest
from pathlib import Path

from validate_state import validate


SAMPLE = json.loads(Path(__file__).with_name("state.example.json").read_text(encoding="utf-8"))


class ValidateFactionWorldClocksTests(unittest.TestCase):
    def test_example_is_valid(self):
        self.assertEqual(validate(copy.deepcopy(SAMPLE)), [])

    def test_schema_version_must_be_an_integer(self):
        state = copy.deepcopy(SAMPLE)
        state["schemaVersion"] = True
        self.assertIn("$.schemaVersion: expected 1", validate(state))

    def test_resource_amount_key_is_required_but_may_be_null(self):
        state = copy.deepcopy(SAMPLE)
        del state["factions"][1]["resources"][0]["amount"]
        self.assertIn(
            "$.factions[1].resources[0].amount: required key is missing",
            validate(state),
        )
        self.assertEqual(validate(copy.deepcopy(SAMPLE)), [])

    def test_review_status_must_be_an_allowed_string(self):
        for invalid in ([], {}):
            state = copy.deepcopy(SAMPLE)
            state["reviewStatus"] = invalid
            self.assertIn(
                "$.reviewStatus: expected sample, draft, or approved",
                validate(state),
            )

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

    def test_proposal_text_arrays_require_nonempty_strings(self):
        for field in ("costs", "visibleSigns", "alternativeResponses", "uncertainties"):
            for invalid in (None, {}, 1, ""):
                state = copy.deepcopy(SAMPLE)
                state["proposals"][0][field][0] = invalid
                self.assertTrue(
                    any(f"$.proposals[0].{field}[0]: expected a non-empty string" == error
                        for error in validate(state)),
                    (field, invalid),
                )

    def test_proposal_cannot_change_the_same_clock_twice(self):
        state = copy.deepcopy(SAMPLE)
        first_change = state["proposals"][0]["changes"][0]
        first_change["delta"] = 3
        first_change["resultingValue"] = 4
        second_change = copy.deepcopy(first_change)
        second_change["id"] = "change-wardens-watch-again"
        state["proposals"][0]["changes"].append(second_change)
        errors = validate(state)
        self.assertTrue(
            any("duplicate clock change for 'clock-bridge-watch'" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
