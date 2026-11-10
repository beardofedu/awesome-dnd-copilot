# Searchable resource catalog

Open `index.html` directly in a browser, or preview from the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
# Open http://localhost:8000/catalog/
```

The catalog is a static, public-facing directory of this library, not the
campaign player-site template. It has no dependencies, remote scripts, fonts,
analytics, network data requests, or hosting configuration. Opening or building
it does not enable Pages, install resources, or publish anything. Resource links
point to the repository's `main` branch on GitHub, so they also work when opening
the catalog as a local file.

Search covers titles, source descriptions, tags, and paths. Search terms combine
with AND; the four filters also combine with AND. Clear all filters restores the
full list. All resources remain readable and linked with JavaScript disabled.
Native labeled controls, a skip link, visible focus, a polite result count, and
responsive layouts support keyboard and small-screen use.

## Updating the catalog

From the repository root, using Python 3.9+:

```bash
python3 catalog/build.py
python3 catalog/build.py --check
python3 -m unittest discover -s catalog -p 'test_*.py' -v
node --test catalog/catalog.test.cjs
```

Commit regenerated `index.html` when sources change. `page.html`, `styles.css`,
and `catalog.js` are the presentation sources. The generator discovers all three
phase profiles, their custom agents, and root session-kit READMEs. Titles and
introductions come from the current source Markdown (agent summaries use their
front-matter descriptions); setup and feature tags follow shipped kit files.
`AUDIENCES` in `build.py` records non-DM and split-audience kits.
`EXTRAS` includes the workspace/site templates, installer, note importers, and
first-campaign walkthrough. Update these editorial classifications when a
resource's audience or setup changes. Supporting fixtures, nested add-ons, and
internal test tools are not separate catalog entries.

Tags describe relevant capabilities, including optional ones, not availability
or access rights. "No Copilot required" marks independently usable non-AI parts.
Shared-table resources are intended for joint discussion; split DM/player kits
still require their documented repository boundaries. Individual source files
and READMEs remain the authority for setup, approval, limitations, and privacy.

For browser review, try a combined phase/audience/feature filter, a zero-result
query, reset, keyboard-only navigation, a narrow viewport, and JavaScript off.
