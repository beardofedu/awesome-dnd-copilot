import os
import json
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import import_notes


class ImportNotesTests(unittest.TestCase):
    def test_rendered_source_content_cannot_close_its_code_fence(self):
        malicious_text = "Session notes\n```\n# injected heading\n```"
        markdown, marker, filename = import_notes.render_notes(
            "discord",
            [
                {
                    "id": "123",
                    "name": "table`notes\n# not a heading",
                    "updated": "2026-01-10T12:00:00Z",
                    "reference": "https://example.test/a`b",
                    "text": malicious_text,
                }
            ],
        )

        self.assertIn("````text\n" + malicious_text + "\n````", markdown)
        self.assertIn("table&#x27;notes # not a heading", markdown)
        self.assertIn("`https://example.test/a'b`", markdown)
        self.assertIn(marker, markdown)
        self.assertTrue(filename.startswith("discord-"))

    def test_render_identity_is_stable_and_changes_with_source_content(self):
        record = {"id": "one", "name": "notes", "updated": "", "reference": "id:one", "text": "same"}
        first = import_notes.render_notes("obsidian", [record])
        second = import_notes.render_notes("obsidian", [record])
        changed = import_notes.render_notes("obsidian", [{**record, "text": "different"}])

        self.assertEqual(first[1], second[1])
        self.assertNotEqual(first[1], changed[1])
        self.assertEqual(first[2], second[2])

    def test_empty_or_oversized_import_fails_without_partial_output(self):
        with self.assertRaises(import_notes.ImportFailure):
            import_notes.render_notes("discord", [])
        record = {"id": "1", "name": "large", "updated": "", "reference": "id:1", "text": "x" * 51_000}
        with self.assertRaises(import_notes.ImportFailure):
            import_notes.render_notes("discord", [record])

    def test_docx_text_is_extracted_and_declarations_rejected(self):
        content = BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr(
                "word/document.xml",
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b"<w:p><w:r><w:t>Session note</w:t></w:r></w:p></w:document>",
            )
        self.assertEqual(import_notes._docx_text(content.getvalue(), "notes.docx"), "Session note")

        malicious = BytesIO()
        with zipfile.ZipFile(malicious, "w") as archive:
            archive.writestr(
                "word/document.xml",
                '<!DOCTYPE x [<!ENTITY e "expanded">]><w:document xmlns:w="x">&e;</w:document>'.encode("utf-16"),
            )
        with self.assertRaises(import_notes.ImportFailure):
            import_notes._docx_text(malicious.getvalue(), "notes.docx")

    def test_docx_preserves_manual_line_breaks_and_tabs(self):
        content = BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr(
                "word/document.xml",
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b"<w:p><w:r><w:t>Alice: scout</w:t><w:br/><w:t>Bob:</w:t><w:tab/><w:t>rest</w:t>"
                b"<w:cr/><w:t>Carol: watch</w:t></w:r></w:p></w:document>",
            )

        self.assertEqual(
            import_notes._docx_text(content.getvalue(), "notes.docx"),
            "Alice: scout\nBob:\trest\nCarol: watch",
        )

    def test_docx_does_not_collect_nested_text_box_paragraphs_twice(self):
        content = BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr(
                "word/document.xml",
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b"<w:p><w:r><w:t>Anchor</w:t></w:r><w:drawing><w:txbxContent>"
                b"<w:p><w:r><w:t>Text box note</w:t></w:r></w:p>"
                b"</w:txbxContent></w:drawing></w:p></w:document>",
            )

        text = import_notes._docx_text(content.getvalue(), "notes.docx")
        self.assertEqual(text, "Anchor\nText box note")
        self.assertEqual(text.count("Text box note"), 1)

    def test_google_drive_paginates_through_short_and_empty_pages(self):
        def response(payload):
            result = Mock(status_code=200)
            result.raw.read.return_value = json.dumps(payload).encode()
            return result

        session = Mock()
        session.get.side_effect = [
            response({"files": [{"id": "one"}], "nextPageToken": "empty-page"}),
            response({"files": [], "nextPageToken": "last-page"}),
            response({"files": [{"id": "two"}]}),
        ]

        files = import_notes._google_drive_files(
            session,
            {"pageSize": "2"},
            2,
            (import_notes.requests.RequestException,),
        )

        self.assertEqual([file["id"] for file in files], ["one", "two"])
        self.assertEqual(session.get.call_count, 3)
        self.assertEqual(session.get.call_args_list[1].kwargs["params"]["pageToken"], "empty-page")
        self.assertEqual(session.get.call_args_list[2].kwargs["params"]["pageToken"], "last-page")

    def test_google_drive_page_cap_fails_instead_of_returning_partial_files(self):
        def response(payload):
            result = Mock(status_code=200)
            result.raw.read.return_value = json.dumps(payload).encode()
            return result

        session = Mock()
        session.get.side_effect = [
            response({"files": [{"id": "one"}], "nextPageToken": "next"}),
            response({"files": [], "nextPageToken": "still-next"}),
        ]
        with patch.object(import_notes, "MAX_GOOGLE_DRIVE_PAGES", 2):
            with self.assertRaisesRegex(import_notes.ImportFailure, "page limit"):
                import_notes._google_drive_files(
                    session,
                    {"pageSize": "2"},
                    2,
                    (import_notes.requests.RequestException,),
                )

    def test_obsidian_note_read_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "notes").mkdir()
            note = mock_open(read_data=b"x" * (import_notes.MAX_ITEM_BYTES + 1))
            with patch.dict(os.environ, {"OBSIDIAN_VAULT_PATH": "notes"}), \
                    patch("import_notes.Path.cwd", return_value=root), \
                    patch("import_notes.subprocess.run", return_value=Mock(stdout=b"notes/one.md\0")), \
                    patch.object(Path, "open", note):
                with self.assertRaises(import_notes.ImportFailure):
                    import_notes.import_obsidian(1)

        note().read.assert_called_once_with(import_notes.MAX_ITEM_BYTES + 1)

    def test_obsidian_rejects_tracked_markdown_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "notes"
            vault.mkdir()
            target = vault / "private.txt"
            target.write_text("not a Markdown note")
            (vault / "linked.md").symlink_to(target)
            with patch.dict(os.environ, {"OBSIDIAN_VAULT_PATH": "notes"}), \
                    patch("import_notes.Path.cwd", return_value=root), \
                    patch(
                        "import_notes.subprocess.run",
                        return_value=Mock(stdout=b"notes/linked.md\0"),
                    ):
                with self.assertRaisesRegex(import_notes.ImportFailure, "symlink"):
                    import_notes.import_obsidian(1)

    @patch("import_notes.requests.request")
    def test_redirect_is_not_followed_automatically(self, request):
        response = request.return_value
        response.status_code = 302
        response.headers = {"Location": "https://storage.example/download"}
        response.raw.read.return_value = b""

        status, headers, _ = import_notes._request(
            "https://graph.microsoft.com/content",
            headers={"Authorization": "Bearer token"},
        )

        self.assertEqual(status, 302)
        self.assertEqual(headers["Location"], "https://storage.example/download")
        self.assertFalse(request.call_args.kwargs["allow_redirects"])

    def test_obsidian_path_traversal_is_rejected(self):
        with patch.dict(os.environ, {"OBSIDIAN_VAULT_PATH": "../private"}):
            with self.assertRaises(import_notes.ImportFailure):
                import_notes.import_obsidian(1)

    def test_graph_download_redirect_does_not_forward_access_token(self):
        content = BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr(
                "word/document.xml",
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b"<w:p><w:r><w:t>DM notes</w:t></w:r></w:p></w:document>",
            )
        responses = [
            (200, {}, b'{"access_token":"secret-token"}'),
            (200, {}, json.dumps({"value": [{
                "id": "item-1",
                "name": "session.docx",
                "file": {},
                "lastModifiedDateTime": "2026-01-10T12:00:00Z",
                "webUrl": "https://example.test/session.docx",
            }]}).encode()),
            (302, {"Location": "https://tenant.sharepoint.com/download"}, b""),
            (200, {}, content.getvalue()),
        ]
        with patch.dict(
            os.environ,
            {
                "MS_GRAPH_TENANT_ID": "tenant",
                "MS_GRAPH_CLIENT_ID": "client",
                "MS_GRAPH_CLIENT_SECRET": "secret",
                "MS_GRAPH_DRIVE_ID": "drive",
                "MS_GRAPH_FOLDER_ID": "folder",
            },
        ), patch("import_notes._request", side_effect=responses) as request:
            records = import_notes.import_microsoft_365(1)

        self.assertEqual(records[0]["text"], "DM notes")
        self.assertIn("Authorization", request.call_args_list[2].kwargs["headers"])
        self.assertNotIn("Authorization", request.call_args_list[3].kwargs.get("headers", {}))

    def test_graph_download_rejects_unexpected_host(self):
        with patch("import_notes._request") as request:
            with self.assertRaises(import_notes.ImportFailure):
                import_notes._graph_download("https://attacker.example/file")
        request.assert_not_called()

    def test_google_folder_id_is_validated_before_authentication(self):
        with patch.dict(
            os.environ,
            {
                "GOOGLE_SERVICE_ACCOUNT_JSON": "{}",
                "GOOGLE_DRIVE_FOLDER_ID": "id' or trashed=false",
            },
        ):
            with self.assertRaises(import_notes.ImportFailure):
                import_notes.import_google_drive(1)


if __name__ == "__main__":
    unittest.main()
