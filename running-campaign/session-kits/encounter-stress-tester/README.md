# Encounter Stress Tester

A dependency-free, deterministic Python CLI for checking arithmetic from
**fictional or user-supplied encounter numbers** before play. It reports action
counts, HP-only effective HP, simplified expected damage/round estimates,
approximate time-to-down ranges, and optional user-supplied XP-budget
comparisons. It does not declare encounters safe, fair, or balanced.

This is not rules-complete: explicitly select D&D 5e **2014** or **2024** in
each input. The label is recorded, not used to load rule tables. No copyrighted
stat blocks or XP tables are bundled. Supply the numbers and assumptions you
are authorized to use. The estimator omits saves, critical damage, defenses,
conditions, movement, initiative, control effects, healing, resource use, and
other modifiers; omitted combat fields are reported, not silently defaulted.
Unknown input keys are listed as unsupported and never applied. Ranges remain
ranges. Expected damage and time-to-down are rough arithmetic,
not combat predictions.

## Files

- `encounter_stress_tester.py` — Python 3 standard-library CLI.
- `input.example.json` / `output.example.json` — fictional sample input and its
  generated report; not a published creature or real party.
- `ai-tactical-review.prompt.md` — optional human-invoked tactical review
  prompt. It proposes alternatives but never runs combat or changes canon.
- `tests/test_encounter_stress_tester.py` — focused validation and arithmetic
  tests.
- `workflow-dispatch.yml.example` — opt-in, manual-only workflow template. It
  is not an active library workflow.

## Run locally

Requires Python 3.9 or newer; there are no packages to install.

```sh
python3 running-campaign/session-kits/encounter-stress-tester/encounter_stress_tester.py \
  running-campaign/session-kits/encounter-stress-tester/input.example.json
python3 -m unittest discover -s running-campaign/session-kits/encounter-stress-tester/tests -v
```

The CLI prints JSON to stdout; optionally pass `--output report.json` to write
to a chosen path. To verify the documented sample report:

```sh
python3 running-campaign/session-kits/encounter-stress-tester/encounter_stress_tester.py \
  running-campaign/session-kits/encounter-stress-tester/input.example.json \
  --output running-campaign/session-kits/encounter-stress-tester/output.example.json
```

## Input contract and interpretation

Every input must supply `rules_version`, the explicit `assumptions` shown in
the sample, and non-empty `party` and `monsters` arrays. Every entry needs a
unique nonblank `id`, `hp`, and `ac`. For combat estimates, provide all of
`attack_bonus`, `damage_per_hit`, `attacks_per_action`, and
`actions_per_round`; missing fields visibly prevent those estimates. Supply
monster `xp` and `thresholds.xp_budget` only when you have values you intend to
compare.

Any numeric input can be a finite number or `{ "min": number, "max": number }`.
Ranges are validated, including nonnegative HP/damage/action/XP values;
booleans, NaN, infinity, reversed ranges, missing required values, and
duplicate IDs are errors. HP may be zero; zero damage is valid and produces a
null time-to-down instead of division by zero. Attack chance uses a simplified
d20 formula clamped to 5%-95% for natural 1/20. Displayed numeric outputs are
rounded to four decimal places; calculations use unrounded values.

The report's focused-fire estimate assumes the party focuses one target and
monsters focus a party target. AC/attack ranges are propagated conservatively.
The time-to-down output pairs the lowest target HP with highest estimated DPR
and vice versa; it is a broad bound, not a turn-by-turn simulation. XP budgets
are compared only to supplied XP: missing XP is `not_evaluable`, overlapping
ranges are `overlaps`, and no danger classifier or universal threshold is
invented.

## Optional GitHub Actions template

To opt in for a campaign repository, copy this kit into
`.github/session-kits/encounter-stress-tester/` and copy
`workflow-dispatch.yml.example` to `.github/workflows/encounter-stress-test.yml`.
Review the workflow and sample data, then run it manually using the repository's
Actions **Run workflow** control. It has read-only repository permissions,
checks out the triggering ref with credentials not persisted, uses no secrets,
and only runs the local standard-library CLI against the fictional example.
It does not execute pull-request code, use `pull_request_target`, or post
results. The template is intentionally not installed or enabled in this
library.
