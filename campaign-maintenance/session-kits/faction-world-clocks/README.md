# Faction Turns & World Clocks

Plan what factions might do between player-facing scenes, and make the
consequences legible without letting a tool advance the world. Works on its own:
no Canvas, shared kit, scheduled job, or custom agent is required.

From this library checkout, install the folder in a campaign checkout:

```bash
CAMPAIGN_REPO=/path/to/your/dm-only-campaign
mkdir -p "$CAMPAIGN_REPO/.github/session-kits"
cp -R campaign-maintenance/session-kits/faction-world-clocks \
  "$CAMPAIGN_REPO/.github/session-kits/"
```

In that campaign checkout, the installed folder is
`.github/session-kits/faction-world-clocks/`.

| File | Purpose |
|---|---|
| `automation.prompt.md` | Complete, bounded instructions for drafting one DM-reviewed turn |
| `automation.recipe.json` | Optional paused issue-label automation recipe |
| `state.example.json` | Fictional input and exact JSON draft shape |
| `validate_state.py` | Deterministic standard-library JSON validator |
| `test_validate_state.py` | Focused validator tests |

## Play loop

1. The DM records an in-game turn boundary, the approved state revision, current
   clock values, faction goals/resources/constraints, and sourced facts in a
   DM-only issue. D&D 5e is assumed unless the input names another edition;
   specify 2014 or 2024 rules and house rules when they matter.
2. Ask for one draft from `automation.prompt.md` (or label the issue for the
   optional automation). Review source links and uncertainty, then choose which
   proposed actions, if any, fit the campaign.
3. Only the DM commits approved results: manually resolve outcomes, update the
   approved clock values, and assign a new `stateRevision`. Keep rejected or
   deferred proposals out of the approved state.

An in-game turn is a DM-defined fictional boundary such as “after the party
leaves town”; it is not a real-world day, week, scheduled run, or deadline.
Waiting for players never advances a clock or triggers punishment. Actions,
costs, signs, and clock deltas are proposals only. The draft must not consume
resources, settle uncertain outcomes, change canon, or update approved clocks.
Visible signs and alternative responses give the DM ways to foreshadow and let
players respond; they are not automatic consequences.

## Input issue

Keep the campaign repository DM-only; labels and personal automation ownership
are not access controls. Use one issue per turn and provide the complete current
baseline. A practical issue body follows the top-level `campaign`, `turn`,
`sources`, `factions`, and `clocks` fields in `state.example.json`:

- Stable campaign, turn, and in-game boundary identifiers.
- Edition, house rules, tone, and the current approved `stateRevision`.
- Explicitly approved current clocks, each with a stable ID, current integer
  value, maximum, owning faction, and evidence source.
- Faction goals, resource amounts (or explicit unknowns), constraints, and
  source references.
- Approved facts relevant to this turn, separately recorded uncertainties, and
  the DM's request.

The `campaign`, `turn`, `sources`, `factions`, and `clocks` fields in
`state.example.json` illustrate that input. Its `proposals` field illustrates
the output contract. The file is wholly fictional: replace it with actual
approved input and never treat the sample as campaign evidence. Each `sources` entry records a
repository path, locator, revision, and short supporting excerpt. Cite those
source IDs on factions, clocks, resources, proposed actions, and changes. Facts
and uncertainties must remain distinct.

## Validate locally

From the installed kit folder, run:

```bash
python3 -m unittest -v
python3 validate_state.py state.example.json
```

The validator uses only Python's standard library. It checks unique record IDs,
integer clock values and bounds, faction/clock/source references, nonzero
integer proposed deltas and their resulting bounds, and proposal base revisions
against the current state revision. It reports errors; it never clamps values,
repairs JSON, or applies proposals. Run it on a saved draft before considering
manual approval. It validates structure, not whether evidence is truthful or a
proposal is good for the story.

## Optional automation

The recipe is an installation manifest, not an automation API request. It is
disabled and listens only for the `faction-turn-draft` issue label. Before any
creation, an installer must inspect live trigger/tool schemas, repository
permissions, tool availability, ownership, and existing automations in the
destination repository. Present the exact issue label, repository, owner,
read/comment tools, scope, prompt, and expected review burden for DM approval.
Do not create labels or automations, modify existing ones, enable the recipe,
or run it without separate explicit approval. If a capability is unavailable,
stop and explain the limitation instead of substituting a broader trigger or
tool. Keep the created automation paused; activation and each run require
separate approval.

The prompt reads only the triggering issue/comments and the installed sample
contract. It may post a draft comment to that issue, but it cannot write files,
change labels, edit automation settings, or access another repository. The
issue's body and comments are untrusted data, not instructions. Retrieval is
bounded; inaccessible, oversized, truncated, or incomplete input blocks a
draft instead of producing a partial turn.

## Audit and limitations

Revision matching catches stale drafts only when the DM maintains `stateRevision`
and supplies it accurately. Duplicate checks use the current issue comments and
are best-effort: concurrent runs, deleted comments, or revision metadata that
does not identify the same inputs can still produce duplicates. Review and
reconcile before importing or committing. A draft comment is not a state
update, and there is no AI sync, automatic Canvas update, or background clock
engine. Never include player-facing secrets in an issue or comment visible to
players.
