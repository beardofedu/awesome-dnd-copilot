# Example Adventure Playtester review

> Fictional demonstration only. This is a thought experiment from the sample
> input in `input.template.md`, not an executed session or exhaustive test.

## Target and revision

- Mode: supplied text; no live PR was verified.
- Source: `adventures/bell-beneath-brackenford.md` at `demo-head-7f31c2a`.
- Rules: D&D 5e, version unspecified. Ask whether 2014 or 2024 mechanics apply
  before making version-dependent rulings.
- Scope: only the supplied adventure excerpt. Its supplied markdown lines below
  refer to the sample block in `input.template.md`; no other files were read.
- Verdict: **Review complete** for this excerpt only.

## Summary

The adventure provides multiple routes into the lower sluice and an explicit
noncombat goal, but the stated required clue depends on one Investigation check.
The excerpt also leaves the spill-channel wheel's operation unspecified, so the
party may know the spirit's request yet lack a described way to achieve it. The
sample is too small to establish whether other clues, scene timing, or recovery
details exist elsewhere.

## Findings

| ID | Category | Severity | Confidence | Source | Evidence, impact, and concrete alternatives |
|---|---|---|---|---|---|
| AP-1 | Clue resilience / failed check | Major | High | `adventures/bell-beneath-brackenford.md`, sample-block lines 20–26, “Flooded archive” | The archive is labeled required; one DC 13 Investigation success finds the only stated explanation, while failure explicitly means the plate is not found. In the simulated failure path, the party can still reach the sluice but may lack information needed to make an informed choice. Consider making the plate discoverable with time/no roll, adding a second source (for example a mark on the bell rope), or letting a failed check reveal it with a cost. Those are alternatives for the DM, not canon changes. |
| AP-2 | Objective accessibility / rules support | Major | Medium | `adventures/bell-beneath-brackenford.md`, sample-block lines 30–33 and 42–44, “Lower sluice” / “Aftermath” | The spirit asks the party to open the narrow spill channel, but the rusted wheel has no described operation, obstacle, or alternative. If there is no omitted procedure elsewhere, the objective may stall; the sample does not establish that it is physically impossible. Consider specifying a simple handle/lever approach, a non-check alternative, or what information the wheel gives when examined. The 5e version remains unknown; this finding is about missing adventure procedure, not an asserted rules violation. |
| AP-3 | Pacing and recovery | Question | Medium | `adventures/bell-beneath-brackenford.md`, sample-block lines 42–44, “Aftermath” | The excerpt says no recovery timing is given before the spirit's attack but does not state when the attack begins or how long the party has. It is not possible to determine whether a rest is intended, practical, or disruptive. Clarify the time pressure and whether a short rest or other pause can fit if that matters to the intended party. |

## Counterfactual player paths

1. **Investigation check missed (simulation):** Assume the party searches the archive,
   fails the stated DC 13 check, and follows another entrance to the sluice.
   The three entry routes are explicitly available (sample-block lines 8–11), but the
   failed check withholds the only stated reason for Ilyra's action (sample-block lines
   20–26). The stated objective remains reachable physically; informed
   negotiation may be compromised. This does not predict actual dice or players.
2. **Miller unavailable or hostile (simulation):** Assume Tamsin cannot help.
   The text says the ledger is optional and two other entry routes remain
   (sample-block lines 13–18), so the route to the sluice is still supported. It is unknown
   whether the party can recover the ledger clue elsewhere; no issue is asserted
   for reaching the location.
3. **Party refuses to attack and tries the requested solution (simulation):**
   Assume the party speaks with the spirit and tries to open the channel. The
   spirit requests that action (sample-block lines 30–33), but the wheel operation is
   unspecified (sample-block line 33). A noncombat approach is invited, yet its key objective
   has no described procedure in the excerpt. The sample does not establish
   what the DM would adjudicate.
4. **Party cuts only the rope (simulation):** Assume the party accepts the stated
   consequence and cuts the rope without opening the channel. The text names a
   village flood at midnight (sample-block lines 35–38), so this is a legible consequential
   choice. The consequences after a flood are outside the supplied excerpt and
   cannot be evaluated.

## Coverage checklist

| Check | Status | Note |
|---|---|---|
| Clue resilience | Issue found | AP-1: one stated required clue depends on a check. |
| Missed checks / NPC unavailable | Issue found | AP-1; miller unavailability is covered by alternate routes. |
| Refusal / alternate approaches | Issue found | Noncombat goal is present; wheel procedure is unspecified (AP-2). |
| Objective accessibility | Issue found | Wheel operation is not described in supplied text (AP-2). |
| Unsupported rulings | Not assessable | No version-specific ruling assessed; 5e version unknown. |
| Meaningful choices | No supported issue found | Cutting only the rope has a stated consequence; other options are limited in excerpt. |
| Pacing / recovery | Not assessable | Timing and recovery expectation are unspecified (AP-3). |
| Optional vs required scenes | Issue found | Required archive contains the only stated explanation (AP-1). |

## Limitations

This is a fictional, bounded text review and not a played session, exhaustive
path analysis, or proof that the adventure will succeed or fail. Only the sample
excerpt was supplied; missing context is not treated as a confirmed defect. No
files were edited, and no PR action was taken.
