# Campaign player site

A reusable, plain HTML/CSS player hub for any D&D 5e campaign. No framework,
build step, external fonts, analytics, or JavaScript is required. The Wayfarer's
Table content is fictional demonstration material, not your campaign's canon.

## Choose the right repository

Use a **separate player-facing repository** containing only material approved
for its readers and for public publication. Do not install this site in a
DM-only repository or give it access to DM notes. A private repository does not
by itself make a Pages site private. Treat the site as publicly accessible
unless you have independently configured and verified supported access controls.

Folders, HTML comments, hidden panels, branches, and unlinked files do not hide
spoilers. Review all files in `docs/`, including images and metadata, before
publishing. Never commit unreleased notes to a public repository; deleting a
file later does not remove it from Git history. Do not include player contact
details, personal safety disclosures, private document links, or credentials.

The [player-safe-release kit](../../../campaign-maintenance/session-kits/player-safe-release/)
provides a manual review and exact-byte export process. Its validator verifies
file integrity and format, not confidentiality. Editing approved exports into
website pages requires another human review of the final pages. This scaffold
does not import exports, read another repository, or publish automatically.

## Copy into your repository

From a checkout of this library, choose a fresh player-repository destination:

```bash
PLAYER_REPO=/path/to/player-repository
mkdir -p "$PLAYER_REPO/.github/prompts"
cp -R campaign-creation/templates/campaign-player-site/docs "$PLAYER_REPO/"
cp campaign-creation/templates/campaign-player-site/customize.prompt.md \
  "$PLAYER_REPO/.github/prompts/customize-campaign-site.prompt.md"
```

If `docs/` or the destination prompt already exists, stop and reconcile manually
instead of running these copy commands. The
[selective installer](../../../tools/campaign-starter/README.md) can preview
and copy both resources without overwriting:

```bash
python3 tools/campaign-starter/install.py "$PLAYER_REPO" \
  --player-starter --player-site
# After reviewing the preview, repeat with --apply.
```

`--player-starter` also adds an empty player workspace and its instructions.
Do not combine it with a DM profile. For an existing player workspace, use
`--player-site` alone to preserve its instructions and install only the site
and customization prompt.

## Customize

| File | Use |
|---|---|
| `docs/index.html` | Campaign pitch, quick facts, next-session preparation |
| `docs/party.html` | Approved character summaries, without real player identities |
| `docs/journal.html` | Reviewed recaps, known quests, and separate party theories |
| `docs/world.html` | Places, NPCs, and factions the party already knows |
| `docs/rules.html` | Explicit rules version, house rulings, and authorized references |
| `docs/safety.html` | General table procedures, not personal disclosures |
| `docs/assets/style.css` | Shared colors, responsive layout, navigation, print styling |
| `docs/.nojekyll` | Publish these files without Jekyll processing |

Replace the fictional content, page titles, campaign brand, rules version, and
next-session details. Keep the demonstration notices until all sample material
is removed. Keep navigation consistent across pages. Add optional character
guides, a home-base page, or a gallery only when needed; use images you have
permission to publish, with descriptive alt text and reviewed metadata.

Ask Copilot in the **player repository**:

```text
Read .github/prompts/customize-campaign-site.prompt.md. Help me customize docs/
using only the approved player content I supply. Show unresolved decisions
before editing; do not enable Pages, publish, or access a DM repository.
```

Plain HTML favors a dependency-free first installation. Navigation is repeated
in six pages; update all six when adding or renaming pages. Use relative paths
such as `party.html` and `assets/style.css`, not `/party.html`: project Pages
sites normally live beneath a repository-name URL prefix.

## Preview and review

From your player repository:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open `http://localhost:8000`, then stop the server with Ctrl+C. In a remote
workspace, use its approved port-forwarding or preview facility. Check every
navigation link, narrow-screen layout, keyboard focus, and print preview.
Review the complete source, not just what the browser displays.

Local preview is not deployment approval. Agree with the group what may be
public, and have the DM review the exact final files before committing them.
Do not reproduce paid rules text or publish artwork without permission.

## Enable GitHub Pages explicitly

After review, commit the approved site files to the player repository's
publishing branch. These steps require suitable repository permissions and
Pages availability for your account or organization:

1. Open the player repository's **Settings > Pages**.
2. Under **Build and deployment**, select **Deploy from a branch**.
3. Select `main` (or your actual publishing branch) and `/docs`, then **Save**.
4. Wait for deployment and follow the site URL shown in Pages settings.
5. Verify links at that deployed URL, including its repository-name prefix.

Subsequent pushes to the selected branch's `docs/` publish updates. Review
changes before merging; copying this template or running the installer does
not enable Pages. No Actions deployment workflow or token is included.

Source: [GitHub Pages publishing configuration](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
If deployment fails, check Pages availability, the selected branch and folder,
and the deployment run before changing publishing settings.
