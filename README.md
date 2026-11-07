# awesome-dnd-copilot- 🐉

A curated collection of high-quality **GitHub Copilot** instruction files and custom agents for **Dungeons & Dragons** — covering campaign creation, campaign maintenance, and running actual sessions.

## What's in here?

Each folder contains ready-to-use Copilot files. Copy what you need into your own repository's `.github/` directory.

| Folder | Purpose |
|---|---|
| [`campaign-creation/`](./campaign-creation/) | Build worlds, write lore, design adventures, and generate NPCs |
| [`campaign-maintenance/`](./campaign-maintenance/) | Track story arcs, manage session notes, and keep lore consistent |
| [`running-campaign/`](./running-campaign/) | Run sessions, improvise encounters, voice NPCs, and narrate scenes |

## Start a campaign workspace

Use the [campaign starter and selective installer](./tools/campaign-starter/README.md)
to preview an empty DM workspace and choose one instruction profile, agents,
and session kits. Applying is explicit; copying files does not activate services
or make a repository private. Review player exports separately.

## Copilot App session kits

Use [plug-and-play session kits](./session-kits.md) alongside your existing
campaign instructions. Copy one kit, mix them, or install all three:

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

## How to use these files

### Copilot Instructions (`copilot-instructions.md`)

These files go in your repository at `.github/copilot-instructions.md`. They set the context so GitHub Copilot understands you're working on a D&D campaign.

```bash
# Copy a template to your own repo
cp campaign-creation/copilot-instructions.md /path/to/your-repo/.github/copilot-instructions.md
```

### Custom Agents (`agents/*.md`)

Each `agents/` subdirectory contains individual Copilot agent definition files. Copy any agents you want to use into your own repo at `.github/agents/`.

```bash
# Copy all campaign-creation agents
cp -r campaign-creation/agents/ /path/to/your-repo/.github/agents/
```

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
│   ├── copilot-instructions.md   # Base instructions for campaign creation
│   └── agents/
│       ├── world-builder.md      # Agent for world and setting creation
│       ├── npc-creator.md        # Agent for NPC generation
│       └── adventure-designer.md # Agent for quest and encounter design
├── campaign-maintenance/
│   ├── copilot-instructions.md   # Base instructions for campaign maintenance
│   ├── agents/
│   │   ├── lore-keeper.md        # Agent for lore consistency
│   │   ├── session-notes.md      # Agent for session summaries and notes
│   │   ├── campaign-tracker.md   # Agent for tracking story arcs and threads
│   │   └── notes-analysis.md     # Agent for analyzing GitHub Issue notes and campaign impact
│   └── session-kits/
│       ├── session-bridge/       # Recap and continuity automation/Canvas kit
│       └── party-journal/        # Player journal automation/Canvas kit
└── running-campaign/
    ├── copilot-instructions.md   # Base instructions for running sessions
    ├── agents/
    │   ├── dungeon-master.md     # Agent for DM narration and rulings
    │   ├── npc-voice.md          # Agent for voicing and roleplaying NPCs
    │   └── encounter-improv.md   # Agent for improvising encounters
    └── session-kits/
        └── dm-session-cockpit/   # Prep automation and table-facing Canvas kit
```

## Contributing

Feel free to open a PR with your own Copilot instruction files and agents! The goal is to grow a high-quality library of D&D-focused AI tools.
