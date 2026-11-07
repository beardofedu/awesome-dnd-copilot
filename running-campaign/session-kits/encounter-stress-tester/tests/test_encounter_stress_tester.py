import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))
import encounter_stress_tester as tester


def sample():
    return json.loads((KIT / "input.example.json").read_text(encoding="utf-8"))


class EncounterStressTesterTests(unittest.TestCase):
    def test_sample_action_counts_damage_and_xp_budget(self):
        report = tester.analyze(sample())
        self.assertEqual(report["action_counts_per_round"]["party"], [2.0, 2.0])
        self.assertEqual(report["action_counts_per_round"]["monsters"], [2.0, 2.0])
        self.assertEqual(report["xp"]["encounter_total"], [300.0, 300.0])
        self.assertEqual(report["xp"]["budget_result"]["status"], "within")
        self.assertEqual(report["expected_damage_per_round"]["party_focused_on_monster_group"], [12.4, 16.0])

    def test_low_and_high_ac_probability_boundaries_and_rounding(self):
        self.assertEqual(tester._attack_probability(-100, 1000), 0.05)
        self.assertEqual(tester._attack_probability(1000, -100), 0.95)
        self.assertEqual(tester._rounded(1 / 3), 0.3333)

    def test_zero_hp_and_damage_do_not_divide_by_zero(self):
        data = sample()
        data["monsters"][0]["hp"] = 0
        data["monsters"][1]["hp"] = 0
        data["party"][0]["damage_per_hit"] = 0
        data["party"][1]["damage_per_hit"] = 0
        for monster in data["monsters"]:
            monster["damage_per_hit"] = 0
        report = tester.analyze(data)
        self.assertEqual(report["effective_hp"]["monster_total"], [0.0, 0.0])
        self.assertEqual(report["approximate_rounds_to_down"]["one_monster_at_extreme_supplied_hp"], [0.0, 0.0])
        self.assertEqual(report["approximate_rounds_to_down"]["party_member_at_extreme_supplied_hp"], [None, None])

    def test_missing_attack_modifier_is_reported_and_estimate_omitted(self):
        data = sample()
        del data["party"][0]["attack_bonus"]
        report = tester.analyze(data)
        self.assertIsNone(report["expected_damage_per_round"]["party_focused_on_monster_group"])
        self.assertIn("attack_bonus", report["unsupported_or_missing"][0]["missing_fields"])

    def test_user_supplied_unsupported_modifiers_are_visible_not_applied(self):
        data = sample()
        data["party"][0]["resistance"] = "fictional damage type"
        data["assumptions"]["terrain_modifier"] = 2
        report = tester.analyze(data)
        self.assertIn("resistance", report["unsupported_or_missing"][0]["unsupported_fields"])
        self.assertIn("assumptions.terrain_modifier", report["unsupported_input_fields"])
        self.assertIn("resistances", " ".join(report["notes"]))

    def test_supplied_budget_ranges_are_not_collapsed_to_a_guess(self):
        data = sample()
        data["thresholds"]["xp_budget"] = {"min": 250, "max": 350}
        self.assertEqual(tester.analyze(data)["xp"]["budget_result"]["status"], "overlaps")

    def test_invalid_nonfinite_boolean_duplicate_and_missing_values_rejected(self):
        cases = []
        data = sample()
        data["party"][0]["hp"] = True
        cases.append(data)
        data = sample()
        data["monsters"][0]["ac"] = math.inf
        cases.append(data)
        data = sample()
        data["monsters"][0]["hp"] = float("nan")
        cases.append(data)
        data = sample()
        data["monsters"][0]["id"] = data["party"][0]["id"]
        cases.append(data)
        data = sample()
        del data["party"][0]["ac"]
        cases.append(data)
        data = sample()
        del data["party"][0]["id"]
        cases.append(data)
        data = sample()
        data["party"][0]["id"] = "  "
        cases.append(data)
        data = sample()
        data["party"][0]["hp"] = {"min": 9, "max": 2}
        cases.append(data)
        for invalid in cases:
            with self.subTest(invalid=invalid):
                with self.assertRaises(tester.InputError):
                    tester.analyze(invalid)

    def test_arithmetic_overflow_is_reported_as_invalid(self):
        data = sample()
        data["party"][0]["damage_per_hit"] = 1e308
        data["party"][0]["attacks_per_action"] = 1e308
        with self.assertRaises(tester.InputError):
            tester.analyze(data)
        data = sample()
        data["party"][0]["hp"] = 10 ** 10000
        with self.assertRaises(tester.InputError):
            tester.analyze(data)

    def test_zero_damage_time_estimate_is_null(self):
        data = sample()
        for monster in data["monsters"]:
            monster["damage_per_hit"] = 0
        report = tester.analyze(data)
        self.assertEqual(report["expected_damage_per_round"]["monsters_focusing_party_group"], [0.0, 0.0])
        self.assertEqual(report["approximate_rounds_to_down"]["party_member_at_extreme_supplied_hp"], [None, None])

    def test_cli_matches_committed_fictional_output(self):
        result = subprocess.run(
            [sys.executable, str(KIT / "encounter_stress_tester.py"), str(KIT / "input.example.json")],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), json.loads((KIT / "output.example.json").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
