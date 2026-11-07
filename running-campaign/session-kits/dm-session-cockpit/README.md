# DM Session Cockpit

Keep scene cards, NPC references, hooks, and combat bookkeeping beside Copilot
chat. Works alone; it does not require Session Bridge.

Follow the library's [copy-in setup guide](https://github.com/beardofedu/awesome-dnd-copilot/blob/main/session-kits.md). In your own
campaign, this folder belongs at `.github/session-kits/dm-session-cockpit/`.

| File | Purpose |
|---|---|
| `canvas.prompt.md` | Generate the native table-facing DM Canvas |
| `automation.prompt.md` | Standalone prep-drafting instructions |
| `automation.recipe.json` | Paused, label-triggered preparation settings |
| `state.example.json` | Fictional scenes and combat state |

## Quick start after copying

In an App session for your campaign repository, run:

```text
/create-canvas Read .github/session-kits/dm-session-cockpit/canvas.prompt.md and build that Canvas.
```

Start empty before real play. For optional automation, ask Copilot to read this
kit's `automation.recipe.json` and `automation.prompt.md`, check live support,
and propose creating it paused in the selected campaign repository. Approve
creation and activation separately; copying files does not install or enable it.
The recipe's `prompt_file` must be resolved to the complete prompt text.

## Prep input

Create an issue in a **DM-only repository**:

```markdown
## Session
ID: session-02
Date: 2026-01-17
Rules: D&D 5e 2024; list house rules here
Tone: adventurous high fantasy

## Approved context
Paste approved facts and follow-ups, or exact paths to relevant campaign files.

## Prep request
Prepare three scene cards, two NPC references, and unresolved hooks.
Keep new encounter ideas clearly marked as proposals.
```

Create the `session-prep` label during approved setup and apply it when ready.
The automation drafts at most five scenes, ten NPC references, and ten hooks.
It never changes canon, rolls dice, advances initiative, or runs combat unattended.
A label-triggered recipe avoids scheduling guesses; you can separately approve
a weekly schedule if that better fits your group.

## At the table

Import and review prep, then enter combatants and rolled initiative yourself.
HP, rounds, and conditions use deterministic controls, not model arithmetic.
The DM resolves initiative ties and condition expiry; "next turn" does not
automatically decide concentration, saving throws, death, or resource recovery.
Specify 2014/2024 rules and house rules before asking Copilot for a ruling.

Record information-finding interruptions and correction effort after play if
you want evidence for later prompt improvements.

For manual drafting, ask an App agent to follow `automation.prompt.md` for a
supplied issue; unavailable posting must be reported as an unsaved chat draft.
