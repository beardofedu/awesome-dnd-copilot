# Canon Consistency kit

Use this copy-in kit in a **campaign** repository, not this template library.
It combines a bounded, manual AI review with an independent, offline JSON
manifest checker. The checker validates structure and references only: it
**cannot detect narrative contradictions**, prove sources exist, or decide
what is canon. The DM adjudicates every finding.

| File | Purpose |
|---|---|
| `review.prompt.md` | Standalone, source-linked AI review task |
| `check_canon.py` | Python standard-library manifest checker |
| `canon.example.json` | Fictional example with both canon and draft claims |
| `tests/test_check_canon.py` | Focused standard-library tests |
| `workflow.template.yml` | Optional GitHub Actions template; inactive here |
| `../../agents/canon-consistency.md` | Optional custom agent, installed separately |

## Copy and run

From a checkout of this library, use a **fresh** destination campaign checkout
to avoid overwriting existing files (set the variable to its absolute path):

```bash
CAMPAIGN_REPO=/path/to/your/campaign
mkdir -p "$CAMPAIGN_REPO/.github/session-kits" "$CAMPAIGN_REPO/.github/agents" "$CAMPAIGN_REPO/canon"
cp -R campaign-maintenance/session-kits/canon-consistency "$CAMPAIGN_REPO/.github/session-kits/"
cp campaign-maintenance/agents/canon-consistency.md "$CAMPAIGN_REPO/.github/agents/canon-consistency.md"
cp "$CAMPAIGN_REPO/.github/session-kits/canon-consistency/canon.example.json" "$CAMPAIGN_REPO/canon/facts.json"
cd "$CAMPAIGN_REPO"
python3 .github/session-kits/canon-consistency/check_canon.py canon/facts.json
python3 -m unittest discover -s .github/session-kits/canon-consistency/tests -v
```

Replace the fictional manifest with your own, preserving `canon` versus `draft`
status. Do not copy fictional claims into actual campaign canon. The example
deliberately contains a possible conflict; it passes structural validation.
Specify `"2014"` or `"2024"` only when confirmed; otherwise retain `"unknown"`.
Review sources, permissions, and DM secrets before committing anything.

## Manifest contract

UTF-8 JSON has exactly `schemaVersion` (integer `1`), `rulesVersion` (string
`"2014"`, `"2024"`, or `"unknown"`), and `facts` (array, possibly empty).
Each fact is an object with exactly:

- `id`: unique lowercase ASCII letters/digits separated by single hyphens;
- `status`: `"canon"` or `"draft"`; this is a label, not approval;
- `text`: nonblank claim; `source`: nonblank human-readable source and revision;
- `references`: array of unique IDs present in this manifest, including forward
  references if needed. These are associations, not proof or assertions of truth.

No extra keys, duplicate JSON object keys, or non-JSON numeric constants are
accepted. The checker does not verify source paths, revision identifiers, status
authority, editions beyond the label, or semantic content.

Run `python3 .github/session-kits/canon-consistency/check_canon.py canon/facts.json`.
It prints one JSON object to stdout: `{"ok": true, "diagnostics": []}` on
success, otherwise `ok: false` and an array of objects with `code`, `path`
(JSON Pointer, empty string for the document), and `message`. Exit 0 means
valid structure, 1 means validation findings, and 2 means usage or input/JSON
read failure. Diagnostic order follows field checks, then fact order, then
unresolved references. Error messages may include operating-system details;
do not treat them as stable identifiers.

## Manual review

In a Copilot session with this campaign selected, supply the complete PR diff
and exact base/head commit IDs (or complete versioned draft), plus up to three
explicitly identified versioned context files and their approval statuses.
Ask:

```text
Follow .github/session-kits/canon-consistency/review.prompt.md.
Review the supplied change and context; return the report here only.
```

Alternatively select the installed Canon Consistency Reviewer agent and supply
the same inputs. Its empty tool list means it needs the prompt and evidence
provided in the conversation if it cannot read them; paste the prompt too.
The AI review is manual, potentially incomplete, and never edits canon or
posts a PR comment. Verify source lines and intentional retcons yourself.
The rules edition is not guessed when missing. Do not share DM secrets with
users or services not authorized to see them.

## Optional Actions checks

After installing and committing the checker and `canon/facts.json` on the
campaign's default/base branch, inspect this template and opt in:

```bash
mkdir -p .github/workflows
cp .github/session-kits/canon-consistency/workflow.template.yml .github/workflows/canon-consistency.yml
```

Review and commit the workflow in the campaign repository. It runs on PRs,
checks out the base revision's checker separately from the PR head's manifest,
uses Python isolated mode, rejects symlinked manifest paths, and executes no
PR-provided scripts. It uses `pull_request`, read-only contents permission,
no persisted checkout credentials, secrets, or model API. A first installation
PR needs the checker already on its base branch; otherwise install the workflow
in a later PR. The template checks only `canon/facts.json`; adjust the literal
path if your campaign differs. A missing file fails the job. Inspect logs for
the JSON result; this is not an AI review or a PR comment.

Keep GitHub's fork-PR approval protections enabled; do not approve untrusted
workflow changes without review. A PR can propose changing the workflow itself,
so base-checker isolation is not protection against a modified workflow.
Use ephemeral GitHub-hosted runners, not privileged self-hosted runners with
secrets. Check organization Actions policies and pinned action availability;
this template does not enable Actions or bypass repository policy.

For any separate cloud automation, request live configuration rather than
assuming features exist. In the destination repository ask an authorized
operator to check current availability, tools, trigger schemas, permissions,
ownership, costs and existing installations, then present an exact proposed
configuration for approval. Create nothing, enable nothing, and do not invent
tools or triggers. The supplied manual review prompt is not an automatic PR
commenter; adapting its output or write scope requires separate review and
approval. Copying this kit does not create any automation.
