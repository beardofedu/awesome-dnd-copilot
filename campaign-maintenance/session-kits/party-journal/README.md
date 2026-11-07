# Party Journal & Quest Board

Give players a shared reference for known quests, discoveries, inventory, and
next-session plans. Works alone; no access to a DM kit is needed or granted.

Follow the library's [copy-in setup guide](https://github.com/beardofedu/awesome-dnd-copilot/blob/main/session-kits.md). In your own
campaign, this folder belongs at `.github/session-kits/party-journal/`.

| File | Purpose |
|---|---|
| `canvas.prompt.md` | Generate the player-facing journal and planning board |
| `automation.prompt.md` | Standalone player-note drafting instructions |
| `automation.recipe.json` | Paused request-label automation settings |
| `state.example.json` | Fictional player-visible quest and inventory data |

## Quick start after copying

In an App session for your campaign repository, run:

```text
/create-canvas Read .github/session-kits/party-journal/canvas.prompt.md and build that Canvas.
```

Start empty before real play. For optional automation, ask Copilot to read this
kit's `automation.recipe.json` and `automation.prompt.md`, check live support,
and propose creating it paused in the selected campaign repository. Approve
creation and activation separately; copying files does not install or enable it.
The recipe's `prompt_file` must be resolved to the complete prompt text.

## Player-safe input

Use a party repository that contains **only information its readers may know**.
The DM explicitly exports approved information here; do not give this automation
DM-repository access. A `player-safe` label is a workflow convention, not privacy.

Create one session issue:

```markdown
## Session
ID: session-01
Date: 2026-01-10
Rules: D&D 5e 2024; list known house rules here
Tone: adventurous high fantasy

## Approved player notes
List things the party actually learned or did. Do not include DM secrets.

## Confirmed inventory changes
Record item, resulting total quantity, holder, and who confirmed the total.

## Player questions
List uncertain details or theories separately from established facts.
```

Create `player-safe` and `journal-update` labels during approved setup.
After checking the issue and comments for spoilers, add `player-safe`, then
`journal-update` to request a draft. The latter is the event label; the former
is an additional eligibility filter. Writer-only triggers mean a player without
write permission needs a writer to apply the request label.

## Use it together

The Canvas supports quest cards, known NPC/location references, inventory,
theories, and plans with manually recorded votes. This is shared repository
content, **not live multi-user synchronization or authenticated polling**.
Persisted changes require explicit commits to share; concurrent file changes
must be reconciled, not silently overwritten.

Imports default to reviewed updates, preserving older quests, inventory,
references, and plans. Confirm each addition/change; reconcile stable IDs for
existing entries. Full replacement is a separate explicit action.

Inventory is a record, not an economy engine. Confirm quantities and ownership;
the automation never spends gold, awards treasure, or decides rewards.
Measure forgotten goals and correction effort after play if you want evidence
for later improvements.

For manual drafting, ask an App agent to follow `automation.prompt.md` for a
supplied issue; it must distinguish unsaved chat output from a posted comment.
