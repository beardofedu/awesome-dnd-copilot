# Character Arc Weaver

Turn a player's explicitly approved fictional character goal and DM-approved
quest list into a small menu of optional story connections. This is a
DM-facing drafting aid, not a character simulator or campaign-canon editor.

Keep the kit in a **DM-only repository** at
`.github/session-kits/character-arc-weaver/`. Do not install it in a player
repository: its input, output, comments, and logs may contain DM-only context.
Nothing is synchronized or transferred to players. A DM must review and
manually transfer any separately approved, player-safe material.

| File | Purpose |
|---|---|
| `goal-intake.md` | Player-approved fictional-character goal form |
| `automation.prompt.md` | Complete bounded manual/automation drafting task |
| `automation.recipe.json` | Optional paused request-label recipe |
| `sample.input.md` | Fictional approved goal and quest input |
| `sample.output.json` | Matching fictional DM draft |

## Intake

Use `goal-intake.md` to record a goal in the player's own words, with explicit
permission to use it for DM-only story brainstorming. Keep goals specific and
fictional. Do not collect personal explanations, health information, or
identity data. The player can set boundaries, revise, or withdraw approval;
withdrawing means the DM should stop using that goal in future drafts.

## Quick start

1. Copy the folder into the DM-only campaign repository.
2. Fill in an intake for each participating character, then have the DM add
   only approved quest entries with source links.
3. Use the complete `automation.prompt.md` manually for a draft, or consider
   the optional recipe below. Review `sample.input.md` and
   `sample.output.json` first; both are fictional.

The prompt asks for two or three optional hooks per supplied goal, each linked
to an approved quest. It preserves player agency, balances attention across
characters, and offers payoff and longer-arc possibilities without deciding
character actions, consent, rewards, or backstory.

## Optional automation setup

The recipe is setup data only; copying it creates no GitHub resources. In an
App session with the **intended DM-only destination repository selected**:

- Verify the live destination owner/repository, automation availability,
  permissions, exact trigger/tool schemas, and that issue comments/logs are
  appropriate for the DM-only material. The destination must contain this
  kit's prompt and recipe at the paths they name. Do not infer access control
  from a label or personal ownership.
- Present the exact repository, ownership, request label, read/write scope,
  tools, full runtime prompt, and expected review burden. Check for existing
  installations; do not adopt or replace one based on its name.
- Obtain separate explicit approval to **create**, to **enable**, and to
  **run**. Create only the approved automation paused. Do not create labels,
  enable it, or run it as part of setup without its separate approval.
- Resolve `prompt_file` to the complete `automation.prompt.md` text. Validate
  all settings against the live service; if verification fails or differs,
  stop and explain the blocker rather than creating resources.

The recipe uses a writer-applied `character-arc-review` issue label. Apply it
only to an issue containing the approved intake and supplied approved quests.
Label events are not live subscriptions: edits need a separately approved new
run/relabel. Draft comments stay in the DM-only issue. Do not copy them to a
player-facing repository; any player-safe transfer is a separate manual DM
review and action.

For manual use, the same prompt can be followed in chat. If comment tools are
unavailable, present an explicitly unsaved draft instead of claiming it was
posted.
