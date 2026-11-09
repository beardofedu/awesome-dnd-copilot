# DM/player campaign starter and selective installer

From the root of a checkout of this library, use Python 3.9+ and Git. The
installer reads tracked paths from the current checkout's `HEAD`, including
newly committed profiles, agents, complete session kits, and workspace/site
templates. It copies local
working-tree contents for those paths: review local changes first. Untracked or
uncommitted new paths are not discovered. A discoverable kit has a root
`README.md` and at least one root `*.prompt.md`. Files listed in a README's
`File` table or bulleted `Files`/`Contents` section must also be committed.
This accommodates manual and Canvas/automation kits without prescribing their
other filenames. All tracked files beneath the selected kit are copied.
Discovery checks these structural signals, not semantic completeness; review
the kit's instructions and contents before use. Source and destination must
not contain symlink components; selected source files must be ordinary files.
Every installation also includes the root `LICENSE`; retain it when sharing
copied original material. For manual copies, follow the
[attribution guidance](../../ATTRIBUTION.md).

```bash
# Discover exact identifiers in this checkout.
python3 tools/campaign-starter/install.py --list

# Create or choose your own existing, separate local campaign directory first.
mkdir -p /path/to/campaign
# Preview a DM workspace (no destination writes); select exactly one profile.
python3 tools/campaign-starter/install.py /path/to/campaign \
  --profile campaign-creation --agent campaign-creation/world-builder.md \
  --kit campaign-maintenance/session-bridge --starter
# After reviewing the preview, repeat the same command with --apply.
python3 tools/campaign-starter/install.py /path/to/campaign \
  --profile campaign-creation --agent campaign-creation/world-builder.md \
  --kit campaign-maintenance/session-bridge --starter --apply
```

## Separate player workspace and website

Use a **separate player-facing destination**, not your DM workspace:

```bash
mkdir -p /path/to/player-campaign
python3 tools/campaign-starter/install.py /path/to/player-campaign \
  --player-starter --player-site
# After review, repeat with --apply.
```

`--player-starter` installs empty shared metadata, `journal/`, `quests/`,
`world/`, a README, and player-facing `.github/copilot-instructions.md`.
`--player-site` installs only the fictional HTML/CSS site in `docs/` and
`.github/prompts/customize-campaign-site.prompt.md`. Neither flag may be
combined with a DM `--profile` or `--starter`. They may be used separately:
`--player-site` alone preserves an existing workspace and its instructions.

Optional `--agent` and `--kit` selections still require manual audience review;
the installer does not assess whether a resource or its future inputs belong
in a player repository. No site workflow is installed and no Pages settings
are changed. Follow the [site guide](../../campaign-creation/templates/campaign-player-site/)
for customization, local preview, and explicit publication approval. All
fictional examples must be replaced or removed before publishing real content.

## Placement and safeguards

Omit `--starter`, `--agent`, or `--kit` to skip them; repeat `--agent` and
`--kit` for multiple selections. For DM installs, `--profile` is required.
Profiles install as the single
`.github/copilot-instructions.md`, agents under `.github/agents/`, and whole
kits under `.github/session-kits/`. Any kit workflow files remain templates
inside that kit, never under `.github/workflows/`. The empty starter installs
its README, metadata, and DM workspace at the destination root. Kit samples are
fictional, not approved canon. The installer does not create a GitHub repository,
change permissions, contact a network, or create/activate cloud resources.

Every target is preflighted before writing. Existing target files conflict even
if identical, except that an identical root `LICENSE` is reused without
rewriting it when adding resources to an existing workspace. Nothing else is
overwritten, and unrelated destination files are left alone. On a write error
the installer attempts to remove only files and empty directories it created,
reporting incomplete rollback. Preview is not a reservation: rerun it if the
checkout or destination changes. Use a trusted, quiescent local checkout and
destination; protection against concurrent malicious filesystem changes is not
provided. No installation can guarantee available disk space or write
permission in advance. If an error reports incomplete rollback, inspect the
listed paths manually.

The DM must arrange suitable private repository access separately. Folder names
are not access controls. Export only reviewed player-safe material to a separate
player-accessible repository. Review each kit's README and
[session kit guide](../../session-kits.md) for optional manual setup, approvals,
and permissions; copying files activates no workflow, Canvas, or automation.

Run focused tests from this checkout:

```bash
python3 -m unittest discover -s tools/campaign-starter -p 'test_*.py' -v
```

This includes site navigation and asset-link checks at a repository-prefixed
URL. They do not prove accessibility, confidentiality, or human approval;
review the rendered site and its complete source too.
