# Session-Zero Campaign Builder

Turn a staged group discussion into a **proposed**, player-facing campaign
brief and reusable Copilot instructions. The builder works manually; an
optional paused automation recipe is provided. Copying this kit does not
install an automation or Canvas, create an issue or label, or change canon.

| File | Purpose |
|---|---|
| `intake.md` | Staged, fill-in discussion and approval worksheet |
| `builder.prompt.md` | Complete manual drafting prompt |
| `example.md` | Fictional intake and matching proposed output |
| `automation.recipe.json` | Optional paused issue-label setup manifest |

## Use

1. Discuss boundaries privately using whatever process the group chooses.
   Never enter personal explanations, trauma, health or identity information,
   or named safety/preference records. Default to omitting sensitive detail.
   Record only group-approved, non-sensitive fictional-content constraints,
   without attribution; a blank means unknown, not consent.
2. Copy `intake.md` to a suitable **private** workspace, fill the stages with
   the group, and record unresolved decisions rather than forcing agreement.
   Do not include DM secrets in shared material. If sharing an issue or file,
   all repository readers and potentially run logs may see it; labels, folders,
   and personal ownership are not privacy controls.
3. Give `builder.prompt.md` and the completed intake to a Copilot session.
   Supply only the explicitly selected, access-appropriate canon excerpts or
   existing instructions needed for comparison, with source names and revisions.
   Ask for a draft; copying these files alone neither installs nor runs anything.
4. Review the player brief with the group and any separate DM-only material
   privately. Resolve open questions together. Review suggested instruction
   changes against current `.github/copilot-instructions.md` and campaign canon;
   apply selected changes manually only after explicit approval. Never paste DM
   secrets into a player-accessible repository or shared run.

## Optional automation

Copy this folder to `.github/session-kits/session-zero/` in the destination
repository and commit it if using cloud automation. Ask an installer to read
`automation.recipe.json` and resolve its `prompt_file` to the complete text of
`builder.prompt.md`; the recipe is setup data, not an API request or authority.
Check live availability, destination, existing installations, permissions,
trigger schema and tool grants. Present exact ownership, labels, write scope,
prompt and estimated review burden. Request approval before creating any
missing label or automation; never replace an existing one by name silently.
Create only approved resources paused. Setup approval is not activation
approval: seek separate approval before enabling or running anything. Report
saved IDs and paused state; do not run it during setup.

After separate activation approval, a repository writer can apply the request
label `session-zero-draft` to an issue containing the sanitized intake. The
`player-safe` label is an additional filter, not evidence of approval or
privacy. Use one intake per issue. A label event is not a live subscription:
reapply the request label to request a draft after edits. Review the issue and
all comments before labeling. Only enter material all repository readers may
see: automation logs and issue comments may also be visible to them. Never use
this path for private discussion or DM secrets. The automation comments only
on the triggering issue and cannot write campaign files. Manual mode remains
available without automation. See the library's `session-kits.md` for general
kit guidance.

Use an `## Approved for sharing` section in the issue body containing the
sanitized intake and an explicit group statement that those contents may be
shared with all repository readers. If a comment clarifies the intake, include
the same explicit approval in that comment; other comments are not evidence.
Neither statement is a named preference or individual consent record. The
group must still review the generated draft before using it.
