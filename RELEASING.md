# Versions and releases

## Pin a library snapshot

For DMs and players copying resources, a pin identifies the exact library
snapshot used by a campaign. `main` changes over time; use a published tag
from [GitHub Releases](https://github.com/beardofedu/awesome-dnd-copilot/releases)
when one exists, or a full commit SHA. Read the
[changelog](./CHANGELOG.md) before updating.

There were no tags or published releases when this guide was introduced.
The unversioned baseline in the changelog can be pinned now:

```bash
git clone https://github.com/beardofedu/awesome-dnd-copilot.git awesome-dnd-copilot
cd awesome-dnd-copilot
git checkout --detach 29185b15b1b641d69815c71c7fab2dc7abda7e1a
git rev-parse HEAD
```

For a later snapshot, replace the SHA with an actual published tag or full
commit SHA, not a branch name. Record the resolved full SHA, the tag if used,
and the resource paths you copied in your campaign's own notes. Copy only
selected resources using the instructions in that snapshot; a detached checkout
does not install or activate anything.

Copied files do not update automatically. Before replacing them, save your
campaign customizations, compare the pinned and proposed snapshots, and review
any migration or activation notes. A pin fixes library files, not Copilot
behavior, provider APIs, dependencies, permissions, or service availability;
the [compatibility guide](./COMPATIBILITY.md) still applies.

## Prepare a release (maintainers)

Releases are manual. This guide does not establish a release schedule,
long-term support policy, or backwards-compatibility guarantee.

1. Review the changes since the previous release, or since the documented
   unversioned baseline for the first release. Add concise user-facing entries
   under **Unreleased** in `CHANGELOG.md`, grouping additions, changes, fixes,
   and removals as needed. Call out affected paths, changed setup or activation,
   and migration steps; do not infer historical releases from commit dates.
2. Choose an unused `vMAJOR.MINOR.PATCH` tag for the snapshot. Select the first
   version deliberately at release time; none is assigned by this guide.
   Use major increments for incompatible installation or resource-contract
   changes, minor increments for compatible additions, and patch increments
   for compatible fixes. Describe prompt behavior changes explicitly rather
   than implying that a version guarantees generated output.
3. Prepare a release PR following [CONTRIBUTING.md](./CONTRIBUTING.md). Move
   the entries being released into a heading with the chosen version, leaving
   **Unreleased** available for subsequent changes. Add the actual publication
   date when known, not a guessed date. Include upgrade instructions and link
   the version heading to its intended GitHub release page.
4. Review the exact release candidate on `main` after merging. Confirm the
   [repository checks](./.github/workflows/prompt-regression.yml) pass for that
   commit and manually review changed prompts and examples. Static checks do
   not establish output quality or spoiler safety.
5. In GitHub Releases, prepare a draft targeting that exact commit with the
   chosen tag and the corresponding changelog entries. Verify the commit,
   version, installation caveats, and migration notes before publishing.
   Publishing the release and creating its tag are explicit maintainer actions,
   not consequences of merging documentation.
6. Confirm the published tag resolves to the intended commit and that the
   release notes and changelog agree. Record the publication date in the
   changelog if it was not known in the release PR. Never move or reuse a
   published tag; correct released files in a new version instead.

Keep the unversioned baseline as historical context. The first release notes
should identify that baseline and summarize the resulting library snapshot
without presenting earlier commits as separately versioned releases.
