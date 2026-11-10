# awesome-dnd-copilot- 🐉

A curated collection of high-quality **GitHub Copilot** instruction files and custom agents for **Dungeons & Dragons** — covering campaign creation, campaign maintenance, and running actual sessions.

## What's in here?

Each folder contains ready-to-use Copilot files. Copy what you need into your own repository's `.github/` directory.

Templates are the exception: campaign workspace files go at the destination
repository root, and website files go in `docs/`. See the placement table below.

| Folder | Purpose |
|---|---|
| [`campaign-creation/`](./campaign-creation/) | Build worlds, write lore, design adventures, and generate NPCs |
| [`campaign-maintenance/`](./campaign-maintenance/) | Track story arcs, manage session notes, and keep lore consistent |
| [`running-campaign/`](./running-campaign/) | Run sessions, improvise encounters, voice NPCs, and narrate scenes |

## Choose a starting point

| If you want to... | Start here |
|---|---|
| Create a world, campaign brief, or adventure | [`campaign-creation/`](./campaign-creation/) |
| Keep notes, canon, arcs, or factions consistent | [`campaign-maintenance/`](./campaign-maintenance/) |
| Prepare or run a session | [`running-campaign/`](./running-campaign/) |
| Give players a separate, reviewed workspace or website | [Player starter](./campaign-creation/templates/player-starter/) and [player-site guide](./campaign-creation/templates/campaign-player-site/) |
| See the resources used together from setup through sharing | [First campaign walkthrough](./examples/first-campaign/README.md) |

New to the library? Start with the [five-minute quickstart](./QUICKSTART.md)
to choose, preview, install, and inspect a fictional sample. Read the
[compatibility guide](./COMPATIBILITY.md) for feature requirements; availability
depends on your account, repository, and organization settings.

## Start a campaign workspace

Use the [campaign starter and selective installer](./tools/campaign-starter/README.md)
to preview an empty DM workspace with one instruction profile, or a separate
[player workspace](./campaign-creation/templates/player-starter/). Choose agents
and session kits individually. Applying is explicit; copying files does not
activate services or change repository permissions.

## Build a campaign player website

The [campaign player-site scaffold](./campaign-creation/templates/campaign-player-site/)
provides a responsive HTML/CSS hub: overview, party, journal and quests,
discovered world, rules, and general table-safety procedures. It includes
fictional examples, a Copilot customization prompt, local preview instructions,
and explicit GitHub Pages setup. No framework or build step is required.

From this library's checkout, preview a new, separate player workspace:

```bash
mkdir -p /path/to/player-repository
python3 tools/campaign-starter/install.py /path/to/player-repository \
  --player-starter --player-site
# After reviewing the preview, repeat with --apply.
```

Use `--player-site` alone for an existing player workspace. Keep DM secrets in
a different repository. Sharing with players is not permission for public
publication; review all final site files before enabling Pages. Use the
[player-safe-release kit](./campaign-maintenance/session-kits/player-safe-release/)
for reviewed manual exports, not automated DM-repository access.

## Copilot App session kits

Use [plug-and-play session kits](./session-kits.md) alongside your existing
campaign instructions. The three Canvas starter kits are:

| Kit | Helps with |
|---|---|
| [Session Bridge](./campaign-maintenance/session-kits/session-bridge/) | Recaps, continuity, and next-session follow-ups |
| [DM Session Cockpit](./running-campaign/session-kits/dm-session-cockpit/) | Scene cards, NPC references, initiative, and conditions |
| [Party Journal & Quest Board](./campaign-maintenance/session-kits/party-journal/) | Player-visible quests, inventory, discoveries, and plans |

Each includes a native Canvas creation prompt, an optional paused cloud
automation recipe, and fictional sample data. Canvases are generated once in
the App, not registered just by copying files. See the
[setup guide](./session-kits.md) for copy commands, activation approval, and
the DM-secret/player-data boundary.

The [complete kit catalog](./session-kits.md#complete-kit-catalog) also covers
session zero, adventure playtesting, campaign health, canon checks, character
arcs, continuity, faction clocks, player submissions, player-safe releases,
and encounter stress testing. Each kit's own README is its setup authority;
not every kit uses a Canvas or cloud automation.

## How to use these files

### Installation destinations and activation

Paths below are in **your campaign repository**, not this template library.
Use fresh destinations for manual copies; the selective installer refuses to
overwrite existing files and keeps workflows inactive.

| Resource in this library | Destination | What activates it |
|---|---|---|
| One `<phase>/copilot-instructions.md` | `.github/copilot-instructions.md` in a DM workspace | Copilot reads repository instructions |
| Selected `<phase>/agents/*.md` | `.github/agents/` | Select the custom agent in a supported Copilot surface |
| Selected `<phase>/session-kits/<kit>/` | `.github/session-kits/<kit>/` | Follow that kit's README; copying alone activates nothing |
| DM or player workspace template contents | Repository root, preserving nested paths | Manual editing; no service activation |
| Player-site `docs/` | Player repository's `docs/` | Explicitly configure Pages after public-content review |
| Player-site `customize.prompt.md` | `.github/prompts/customize-campaign-site.prompt.md` | Explicitly request customization; it does not publish |
| Kit workflow templates | Keep inside the kit until reviewed; then `.github/workflows/<name>.yml` | Committing an active workflow enables its configured triggers |
| Session-note importer | `.github/session-note-importers/` plus selected `.github/workflows/` files | Configure dependencies, credentials, and permissions; manually dispatch |

Do not copy multiple profiles over one another, install task prompts as agents,
or place the website under `.github/`. A cloud recipe is installation data,
not a directly importable resource. Canvas generation, automation creation and
activation, workflow installation, and Pages publication are separate decisions.
Repository access is enforced by permissions, never by folders or labels.

### Copilot Instructions (`copilot-instructions.md`)

These files go in your repository at `.github/copilot-instructions.md`. They set the context so GitHub Copilot understands you're working on a D&D campaign.

```bash
# Copy a template to your own repo
mkdir -p /path/to/your-repo/.github
cp campaign-creation/copilot-instructions.md /path/to/your-repo/.github/copilot-instructions.md
```

### Custom Agents (`agents/*.md`)

Each `agents/` subdirectory contains individual Copilot agent definition files. Copy any agents you want to use into your own repo at `.github/agents/`.

```bash
# Copy one selected agent into a fresh destination
mkdir -p /path/to/your-repo/.github/agents
cp campaign-creation/agents/world-builder.md /path/to/your-repo/.github/agents/
```

### Custom agent catalog

| Phase | Agents |
|---|---|
| Campaign creation | [World Builder](./campaign-creation/agents/world-builder.md), [NPC Creator](./campaign-creation/agents/npc-creator.md), [Adventure Designer](./campaign-creation/agents/adventure-designer.md), [Adventure Playtester](./campaign-creation/agents/adventure-playtester.md), [Session Zero](./campaign-creation/agents/session-zero.md) |
| Campaign maintenance | [Lore Keeper](./campaign-maintenance/agents/lore-keeper.md), [Session Notes](./campaign-maintenance/agents/session-notes.md), [Campaign Tracker](./campaign-maintenance/agents/campaign-tracker.md), [Notes Analysis](./campaign-maintenance/agents/notes-analysis.md), [Canon Consistency](./campaign-maintenance/agents/canon-consistency.md), [Character Arc Weaver](./campaign-maintenance/agents/character-arc-weaver.md) |
| Running a campaign | [Dungeon Master](./running-campaign/agents/dungeon-master.md), [NPC Voice](./running-campaign/agents/npc-voice.md), [Encounter Improv](./running-campaign/agents/encounter-improv.md) |

### Session note import workflows

The [source-specific GitHub Actions templates](./campaign-maintenance/actions/session-note-importers/)
import approved notes from Discord, Google Docs, Microsoft 365, or a Git-tracked
Obsidian folder. Install each workflow independently in a private, DM-only
campaign repository and choose an Issue or Pull request for review on each
manual run. Provider credentials and API permissions are configured by the
campaign owner.

## Structure

```
awesome-dnd-copilot-/
├── campaign-creation/
│   ├── copilot-instructions.md
│   ├── agents/
│   ├── session-kits/
│   └── templates/
│       ├── campaign-starter/     # Private DM workspace
│       ├── player-starter/       # Separate player workspace
│       └── campaign-player-site/ # Public player-hub scaffold
├── campaign-maintenance/
│   ├── copilot-instructions.md
│   ├── agents/
│   ├── actions/session-note-importers/
│   └── session-kits/
├── running-campaign/
│   ├── copilot-instructions.md
│   ├── agents/
│   └── session-kits/
├── tools/
│   ├── campaign-starter/         # Selective installer and scaffold checks
│   └── prompt-regression/        # Deterministic output-contract checks
└── session-kits.md               # Complete kit catalog and Canvas setup
```

## Deterministic checks

The [library CI workflow](./.github/workflows/prompt-regression.yml) runs the
installer and website checks, prompt contracts, note-importer tests, campaign
health checks, canon checks, faction clocks, player-export validation, and
encounter tests. Importer tests use mocked providers, not live credentials.
Use the focused commands in each resource's README for local development.
Static checks do not prove prompt quality, factual accuracy, or spoiler safety.

## Contributing

Contributions are welcome. Read the [contribution guide](./CONTRIBUTING.md)
before opening an issue or pull request. This repository is licensed under the
[MIT License](./LICENSE); see [attribution and third-party content guidance](./ATTRIBUTION.md)
for the scope of that license and references to Dungeons & Dragons.
