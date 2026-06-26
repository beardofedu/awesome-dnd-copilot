# awesome-dnd-copilot- 🐉

A curated collection of high-quality **GitHub Copilot** instruction files and custom agents for **Dungeons & Dragons** — covering campaign creation, campaign maintenance, and running actual sessions.

## What's in here?

Each folder contains ready-to-use Copilot files. Copy what you need into your own repository's `.github/` directory.

| Folder | Purpose |
|---|---|
| [`campaign-creation/`](./campaign-creation/) | Build worlds, write lore, design adventures, and generate NPCs |
| [`campaign-maintenance/`](./campaign-maintenance/) | Track story arcs, manage session notes, and keep lore consistent |
| [`running-campaign/`](./running-campaign/) | Run sessions, improvise encounters, voice NPCs, and narrate scenes |

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
│   └── agents/
│       ├── lore-keeper.md        # Agent for lore consistency
│       ├── session-notes.md      # Agent for session summaries and notes
│       ├── campaign-tracker.md   # Agent for tracking story arcs and threads
│       └── notes-analysis.md     # Agent for analyzing GitHub Issue notes and campaign impact
└── running-campaign/
    ├── copilot-instructions.md   # Base instructions for running sessions
    └── agents/
        ├── dungeon-master.md     # Agent for DM narration and rulings
        ├── npc-voice.md          # Agent for voicing and roleplaying NPCs
        └── encounter-improv.md   # Agent for improvising encounters
```

## Contributing

Feel free to open a PR with your own Copilot instruction files and agents! The goal is to grow a high-quality library of D&D-focused AI tools.
