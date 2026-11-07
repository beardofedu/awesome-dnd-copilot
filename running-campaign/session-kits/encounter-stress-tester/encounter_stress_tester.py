#!/usr/bin/env python3
"""Deterministic, assumption-driven encounter arithmetic for fictional/user data."""

import argparse
import json
import math
import sys
from pathlib import Path

ROUND_DIGITS = 4
RULES_VERSIONS = {"2014", "2024"}
COMBAT_FIELDS = ("attack_bonus", "damage_per_hit", "attacks_per_action", "actions_per_round")


class InputError(ValueError):
    """Raised when input is incomplete or invalid."""


def _number(value, path, *, minimum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{path}: expected a finite number (booleans are not numbers)")
    try:
        finite = math.isfinite(value)
        number = float(value)
    except (OverflowError, ValueError):
        finite, number = False, 0.0
    if not finite or not math.isfinite(number):
        raise InputError(f"{path}: expected a finite number representable for arithmetic")
    if minimum is not None and number < minimum:
        raise InputError(f"{path}: must be at least {minimum}")
    return number


def _range(value, path, *, minimum=None):
    if isinstance(value, dict):
        if set(value) != {"min", "max"}:
            raise InputError(f"{path}: range must contain exactly 'min' and 'max'")
        low = _number(value["min"], f"{path}.min", minimum=minimum)
        high = _number(value["max"], f"{path}.max", minimum=minimum)
        if low > high:
            raise InputError(f"{path}: min must not exceed max")
        return [low, high]
    number = _number(value, path, minimum=minimum)
    return [number, number]


def _rounded(value):
    if value is None:
        return None
    if not math.isfinite(value):
        raise InputError("calculation exceeded finite numeric range")
    return round(value, ROUND_DIGITS)


def _bounds(value):
    return [_rounded(value[0]), _rounded(value[1])]


def _multiply(left, right):
    return [left[0] * right[0], left[1] * right[1]]


def _validate(data):
    if not isinstance(data, dict):
        raise InputError("$: expected a JSON object")
    rules_version = data.get("rules_version")
    if not isinstance(rules_version, str) or rules_version not in RULES_VERSIONS:
        raise InputError("$.rules_version: explicitly choose '2014' or '2024'")
    assumptions = data.get("assumptions")
    if not isinstance(assumptions, dict):
        raise InputError("$.assumptions: required object with explicit assumptions")
    if assumptions.get("attack_model") != "d20_natural_1_20":
        raise InputError("$.assumptions.attack_model: explicitly use 'd20_natural_1_20'")
    if assumptions.get("party_focus_fire") is not True:
        raise InputError("$.assumptions.party_focus_fire: must explicitly be true for focused-fire estimate")

    party, monsters = data.get("party"), data.get("monsters")
    if not isinstance(party, list) or not isinstance(monsters, list):
        raise InputError("$.party and $.monsters: both must be arrays")
    if not party or not monsters:
        raise InputError("$.party and $.monsters: each must contain at least one entry")

    ids = set()
    parsed = {}
    for group_name, entries in (("party", party), ("monsters", monsters)):
        parsed[group_name] = []
        for index, entry in enumerate(entries):
            path = f"$.{group_name}[{index}]"
            if not isinstance(entry, dict):
                raise InputError(f"{path}: expected an object")
            entity_id = entry.get("id")
            if not isinstance(entity_id, str) or not entity_id.strip():
                raise InputError(f"{path}.id: required non-empty string")
            if entity_id != entity_id.strip():
                raise InputError(f"{path}.id: leading/trailing whitespace is not allowed")
            if entity_id in ids:
                raise InputError(f"{path}.id: duplicate ID {entity_id!r}")
            ids.add(entity_id)

            known_fields = {"id", "hp", "ac", "xp", *COMBAT_FIELDS}
            entity = {"id": entity_id, "unsupported_fields": sorted(set(entry) - known_fields)}
            for name in ("hp", "ac"):
                if name not in entry:
                    raise InputError(f"{path}.{name}: required; missing values are not defaulted")
                entity[name] = _range(entry[name], f"{path}.{name}", minimum=0 if name == "hp" else None)
            for name in COMBAT_FIELDS:
                entity[name] = (
                    _range(entry[name], f"{path}.{name}", minimum=0 if name != "attack_bonus" else None)
                    if name in entry else None
                )
            entity["xp"] = _range(entry["xp"], f"{path}.xp", minimum=0) if "xp" in entry else None
            parsed[group_name].append(entity)

    thresholds = data.get("thresholds")
    xp_budget = None
    if thresholds is not None:
        if not isinstance(thresholds, dict):
            raise InputError("$.thresholds: expected an object")
        if "xp_budget" in thresholds:
            xp_budget = _range(thresholds["xp_budget"], "$.thresholds.xp_budget", minimum=0)
    return parsed, xp_budget


def _attack_probability(attack_bonus, armor_class):
    # Natural 1 always misses and natural 20 always hits in this simplified model.
    return min(0.95, max(0.05, (21 + attack_bonus - armor_class) / 20))


def _dpr(entity, targets):
    if any(entity[field] is None for field in COMBAT_FIELDS):
        return None
    probabilities = [
        _attack_probability(attack_bonus, armor_class)
        for attack_bonus in entity["attack_bonus"]
        for target in targets
        for armor_class in target
    ]
    base_damage = _multiply(
        _multiply(entity["damage_per_hit"], entity["attacks_per_action"]),
        entity["actions_per_round"],
    )
    return [base_damage[0] * min(probabilities), base_damage[1] * max(probabilities)]


def analyze(data):
    """Return a JSON-serializable analysis; values are rounded to four decimals."""
    parsed, xp_budget = _validate(data)
    party, monsters = parsed["party"], parsed["monsters"]

    def action_total(entities):
        if any(entity["actions_per_round"] is None for entity in entities):
            return None
        return [sum(entity["actions_per_round"][i] for entity in entities) for i in (0, 1)]

    party_actions, monster_actions = action_total(party), action_total(monsters)
    party_complete = all(all(entity[field] is not None for field in COMBAT_FIELDS) for entity in party)
    monster_complete = all(all(entity[field] is not None for field in COMBAT_FIELDS) for entity in monsters)

    party_dpr_low = party_dpr_high = 0.0
    for attacker in party:
        dpr = _dpr(attacker, [monster["ac"] for monster in monsters])
        if dpr is not None:
            party_dpr_low += dpr[0]
            party_dpr_high += dpr[1]

    monster_dpr_low = monster_dpr_high = 0.0
    for attacker in monsters:
        dpr = _dpr(attacker, [member["ac"] for member in party])
        if dpr is not None:
            monster_dpr_low += dpr[0]
            monster_dpr_high += dpr[1]

    target_hp = [min(monster["hp"][0] for monster in monsters), max(monster["hp"][1] for monster in monsters)]
    rounds_to_down = None
    if party_complete:
        rounds_to_down = [
            0.0 if target_hp[0] == 0 else target_hp[0] / party_dpr_high if party_dpr_high > 0 else None,
            0.0 if target_hp[1] == 0 else target_hp[1] / party_dpr_low if party_dpr_low > 0 else None,
        ]

    party_hp = [sum(entity["hp"][i] for entity in party) for i in (0, 1)]
    party_hit_points = [min(entity["hp"][0] for entity in party), max(entity["hp"][1] for entity in party)]
    damage_rounds = None
    if monster_complete:
        damage_rounds = [
            None if monster_dpr_high == 0 else party_hit_points[0] / monster_dpr_high,
            None if monster_dpr_low == 0 else party_hit_points[1] / monster_dpr_low,
        ]

    xp_complete = all(monster["xp"] is not None for monster in monsters)
    xp_total = [sum(monster["xp"][i] for monster in monsters) for i in (0, 1)] if xp_complete else None
    threshold_result = None
    if xp_budget is not None:
        if xp_total is None:
            threshold_result = {"status": "not_evaluable", "reason": "monster XP is missing"}
        elif xp_total[1] <= xp_budget[0]:
            threshold_result = {"status": "within", "comparison": "maximum encounter XP <= minimum supplied budget"}
        elif xp_total[0] > xp_budget[1]:
            threshold_result = {"status": "over", "comparison": "minimum encounter XP > maximum supplied budget"}
        else:
            threshold_result = {"status": "overlaps", "comparison": "supplied ranges overlap; cannot determine pass/fail"}

    notes = [
        "Approximation only: not rules-complete or a guarantee of encounter balance.",
        "Uses the supplied 2014/2024 label for context only; no rules tables or edition-specific modifiers are applied.",
        "Attack probability is a simplified d20 model with automatic miss on 1, hit on 20; damage assumes each attack hits for the supplied average.",
        "Ranges are propagated independently and conservatively; correlations, defenses, conditions, saves, critical damage, initiative, and player tactics are not modeled.",
        "XP budget comparison uses only supplied XP and budget values; no XP thresholds are inferred.",
        "Effective HP is reported as supplied HP only; resistances, vulnerabilities, temporary HP, and healing are not inferred.",
    ]
    unsupported = []
    for group_name in ("party", "monsters"):
        for entity in parsed[group_name]:
            missing = [field for field in COMBAT_FIELDS if entity[field] is None]
            if missing or entity["unsupported_fields"]:
                item = {"id": entity["id"]}
                if missing:
                    item["missing_fields"] = missing
                if entity["unsupported_fields"]:
                    item["unsupported_fields"] = entity["unsupported_fields"]
                unsupported.append(item)

    unsupported_input_fields = set(data) - {"rules_version", "assumptions", "party", "monsters", "thresholds"}
    unsupported_input_fields.update(
        f"assumptions.{field}" for field in set(data["assumptions"]) - {"attack_model", "party_focus_fire"}
    )
    if isinstance(data.get("thresholds"), dict):
        unsupported_input_fields.update(
            f"thresholds.{field}" for field in set(data["thresholds"]) - {"xp_budget"}
        )

    return {
        "rules_version": data["rules_version"],
        "assumptions": {"attack_model": "d20_natural_1_20", "party_focus_fire": True, "rounding_decimal_places": ROUND_DIGITS},
        "action_counts_per_round": {
            "party": None if party_actions is None else _bounds(party_actions),
            "monsters": None if monster_actions is None else _bounds(monster_actions),
        },
        "effective_hp": {
            "party_total": _bounds(party_hp),
            "monster_total": _bounds([sum(entity["hp"][i] for entity in monsters) for i in (0, 1)]),
            "basis": "supplied HP only; defenses and healing excluded",
        },
        "expected_damage_per_round": {
            "party_focused_on_monster_group": _bounds([party_dpr_low, party_dpr_high]) if party_complete else None,
            "monsters_focusing_party_group": _bounds([monster_dpr_low, monster_dpr_high]) if monster_complete else None,
        },
        "approximate_rounds_to_down": {
            "one_monster_at_extreme_supplied_hp": None if rounds_to_down is None else [_rounded(value) for value in rounds_to_down],
            "party_member_at_extreme_supplied_hp": None if damage_rounds is None else [_rounded(value) for value in damage_rounds],
            "null_means_zero_damage_or_missing_required_statistics": True,
        },
        "xp": {
            "encounter_total": None if xp_total is None else _bounds(xp_total),
            "supplied_budget": None if xp_budget is None else _bounds(xp_budget),
            "budget_result": threshold_result,
        },
        "unsupported_or_missing": unsupported,
        "unsupported_input_fields": sorted(unsupported_input_fields),
        "notes": notes,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="path to a user-supplied JSON encounter")
    parser.add_argument("-o", "--output", type=Path, help="write JSON here instead of stdout")
    args = parser.parse_args(argv)
    try:
        with args.input.open(encoding="utf-8") as source:
            result = analyze(json.load(source))
        rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, json.JSONDecodeError, InputError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
