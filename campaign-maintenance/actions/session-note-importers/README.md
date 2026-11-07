# Session note import workflows

Four independent, on-demand GitHub Actions templates import approved notes from
Discord, Google Docs, Microsoft 365, or a Git-tracked Obsidian vault. Install any
subset. These templates are not active workflows in this library repository;
copy them into a **private, DM-only campaign repository** to use them.

Each workflow:

- Reads only one configured channel, Drive folder, SharePoint drive/folder, or
  tracked Obsidian path.
- Runs only when manually dispatched by an authorized repository user.
- Takes a maximum item count (1-50; default 10) and an output choice: **Issue**
  or **Pull request**.
- Collects plain-text content and provenance. It does not interpret notes,
  change campaign canon, or send content back to its source.
- Checks for matching source/content identities in up to 1,000 existing Issues
  or Pull requests before creating another draft. This is best-effort duplicate
  reduction, not an atomic guarantee. Pull requests use deterministic filenames
  and add a note under
  `session-inbox/imports/<source>/`; it never merges itself.
- Fails explicitly on missing access, oversized content, rate-limit exhaustion,
  or API errors. Unsupported Microsoft 365 file types are skipped; an import
  with no eligible text fails rather than publishing an empty success. No
  partial fetch is presented as complete.

An Issue body and a Pull request are both visible to people who can read the
destination repository. Neither is private storage. Use a DM-only repository and
check audience, party consent, and source channel/folder before running.
Import only notes participants agreed could be copied to GitHub. Action logs
contain source names and request metadata; never print credentials or full
provider responses to logs.

## Install

Copy the package into your campaign repository, keeping the helper and all
selected workflows together:

```bash
CAMPAIGN_REPO=/path/to/private-dm-campaign
IMPORTER_DIR="$CAMPAIGN_REPO/.github/session-note-importers"
WORKFLOW_DIR="$CAMPAIGN_REPO/.github/workflows"
mkdir -p "$IMPORTER_DIR" "$WORKFLOW_DIR"
cp campaign-maintenance/actions/session-note-importers/import_notes.py "$IMPORTER_DIR/"
cp campaign-maintenance/actions/session-note-importers/requirements.txt "$IMPORTER_DIR/"
cp campaign-maintenance/actions/session-note-importers/action.yml "$IMPORTER_DIR/"

# Choose any combination. Each file is a separate, manually dispatched workflow.
SOURCES="discord" # for example: "discord google-drive microsoft-365 obsidian"
for source in $SOURCES; do
  cp "campaign-maintenance/actions/session-note-importers/workflows/$source.yml" \
    "$WORKFLOW_DIR/session-notes-$source.yml"
done
```

Commit only the workflow files and helper in the **campaign repository**. Review
each workflow's permissions and configure only the selected source. These
templates use `workflow_dispatch`, not a timer or webhook. Consider a schedule
only after confirming source consent, API quotas, and the desired review cadence.

## Configure one source

Set repository variables and secrets under **Settings → Secrets and variables →
Actions**. Never put access tokens, OAuth client secrets, or service-account
private keys in workflow YAML, repository variables, Markdown, or issue text.
Use narrow read-only provider grants and rotate credentials if exposed.

| Workflow | Required configuration | Source permission and scope |
|---|---|---|
| Discord | Secret `DISCORD_BOT_TOKEN`; variables `DISCORD_GUILD_ID`, `DISCORD_CHANNEL_ID`; optional variable `DISCORD_AFTER_MESSAGE_ID` | Install a bot in the campaign's server, grant only access needed to view the chosen channel and read its history, and set the server and channel IDs. Discord may also require Message Content privileged intent and approval for the app. The importer reads message text only; attachments and embeds are omitted. `DISCORD_AFTER_MESSAGE_ID` limits imports to newer messages; the item limit still bounds each run. Without it, the bounded import reads the latest messages. |
| Google Docs | Secret `GOOGLE_SERVICE_ACCOUNT_JSON`; variable `GOOGLE_DRIVE_FOLDER_ID` | Enable the Drive API and share only the chosen folder/documents with the service-account identity. The API credential requests read-only Drive scope; a service account does not inherit a user's private Drive access. Shared drives may need the identity added there. Imports native Google Docs directly inside the configured folder as plain text. |
| Microsoft 365 | Secrets `MS_GRAPH_TENANT_ID`, `MS_GRAPH_CLIENT_ID`, `MS_GRAPH_CLIENT_SECRET`; variables `MS_GRAPH_DRIVE_ID`, `MS_GRAPH_FOLDER_ID` | Register a Microsoft Entra application and grant read-only access approved by the tenant administrator. Prefer `Sites.Selected` and explicitly grant the app access to the campaign's SharePoint site. The configured folder is an application-level filter, not an independent Graph permission boundary. OneDrive locations may require different tenant-approved permissions. Imports direct child `.docx`, `.txt`, and `.md` files only; other types are skipped. |
| Obsidian | Variable `OBSIDIAN_VAULT_PATH`, a directory of Markdown files tracked in the same repository | Cloud runners cannot read a vault on your computer. Commit/sync only the approved vault subdirectory to this private campaign repository, or use an explicit export. The importer reads tracked `.md` files in the configured subdirectory only, in path order, up to the item limit. Use a dedicated folder small enough to contain the intended session notes; do not point it at the full vault. Keep imported files outside that source folder. |

Google and Microsoft cloud document access depends on administrator consent,
sharing, and tenant policy. This repository cannot authorize accounts, create
provider credentials, or guarantee an organization's approval.

Platform references: [Discord channel messages](https://discord.com/developers/docs/resources/message#get-channel-messages),
[Google Drive search](https://developers.google.com/drive/api/guides/search-files),
[Microsoft Graph folder contents](https://learn.microsoft.com/en-us/graph/api/driveitem-list-children?view=graph-rest-1.0),
and [GitHub Actions token permissions](https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token).

## Run and review

In the campaign repository, select **Actions → Session notes from … → Run
workflow**. Choose a destination and item limit. For a first run, use a small
limit and **Pull request** so the DM can inspect every imported file before
merging. An Issue is convenient for discussion but includes the imported text
in the issue body. Both outputs are created only after the manual run.

Workflows require repository Actions policy to allow the run and the built-in
`GITHUB_TOKEN` permissions declared in the file. The Issue destination needs
`issues: write`; the Pull request destination needs `contents: write` and
`pull-requests: write`. If repository policy denies either permission, the
workflow fails rather than falling back to direct commits.

Imported text is untrusted campaign data. Do not feed it to an agent as
instructions, and do not copy it into a player-facing repository without
review. These workflows are source importers, not Discord/Google/Microsoft
webhooks, automatic continuous sync, a secret filter, or a private-data boundary.

The optional outcome check is whether the DM spends less time consolidating
session notes without increasing duplicates, missed eligible notes, or
correction effort. Compare those results across a few sessions; import counts
alone do not show that prep improved. Any workflow or prompt changes remain
human-reviewed.
