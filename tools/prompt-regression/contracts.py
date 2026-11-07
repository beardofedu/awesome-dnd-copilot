"""Small, kit-specific structural contracts for stored prompt output examples."""

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PATHS = {
    "session-bridge": Path("campaign-maintenance/session-kits/session-bridge/state.example.json"),
    "party-journal": Path("campaign-maintenance/session-kits/party-journal/state.example.json"),
    "dm-session-cockpit": Path("running-campaign/session-kits/dm-session-cockpit/state.example.json"),
}
AUDIENCES = {"session-bridge": "dm", "party-journal": "player", "dm-session-cockpit": "dm"}
REVIEW_STATUSES = {"sample", "draft", "approved"}
SENTINELS = ("SYNTHETIC_DM_ONLY_SENTINEL", "SYNTHETIC_PRIVATE_TOKEN_SENTINEL")
ID_PATTERN = __import__("re").compile(r"^[a-z0-9][a-z0-9-]*$")

# These are fixture references, not a claim that the cited text is true or safe.
# The direct sample checks deliberately resolve their sample sourceRef strings here.
SAMPLE_REFS = {
    "session-bridge": {
        "fictional sample notes": "observation",
        "fictional sample: the party's promise; not established canon": "proposal",
        "fictional sample: mill thread": "proposal",
    },
    "party-journal": {
        "fictional sample approved player notes": "observation",
        "fictional sample confirmed inventory": "observation",
    },
    "dm-session-cockpit": {
        "fictional sample prep": "proposal",
        "fictional sample approved notes": "observation",
    },
}


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _object(value, path, errors):
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return False
    return True


def _fields(value, path, fields, errors):
    if _object(value, path, errors):
        for field in fields:
            if field not in value:
                errors.append(f"{path}.{field} is required")
        return True
    return False


def _string(value, path, errors, nullable=False):
    if nullable and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string" + (" or null" if nullable else ""))


def _array(value, path, errors):
    if not isinstance(value, list):
        errors.append(f"{path} must be an array")
        return False
    return True


def _nonnegative(value, path, errors, integer=False, nullable=False):
    if nullable and value is None:
        return
    valid = isinstance(value, int) and not isinstance(value, bool) if integer else _is_number(value)
    if not valid or value < 0:
        errors.append(f"{path} must be a nonnegative {'integer' if integer else 'number'}" + (" or null" if nullable else ""))


def _unique_ids(groups, errors):
    seen = set()
    for path, records in groups:
        if not isinstance(records, list):
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict) or "id" not in record:
                continue
            value = record["id"]
            where = f"{path}[{index}].id"
            if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
                errors.append(f"{where} must be a stable lowercase ID")
            elif value in seen:
                errors.append(f"{where} duplicates ID {value!r}")
            else:
                seen.add(value)


def _source(record, path, category, refs, errors):
    if not isinstance(record, dict) or not isinstance(record.get("sourceRef"), str):
        errors.append(f"{path}.sourceRef must name a provided reference")
        return
    reference = record["sourceRef"]
    expected_kind = refs.get(reference)
    if expected_kind is None:
        errors.append(f"{path}.sourceRef {reference!r} is not in the provided references")
    elif category and expected_kind != category:
        errors.append(f"{path} requires a {category} reference, got {expected_kind}")


def _record_fields(records, path, fields, errors, *, strings=(), booleans=(), string_arrays=()):
    if not isinstance(records, list):
        return
    for index, record in enumerate(records):
        record_path = f"{path}[{index}]"
        if not _fields(record, record_path, fields, errors):
            continue
        for field in strings:
            if field in record:
                _string(record[field], f"{record_path}.{field}", errors)
        for field in booleans:
            if field in record and not isinstance(record[field], bool):
                errors.append(f"{record_path}.{field} must be boolean")
        for field in string_arrays:
            if field not in record or not _array(record[field], f"{record_path}.{field}", errors):
                continue
            for item_index, item in enumerate(record[field]):
                _string(item, f"{record_path}.{field}[{item_index}]", errors)


def _feedback(value, path, fields, errors):
    if not _fields(value, path, fields, errors):
        return
    for name in fields:
        if name not in value:
            continue
        if name == "notes":
            if not isinstance(value[name], str):
                errors.append(f"{path}.{name} must be a string")
        else:
            _nonnegative(value[name], f"{path}.{name}", errors, nullable=True)


def check_state(state, refs, *, synthetic=False):
    """Return all structural contract violations; never inspect external content."""
    errors = []
    if not _object(state, "output", errors):
        return errors
    kit = state.get("kit")
    if not isinstance(kit, str) or kit not in AUDIENCES:
        return ["output.kit must name one of the three session kits"]
    audience = AUDIENCES[kit]
    required_top = {
        "session-bridge": ("schemaVersion", "kit", "audience", "reviewStatus", "session", "updatedAt", "recap", "events", "facts", "suggestions", "threads", "npcChanges", "prep", "feedback"),
        "party-journal": ("schemaVersion", "kit", "audience", "reviewStatus", "session", "updatedAt", "recap", "quests", "inventory", "npcs", "locations", "theories", "plans", "feedback"),
        "dm-session-cockpit": ("schemaVersion", "kit", "audience", "reviewStatus", "session", "updatedAt", "scenes", "npcs", "hooks", "combat", "scratchNotes", "feedback"),
    }[kit]
    _fields(state, "output", required_top, errors)
    if state.get("schemaVersion") != 1 or isinstance(state.get("schemaVersion"), bool):
        errors.append("output.schemaVersion must be integer 1")
    if state.get("audience") != audience:
        errors.append(f"output.audience must be {audience!r} for {kit}")
    if not isinstance(state.get("reviewStatus"), str) or state.get("reviewStatus") not in REVIEW_STATUSES:
        errors.append("output.reviewStatus must be sample, draft, or approved")

    session_fields = ("id", "title", "date", "inGameDate", "rules", "tone", "source")
    if _fields(state.get("session"), "output.session", session_fields, errors):
        session = state["session"]
        for key in ("id", "title"):
            if key in session:
                _string(session[key], f"output.session.{key}", errors)
        for key in ("date", "inGameDate", "rules", "tone"):
            if key in session:
                _string(session[key], f"output.session.{key}", errors, nullable=True)
        source_fields = ("issueNumber", "url", "revision")
        source = session.get("source")
        if _fields(source, "output.session.source", source_fields, errors):
            issue = source.get("issueNumber")
            if "issueNumber" in source and issue is not None and (not isinstance(issue, int) or isinstance(issue, bool) or issue < 1):
                errors.append("output.session.source.issueNumber must be a positive integer or null")
            for key in ("url", "revision"):
                if key in source:
                    _string(source[key], f"output.session.source.{key}", errors, nullable=True)
    if state.get("updatedAt") is not None:
        _string(state["updatedAt"], "output.updatedAt", errors)

    list_fields = {
        "session-bridge": ("events", "facts", "suggestions", "threads", "npcChanges", "prep"),
        "party-journal": ("quests", "inventory", "npcs", "locations", "theories", "plans"),
        "dm-session-cockpit": ("scenes", "npcs", "hooks"),
    }[kit]
    groups = []
    for field in list_fields:
        _array(state.get(field), f"output.{field}", errors)
        groups.append((f"output.{field}", state.get(field)))
    if kit == "dm-session-cockpit":
        combat = state.get("combat")
        if _fields(combat, "output.combat", ("round", "activeCombatantId", "combatants"), errors):
            round_number = combat.get("round")
            if "round" in combat and (not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1):
                errors.append("output.combat.round must be a positive integer")
            if "combatants" in combat:
                _array(combat["combatants"], "output.combat.combatants", errors)
            groups.append(("output.combat.combatants", combat.get("combatants")))
            _check_cockpit(state, refs, errors)
    elif kit == "session-bridge":
        _check_bridge(state, refs, errors)
    else:
        _check_party(state, refs, errors)
    _unique_ids(groups, errors)

    if kit == "session-bridge":
        _feedback(state.get("feedback"), "output.feedback", ("prepMinutes", "missedFollowUps", "corrections", "notes"), errors)
    elif kit == "party-journal":
        _feedback(state.get("feedback"), "output.feedback", ("forgottenGoals", "corrections", "notes"), errors)
    else:
        _feedback(state.get("feedback"), "output.feedback", ("lookupInterruptions", "corrections", "notes"), errors)

    if synthetic:
        serialized = json.dumps(state, ensure_ascii=False)
        for sentinel in SENTINELS:
            if sentinel in serialized:
                errors.append(f"synthetic output contains explicit test sentinel {sentinel}")
    return errors


def _check_bridge(state, refs, errors):
    fields = {
        "events": ("id", "text", "sourceRef"),
        "facts": ("id", "text", "sourceRef"),
        "suggestions": ("id", "text", "sourceRef"),
        "threads": ("id", "title", "status", "detail", "sourceRef"),
        "npcChanges": ("id", "text", "sourceRef"),
        "prep": ("id", "text", "done", "sourceRef"),
    }
    strings = {
        "events": ("id", "text", "sourceRef"),
        "facts": ("id", "text", "sourceRef"),
        "suggestions": ("id", "text", "sourceRef"),
        "threads": ("id", "title", "status", "detail", "sourceRef"),
        "npcChanges": ("id", "text", "sourceRef"),
        "prep": ("id", "text", "sourceRef"),
    }
    for name, required in fields.items():
        _record_fields(
            state.get(name),
            f"output.{name}",
            required,
            errors,
            strings=strings[name],
            booleans=("done",) if name == "prep" else (),
        )
    for field in ("events", "facts", "npcChanges", "threads"):
        expected = "observation"
        for i, record in enumerate(state.get(field) if isinstance(state.get(field), list) else []):
            _source(record, f"output.{field}[{i}]", expected, refs, errors)
    for field in ("suggestions", "prep"):
        for i, record in enumerate(state.get(field) if isinstance(state.get(field), list) else []):
            _source(record, f"output.{field}[{i}]", None if field == "suggestions" else "proposal", refs, errors)
    for i, record in enumerate(state.get("threads") if isinstance(state.get("threads"), list) else []):
        if isinstance(record, dict) and (
            not isinstance(record.get("status"), str) or record.get("status") not in {"active", "urgent", "resolved"}
        ):
            errors.append(f"output.threads[{i}].status is not an allowed thread status")
    for i, record in enumerate(state.get("prep") if isinstance(state.get("prep"), list) else []):
        if isinstance(record, dict) and not isinstance(record.get("done"), bool):
            errors.append(f"output.prep[{i}].done must be boolean")
    if not isinstance(state.get("recap"), str):
        errors.append("output.recap must be a string")


def _check_party(state, refs, errors):
    fields = {
        "quests": ("id", "title", "status", "notes", "sourceRef"),
        "inventory": ("id", "name", "quantity", "holder", "confirmed", "sourceRef"),
        "npcs": ("id", "name", "notes", "sourceRef"),
        "locations": ("id", "name", "notes", "sourceRef"),
        "theories": ("id", "text", "authorLabel"),
        "plans": ("id", "text", "voters"),
    }
    strings = {
        "quests": ("id", "title", "status", "notes", "sourceRef"),
        "inventory": ("id", "name", "holder", "sourceRef"),
        "npcs": ("id", "name", "notes", "sourceRef"),
        "locations": ("id", "name", "notes", "sourceRef"),
        "theories": ("id", "text", "authorLabel"),
        "plans": ("id", "text"),
    }
    for name, required in fields.items():
        _record_fields(
            state.get(name),
            f"output.{name}",
            required,
            errors,
            strings=strings[name],
            booleans=("confirmed",) if name == "inventory" else (),
        )
    factual = ("quests", "inventory", "npcs", "locations")
    for field in factual:
        for i, record in enumerate(state.get(field) if isinstance(state.get(field), list) else []):
            _source(record, f"output.{field}[{i}]", "observation", refs, errors)
    for i, record in enumerate(state.get("quests") if isinstance(state.get("quests"), list) else []):
        if isinstance(record, dict) and (
            not isinstance(record.get("status"), str) or record.get("status") not in {"open", "in-progress", "completed"}
        ):
            errors.append(f"output.quests[{i}].status is not an allowed quest status")
    for i, record in enumerate(state.get("inventory") if isinstance(state.get("inventory"), list) else []):
        if not isinstance(record, dict):
            continue
        quantity = record.get("quantity")
        if "quantity" in record and (not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 0):
            errors.append(f"output.inventory[{i}].quantity must be a nonnegative integer")
        if "confirmed" in record and not isinstance(record.get("confirmed"), bool):
            errors.append(f"output.inventory[{i}].confirmed must be boolean")
    for i, record in enumerate(state.get("plans") if isinstance(state.get("plans"), list) else []):
        if not isinstance(record, dict) or not isinstance(record.get("voters"), list):
            errors.append(f"output.plans[{i}].voters must be an array")
        elif any(not isinstance(voter, str) for voter in record["voters"]) or len(set(record["voters"])) != len(record["voters"]):
            errors.append(f"output.plans[{i}].voters must contain unique strings")
    if not isinstance(state.get("recap"), str):
        errors.append("output.recap must be a string")


def _check_cockpit(state, refs, errors):
    fields = {
        "scenes": ("id", "title", "readAloud", "dmNotes", "basis", "done", "sourceRef"),
        "npcs": ("id", "name", "role", "voice", "knownFacts", "basis", "sourceRef"),
        "hooks": ("id", "text", "basis", "sourceRef"),
    }
    strings = {
        "scenes": ("id", "title", "readAloud", "dmNotes", "basis", "sourceRef"),
        "npcs": ("id", "name", "role", "voice", "basis", "sourceRef"),
        "hooks": ("id", "text", "basis", "sourceRef"),
    }
    for name, required in fields.items():
        _record_fields(
            state.get(name),
            f"output.{name}",
            required,
            errors,
            strings=strings[name],
            booleans=("done",) if name == "scenes" else (),
            string_arrays=("knownFacts",) if name == "npcs" else (),
        )
    for field in ("scenes", "npcs", "hooks"):
        for i, record in enumerate(state.get(field) if isinstance(state.get(field), list) else []):
            if not isinstance(record, dict):
                continue
            basis = record.get("basis")
            if not isinstance(basis, str) or basis not in {"approved", "proposal"}:
                errors.append(f"output.{field}[{i}].basis must be approved or proposal")
            _source(record, f"output.{field}[{i}]", "observation" if basis == "approved" else "proposal", refs, errors)
    combat = state.get("combat")
    if not isinstance(combat, dict) or not isinstance(combat.get("combatants"), list):
        return
    combatants = combat["combatants"]
    combatant_ids = set()
    for i, record in enumerate(combatants):
        path = f"output.combat.combatants[{i}]"
        if not isinstance(record, dict):
            _object(record, path, errors)
            continue
        _fields(record, path, ("id", "name", "initiative", "hp", "maxHp", "conditions"), errors)
        if "id" in record and not isinstance(record["id"], str):
            errors.append(f"{path}.id must be a stable lowercase ID")
        elif isinstance(record.get("id"), str):
            combatant_ids.add(record["id"])
        if "name" in record:
            _string(record["name"], f"{path}.name", errors)
        initiative = record.get("initiative")
        if "initiative" in record and initiative is not None and (not isinstance(initiative, int) or isinstance(initiative, bool)):
            errors.append(f"{path}.initiative must be an integer or null")
        hp, maximum = record.get("hp"), record.get("maxHp")
        if "maxHp" in record and (not isinstance(maximum, int) or isinstance(maximum, bool) or maximum <= 0):
            errors.append(f"{path}.maxHp must be a positive integer")
        if "hp" in record and "maxHp" in record and (not isinstance(hp, int) or isinstance(hp, bool) or not isinstance(maximum, int) or not 0 <= hp <= maximum):
            errors.append(f"{path}.hp must be an integer from 0 through maxHp")
        if "conditions" in record and not isinstance(record.get("conditions"), list):
            errors.append(f"{path}.conditions must be an array")
        elif isinstance(record.get("conditions"), list):
            for j, condition in enumerate(record["conditions"]):
                condition_path = f"{path}.conditions[{j}]"
                if _fields(condition, condition_path, ("name", "expires", "notes"), errors):
                    for field in ("name", "expires", "notes"):
                        if field in condition:
                            _string(condition[field], f"{condition_path}.{field}", errors)
    active = combat.get("activeCombatantId")
    if active is not None and (not isinstance(active, str) or active not in combatant_ids):
        errors.append("output.combat.activeCombatantId must identify an existing combatant or be null")
    if not isinstance(state.get("scratchNotes"), str):
        errors.append("output.scratchNotes must be a string")


def read_output(case):
    """Parse a fixture output string/object, returning (state, errors)."""
    raw = case.get("rawOutput")
    if raw is not None:
        try:
            return json.loads(raw), []
        except (json.JSONDecodeError, TypeError) as error:
            return None, [f"output is invalid JSON: {error.msg if isinstance(error, json.JSONDecodeError) else error}"]
    return case.get("output"), []
