# Private DM review add-on

Install this add-on **only** in a repository readable by the DM and authorized
co-DMs. It drafts private analysis of one DM-selected player submission. It
does not read the player repository or transfer anything between repositories.

Copy the parent `player-submissions` kit into the DM repository at
`.github/session-kits/player-submissions/`, preserving this `dm-review/`
directory. A DM manually creates one private issue per selected submission,
copies only reviewed text, records the public source issue URL/number and source
revision, and marks the copied text as untrusted player intent. Do not copy
unsuitable or unnecessary details. Never treat a player-side label or comment
as permission to expose the DM repository.

Before applying the review label, include the required transfer metadata in the
private issue body: the public player issue URL and number, its
`playerRevision` (`body:<update timestamp>;last-comment:<id>@<timestamp-or-none>`),
a DM-supplied `transferRevision` that changes whenever the selected text changes,
and an explicit declaration that the input was manually transferred and DM
reviewed. Clearly delimit the copied text, for example:

```text
Transfer status: Manually transferred and DM-reviewed by <DM>.
Player source: <issue URL> (issue <number>)
Player revision: body:<update timestamp>;last-comment:<id>@<timestamp-or-none>
Transfer revision: <DM-supplied revision>

BEGIN PLAYER SUBMISSION
<selected player text>
END PLAYER SUBMISSION
```

The optional recipe watches for `player-submission-review` in the DM-only
repository and comments a draft on that private issue only. The DM/writer applies
the label after transfer and review. Read-only players can submit in the public
repository; they do not need write access there or in the DM repository.

For setup, use the parent README's live-catalog validation and separate
approval requirements. Validate the trigger and tool grants against the live
catalog/settings and repo policy; the paused recipe is an example, not a
guarantee of availability. Approve creation paused, enablement, and any manual
run separately. Use the full `automation.prompt.md` text as the prompt; resolve
the recipe's `prompt_file` locally. Do not create labels/resources without
approval. The recipe is independent of the public acknowledgement automation:
there is no automatic chain, and each run may incur separate AI-credit charges.

Only the DM determines whether to respond, whether a plan is feasible, and what
becomes an action, ruling, reward, or canon. The draft must remain a proposal
for review, never a resolution.
