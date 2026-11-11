"""Focused generation, source-link, and progressive-enhancement checks."""

from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlparse

import build


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class CatalogTests(unittest.TestCase):
    def test_committed_page_matches_current_sources(self):
        self.assertEqual((build.HERE / "index.html").read_text(encoding="utf-8"),
                         build.render())

    def test_complete_primary_inventory_and_unique_paths(self):
        paths = [entry["path"] for entry in build.resources()]
        self.assertEqual(len(paths), len(set(paths)))
        expected = set()
        for phase in build.PHASES:
            expected.add(f"{phase}/copilot-instructions.md")
            for pattern in ("agents/*.md", "session-kits/*/README.md"):
                expected.update(path.relative_to(build.ROOT).as_posix()
                                for path in (build.ROOT / phase).glob(pattern))
        self.assertTrue(expected.issubset(paths))

    def test_links_resolve_to_real_resources_and_assets(self):
        page = Page(build.render())
        ids = {attrs["id"] for _, attrs in page.tags if "id" in attrs}
        for tag, attrs in page.tags:
            for attribute in ("href", "src"):
                if attribute not in attrs:
                    continue
                link = attrs[attribute]
                if link.startswith("#"):
                    self.assertIn(link[1:], ids)
                elif link.startswith("https:"):
                    url = urlparse(link)
                    self.assertEqual(url.netloc, "github.com")
                    prefix = "/beardofedu/awesome-dnd-copilot"
                    self.assertTrue(url.path.startswith(prefix))
                    if url.path != prefix:
                        self.assertTrue(url.path.startswith(prefix + "/blob/main/"))
                        source = unquote(url.path.removeprefix(prefix + "/blob/main/"))
                        self.assertTrue((build.ROOT / source).is_file(), link)
                else:
                    self.assertTrue((build.HERE / link).is_file(), link)

    def test_controls_are_labeled_and_all_cards_visible_without_scripts(self):
        page = Page(build.render())
        labels = {attrs["for"] for tag, attrs in page.tags if tag == "label"}
        controls = [attrs for tag, attrs in page.tags if tag in ("input", "select")]
        self.assertEqual(len(controls), 5)
        self.assertTrue(all(attrs["id"] in labels for attrs in controls))
        cards = [attrs for tag, attrs in page.tags if attrs.get("class") == "resource"]
        self.assertEqual(len(cards), len(build.resources()))
        self.assertTrue(all("hidden" not in attrs for attrs in cards))
        self.assertTrue(any(attrs.get("role") == "status" for _, attrs in page.tags))
        ids = [attrs["id"] for _, attrs in page.tags if "id" in attrs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_player_boundaries_and_optional_setup_tags(self):
        entries = {entry["path"]: entry for entry in build.resources()}
        party = entries["campaign-maintenance/session-kits/party-journal/README.md"]
        self.assertEqual(party["audience"], ["Players"])
        self.assertIn("Canvas", party["feature"])
        self.assertIn("Optional cloud automation", party["setup"])
        release = entries["campaign-maintenance/session-kits/player-safe-release/README.md"]
        self.assertEqual(release["audience"], ["DM", "Players"])
        self.assertNotIn("Cloud automations", release["feature"])
        adventure = entries["campaign-creation/session-kits/adventure-playtester/README.md"]
        self.assertEqual(adventure["feature"], ["Chat prompts"])
        self.assertEqual(adventure["audience"], ["DM"])

    def test_source_extraction_handles_markdown_and_escapes_html(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.md").write_text(
                "# Example <tool>\n\nUse **approved** [notes](notes.md)\n"
                "and `files` & review.\n\n## Setup\n", encoding="utf-8")
            with patch.object(build, "ROOT", root):
                title, summary = build.source_text("source.md")
                self.assertEqual(title, "Example <tool>")
                self.assertEqual(summary, "Use approved notes and files & review.")
                entry = build.resource("source.md", ["Creation"], ["DM"], ["Copy"], ["Chat"])
                with patch.object(build, "resources", return_value=[entry]):
                    rendered = build.render()
                    self.assertIn("Example &lt;tool&gt;", rendered)
                    self.assertNotIn("<tool>", rendered)


if __name__ == "__main__":
    unittest.main()
