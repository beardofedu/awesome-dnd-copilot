# Deterministic prompt regression contracts

Run from the repository root with Python 3 and no installed dependencies:

```bash
python3 -m unittest discover -s tools/prompt-regression/tests -v
python3 tools/prompt-regression/run.py
```

The runner discovers `fixtures/*.json` without knowing about pull requests or
other not-yet-merged work. Each fixture declares `expected: "pass"` or
`"fail"` and failing cases name an `expectedError` fragment, so unrelated
validation failures do not mask a regression. A fixture can extend
`accepted-party-journal.json` by setting JSON-style paths under `set`. To check
a single fixture as if it were accepted output, use:

```bash
python3 tools/prompt-regression/run.py --check-fixture accepted-party-journal.json
```

The same command against a deliberately failing fixture must exit nonzero:

```bash
python3 tools/prompt-regression/run.py --check-fixture fail-observation-proposal-mix.json
```

The runner also loads and checks the three committed `state.example.json`
files, their paths, and their references. Reference records in synthetic
fixtures declare observation or proposal status. The checker verifies that
fact-like output fields cite a provided observation and proposal fields cite a
provided proposal. This checks references and category boundaries, **not**
whether a citation actually supports the statement.

The kit-specific checks cover required output members, kit/audience matching,
import incompatibilities, schema version, IDs, numeric bounds, enumerated
statuses, combat references and inventory/voter constraints relevant to each
kit. Explicit `SYNTHETIC_*_SENTINEL` strings are searched only in synthetic
fixture outputs. They are test markers, not real secrets, and this narrow
sentinel check is not a general confidentiality scanner.

These are static contract tests, not prompt execution. They cannot establish
factual fidelity, confidentiality, spoiler safety, prompt quality, whether an
AI obeys instructions, or whether the current prompts would generate the
stored sample outputs. In particular, checking `state.example.json` confirms
its shape and references only; it does not evaluate the prompts.

## Optional manual AI evaluation

Do not invoke a live model from CI or this suite. For any separately authorized
manual evaluation:

1. Freeze and record the exact standalone prompt file revision/hash, fixture
   input, expected-output rubric, and any relevant kit contract revision.
2. Obtain explicit budget approval **before** sending any live evaluation.
   Record the approved maximum spend and stop at that limit; otherwise do not
   run it. Do not send real campaign secrets or personal data.
3. Run each frozen input once with the approved provider/model and record
   provider, model/version, date, prompt/input revision, cost, and rubric
   findings. A human reviewer may add optional sanitized artifacts; do not
   record credentials, tokens, private campaign material, or unreviewed output.
4. Report observations and limitations. Do not let an evaluation alter prompts
   or fixtures automatically. Any improvement is a separate human-reviewed
   change. There are no self-improving loops, recurring evaluations, or
   unapproved resource use.
