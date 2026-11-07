#!/usr/bin/env python3
"""Validate manifest format and exact bytes in a local player-safe export."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST_NAME = "player-safe-export.manifest.json"
EXPORT_DIR_NAME = "approved-export"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
FILENAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,123}\.(?:md|txt)\Z")


class ValidationError(ValueError):
    pass


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_manifest(path):
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValidationError(f"cannot read valid UTF-8 JSON manifest: {error}") from error


def _validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise ValidationError("manifest must be a JSON object")
    if set(manifest) != {"format_version", "export_id", "approval", "files"}:
        raise ValidationError("manifest keys must be format_version, export_id, approval, files")
    if type(manifest["format_version"]) is not int or manifest["format_version"] != 1:
        raise ValidationError("format_version must be integer 1")
    if not isinstance(manifest["export_id"], str) or not manifest["export_id"].strip():
        raise ValidationError("export_id must be a non-empty string")

    approval = manifest["approval"]
    if not isinstance(approval, dict) or set(approval) != {"approved_by", "approved_on"}:
        raise ValidationError("approval must contain only approved_by and approved_on")
    if not isinstance(approval["approved_by"], str) or not approval["approved_by"].strip():
        raise ValidationError("approval.approved_by must be a non-empty string")
    if not isinstance(approval["approved_on"], str) or not DATE_RE.fullmatch(approval["approved_on"]):
        raise ValidationError("approval.approved_on must use YYYY-MM-DD format")

    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise ValidationError("files must be a non-empty array")
    seen = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise ValidationError("each files entry must contain only path and sha256")
        path = entry["path"]
        digest = entry["sha256"]
        prefix = f"{EXPORT_DIR_NAME}/"
        if (
            not isinstance(path, str)
            or not path.startswith(prefix)
            or not FILENAME_RE.fullmatch(path[len(prefix):])
            or "\x00" in path
        ):
            raise ValidationError(f"file path must be a plain filename under {EXPORT_DIR_NAME}/")
        if path in seen:
            raise ValidationError(f"duplicate file path: {path}")
        seen.add(path)
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise ValidationError(f"sha256 for {path} must be 64 lowercase hexadecimal characters")
    return {entry["path"]: entry["sha256"] for entry in files}


def validate_export(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValidationError("repository root must be a non-symlink directory")

    manifest_path = root / MANIFEST_NAME
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValidationError(f"{MANIFEST_NAME} must be a regular, non-symlink file")

    manifest = _read_manifest(manifest_path)
    expected = _validate_manifest(manifest)

    export_dir = root / EXPORT_DIR_NAME
    if export_dir.is_symlink() or not export_dir.is_dir():
        raise ValidationError(f"{EXPORT_DIR_NAME} must be a regular, non-symlink directory")

    try:
        children = list(export_dir.iterdir())
    except OSError as error:
        raise ValidationError(f"cannot list {EXPORT_DIR_NAME}: {error}") from error
    actual = set()
    for child in children:
        if child.is_symlink() or not child.is_file():
            raise ValidationError(f"{EXPORT_DIR_NAME} may contain only regular files: {child.name}")
        actual.add(f"{EXPORT_DIR_NAME}/{child.name}")
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        unlisted = sorted(actual - set(expected))
        raise ValidationError(f"export file set differs from manifest (missing={missing}, unlisted={unlisted})")

    for relative_path, expected_digest in expected.items():
        file_path = root / relative_path
        try:
            content = file_path.read_bytes()
        except OSError as error:
            raise ValidationError(f"cannot read {relative_path}: {error}") from error
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValidationError(f"export must be UTF-8 plain text: {relative_path}") from error
        if b"\x00" in content:
            raise ValidationError(f"export must not contain NUL bytes: {relative_path}")
        digest = hashlib.sha256(content).hexdigest()
        if digest != expected_digest:
            raise ValidationError(f"SHA-256 mismatch: {relative_path}")
    return len(expected)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".", help="player repository root (default: current directory)")
    args = parser.parse_args(argv)
    try:
        count = validate_export(args.repository)
    except ValidationError as error:
        print(f"Invalid player-safe export: {error}", file=sys.stderr)
        return 1
    print(f"Valid manifest and SHA-256 for {count} approved export file(s).")
    print("This check does not authenticate approval or prove confidentiality.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
