#!/usr/bin/env python3
"""Validate the structure and internal references of a canon manifest."""

import json
import re
import sys
from pathlib import Path


class DuplicateKey(ValueError):
    pass


def object_without_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def validate(data):
    diagnostics = []

    def error(code, path, message):
        diagnostics.append({"code": code, "path": path, "message": message})

    def fields(value, expected, path):
        if not isinstance(value, dict):
            error("type", path, "expected object")
            return False
        for key in sorted(expected - value.keys()):
            error("missing", f"{path}/{key}", "required field is missing")
        for key in sorted(value.keys() - expected):
            escaped = key.replace("~", "~0").replace("/", "~1")
            error("unknown", f"{path}/{escaped}", "unknown field")
        return True

    if not fields(data, {"schemaVersion", "rulesVersion", "facts"}, ""):
        return diagnostics
    if "schemaVersion" in data and (
        type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1
    ):
        error("version", "/schemaVersion", "expected integer 1")
    if "rulesVersion" in data and data["rulesVersion"] not in ("2014", "2024", "unknown"):
        error("rules_version", "/rulesVersion", 'expected "2014", "2024", or "unknown"')
    if "facts" not in data:
        return diagnostics
    if not isinstance(data["facts"], list):
        error("type", "/facts", "expected array")
        return diagnostics

    ids = set()
    references = []
    for index, fact in enumerate(data["facts"]):
        path = f"/facts/{index}"
        if not fields(fact, {"id", "status", "text", "source", "references"}, path):
            continue
        identifier = fact.get("id")
        if "id" in fact:
            if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
                error("id", path + "/id", "expected lowercase hyphen-separated identifier")
            elif identifier in ids:
                error("duplicate_id", path + "/id", f"duplicate id: {identifier}")
            else:
                ids.add(identifier)
        if "status" in fact and fact["status"] not in ("canon", "draft"):
            error("status", path + "/status", 'expected "canon" or "draft"')
        for key in ("text", "source"):
            if key in fact and (not isinstance(fact[key], str) or not fact[key].strip()):
                error("text", path + "/" + key, "expected non-empty string")
        if "references" in fact:
            if not isinstance(fact["references"], list):
                error("type", path + "/references", "expected array")
            else:
                seen = set()
                for ref_index, ref in enumerate(fact["references"]):
                    ref_path = f"{path}/references/{ref_index}"
                    if not isinstance(ref, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ref):
                        error("reference", ref_path, "expected lowercase hyphen-separated identifier")
                    elif ref in seen:
                        error("duplicate_reference", ref_path, f"duplicate reference: {ref}")
                    else:
                        seen.add(ref)
                        references.append((ref, ref_path))
    for ref, path in references:
        if ref not in ids:
            error("unresolved_reference", path, f"unknown id: {ref}")
    return diagnostics


def main(argv):
    if len(argv) != 2:
        print(json.dumps({"ok": False, "diagnostics": [
            {"code": "usage", "path": "", "message": "usage: check_canon.py MANIFEST.json"}
        ]}))
        return 2
    try:
        with Path(argv[1]).open(encoding="utf-8") as file:
            data = json.load(file, object_pairs_hook=object_without_duplicates,
                             parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid JSON constant: {value}")))
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(json.dumps({"ok": False, "diagnostics": [
            {"code": "input", "path": "", "message": str(exc)}
        ]}, ensure_ascii=False))
        return 2
    diagnostics = validate(data)
    print(json.dumps({"ok": not diagnostics, "diagnostics": diagnostics}, ensure_ascii=False))
    return 1 if diagnostics else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
