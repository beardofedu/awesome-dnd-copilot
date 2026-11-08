import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location("installer", HERE / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.dest = self.root / "campaign"
        self.source.mkdir()
        self.dest.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.write("campaign-creation/copilot-instructions.md", "profile")
        self.write("campaign-maintenance/copilot-instructions.md", "other profile")
        self.write("campaign-creation/agents/world-builder.md", "agent")
        self.write("campaign-creation/agents/npc-creator.md", "other agent")
        self.add_kit("first")
        self.add_kit("other")
        self.write("campaign-creation/templates/campaign-starter/canon/README.md", "empty")
        self.write("campaign-creation/templates/player-starter/.github/copilot-instructions.md", "players only")
        self.write("campaign-creation/templates/player-starter/journal/README.md", "approved recaps")
        self.write("campaign-creation/templates/player-starter/README.md", "player workspace")
        self.write("campaign-creation/templates/player-starter/campaign.md", "shared metadata")
        self.write("campaign-creation/templates/player-starter/quests/README.md", "known quests")
        self.write("campaign-creation/templates/player-starter/world/README.md", "discovered world")
        self.write("campaign-creation/templates/campaign-player-site/README.md", "library setup guide")
        self.write("campaign-creation/templates/campaign-player-site/customize.prompt.md", "customize")
        self.write("campaign-creation/templates/campaign-player-site/docs/index.html", "fictional hub")
        self.write("campaign-creation/templates/campaign-player-site/docs/.nojekyll", "")
        self.write("campaign-creation/templates/campaign-player-site/docs/assets/style.css", "styles")
        for name in ("party", "journal", "world", "rules", "safety"):
            self.write(f"campaign-creation/templates/campaign-player-site/docs/{name}.html", name)
        self.commit()

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.source), *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def write(self, name, content):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def add_kit(self, name):
        for file in ("README.md", "automation.prompt.md", "automation.recipe.json",
                     "canvas.prompt.md", "state.example.json"):
            self.write(f"running-campaign/session-kits/{name}/{file}", file)
        self.write(f"running-campaign/session-kits/{name}/workflows/template.yml", "not active")

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def plan(self, **kwargs):
        return installer.plan(self.source, self.dest, kwargs.get("profile", "campaign-creation"),
                              kwargs.get("agents", []), kwargs.get("kits", []), kwargs.get("starter", False))

    def test_preview_writes_nothing_and_apply_selects_only_requested(self):
        with mock.patch.object(installer, "SOURCE", self.source), contextlib.redirect_stdout(io.StringIO()):
            args = [str(self.dest), "--profile", "campaign-creation", "--agent",
                    "campaign-creation/world-builder.md", "--kit", "running-campaign/first", "--starter"]
            self.assertEqual(installer.main(args), 0)
            self.assertEqual(list(self.dest.iterdir()), [])
            self.assertEqual(installer.main(args + ["--apply"]), 0)
        self.assertEqual((self.dest / ".github/copilot-instructions.md").read_text(), "profile")
        self.assertEqual((self.dest / ".github/agents/world-builder.md").read_text(), "agent")
        self.assertFalse((self.dest / ".github/agents/npc-creator.md").exists())
        self.assertTrue((self.dest / ".github/session-kits/first/workflows/template.yml").exists())
        self.assertFalse((self.dest / ".github/session-kits/other").exists())
        self.assertFalse((self.dest / ".github/workflows").exists())
        self.assertTrue((self.dest / "canon/README.md").exists())

    def test_conflict_prevents_all_writes_even_identical_and_preserves_unrelated(self):
        agent = self.dest / ".github/agents/world-builder.md"
        agent.parent.mkdir(parents=True)
        agent.write_text("agent")
        unrelated = self.dest / "notes.md"
        unrelated.write_text("keep")
        with self.assertRaises(installer.InstallError):
            self.plan(agents=["campaign-creation/world-builder.md"])
        self.assertFalse((self.dest / ".github/copilot-instructions.md").exists())
        self.assertEqual(agent.read_text(), "agent")
        self.assertEqual(unrelated.read_text(), "keep")

    def test_player_templates_preview_and_install_without_dm_files_or_activation(self):
        with mock.patch.object(installer, "SOURCE", self.source), contextlib.redirect_stdout(io.StringIO()):
            args = [str(self.dest), "--player-starter", "--player-site"]
            self.assertEqual(installer.main(args), 0)
            self.assertEqual(list(self.dest.iterdir()), [])
            self.assertEqual(installer.main(args + ["--apply"]), 0)
        self.assertEqual((self.dest / ".github/copilot-instructions.md").read_text(), "players only")
        self.assertTrue((self.dest / "journal/README.md").is_file())
        self.assertTrue((self.dest / "docs/.nojekyll").is_file())
        self.assertEqual((self.dest / "docs/assets/style.css").read_text(), "styles")
        self.assertEqual((self.dest / ".github/prompts/customize-campaign-site.prompt.md").read_text(),
                         "customize")
        self.assertFalse((self.dest / "canon").exists())
        self.assertFalse((self.dest / ".github/workflows").exists())
        self.assertEqual((self.dest / "README.md").read_text(), "player workspace")

    def test_site_only_preserves_existing_player_instructions(self):
        instructions = self.dest / ".github/copilot-instructions.md"
        instructions.parent.mkdir()
        instructions.write_text("existing player instructions")
        entries = installer.plan(self.source, self.dest, None, [], [], False,
                                 with_player_site=True)
        installer.apply(entries, self.dest)
        self.assertEqual(instructions.read_text(), "existing player instructions")
        self.assertTrue((self.dest / "docs/index.html").is_file())
        self.assertFalse((self.dest / "journal").exists())

    def test_player_templates_reject_dm_combinations_and_existing_site_before_writes(self):
        for player_starter, player_site in ((True, False), (False, True), (True, True)):
            with self.subTest(player_starter=player_starter, player_site=player_site):
                with self.assertRaisesRegex(installer.InstallError, "cannot be combined"):
                    installer.plan(self.source, self.dest, "campaign-creation", [], [], False,
                                   player_starter, player_site)
                with self.assertRaisesRegex(installer.InstallError, "cannot be combined"):
                    installer.plan(self.source, self.dest, None, [], [], True,
                                   player_starter, player_site)
        page = self.dest / "docs/index.html"
        page.parent.mkdir()
        page.write_text("keep")
        with self.assertRaisesRegex(installer.InstallError, "already exists"):
            installer.plan(self.source, self.dest, None, [], [], False, True, True)
        self.assertEqual(page.read_text(), "keep")
        self.assertFalse((self.dest / ".github").exists())

    def test_player_site_symlink_and_missing_committed_templates_are_rejected(self):
        (self.dest / "docs").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(installer.InstallError, "Symlink"):
            installer.plan(self.source, self.dest, None, [], [], False, with_player_site=True)
        (self.dest / "docs").unlink()
        self.git("rm", "-qr", "campaign-creation/templates/campaign-player-site")
        self.commit()
        with self.assertRaisesRegex(installer.InstallError, "No committed player site"):
            installer.plan(self.source, self.dest, None, [], [], False, with_player_site=True)

    def test_incomplete_player_templates_do_not_install_a_partial_workspace_or_site(self):
        self.git("rm", "campaign-creation/templates/player-starter/.github/copilot-instructions.md",
                 "campaign-creation/templates/campaign-player-site/docs/party.html")
        self.commit()
        for option in ("with_player_starter", "with_player_site"):
            with self.subTest(option=option):
                with self.assertRaisesRegex(installer.InstallError, "Incomplete player"):
                    installer.plan(self.source, self.dest, None, [], [], False, **{option: True})
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_rejects_source_and_destination_symlinks_and_traversal(self):
        (self.dest / ".github").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            self.plan()
        (self.dest / ".github").unlink()
        agent = self.source / "campaign-creation/agents/world-builder.md"
        agent.unlink()
        agent.symlink_to(self.source / "campaign-creation/copilot-instructions.md")
        with self.assertRaises(installer.InstallError):
            self.plan(agents=["campaign-creation/world-builder.md"])
        with self.assertRaises(installer.InstallError):
            self.plan(kits=["../first"])
        with self.assertRaises(installer.InstallError):
            installer.clean_relative("a/../outside")
        with self.assertRaises(installer.InstallError):
            installer.plan(self.source, self.source, "campaign-creation", [], [], False)
        with self.assertRaises(installer.InstallError):
            installer.plan(self.source, self.source / "campaign-creation", "campaign-creation", [], [], False)
        with self.assertRaises(installer.InstallError):
            installer.plan(self.source, self.dest / ".." / "campaign", "campaign-creation", [], [], False)

    def test_later_committed_complete_kit_is_discovered(self):
        self.add_kit("later")
        self.assertNotIn("running-campaign/later", installer.discover(self.source)[2])
        self.write("running-campaign/session-kits/incomplete/README.md", "incomplete")
        self.commit()
        kits = installer.discover(self.source)[2]
        self.assertIn("running-campaign/later", kits)
        self.assertNotIn("running-campaign/incomplete", kits)
        entries = self.plan(kits=["running-campaign/later"])
        installer.apply(entries, self.dest)
        self.assertTrue((self.dest / ".github/session-kits/later/state.example.json").exists())

    def test_manual_kit_requires_its_documented_committed_files(self):
        prefix = "campaign-creation/session-kits/adventure-playtester"
        self.write(f"{prefix}/README.md", """# Adventure Playtester
## Contents
| File | Purpose |
|---|---|
| `adventure-playtester.prompt.md` | Prompt |
| `input.template.md` | Input |
| `review-contract.md` | Contract |
| `example-review.md` | Example |
| `LICENSE` | License |
""")
        for name in ("adventure-playtester.prompt.md", "input.template.md", "review-contract.md"):
            self.write(f"{prefix}/{name}", name)
        self.commit()
        self.write(f"{prefix}/example-review.md", "fictional review")
        self.commit()
        self.assertNotIn("campaign-creation/adventure-playtester", installer.discover(self.source)[2])
        self.write(f"{prefix}/LICENSE", "license")
        self.commit()
        self.write(f"{prefix}/untracked.md", "not installed")
        entries = self.plan(kits=["campaign-creation/adventure-playtester"])
        installer.apply(entries, self.dest)
        installed = self.dest / ".github/session-kits/adventure-playtester"
        self.assertEqual({p.name for p in installed.iterdir()}, {
            "README.md", "adventure-playtester.prompt.md", "input.template.md",
            "review-contract.md", "example-review.md", "LICENSE"})

    def test_write_failure_rolls_back_only_created_paths(self):
        unrelated = self.dest / "keep.txt"
        unrelated.write_text("keep")
        entries = self.plan(agents=["campaign-creation/world-builder.md"])
        original = Path.open
        def fail_on_agent(path, *args, **kwargs):
            if path.name == "world-builder.md" and args and args[0] == "xb":
                raise OSError("simulated write failure")
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "open", fail_on_agent), self.assertRaises(installer.InstallError):
            installer.apply(entries, self.dest)
        self.assertEqual(unrelated.read_text(), "keep")
        self.assertFalse((self.dest / ".github").exists())

    def test_duplicate_profile_and_colliding_agents_are_rejected(self):
        with mock.patch.object(installer, "SOURCE", self.source), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(installer.main([str(self.dest), "--profile", "campaign-creation",
                                             "--profile", "campaign-maintenance"]), 1)
        self.write("running-campaign/agents/world-builder.md", "different")
        self.commit()
        with self.assertRaises(installer.InstallError):
            self.plan(agents=["campaign-creation/world-builder.md", "running-campaign/world-builder.md"])


if __name__ == "__main__":
    unittest.main()
