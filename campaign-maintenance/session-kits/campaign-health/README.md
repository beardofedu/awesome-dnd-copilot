# Campaign health: operational hygiene

A standalone, deterministic Python standard-library check of **supplied metadata
and explicit local file references**. It does not read or interpret narrative,
find all campaign files, assess continuity, measure engagement, or infer player
enjoyment. It complements rather than duplicates Session Bridge. The example is
fictional; its paths do not exist in this library and its thresholds are examples,
not recommendations.

## Privacy first

Use a DM-only repository and DM-authorized computing environment when metadata,
paths, or source files are private. JSON, summaries, source links, workflow logs,
and artifacts expose paths and identifiers to repository readers; Actions
permissions, artifact retention, and personal ownership are not privacy controls.
Do not put secrets in metadata, URLs, filenames, reports, or prompts. No source
file content is exported by the checker, and it makes no network requests. Do not
copy reports into a player repository. Review any sharing manually.

## Copy and configure

From the library checkout, using a fresh destination:

```bash
CAMPAIGN_REPO=/path/to/your/private-campaign
mkdir -p "$CAMPAIGN_REPO/.github/session-kits"
cp -R campaign-maintenance/session-kits/campaign-health "$CAMPAIGN_REPO/.github/session-kits/"
cd "$CAMPAIGN_REPO"
cp .github/session-kits/campaign-health/manifest.example.json .github/session-kits/campaign-health/manifest.json
# Edit manifest.json and replace ALL fictional IDs, paths, dates and thresholds.
```

Python 3.11+ is required; no packages or API tokens are needed. Choose the
thresholds yourself, reflecting your own review cadence. Mark only metadata you
actually maintain; every object must have the fields below (unknown fields are
rejected). Arrays may be empty, but at least one entry across them is required.
IDs are lowercase kebab-case and unique within each collection. Paths are
case-sensitive, repository-root-relative POSIX paths to regular files; `.`/`..`,
absolute paths, backslashes, unsafe characters and symlinks escaping the root are
rejected. Allowed path-component characters are ASCII letters, digits, spaces,
periods, `_` and `-`. No globbing. An uninspectable path is an error, not a
missing file. Symlinks within the repository are followed; do not run the checker
on untrusted or concurrently changing filesystems.

| Field | Contract |
|---|---|
| `version` | integer `1` |
| `thresholds.npcReviewDays`, `thresholds.prepReviewDays` | nonnegative integer maximum age in calendar days; stale only when age is **greater** than the configured maximum |
| `sessions[]` | `id`, completed `date`, `recap` (path or null), `npcRefs` (NPC ID array), `fileRefs` (path array) |
| `npcs[]` | `id`, `file`, `reviewedOn` (date or null) |
| `prep[]` | `id`, `file`, `reviewStatus` (`reviewed`, `unreviewed`, `unknown`), `reviewedOn` (date only for `reviewed`, otherwise null) |

Dates are strict `YYYY-MM-DD` calendar dates, never timestamps or local-time
conversions. The default check date is the current **UTC** date. Completed
sessions and reviews cannot be future-dated; planned sessions belong elsewhere.
`--today` injects the date for repeatable historical runs, and must be at least
as late as every supplied date. For example, on January 20 a review on January 10
is exactly 10 days old; a 10-day threshold becomes stale January 21.

Confirmed findings are missing explicitly referenced recap/NPC/prep/other files,
NPC IDs absent from the supplied registry, explicitly unreviewed prep, and reviews
older than the configured limit. A null recap means the **path was not supplied**,
not proof no recap exists; null NPC review dates and `unknown` prep status are
also unknown. A dangling NPC is relative to this manifest, not proof the NPC is
absent from the campaign. Check findings manually; no status establishes canon.
JSON findings have deterministic IDs and exact manifest JSON pointers (array
indexes refer to that revision) and target values where applicable. Markdown
links identify the manifest; pointers identify the exact metadata field.

## Run and interpret

```bash
python3 .github/session-kits/campaign-health/check.py \
  --root . --manifest .github/session-kits/campaign-health/manifest.json \
  --output-dir .campaign-health-report --today 2026-01-20
# Omit --today for the current UTC date.
python3 -m unittest discover -s .github/session-kits/campaign-health -p 'test_*.py'
```

The fixed report filenames are `.campaign-health-report/report.json` and
`summary.md`; keep them private and remove or ignore them as appropriate. For
clickable immutable source links, optionally pass `--source-base-url` followed by
an HTTPS revision URL such as `https://github.com/OWNER/REPO/blob/COMMIT` (no
credentials, query or fragment); without it, links are repository-relative.
Reports are deterministic for the same manifest, file state, date, and URL.
Exit `0` means no **confirmed** findings, not that unknowns or unlisted data are
healthy; `1` means confirmed findings; `2` means invalid/missing input, unsafe
path, or output error. A failed run can leave an older report on disk; never
interpret it as the failed run. Check the exit status before using output.

For optional AI interpretation, in a private authorized session supply both
fresh report files and the complete `interpretation.prompt.md` to an AI assistant.
The output is a draft for DM review, not a scheduler or automatic publication.
Using an AI service may send supplied data to that service and incur charges;
check eligibility, privacy, permissions, estimated costs and obtain appropriate
approval before using it. The checker and Actions template do not invoke AI.

## Optional GitHub Actions template

Only in your **private campaign repository**, after checking Actions access,
minutes/storage costs, retention, and the readers of logs/artifacts, opt in:

```bash
mkdir -p .github/workflows
cp .github/session-kits/campaign-health/workflow.template.yml .github/workflows/campaign-health.yml
# Review the workflow, cron, paths, action versions, retention, and manifest; then commit them.
```

The template runs weekly on the default branch and via `workflow_dispatch`;
GitHub may delay scheduled runs. Configure or remove the cron as desired. It uses
read-only repository permissions, checks out without persisted credentials, pins
source links to the run's commit, and uploads a stable named artifact containing
only the two reports. It publishes a summary/artifact for checker exit 0 or 1,
then fails the job for confirmed findings. Exit 2 publishes an error summary,
no artifact, and fails the job; upload failures also fail the job. Unknowns alone
are visible but do not fail it. A checkout/setup failure also fails the job.
Artifacts and logs are accessible to repository readers subject to GitHub policy;
never enable this in a public repo with private data. No workflow is activated by
copying the kit to this library, and this kit creates no cloud automation.
