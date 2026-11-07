import json
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_export

HERE = Path(__file__).parent
EXAMPLE = HERE / "example"


class ValidateExportTests(unittest.TestCase):
    def test_fictional_example_is_valid(self):
        self.assertEqual(validate_export.validate_export(EXAMPLE), 1)

    def test_changed_bytes_fail_hash_check(self):
        export_file = EXAMPLE / "approved-export" / "session-01.md"
        original_read_bytes = Path.read_bytes

        def changed_content(path):
            content = original_read_bytes(path)
            return content + b"changed" if path == export_file else content

        with patch.object(Path, "read_bytes", autospec=True, side_effect=changed_content):
            with self.assertRaisesRegex(validate_export.ValidationError, "SHA-256 mismatch"):
                validate_export.validate_export(EXAMPLE)

    def test_path_traversal_and_nested_paths_are_rejected(self):
        for unsafe in (
            "../secret.md",
            "approved-export/../secret.md",
            "approved-export/nested/file.md",
            r"approved-export\secret.md",
            "/approved-export/secret.md",
            "approved-export/.hidden",
            "approved-export/name with spaces.md",
            "approved-export/image.png",
        ):
            with self.subTest(path=unsafe):
                with self.assertRaises(validate_export.ValidationError):
                    validate_export._validate_manifest(self._manifest(unsafe))

    def test_duplicate_paths_and_duplicate_json_keys_are_rejected(self):
        manifest = self._manifest("approved-export/session-01.md")
        manifest["files"].append(dict(manifest["files"][0]))
        with self.assertRaisesRegex(validate_export.ValidationError, "duplicate file path"):
            validate_export._validate_manifest(manifest)
        with self.assertRaisesRegex(validate_export.ValidationError, "duplicate JSON key"):
            json.loads('{"key": 1, "key": 2}', object_pairs_hook=validate_export._unique_object)

    def test_approval_date_must_be_a_real_calendar_date(self):
        manifest = self._manifest("approved-export/session-01.md")
        manifest["approval"]["approved_on"] = "2026-02-30"
        with self.assertRaisesRegex(validate_export.ValidationError, "valid calendar date"):
            validate_export._validate_manifest(manifest)

    def test_symlink_manifest_is_rejected(self):
        manifest = EXAMPLE / validate_export.MANIFEST_NAME
        with patch.object(Path, "is_symlink", autospec=True,
                          side_effect=lambda path: path == manifest):
            with self.assertRaisesRegex(validate_export.ValidationError, "regular, non-symlink"):
                validate_export.validate_export(EXAMPLE)

    def test_binary_export_is_rejected(self):
        export_file = EXAMPLE / "approved-export" / "session-01.md"
        original_read_bytes = Path.read_bytes

        def binary_content(path):
            return b"\x00\xff" if path == export_file else original_read_bytes(path)

        with patch.object(Path, "read_bytes", autospec=True, side_effect=binary_content):
            with self.assertRaisesRegex(validate_export.ValidationError, "UTF-8 plain text"):
                validate_export.validate_export(EXAMPLE)

    def test_symlink_export_directory_and_file_are_rejected(self):
        export_dir = EXAMPLE / validate_export.EXPORT_DIR_NAME
        export_file = export_dir / "session-01.md"
        for symlink in (export_dir, export_file):
            with self.subTest(path=symlink):
                with patch.object(Path, "is_symlink", autospec=True,
                                  side_effect=lambda path: path == symlink):
                    with self.assertRaises(validate_export.ValidationError):
                        validate_export.validate_export(EXAMPLE)

    def test_extra_or_nested_export_entries_are_rejected(self):
        export_dir = EXAMPLE / validate_export.EXPORT_DIR_NAME
        original_iterdir = Path.iterdir

        def with_extra(path):
            children = list(original_iterdir(path))
            if path == export_dir:
                children.append(export_dir / "unlisted.md")
            return iter(children)

        original_is_file = Path.is_file

        def extra_is_file(path):
            return True if path == export_dir / "unlisted.md" else original_is_file(path)

        with patch.object(Path, "iterdir", autospec=True, side_effect=with_extra), \
             patch.object(Path, "is_file", autospec=True, side_effect=extra_is_file):
            with self.assertRaisesRegex(validate_export.ValidationError, "file set differs"):
                validate_export.validate_export(EXAMPLE)

    @staticmethod
    def _manifest(path):
        return {
            "format_version": 1,
            "export_id": "fictional-example",
            "approval": {"approved_by": "Example DM", "approved_on": "2026-01-11"},
            "files": [{"path": path, "sha256": "0" * 64}],
        }


if __name__ == "__main__":
    unittest.main()
