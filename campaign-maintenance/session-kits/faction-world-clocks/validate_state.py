#!/usr/bin/env python3
"""Validate a faction-world-clocks JSON draft without changing it."""

import json
import sys
from pathlib import Path


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["$: expected an object"]

    def error(path, message):
        errors.append(f"{path}: {message}")

    def records(path, value):
        if not isinstance(value, list):
            error(path, "expected an array")
            return []
        valid = []
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]"
            if not isinstance(item, dict):
                error(item_path, "expected an object")
            else:
                valid.append((item_path, item))
        return valid

    def required_text(item, key, path):
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            error(f"{path}.{key}", "expected a non-empty string")
            return None
        return value

    if data.get("schemaVersion") != 1:
        error("$.schemaVersion", "expected 1")
    if data.get("kit") != "faction-world-clocks":
        error("$.kit", 'expected "faction-world-clocks"')
    review_status = data.get("reviewStatus")
    if not isinstance(review_status, str) or review_status not in {"sample", "draft", "approved"}:
        error("$.reviewStatus", "expected sample, draft, or approved")

    campaign = data.get("campaign")
    if not isinstance(campaign, dict):
        error("$.campaign", "expected an object")
        campaign = {}
    else:
        register_campaign_id = campaign.get("id")
        if not isinstance(register_campaign_id, str) or not register_campaign_id.strip():
            error("$.campaign.id", "expected a non-empty string")
    turn = data.get("turn")
    if not isinstance(turn, dict):
        error("$.turn", "expected an object")
        turn = {}
    else:
        turn_id = turn.get("id")
        if not isinstance(turn_id, str) or not turn_id.strip():
            error("$.turn.id", "expected a non-empty string")
    state_revision = required_text(turn, "stateRevision", "$.turn")
    required_text(turn, "sourceRevision", "$.turn")
    required_text(turn, "turnBoundary", "$.turn")

    seen_ids = set()

    def register_id(item, path):
        record_id = required_text(item, "id", path)
        if record_id is not None:
            if record_id in seen_ids:
                error(f"{path}.id", f"duplicate ID {record_id!r}")
            seen_ids.add(record_id)
        return record_id

    if isinstance(campaign, dict) and isinstance(campaign.get("id"), str) and campaign["id"].strip():
            register_id(campaign, "$.campaign")
    if isinstance(turn, dict) and isinstance(turn.get("id"), str) and turn["id"].strip():
            register_id(turn, "$.turn")

    sources = {}
    for path, source in records("$.sources", data.get("sources")):
        source_id = register_id(source, path)
        for field in ("path", "locator", "revision", "excerpt"):
            required_text(source, field, path)
        if source_id is not None:
            sources[source_id] = source

    for collection in ("approvedFacts", "uncertainties"):
        entries = turn.get(collection)
        for path, entry in records(f"$.turn.{collection}", entries):
            register_id(entry, path)
            required_text(entry, "text", path)
            refs = entry.get("sourceRefs")
            if not isinstance(refs, list) or not refs:
                error(f"{path}.sourceRefs", "expected a non-empty array of source IDs")
            else:
                for index, source_ref in enumerate(refs):
                    if not isinstance(source_ref, str) or source_ref not in sources:
                        error(f"{path}.sourceRefs[{index}]", f"unknown source {source_ref!r}")

    factions = {}
    faction_items = records("$.factions", data.get("factions"))
    for path, faction in faction_items:
        faction_id = register_id(faction, path)
        required_text(faction, "name", path)
        required_text(faction, "goal", path)
        if faction_id is not None:
            factions[faction_id] = faction
        for ref in records(f"{path}.resources", faction.get("resources")):
            resource_path, resource = ref
            register_id(resource, resource_path)
            required_text(resource, "name", resource_path)
            required_text(resource, "unit", resource_path)
            amount = resource.get("amount")
            if amount is not None and (type(amount) is not int or amount < 0):
                error(f"{resource_path}.amount", "expected a nonnegative integer or null")
            source_ref = required_text(resource, "sourceRefId", resource_path)
            if source_ref is not None and source_ref not in sources:
                error(f"{resource_path}.sourceRefId", f"unknown source {source_ref!r}")
        source_refs = faction.get("sourceRefs")
        if not isinstance(source_refs, list) or not source_refs:
            error(f"{path}.sourceRefs", "expected a non-empty array of source IDs")
        else:
            for index, source_ref in enumerate(source_refs):
                if not isinstance(source_ref, str) or source_ref not in sources:
                    error(f"{path}.sourceRefs[{index}]", f"unknown source {source_ref!r}")

    clocks = {}
    for path, clock in records("$.clocks", data.get("clocks")):
        clock_id = register_id(clock, path)
        required_text(clock, "name", path)
        required_text(clock, "description", path)
        if clock.get("status") != "approved":
            error(f"{path}.status", 'must be "approved" for a baseline clock')
        faction_ref = required_text(clock, "factionId", path)
        if faction_ref is not None and faction_ref not in factions:
            error(f"{path}.factionId", f"unknown faction {faction_ref!r}")
        value = clock.get("value")
        maximum = clock.get("max")
        if type(maximum) is not int or maximum < 1:
            error(f"{path}.max", "expected a positive integer")
        if type(value) is not int:
            error(f"{path}.value", "expected an integer")
        elif type(maximum) is int and not 0 <= value <= maximum:
            error(f"{path}.value", f"must be in the inclusive range 0..{maximum}")
        source_ref = required_text(clock, "sourceRefId", path)
        if source_ref is not None and source_ref not in sources:
            error(f"{path}.sourceRefId", f"unknown source {source_ref!r}")
        if clock_id is not None:
            clocks[clock_id] = clock

    for path, proposal in records("$.proposals", data.get("proposals")):
        register_id(proposal, path)
        required_text(proposal, "action", path)
        required_text(proposal, "rationale", path)
        faction_ref = required_text(proposal, "factionId", path)
        if faction_ref is not None and faction_ref not in factions:
            error(f"{path}.factionId", f"unknown faction {faction_ref!r}")
        base_revision = required_text(proposal, "baseRevision", path)
        if base_revision is not None and state_revision is not None and base_revision != state_revision:
            error(
                f"{path}.baseRevision",
                f"stale proposal for {base_revision!r}; current state is {state_revision!r}",
            )
        if proposal.get("status") != "proposed":
            error(f"{path}.status", 'must be "proposed"')
        refs = proposal.get("sourceRefs")
        if not isinstance(refs, list) or not refs:
            error(f"{path}.sourceRefs", "expected a non-empty array of source IDs")
        else:
            for index, source_ref in enumerate(refs):
                if not isinstance(source_ref, str) or source_ref not in sources:
                    error(f"{path}.sourceRefs[{index}]", f"unknown source {source_ref!r}")

        for field in ("costs", "visibleSigns", "alternativeResponses", "uncertainties"):
            entries = proposal.get(field)
            if not isinstance(entries, list):
                error(f"{path}.{field}", "expected an array")
                continue
            for index, entry in enumerate(entries):
                if not isinstance(entry, str) or not entry.strip():
                    error(f"{path}.{field}[{index}]", "expected a non-empty string")
        alternatives = proposal.get("alternativeResponses")
        if isinstance(alternatives, list) and len(alternatives) < 2:
            error(f"{path}.alternativeResponses", "expected at least two alternatives")

        seen_clock_refs = set()
        for change_path, change in records(f"{path}.changes", proposal.get("changes")):
            register_id(change, change_path)
            clock_ref = required_text(change, "clockId", change_path)
            if clock_ref is not None:
                if clock_ref in seen_clock_refs:
                    error(f"{change_path}.clockId", f"duplicate clock change for {clock_ref!r}")
                seen_clock_refs.add(clock_ref)
            clock = clocks.get(clock_ref)
            if clock_ref is not None and clock is None:
                error(f"{change_path}.clockId", f"unknown clock {clock_ref!r}")
            delta = change.get("delta")
            if type(delta) is not int or delta == 0:
                error(f"{change_path}.delta", "expected a nonzero integer")
            elif clock is not None:
                current = clock.get("value")
                maximum = clock.get("max")
                if type(current) is int and type(maximum) is int:
                    resulting = current + delta
                    if not 0 <= resulting <= maximum:
                        error(
                            f"{change_path}.delta",
                            f"would move {clock_ref!r} from {current} to {resulting}, outside 0..{maximum}",
                        )
                    claimed_result = change.get("resultingValue")
                    if type(claimed_result) is not int or claimed_result != resulting:
                        error(
                            f"{change_path}.resultingValue",
                            f"must equal current value + delta ({resulting})",
                        )
            required_text(change, "reason", change_path)
            source_ref = required_text(change, "sourceRefId", change_path)
            if source_ref is not None and source_ref not in sources:
                error(f"{change_path}.sourceRefId", f"unknown source {source_ref!r}")

    audit = data.get("audit")
    if not isinstance(audit, dict):
        error("$.audit", "expected an object")
    else:
        audit_revision = required_text(audit, "sourceRevision", "$.audit")
        if audit_revision is not None and turn.get("sourceRevision") != audit_revision:
            error("$.audit.sourceRevision", "must match turn.sourceRevision")
        if not isinstance(audit.get("notes"), list):
            error("$.audit.notes", "expected an array")
    return errors


def main(argv):
    if len(argv) != 2:
        print(f"Usage: {Path(argv[0]).name} STATE.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"{path}: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{path}: valid faction-world-clocks draft")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
