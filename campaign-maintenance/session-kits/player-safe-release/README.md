# Player-safe release

A manual, staged handoff for sharing selected campaign notes from a DM-only
repository to a separate player-accessible repository. It does not publish
anything, connect repositories, or make an AI judgment authoritative.

## Keep the repositories separate

- Keep all DM notes, drafts, review output, and unreleased material in the
  DM-only repository. Never give a player-repository automation or workflow
  access to it.
- The DM reviews sources privately, creates a small plain-text export, approves
  its exact bytes, and manually transfers only that export and its manifest.
- Run the deterministic validator in the player repository. It reads only the
  manifest and files already there; it needs no DM credentials, remote reads, or
  network access.
- Do not use labels, folder names, branches, hidden panels, or audience fields
  as privacy controls. A player-accessible repository is readable by its
  readers.

From a checkout of this library, install the kit in both repositories. Use
fresh destinations. Keep the DM repository private; the kit contains no
campaign-specific secrets.

```bash
KIT=campaign-maintenance/session-kits/player-safe-release
DM_REPO=/path/to/dm-only-repository
PLAYER_REPO=/path/to/player-repository
mkdir -p "$DM_REPO/.github/session-kits" "$PLAYER_REPO/.github/session-kits"
cp -R "$KIT" "$DM_REPO/.github/session-kits/"
cp -R "$KIT" "$PLAYER_REPO/.github/session-kits/"
```

Use the prompt only in the DM-only repository. The player repository copy
provides a local validator and its tests; it does not need the DM's prompt,
review results, or source material. Do not copy the full kit as part of each
release—only the specifically approved export file(s) and manifest described
below.

## Staged release

1. **Review sources in the DM-only repository.** Give the standalone
   `secret-risk-review.prompt.md` the proposed export and relevant source
   excerpts or paths. It should return source-linked concerns and questions,
   not a safety verdict. Keep its input and output in the DM repository. An AI
   review can miss risks, and a clean report, count, label, or asserted audience
   never proves that content is safe.
2. **Prepare the release manually.** Select and rewrite only information the DM
   intends players to know. Remove private notes, secrets, unrevealed clues,
   personal information, credentials, and unnecessary source context. Inspect
   the complete final text in context; do not rely on the AI review alone.
3. **Approve exact bytes.** Keep the final plain-text file(s) in a private DM
   staging folder, outside any player-accessible checkout. Compute each
   SHA-256 after the final edit. Record those digests, the DM's name, and the
   approval date in `player-safe-export.manifest.json` in that private staging
   folder. The DM's approval is for those exact path-and-byte pairs only. Any
   edit, line-ending conversion, rename, or other byte change requires another
   manual review, new digest, and renewed approval.
4. **Transfer manually.** From the DM repository, copy only the approved
   plain-text export file(s) and that manifest into the player repository,
   mapping files into `approved-export/`. For example, after replacing these
   local paths with your checkouts and private staging location:

   Before copying, add this rule to the player repository's `.gitattributes` so
   Git preserves the approved export bytes without line-ending conversion:

   ```gitattributes
   approved-export/** -text
   ```

   ```bash
   DM_EXPORT=/private/dm-staging/session-01.md
   DM_MANIFEST=/private/dm-staging/player-safe-export.manifest.json
   PLAYER_REPO=/path/to/player-repository
   mkdir -p "$PLAYER_REPO/approved-export"
   cp -- "$DM_EXPORT" "$PLAYER_REPO/approved-export/session-01.md"
   cp -- "$DM_MANIFEST" "$PLAYER_REPO/player-safe-export.manifest.json"
   ```

   Compute the digest in the DM-only checkout with
   `sha256sum "$DM_EXPORT"` (or Python's `hashlib.sha256` if `sha256sum` is
   unavailable) and put that exact lowercase digest in the manifest before
   copying. Do not copy DM source files, review reports, hidden data, or
   automation credentials. Do not configure cross-repository reads or
   automatic publication.
5. **Validate locally in the player repository.** With Python 3 installed, run:

   ```bash
   cd "$PLAYER_REPO"
   python3 .github/session-kits/player-safe-release/validate_export.py .
   python3 -m unittest discover -s .github/session-kits/player-safe-release -p 'test_*.py'
   ```

   The validator checks the fixed manifest location, manifest format, allowed
   export paths (plain `.md`/`.txt` UTF-8 files only), exact set of files in
   `approved-export/`, and SHA-256 digests. It rejects symlinks, subdirectories,
   unlisted files, path traversal, binary content, and mismatched bytes. It
   neither contacts nor reads the DM repository.
6. **Make a human release decision.** A passing check means only that the files
   match the digests written in the manifest and meet this format. It does not
   establish who wrote or approved the manifest, authenticate the approver,
   prove confidentiality, or establish that the text is player-safe. The
   manifest and files can be changed together by anyone who can edit the
   player repository. The DM must review the exact transferred files and
   repository audience before committing or otherwise sharing them.

## Example files

`example/` is a fully fictional player-repository fixture. From this kit
directory, verify it with:

```bash
python3 validate_export.py example
```

Its manifest digest is for the exact bytes of
`example/approved-export/session-01.md`. If you edit or reformat that file,
validation intentionally fails until a DM reviews the new bytes and replaces
the digest through the approval process.

For approval, `approved_by` and `approved_on` are plain claims, not signatures
or authenticated attestations. Keep the approved source and review trail in the
DM-only repository; the player repository needs only the export, manifest, and
validator.
