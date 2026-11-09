# First campaign walkthrough

This fictional walkthrough shows how the library's resources fit together
without connecting repositories or publishing anything automatically. It uses
the imaginary campaign **The Lanterns of Brackenmere**. Replace all examples
with reviewed campaign material before using them in a real game.

## 1. Keep DM and player workspaces separate

From a checkout of this library, create empty destinations and preview a DM
workspace with a campaign profile, world-building agent, session-zero kit, and
session-bridge kit:

```bash
mkdir -p /path/to/brackenmere-dm /path/to/brackenmere-players
python3 tools/campaign-starter/install.py /path/to/brackenmere-dm \
  --profile campaign-creation \
  --agent campaign-creation/world-builder.md \
  --kit campaign-creation/session-zero \
  --kit campaign-maintenance/session-bridge \
  --starter
```

Review the preview, then repeat the command with `--apply`. The installer
copies selected local files; it does not create GitHub repositories, change
access, or activate services. It also copies the repository's `LICENSE`; keep
it with the workspace. For manual copies, follow the
[attribution guidance](../../ATTRIBUTION.md). Keep the DM workspace private to
the DM team.

Create a separate player workspace and preview its starter and website:

```bash
python3 tools/campaign-starter/install.py /path/to/brackenmere-players \
  --player-starter --player-site
```

Review the preview, then repeat with `--apply`. Keep only content approved for
the players in this repository. Do not install DM notes or give this workspace
access to the DM repository.

## 2. Draft the campaign privately

In the DM workspace, use the Session Zero kit to draft a campaign brief from
the group's agreed, non-sensitive preferences. Review the brief with the
players, then use World Builder to propose places, factions, and starting
conflicts for **The Lanterns of Brackenmere**. Decide which proposals become
canon yourself.

Before a session, use Session Bridge to summarize reviewed notes and suggest
follow-ups. Keep drafts and unrevealed information in the DM workspace. These
prompts do not make factual or safety decisions on the DM's behalf.

## 3. Share only reviewed information

When players need a recap or discovered location, prepare a small export
manually in the DM workspace. Follow the
[player-safe release process](../../campaign-maintenance/session-kits/player-safe-release/README.md):
review sources, remove spoilers and personal information, approve the final
bytes, and transfer only the approved export and manifest to the player
workspace. Run the validator there. A passing check verifies file integrity
and format, not whether the content is safe to share.

Customize the player site using only approved player-facing information. Review
all site files and the rendered pages. To keep this as a local exercise, stop
here; publishing the site requires a separate explicit decision and setup.

## 4. Check the boundaries

- Copying resources does not grant repository access or activate workflows,
  automations, Canvases, or Pages.
- A player-accessible repository must not contain DM-only material, even in an
  unlinked file, branch, hidden panel, or old commit.
- The DM approves the exact material shared with players. AI suggestions and
  validator output do not replace that review.
- This guide is a workflow example, not prewritten campaign canon. Keep the
  fictional name and any sample content out of real campaign releases unless
  deliberately adapted and reviewed.

For other resource requirements and product caveats, see the
[compatibility guide](../../COMPATIBILITY.md).
