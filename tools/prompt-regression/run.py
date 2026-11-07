#!/usr/bin/env python3
"""Run deterministic fixture contracts and verify the checked-in sample states."""

import copy
import argparse
import json
import re
import sys
from pathlib import Path

from contracts import ROOT, SAMPLE_PATHS, SAMPLE_REFS, check_state, read_output

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def _set_path(value, path, replacement):
    parts = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    if not parts:
        raise ValueError(f"unsupported fixture path: {path}")
    keys = [int(part[1:-1]) if part.startswith("[") else part for part in parts]
    target = value
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = replacement


def _load_cases():
    cases = {}
    for path in sorted(FIXTURES.glob("*.json")):
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"{path.name}: cannot read fixture: {error}") from error
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError(f"{path.name}: fixture needs an id")
        if case["id"] in cases:
            raise ValueError(f"{path.name}: duplicate fixture id {case['id']!r}")
        cases[case["id"]] = (path, case)

    resolved = {}
    for case_id, (path, case) in cases.items():
        if case.get("base"):
            base_id = case["base"].removesuffix(".json")
            if base_id not in cases or base_id == case_id:
                raise ValueError(f"{path.name}: unknown or recursive base fixture {base_id!r}")
            base_path, base = cases[base_id]
            output, parse_errors = read_output(base)
            if parse_errors or not isinstance(output, dict):
                raise ValueError(f"{path.name}: base fixture {base_path.name} is not valid JSON")
            case = {
                **case,
                "references": base.get("references", {}),
                "output": copy.deepcopy(output),
            }
            for key, replacement in case.get("set", {}).items():
                _set_path(case["output"], key, replacement)
        resolved[case_id] = (path, case)
    return resolved


def _fixture_references(case):
    refs = {
        entry["id"]: entry["kind"]
        for entry in case.get("references", {}).values()
        if isinstance(entry, dict)
        and isinstance(entry.get("id"), str)
        and entry.get("kind") in {"observation", "proposal"}
    }
    refs.update({
        name: entry["kind"]
        for name, entry in case.get("references", {}).items()
        if isinstance(name, str)
        and isinstance(entry, dict)
        and entry.get("kind") in {"observation", "proposal"}
    })
    return refs


def _fixture_results():
    results = []
    for case_id, (path, case) in _load_cases().items():
        state, parse_errors = read_output(case)
        refs = _fixture_references(case)
        errors = parse_errors or check_state(state, refs, synthetic=case.get("synthetic") is True)
        expected = case.get("expected")
        expected_error = case.get("expectedError")
        passed = (expected == "pass" and not errors) or (
            expected == "fail"
            and bool(errors)
            and isinstance(expected_error, str)
            and any(expected_error in error for error in errors)
        )
        results.append((case_id, passed, errors, expected))
    return results


def _source_sample_results():
    results = []
    for kit, relative in SAMPLE_PATHS.items():
        path = ROOT / relative
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(state, dict):
                errors = check_state(state, SAMPLE_REFS[kit])
            elif state.get("kit") != kit:
                errors = [f"output.kit must be {kit!r} for {relative}"]
            else:
                errors = check_state(state, SAMPLE_REFS[kit])
        except (OSError, json.JSONDecodeError) as error:
            errors = [f"cannot load {relative}: {error}"]
        results.append((f"source-state:{kit}", not errors, errors, "pass"))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-fixture",
        help="check one fixture output as if it were an accepted output (invalid outputs exit nonzero)",
    )
    arguments = parser.parse_args()
    try:
        if arguments.check_fixture:
            fixture_path = Path(arguments.check_fixture)
            if fixture_path.name != arguments.check_fixture or fixture_path.suffix != ".json":
                raise ValueError("--check-fixture accepts a JSON filename from the fixture directory")
            cases = _load_cases()
            if fixture_path.stem not in cases:
                raise ValueError(f"unknown fixture: {fixture_path.name}")
            _, case = cases[fixture_path.stem]
            state, parse_errors = read_output(case)
            refs = _fixture_references(case)
            errors = parse_errors or check_state(state, refs, synthetic=case.get("synthetic") is True)
            if errors:
                print(f"FAIL {fixture_path.name}")
                for error in errors:
                    print(f"  - {error}")
                return 1
            print(f"PASS {fixture_path.name}")
            return 0
        results = _fixture_results() + _source_sample_results()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL runner: {error}", file=sys.stderr)
        return 1
    failed = False
    for name, passed, errors, expected in results:
        label = "PASS" if passed else "FAIL"
        print(f"{label} {name} (expected {expected})")
        if not passed:
            failed = True
            for error in errors or ["fixture result did not match expected outcome"]:
                print(f"  - {error}")
    print(f"{len(results)} checks: {'failed' if failed else 'all expectations met'}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
