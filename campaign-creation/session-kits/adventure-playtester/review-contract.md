# Adventure Playtester review contract

## Required review checks

For each category, report a finding only when supported by the exact reviewed
text. Otherwise mark `No supported issue found` or `Not assessable` and explain
what source/context is missing; do not infer a defect from silence alone.

- **Clue resilience:** Can essential information be reached through more than
  one reasonable clue, source, or approach? Does a single missed roll, ignored
  lead, or unavailable scene halt the objective?
- **Failure and NPC loss:** What if a check fails, a clue is overlooked, or a
  relevant NPC dies, leaves, or refuses? Is there still a playable route?
- **Refusal and alternatives:** Can players decline the hook, bargain, flee,
  investigate differently, or propose a plausible solution without the DM
  forcing the authored path?
- **Objective accessibility:** Are required locations, objects, and actions
  reachable by the stated party? Are physical, informational, social, or
  resource assumptions that may block access made explicit?
- **Rules support:** Flag consequential mechanics with no rule, DC, procedure, or
  stated adjudication. Ask for the edition/version (5e 2014 vs 2024) when
  needed; do not invent official rulings or present a house rule as a rule.
- **Meaningful choices:** Do options differ in stakes, cost, risk, values, or
  consequence? Are consequences understandable enough to make a choice informed?
- **Pacing and recovery:** Look for timing pressure without usable time signals,
  abrupt transitions, encounter/rest assumptions, or resource expectations that
  make the stated session length implausible. Mark unknown party capabilities as
  assumptions, not facts.
- **Required vs optional scenes:** Are required information and outcomes
  mistakenly hidden in optional scenes? Is the intended necessity of a scene
  clear? Do not require every adventure to use a fixed structure or all three
  pillars.

## Counterfactual path contract

Run at least three named paths. Include a missed-check path and an NPC
unavailable/refusal path when relevant; include a player refusal or materially
different approach when relevant. For each, state:

1. the starting assumption(s), tied to the input or explicitly marked unknown;
2. the decisions/events being simulated;
3. the likely route and whether the stated objective remains playable;
4. any exact source-backed blocker or unresolved question.

These are tabletop thought experiments, not executed sessions, probability
estimates, proof of exhaustive coverage, or guarantees of how real players act.
Do not invent dice results, party abilities, NPC behavior, locations, or hidden
canon as established facts.

## Finding contract

Each actionable finding must include:

- stable ID, category, severity (`Blocker`, `Major`, `Minor`, or `Question`),
  and confidence (`High`, `Medium`, or `Low`);
- exact source revision and file/line range, or a stable scene/heading reference
  if line numbers are unavailable;
- concise observed text/behavior and why it matters to play;
- impact stated conditionally where the outcome depends on player choices;
- one or more concrete alternatives for the DM to consider, not a rewrite or
  canon edit;
- missing context or assumptions, if any.

Severity is about play impact, not prose preference: `Blocker` means the supplied
adventure's stated objective has no supported way forward under the described
case; `Major` means a likely brittle route or consequential ambiguity; `Minor`
means a limited friction or clarity issue; `Question` means more context is
needed before deciding whether there is a defect. Confidence describes evidence
strength, not impact. A missing file/context is not itself a confirmed
adventure defect.

## Output contract

1. Target and revision verification, including whether the exact PR base/head
   were verified or whether this was supplied-text-only.
2. Scope processed: exact files and capped diff/context amounts; exclusions or
   overflow stops.
3. Rules version and unresolved rules questions.
4. Short verdict: `Review complete`, `Review partial`, or `Stopped` (with reason).
5. Findings table with the fields above. Use `No supported issue found` if none.
6. Named counterfactual paths and their assumptions/outcomes.
7. Coverage checklist using `Issue found`, `No supported issue found`, or
   `Not assessable` for each required review check.
8. Limitations: simulation is not live/exhaustive playtesting; omitted context
   and unknowns; no merge/approval/write action was taken.

Never claim all paths are safe, that playtesting occurred, or that no issue
exists merely because information was outside the supplied scope.
