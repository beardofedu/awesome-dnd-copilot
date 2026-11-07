# Adventure Playtester

A DM-only, read-only review kit for stress-testing one adventure revision before
play. It looks for brittle clue paths, fragile NPC dependencies, inaccessible
goals, unsupported rules assumptions, thin choices, pacing/recovery problems,
and scenes whose required/optional status is unclear. It proposes small,
concrete alternatives for the DM to consider; it does not rewrite the adventure,
change canon, or claim to replace human playtesting.

## Copy into a campaign repository

Copy this folder to `.github/session-kits/adventure-playtester/` in a repository
accessible only to the DM and trusted co-DMs. Keep adventure drafts, review
outputs, and any PR private to that audience: this kit is not player-safe
material, and a private-looking path or label is not an access control.

The kit is self-contained. No Canvas, automation, custom agent, API key, or
special model is required. To run it manually, provide both
`adventure-playtester.prompt.md` and `review-contract.md` as review instructions
before supplying the completed input described in `input.template.md`. Also
supply the complete referenced diff/files within the prompt's limits. Save the
resulting review wherever the DM chooses; the prompt itself never writes it.

For a PR-based review, name the exact repository and PR, base SHA, and head SHA.
The reviewer must verify those exact revisions before reading the bounded diff
and any explicitly referenced context files. If revision verification, a needed
file, or a size bound fails, stop and request a smaller, exact input rather than
reviewing a partial or moving target. Do not let the reviewer post a comment,
edit files, merge, or approve the PR.

## Contents

| File | Purpose |
|---|---|
| `adventure-playtester.prompt.md` | Standalone bounded review prompt for PR or supplied text |
| `input.template.md` | Copyable input contract; includes the fictional sample adventure |
| `review-contract.md` | Checklist, severity/confidence meanings, and output shape |
| `example-review.md` | Source-linked example that demonstrates a counterfactual review |

`campaign-creation/agents/adventure-playtester.md` in the source library is an
optional custom-agent wrapper around the same review process. The files here are
usable without it.

## Optional cloud automation

This kit intentionally ships no automation recipe. A manual review avoids
installing a write-capable integration for a task that can read a bounded PR and
produce a draft. If you later build an automation, first verify the live trigger
and tool catalog, request only read access plus explicitly approved comment-only
scope, and keep it paused until its exact target, trigger, tools, and prompt are
approved. Creating, enabling, and manually running an automation are separate
approval steps. Never treat a manifest as an API import request or as permission
to execute.

## Rules and evidence

D&D 5e is the repository default, but a review must ask which 5e rules version
(2014 or 2024) applies if mechanics matter and the input does not say. Unknown
rules, omitted context, or ambiguous wording are questions—not proof of a defect.
Counterfactual player paths are named simulations with stated assumptions, not
exhaustive or empirical playtesting.
