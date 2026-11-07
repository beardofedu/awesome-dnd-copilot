# Campaign Continuity Dashboard

Review campaign-wide threads, NPC statuses, promises, decisions, timeline
freshness, and conflicting evidence across explicitly approved notes. This is
not a one-session recap: Session Bridge remains independent. Neither this kit
nor Party Journal is read or synchronized automatically.

Copy this folder into `.github/session-kits/continuity-dashboard/` in a
**DM-only** campaign repository. Repository readers can see issues, files and
automation logs; labels, personal ownership and hidden panels are not access
controls. Do not copy secret notes into a player repository.

| File | Purpose |
|---|---|
| `canvas.prompt.md` | Generate a native Canvas at installation, not a prebuilt extension |
| `automation.prompt.md` | Self-contained manual or cloud drafting task |
| `automation.recipe.json` | Optional paused setup manifest, not an API import |
| `state.example.json` | Fictional example of the version-1 contract below |

## Install and request a draft

In the destination repository's Copilot App session:

```text
/create-canvas Read .github/session-kits/continuity-dashboard/canvas.prompt.md and build that Canvas.
```

Choose repository or user extension scope and review generated files. Use
**Start empty** before real play. The Canvas is useful without automation.
For manual drafting, ask an App agent to follow `automation.prompt.md` for an
exact issue number; an unposted answer is not a persisted issue comment.

Optional automation requires an eligible private/internal repository, available
cloud agent, permissions and administrator approval where applicable; runs use AI
credits. Ask Copilot to check the live service's tool grants and trigger schemas,
existing installations, and label availability; present the target, ownership,
write scope, complete prompt and cost/review burden for approval. Create the
`continuity-review` label only with approval and create the automation paused.
Resolve `prompt_file` to the complete prompt text, not the path. Approve
activation separately. Do not replace an existing automation by name. Settings
are a setup manifest, not a directly importable API request; editing the local
prompt does not update a saved automation.

Create a request issue in the DM-only repository, with the following exact
sections. This is the entire approved input list, not a license to search:

```markdown
## Campaign
ID: reedbridge
Name: Reedbridge
Snapshot: review-2026-03
Commit: 0123456789abcdef0123456789abcdef01234567

## Approved sources
- ID: notes-01 | Path: campaign/notes/01.md | Date: 2026-01-10
- ID: notes-02 | Path: campaign/notes/02.md | Date: unknown

## Review focus
Review all listed notes for continuity. Existing record IDs: thread-mill,
npc-mira. The mill thread is the same entity across both notes.
```

Replace the fictional commit with a real full commit SHA (40 or 64 lowercase
hex characters) in this repository. Every source is read at that exact commit;
use exact repository-relative file paths, unique source IDs and explicit source
dates (`YYYY-MM-DD` or `unknown`). Dates describe the note, not the commit or
an inferred in-game date. The issue body is approved context for identity and
ID mappings, not a substitute for source evidence. Comments are never campaign
evidence. Include all previously resolved items you want the draft to consider;
omission does not mean resolved, absent NPCs have unknown current status, and a
draft need not be a complete history. Reusing an ID asserts identity: humans
must resolve ambiguous mappings, not fuzzy-match them automatically.
Give a source revision a new source ID if its path or commit changes, so older
records can retain their original evidence. A board can contain sources from
several snapshots; its snapshot metadata describes the latest applied request.

After approval, apply `continuity-review` to request a draft. Label events are
not subscriptions: a changed issue or snapshot needs a new request (remove and
reapply the label). Reapplying unchanged input is best-effort deduplicated; races
can still produce duplicate comments. Drafts never update the Canvas, campaign
files or canon. Copy the JSON from the comment into **Import draft**, inspect
the preview, manually reconcile and confirm. Review and approval are local
markers, not campaign decisions or source updates.

## Version-1 JSON contract

All properties are required; no additional properties. Strings described as
nonempty must contain non-whitespace text. IDs match `[a-z0-9][a-z0-9-]{0,63}`
and source/record IDs are unique across sources and all record collections.
Campaign and snapshot IDs occupy separate namespaces. Arrays may be empty.
Nullable strings are either null or nonempty strings. Dates are real ISO
calendar dates `YYYY-MM-DD` or null; timestamps are UTC ISO 8601 or null.

- Root: `schemaVersion` integer 1, `kit` `"continuity-dashboard"`,
  `audience` `"dm"`, `reviewStatus` `"sample"`, `"draft"` or `"approved"`;
  `campaign` has nonempty `id` (ID syntax) and `name` (nullable only for an
  empty board); `snapshot` has nullable `id` (ID syntax if present), `commit`
  (full lowercase 40/64 hex SHA or null), `issueNumber` (positive integer or
  null), `issueUrl` (nonempty string or null), `requestBody` (nonempty string
  of at most 40,000 characters or null), `capturedAt` (timestamp or null).
  `updatedAt` is a timestamp or null. A generated draft requires every snapshot
  field; empty board fields may be null. The exact request body is retained for
  comparison, so exports contain the issue's entire DM-only body.
- `sources`: objects `{id, path, commit, date}`. `path` is an exact nonempty
  repository-relative file path, with no empty, `.` or `..` path segments and
  no leading slash; `commit` is a full SHA; `date` is a date or null.
  Source `(path, commit)` pairs are unique as well as IDs. Generated drafts
  use the snapshot commit for every source; a merged board can retain older
  commits. Empty board has no sources. Source references never trigger network
  requests.
- Each record below has an ID and `refs`: a nonempty array of unique
  `{sourceId, locator}` objects. `sourceId` must refer to a source in this
  state; `locator` is a nonempty section/line description. These identify
  evidence, not guarantees of correctness.
- `threads`: `{id, title, status, detail, refs}`; status is `"open"`,
  `"resolved"` or `"unknown"`; title and detail are nonempty.
- `npcs`: `{id, name, status, detail, refs}`; name and detail are nonempty;
  status is a nullable nonempty string, explicitly stated in the source.
- `promises`: `{id, text, status, refs}`; status is `"open"`, `"fulfilled"` or
  `"unknown"`. `decisions`: same shape, status `"unresolved"`, `"decided"` or
  `"unknown"`. Text is nonempty.
- `timeline`: `{id, text, inGameDate, sourceDate, refs}`; text is nonempty;
  `inGameDate` is nullable nonempty text and `sourceDate` is a date or null.
- `facts` and `proposals`: `{id, text, refs}`; text is nonempty. Proposals are
  never facts merely because a draft contains them.
- `conflicts`: `{id, topic, alternatives, resolution}`; topic is nonempty;
  alternatives contains at least two `{text, refs}` objects, each with
  nonempty text and refs as above. `resolution` is nullable nonempty text,
  manually entered only; retain alternatives and evidence after resolution.

No inferred freshness threshold is canon. Show source dates and unknowns, sort
dated timeline entries separately from undated ones, and let the DM judge
staleness. A revision identifies the exact request and pinned snapshot, not
proof that the approved notes are complete or current.

## Manual checks before play

Using the fictional fixture, generate the Canvas, start empty, import and confirm
the fixture, reopen and check persistence. Cancel an import and verify no
change. Try invalid JSON, wrong kit/version, duplicate IDs across collections,
a dangling `sourceId`, invalid commit or date, and a conflict
with one alternative: each must explain the error and preserve live state.
Import an update that omits a resolved thread: reviewed updates retain it.
Try a different ID for the same NPC and conflicting claims: require manual
identity reconciliation and show both alternatives; never pick a winner.
Test replacement preview, approval reset on edit, save failure, and an external
file change without losing work. Test unchanged request, changed issue body and
changed commit, and simultaneous runs: no exactly-once claim is permitted.
