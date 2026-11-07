import os
import json
import sys
import unittest
import zipfile
from io import BytesIO
from unittest.mock import patch

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
                b'<!DOCTYPE x [<!ENTITY e "expanded">]><w:document xmlns:w="x"/>',
            )
        with self.assertRaises(import_notes.ImportFailure):
            import_notes._docx_text(malicious.getvalue(), "notes.docx")

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
