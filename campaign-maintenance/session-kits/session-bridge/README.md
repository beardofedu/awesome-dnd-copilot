# Session Bridge

Turn one session's rough notes into a reviewable recap, continuity record, and
next-session checklist. Works alone; no other kit or agent is required.

Follow the library's [copy-in setup guide](https://github.com/beardofedu/awesome-dnd-copilot/blob/main/session-kits.md). In your own
campaign, this folder belongs at `.github/session-kits/session-bridge/`.

| File | Purpose |
|---|---|
| `canvas.prompt.md` | Generate the editable session dashboard in the Copilot App |
| `automation.prompt.md` | Complete standalone drafting instructions |
| `automation.recipe.json` | Paused cloud automation settings for the installer |
| `state.example.json` | Fictional example and version-1 state shape |

## Quick start after copying

In an App session for your campaign repository, run:

```text
/create-canvas Read .github/session-kits/session-bridge/canvas.prompt.md and build that Canvas.
```

Start empty before real play. For optional automation, ask Copilot to read this
kit's `automation.recipe.json` and `automation.prompt.md`, check live support,
and propose creating it paused in the selected campaign repository. Approve
creation and activation separately; copying files does not install or enable it.
The recipe's `prompt_file` must be resolved to the complete prompt text.

## Session input

Create an issue in a **DM-only repository** with this body:

```markdown
## Session
ID: session-01
Date: 2026-01-10
In-game date: 12 Harvestfall
Rules: D&D 5e 2024; list house rules here
Tone: adventurous high fantasy

## Notes
Write what actually happened, including choices, discoveries, and unresolved questions.

## Established context
Include relevant previously approved lore and NPC details, or exact repository file paths.
```

The session ID must remain stable. Confirm the 2014 or 2024 rules version;
unspecified mechanics are questions, not an invitation to invent rulings.
Create the `session-complete` label during approved setup. After the session,
apply it to request a draft. The automation reads the issue body and comments,
plus at most three explicitly referenced campaign files.

## At the table

The Canvas separates observed facts from proposed future consequences, provides
a read-aloud recap, and tracks prep items and open threads. Importing requires a
preview and explicit replacement confirmation. Draft approval is a DM review
marker, not permission to commit lore changes.

Measure prep minutes and forgotten follow-ups after play, along with correction
effort. Optionally use that feedback to approve better instructions later.

For manual use, ask an App agent to follow `automation.prompt.md` for a supplied
issue. If it cannot post comments, it must report that limitation and present an
unsaved draft in chat; it must not claim the draft was persisted.
