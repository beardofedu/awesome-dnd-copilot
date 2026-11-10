import os
import json
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, mock_open, patch
from urllib.parse import parse_qs

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


class OneNoteTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(
            os.environ,
            {
                "ONENOTE_TENANT_ID": "consumers",
                "ONENOTE_CLIENT_ID": "client",
                "ONENOTE_REFRESH_TOKEN": "private-refresh-token",
                "ONENOTE_SECTION_ID": "section/id",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        request = patch("import_notes._request")
        self.request = request.start()
        self.addCleanup(request.stop)
        self.token_response = (200, {}, b'{"access_token":"private-access-token","refresh_token":"replacement"}')

    def test_refreshes_token_paginates_and_imports_bounded_plain_text_with_provenance(self):
        first = {
            "id": "page/one",
            "title": "Session one",
            "lastModifiedDateTime": "2026-11-10T12:00:00Z",
            "links": {"oneNoteWebUrl": {"href": "https://onenote.com/session-one"}},
        }
        next_url = "https://graph.microsoft.com/v1.0/me/onenote/sections/section%2Fid/pages?$skip=1"
        self.request.side_effect = [
            self.token_response,
            (200, {}, json.dumps({"value": [first], "@odata.nextLink": next_url}).encode()),
            (200, {}, json.dumps({"value": [], "@odata.nextLink": next_url + "0"}).encode()),
            (200, {}, b'{"value":[{"id":"two","title":"Session two"},{"id":"not-fetched"}]}'),
            (200, {}, (
                b"<html><head><title>Hidden title</title><style>hidden</style></head>"
                b"<body><p>Alice <b>scouts</b> &amp; waits.<br/>Bob rests.</p>"
                b"<ul><li>Find key</li><li>Open gate</li></ul>"
                b"<table><tr><td>Loot</td><td>10 gp</td></tr></table>"
                b'<script>hidden</script><img src="https://example.test/not-fetched"/>'
                b'<object data="https://example.test/attachment"></object></body></html>'
            )),
            (200, {}, "<p>The dragon's lair: caf\u00e9</p>".encode()),
        ]

        records = import_notes.import_onenote(2)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0], {
            "id": "page/one",
            "name": "Session one",
            "updated": first["lastModifiedDateTime"],
            "reference": "https://onenote.com/session-one",
            "text": "Alice scouts & waits.\nBob rests.\nFind key\nOpen gate\nLoot\t10 gp",
        })
        self.assertEqual(records[1]["text"], "The dragon's lair: caf\u00e9")
        token_call = self.request.call_args_list[0]
        self.assertEqual(token_call.args[0], "https://login.microsoftonline.com/consumers/oauth2/v2.0/token")
        grant = parse_qs(token_call.kwargs["data"].decode())
        self.assertEqual(grant["grant_type"], ["refresh_token"])
        self.assertEqual(grant["refresh_token"], ["private-refresh-token"])
        self.assertEqual(grant["scope"], ["https://graph.microsoft.com/Notes.Read offline_access"])
        listing_call = self.request.call_args_list[1]
        self.assertIn("/sections/section%2Fid/pages?", listing_call.args[0])
        self.assertIn("%24top=2", listing_call.args[0])
        self.assertEqual(self.request.call_args_list[2].args[0], next_url)
        self.assertEqual(
            self.request.call_args_list[4].args[0],
            "https://graph.microsoft.com/v1.0/me/onenote/pages/page%2Fone/content",
        )
        self.assertEqual(self.request.call_count, 6)
        markdown, _, _ = import_notes.render_notes("onenote", records)
        self.assertNotIn("private-", markdown)
        self.assertNotIn("replacement", markdown)

    def test_cli_writes_review_markdown_and_identity_outputs_without_credentials(self):
        self.request.side_effect = [
            self.token_response,
            (200, {}, b'{"value":[{"id":"one","title":"Session one"}]}'),
            (200, {}, b"<p>The party reached the keep.</p>"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "notes.md"
            github_output = Path(directory) / "github-output"
            with patch.object(sys, "argv", [
                "import_notes.py", "--source", "onenote", "--max-items", "1",
                "--output", str(output), "--github-output", str(github_output),
            ]), patch("sys.stdout") as stdout:
                self.assertEqual(import_notes.main(), 0)
            markdown = output.read_text()
            outputs = github_output.read_text()
            self.assertIn("The party reached the keep.", markdown)
            self.assertIn("Source ID: `one`", markdown)
            self.assertIn("marker=<!-- dnd-session-import:onenote:", outputs)
            self.assertIn("filename=onenote-", outputs)
            self.assertIn("Prepared 1 source records", str(stdout.write.call_args_list))
            for value in [markdown, outputs, str(stdout.write.call_args_list)]:
                self.assertNotIn("private-", value)
                self.assertNotIn("replacement", value)

    def test_missing_refresh_token_fails_before_network_access(self):
        with patch.dict(os.environ, {"ONENOTE_REFRESH_TOKEN": ""}):
            with self.assertRaisesRegex(import_notes.ImportFailure, "ONENOTE_REFRESH_TOKEN"):
                import_notes.import_onenote(1)
        self.request.assert_not_called()

    def test_sign_in_errors_and_malformed_tokens_do_not_disclose_provider_body(self):
        for response in [
            (400, {}, b'{"error_description":"private-refresh-token"}'),
            (200, {}, b"not-json-private-refresh-token"),
            (200, {}, b"[]"),
            (200, {}, b'{"access_token":""}'),
            (200, {}, b'{"access_token":123}'),
        ]:
            with self.subTest(response=response):
                self.request.side_effect = [response]
                with self.assertRaises(import_notes.ImportFailure) as error:
                    import_notes.import_onenote(1)
                self.assertNotIn("private-refresh-token", str(error.exception))

    def test_rejects_malformed_listings_and_page_ids(self):
        for listing in [[], {}, {"value": {}}, {"value": [None]}, {"value": [{"id": ""}]}]:
            with self.subTest(listing=listing):
                self.request.side_effect = [self.token_response, (200, {}, json.dumps(listing).encode())]
                with self.assertRaises(import_notes.ImportFailure):
                    import_notes.import_onenote(1)

    def test_rejects_untrusted_pagination_before_forwarding_token(self):
        for url in [
            "https://attacker.example/pages",
            "http://graph.microsoft.com/pages",
            "https://graph.microsoft.com:444/pages",
            "https://user@graph.microsoft.com/pages",
            "https://graph.microsoft.com:invalid/pages",
            "https://[invalid/pages",
            "",
            123,
        ]:
            with self.subTest(url=url):
                self.request.reset_mock()
                self.request.side_effect = [
                    self.token_response,
                    (200, {}, json.dumps({"value": [], "@odata.nextLink": url}).encode()),
                ]
                with self.assertRaises(import_notes.ImportFailure):
                    import_notes.import_onenote(2)
                self.assertEqual(self.request.call_count, 2)

    def test_page_scan_cap_does_not_return_partial_notes(self):
        self.request.side_effect = [
            self.token_response,
            *[(200, {}, b'{"value":[],"@odata.nextLink":"https://graph.microsoft.com/next"}')] * 10,
        ]
        with self.assertRaisesRegex(import_notes.ImportFailure, "page limit"):
            import_notes.import_onenote(2)

    def test_content_errors_redirects_and_oversized_pages_fail_without_output(self):
        for response in [
            (403, {}, b"private-provider-error"),
            (302, {"Location": "https://attacker.example/content"}, b""),
            (200, {}, b"x" * (import_notes.MAX_ITEM_BYTES + 1)),
            (200, {}, b"\xff"),
        ]:
            with self.subTest(status=response[0], size=len(response[2])):
                self.request.side_effect = [
                    self.token_response,
                    (200, {}, b'{"value":[{"id":"one"},{"id":"two"}]}'),
                    (200, {}, b"<p>Already fetched</p>"),
                    response,
                ]
                with tempfile.TemporaryDirectory() as directory:
                    output = Path(directory) / "notes.md"
                    with patch.object(sys, "argv", [
                        "import_notes.py", "--source", "onenote", "--max-items", "2", "--output", str(output),
                    ]), patch("sys.stderr"):
                        self.assertEqual(import_notes.main(), 1)
                    self.assertFalse(output.exists())

    def test_empty_section_or_image_only_page_cannot_publish_empty_success(self):
        for responses in [
            [(200, {}, b'{"value":[]}')],
            [(200, {}, b'{"value":[{"id":"one"}]}'), (200, {}, b'<body><img src="image"/></body>')],
        ]:
            with self.subTest(responses=responses):
                self.request.side_effect = [self.token_response, *responses]
                records = import_notes.import_onenote(1)
                self.assertEqual(records, [])
                with self.assertRaisesRegex(import_notes.ImportFailure, "no eligible notes"):
                    import_notes.render_notes("onenote", records)


if __name__ == "__main__":
    unittest.main()
