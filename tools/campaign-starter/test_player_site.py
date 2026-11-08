from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urljoin, urlsplit

SITE = Path(__file__).absolute().parents[2] / "campaign-creation/templates/campaign-player-site/docs"
BASE = "https://example.invalid/campaign-preview/"


class Page(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.navigation = []
        self.main = []
        self.skip_links = []
        self.heading_count = 0
        self.in_nav = False
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.references.append(attrs[key])
        if tag == "nav":
            self.in_nav = True
        if tag == "a" and self.in_nav:
            self.navigation.append(attrs)
        if tag == "main":
            self.main.append(attrs)
        if tag == "h1":
            self.heading_count += 1
        if tag == "a" and "skip-link" in attrs.get("class", "").split():
            self.skip_links.append(attrs)

    def handle_endtag(self, tag):
        if tag == "nav":
            self.in_nav = False


class PlayerSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {path.name: Page(path.read_text(encoding="utf-8"))
                     for path in SITE.glob("*.html")}

    def test_links_and_assets_resolve_under_a_project_pages_prefix(self):
        self.assertTrue(self.pages, "No scaffold pages found")
        for name, page in self.pages.items():
            for reference in page.references:
                with self.subTest(page=name, reference=reference):
                    url = urlsplit(urljoin(BASE + name, reference))
                    self.assertEqual(url.netloc, "example.invalid", "Scaffold must be self-contained")
                    self.assertTrue(url.path.startswith("/campaign-preview/"),
                                    "Root-relative links break project Pages sites")
                    relative = unquote(url.path.removeprefix("/campaign-preview/"))
                    target = (SITE / relative).resolve()
                    self.assertTrue(target.is_relative_to(SITE.resolve()))
                    self.assertTrue(target.is_file(), f"Missing published target: {relative}")
                    if url.fragment:
                        self.assertIn(url.fragment, self.pages[relative].ids)

    def test_navigation_is_consistent_and_identifies_the_current_page(self):
        expected = set(self.pages)
        for name, page in self.pages.items():
            with self.subTest(page=name):
                self.assertEqual({link["href"] for link in page.navigation}, expected)
                current = [link["href"] for link in page.navigation
                           if link.get("aria-current") == "page"]
                self.assertEqual(current, [name])

    def test_each_page_has_a_keyboard_skip_target_and_one_main_heading(self):
        for name, page in self.pages.items():
            with self.subTest(page=name):
                self.assertEqual(page.heading_count, 1)
                self.assertEqual(len(page.main), 1)
                self.assertEqual(len(page.skip_links), 1)
                self.assertEqual(page.skip_links[0]["href"], "#" + page.main[0]["id"])
                self.assertEqual(page.main[0].get("tabindex"), "-1")


if __name__ == "__main__":
    unittest.main()
