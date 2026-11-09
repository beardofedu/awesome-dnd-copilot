# Contributing

Thanks for helping make this library useful to DMs and players. Contributions
should be ready to copy into a real campaign repository and should make their
audience, setup, and limitations clear.

## Before opening an issue or pull request

- Search existing resources and issues so new work complements rather than
  duplicates the library.
- Use fictional examples only. Do not include campaign secrets, player
  personal information, credentials, or private campaign material.
- Keep each resource's setup instructions with the resource. Explain its
  destination, prerequisites, activation steps, and any human review required.
- Make clear whether a resource is for a DM, players, or shared use. Audience
  labels are not access controls.
- D&D 5e is the default ruleset unless a resource explicitly names another
  edition. Avoid reproducing published rules text or art; see
  [Attribution and third-party content](./ATTRIBUTION.md).
- Keep agent definitions in the repository's existing Markdown format with
  YAML front matter, including `description` and `tools`.
- For session kits, include a root `README.md` and at least one root
  `*.prompt.md` file so the selective installer can discover the kit. Keep
  README file lists accurate.
- Avoid implying that prompts guarantee correctness, safety, privacy, or
  access control. Describe deterministic checks and their limits.

## Validate changes

Run the focused checks for the resource you changed. For the shared prompt
contracts, run:

```bash
python3 -m unittest discover -s tools/prompt-regression/tests -v
python3 tools/prompt-regression/run.py
```

The full test matrix is documented in
[`.github/workflows/prompt-regression.yml`](./.github/workflows/prompt-regression.yml).
Mention checks that you could not run in your pull request.

## Pull requests

Use the pull-request template. Explain the problem and intended audience,
summarize the change, and list focused test results. Include only original or
properly licensed material; see the [MIT License](./LICENSE) and
[attribution guidance](./ATTRIBUTION.md). By submitting a contribution, you
agree that your original work may be distributed under this repository's MIT
License.
