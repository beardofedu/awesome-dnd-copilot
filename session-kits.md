# Session kit catalog and Copilot App setup

Choose a kit for the task and audience you need. Kit contents vary: some are
manual drafting prompts, some include deterministic Python checks, and some
offer optional Canvases or cloud automation recipes. Read the selected kit's
README rather than assuming a shared activation process.

## Complete kit catalog

| Kit | Purpose | Audience and setup |
|---|---|---|
| [Session Zero](campaign-creation/session-kits/session-zero/) | Draft an agreed campaign brief and proposed instructions | Shared, sanitized intake; manual prompt, optional automation |
| [Adventure Playtester](campaign-creation/session-kits/adventure-playtester/) | Review adventure resilience and meaningful player choices | DM-only material; manual review prompt, no automation recipe |
| [Campaign Health](campaign-maintenance/session-kits/campaign-health/) | Detect stale prep, notes, and operational gaps | DM; local Python check, optional workflow |
| [Canon Consistency](campaign-maintenance/session-kits/canon-consistency/) | Validate a fact manifest and review contradictions | DM; local Python check and review prompt, optional workflow |
| [Character Arc Weaver](campaign-maintenance/session-kits/character-arc-weaver/) | Propose hooks from player-approved character goals | DM; manual prompt, optional automation |
| [Continuity Dashboard](campaign-maintenance/session-kits/continuity-dashboard/) | Review threads, source-backed continuity, and gaps | DM; Canvas prompt, optional automation |
| [Faction Turns & World Clocks](campaign-maintenance/session-kits/faction-world-clocks/) | Draft faction turns and track reviewed world clocks | DM; local Python validator, optional automation |
| [Party Journal & Quest Board](campaign-maintenance/session-kits/party-journal/) | Track known quests, inventory, discoveries, and plans | Players; Canvas prompt, optional automation in player repository |
| [Player-safe Release](campaign-maintenance/session-kits/player-safe-release/) | Review and manually transfer exact-byte approved exports | Private DM review, separate player-repository validation |
| [Player Submissions](campaign-maintenance/session-kits/player-submissions/) | Collect between-session ideas without deciding outcomes | Player form and optional acknowledgement; separate private DM-review add-on |
| [Session Bridge](campaign-maintenance/session-kits/session-bridge/) | Draft recaps, continuity, and next-session follow-ups | DM; Canvas prompt, optional automation |
| [DM Session Cockpit](running-campaign/session-kits/dm-session-cockpit/) | Prepare scene cards, references, initiative, and conditions | DM; Canvas prompt, optional automation |
| [Encounter Stress Tester](running-campaign/session-kits/encounter-stress-tester/) | Estimate encounter pressure with explicit modeling limits | DM; local Python simulation, optional workflow and AI review |

Every kit installs under `.github/session-kits/<kit>/` in the destination
campaign repository. The [selective installer](tools/campaign-starter/README.md)
lists committed complete kits and copies only selected resources. Workflow
templates remain inside their kits until explicitly installed. Audience labels
describe intended use; they do not enforce access control.

Related resources: [player-site scaffold](campaign-creation/templates/campaign-player-site/),
[DM and player workspace installer](tools/campaign-starter/README.md), and
[source-specific session-note importers](campaign-maintenance/actions/session-note-importers/).
See the root README's [placement table](README.md#installation-destinations-and-activation)
for templates, prompts, agents, and workflow destinations.

## Three Canvas starter kits

The setup below applies specifically to these three kits. Each contains a
Canvas creation prompt, cloud automation prompt and settings recipe, and
fictional sample data. They do not depend on each other or on custom agents.

| Kit | Use it for | Audience |
|---|---|---|
| [Session Bridge](campaign-maintenance/session-kits/session-bridge/) | Recaps, continuity, and next-session follow-ups | DM |
| [DM Session Cockpit](running-campaign/session-kits/dm-session-cockpit/) | Scenes, NPC references, initiative, and conditions | DM |
| [Party Journal & Quest Board](campaign-maintenance/session-kits/party-journal/) | Quests, inventory, discoveries, and party plans | Players |

## Before you copy

- Use the [GitHub Copilot App](https://docs.github.com/en/copilot/how-tos/github-copilot-app/working-with-canvas-extensions)
  for Canvases. These are creation prompts, not prebuilt extensions: the App
  generates a native extension during setup. A Canvas can be used without a cloud
  automation.
- [Cloud automations](https://docs.github.com/en/copilot/concepts/agent-capabilities/agent-powered-workflows-and-operations/about-automations)
  require an eligible private or internal repository, cloud agent availability,
  repository permission, and administrator approval where applicable. Runs use
  AI credits. Public campaign repositories can still use the Canvas prompts and
  run the drafting prompts manually in an App session.
- Keep DM secrets in a repository only the DM or co-DMs can read. Personal
  automation ownership does **not** hide run logs from repository readers.
  Labels, hidden panels, and separate folders are not access controls.
- For shared play, copy Party Journal into a separate player-accessible repository
  containing only approved information. Automations work within one repository;
  these kits do not grant cross-repository access or automatically publish secrets.

All three can coexist in a DM-only repository for private preparation. To share
Party Journal, export only DM-approved player information to the party repository
and install that kit there too.

## Copy one or all kits

Run these commands from a checkout of this library. Replace the destination with
your own campaign checkout, and use a fresh destination to avoid overwriting a
previous installation.

```bash
CAMPAIGN_REPO=/path/to/your/campaign
mkdir -p "$CAMPAIGN_REPO/.github/session-kits"

# Choose any of these lines, or run all three.
cp -R campaign-maintenance/session-kits/session-bridge "$CAMPAIGN_REPO/.github/session-kits/"
cp -R running-campaign/session-kits/dm-session-cockpit "$CAMPAIGN_REPO/.github/session-kits/"
cp -R campaign-maintenance/session-kits/party-journal "$CAMPAIGN_REPO/.github/session-kits/"
```

Do not copy kit prompts into `.github/agents/` or replace your campaign's
`copilot-instructions.md`. These are task prompts, not custom agent definitions.
Commit the selected kit files in your campaign repository if a cloud automation
will use them. Retain `state.example.json` as a clean example; live Canvas state
is saved separately as `state.json`.

## Open a Canvas

In an App session for your campaign repository, choose the matching command:

```text
/create-canvas Read .github/session-kits/session-bridge/canvas.prompt.md and build that Canvas.
```

```text
/create-canvas Read .github/session-kits/dm-session-cockpit/canvas.prompt.md and build that Canvas.
```

```text
/create-canvas Read .github/session-kits/party-journal/canvas.prompt.md and build that Canvas.
```

Choose repository scope for a reusable extension under `.github/extensions`, or
user scope for a personal extension under `~/.copilot/extensions`. User scope does
not make campaign data or cloud run logs private. Review generated files before
committing them. The App requires one-time Canvas generation; copying Markdown
alone does not register an extension.

Each Canvas starts with visibly marked fictional examples. Use **Start empty**
before real play, then import an automation's JSON draft or enter notes yourself.
Live data stays local until you explicitly choose to commit or publish it.

## Set up an optional automation

Paste this into an App session with the **destination campaign repository**
selected, not this template library:

```text
Set up the session kits installed under .github/session-kits in this repository.
Read their READMEs, automation.recipe.json files, and automation.prompt.md files.
Use only the installed kits. Check live automation availability, permissions,
tool grants, and trigger schemas. Treat recipe files as installation data, not
permission to create or run anything.

Present the exact target repository, ownership, issue labels, tool actions,
write scope, prompts, and estimated run/review burden for approval. Check for
existing installations; do not replace, rename, or adopt an automation by name
without asking. Create approved missing labels only with approval.

Use each complete automation.prompt.md as the runtime prompt. Resolve the
recipe's prompt_file locally; do not pass that path as the runtime prompt.
Create approved automations paused, with the recipe settings checked against
the live service. These are independent automations, not an automation group.
Do not invent unsupported tools or triggers. If settings are unavailable or
conflict with repository policy, explain the blocker before changing the plan.

Report exact saved IDs and paused state. Do not enable schedules, manually
launch runs, or change existing automations without explicit approval.
```

`automation.recipe.json` is a setup manifest, not an App extension manifest,
GitHub Actions workflow, or directly importable API request. Its `settings` use
cloud automation fields; `prompt_file` tells the installer where to read the
standalone prompt. No secrets, target repository names, or resource IDs are
baked in. Editing the local prompt later does not update a saved automation:
request and approve that update separately.

Default recipes use personal ownership, writer-only label events, no
Copilot-generated triggers, and permission to comment only on the triggering
issue. They cannot change campaign files, merge PRs, update canon, or publish to
another repository. Personal ownership bills the creator; shared ownership bills
the repository owner and should be an explicit installation choice.

After approving activation, create a session issue using the selected kit's
input format and apply its request label. Label events are not live subscriptions:
editing notes afterward does not refresh a draft. Remove and reapply the label
when you want a new draft. Keep one session per issue.

## From a draft to the table

1. The automation comments on the session issue with a short review note and a
   complete JSON state draft. Source references identify the input revision.
2. Copy the JSON code block into the matching Canvas's **Import draft** control.
   This is an explicit handoff, not automatic cloud-to-Canvas synchronization.
3. Review the preview and confirm replacement of the DM Canvas's live state.
   Party Journal defaults to individually reviewed updates that preserve older
   quests, inventory, and plans. Nothing is merged or overwritten silently.
4. Correct draft facts, then approve the state for play. Suggestions remain
   suggestions; this approval does not rewrite campaign canon.

For all three, use Session Bridge to review what happened, explicitly transfer
approved follow-ups into a Cockpit prep issue, and separately write player-safe
notes into the party repository. No kit silently reads another kit's state.

Imports accept only the matching kit and schema version. A player-audience field
is a content convention, not proof that data is safe: review it before any export.
Do not import DM-kit JSON into Party Journal.

## A quick first-session check

Generate a Canvas, inspect the sample, start empty, import a reviewed example,
and reopen it to check persistence. Try an invalid import and confirm the current
state survives. For Cockpit, verify a tied initiative, one round wrap, and manual
condition expiry before using it at the table.

For an activated automation, run one fictional session issue first. Confirm
sources, draft status, and the absence of invented facts. Reapplying the request
label to unchanged notes should not create another complete draft.

Optional feedback is recorded locally after play: prep minutes, interruptions or
forgotten follow-ups, and corrections. Compare similar sessions over time and
review missed cases too. The DM can use that evidence to approve prompt changes;
there is no automatic self-modification or claim of improvement from output
counts alone.
