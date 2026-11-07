import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from contracts import check_state
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


if __name__ == "__main__":
    unittest.main()
