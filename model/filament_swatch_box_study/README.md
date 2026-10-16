# Filament swatch storage — current designs and decisions

<a id="quiet-tpu-revision--svg-proposals-2026-10-05"></a>

<a id="filament-swatch-box--display-and-compact-archive"></a>

The box stores existing swatch cards notch-up, with a lift-off protective hood
and a shared key for joining modules. There are separate archive and display
uses. **Archive R2 A is accepted; display repairs are deferred; TPU damping is
discontinued.** These states do not qualify one another.

## Current workstreams and next action

| Workstream | Current result | Next authorized action |
| --- | --- | --- |
| Compact 15-card archive | R2 A, exact G hood and I key 3 are the accepted baseline. User reports successful browsing, J4 joining and full-load hood lifting. | Preserve and use this baseline. No redesign requested. |
| Five-card display | J4 is preferred; seated cards still tilt. K4 is looser and its key stop works at only one end. | Record only; user deferred fixes. Keep G hood and I3. |
| Quiet closure experiments | Q1F joining works, but coverage, upper fit and sliding sound disappoint. A full-TPU G hood is somewhat quieter but still unacceptable and locally distorted, though usable. | None: user ended damping development on 2026-10-06. SVG follow-ups are history. |

Actual printed file hashes/settings are not confirmed. Reported successful use
is physical evidence for those assemblies; CAD checks and reference slices for
other variants do not extend it. Joined-row carrying, durability and calibrated
retention/noise remain unqualified.

Read [archive files and printing](#archive-r2--four-printable-15-card-trials)
for the accepted storage setup, [display files and use](#j4k4-recessed-upward-facing-grips--current-base-trials)
for J4/K4, and [requirements](#requirements-to-preserve) before any resumed design.
The detailed [cap/base comparison](notes/cap_comparison.md) preserves decisions
and print reports. The [development record](notes/development_record.md) retains
prototype specifications, calculations, assembly-API work and earlier print evidence.

## What changed and what it established

The archive replaced widely spaced individual display positions with a shared
15-card pocket. Deep scoops in R1 were rejected as unnecessary and sharp-looking;
R2 compared simpler retaining forms. The user selected and printed continuous-wall
A. It contains sparse cards during reported desk browsing, joins J4 and retains
the full load when lifted by G. This settles that reported use, without proving
open-box transport or a numerical retention margin. See the
[A print report](notes/cap_comparison.md#archive-r2-a-print-report--2026-10-04).

Display development separated insertion clearance from seated support and grip.
J4 retained the broader spring/supports and replaced outward ledges with upward
recesses inside the original foot. The user likes the grip and key, but full-seat
tilt remains; excess bottom clearance is the user's hypothesis. K4's inherited
ports did not establish two-ended stopping. These are unresolved physical issues,
not reasons to repeat earlier CAD passes. See the
[J4/K4 report](notes/cap_comparison.md#j4k4-print-report--2026-10-04).

The damping prototypes added a separate TPU jacket to soften closure contact.
Q1F restored the accepted exterior and preserved joining, but printed sliding
noise and upper fit remained unsatisfactory. Substituting TPU for the entire G
hood did not meet the quietness goal either. The user's layer-line explanation
is unconfirmed. Preserve successful joining and negative acoustic/shape feedback;
do not resume the discontinued investigation. See the
[discontinuation and observations](notes/development_record.md#tpu-damping-discontinued-2026-10-06).

## Archive R2 — four printable 15-card trials

**Accepted printed archive storage baseline: A, the continuous-wall version.**
Rigid-closure sound remains unresolved; the TPU damping project is discontinued.
The user selected A as the best form and reports successful use and integration with J4.
B/C/D remain unprinted. All four share the
original footprint, 15-card pocket, exact accepted **G hood** and **I key 3**.
These retained R2 bases use the existing hood/key; the historical
[Q1 experiment](notes/development_record.md#quiet-tpu-revision--q1-prototype-2026-10-05)
has its own matched hood. Older variants remain available.

| Variant | Form | Source / primary print file / secondary file |
| --- | --- | --- |
| **A — walled; printed and accepted** | **Continuous 40 mm walls** | [Python](archive_r2_walled_15.py) · [STEP](archive_r2_walled_15.step) · [STL](archive_r2_walled_15.stl) |
| B — slim | Four L corners, 4 × 3 mm returns | [Python](archive_r2_slim_15.py) · [STEP](archive_r2_slim_15.step) · [STL](archive_r2_slim_15.stl) |
| C — corner | Four L corners, 8 × 6 mm returns | [Python](archive_r2_corner_15.py) · [STEP](archive_r2_corner_15.step) · [STL](archive_r2_corner_15.stl) |
| D — side guides | Two side cheeks with 8 mm returns | [Python](archive_r2_side_guides_15.py) · [STEP](archive_r2_side_guides_15.step) · [STL](archive_r2_side_guides_15.stl) |

[Labelled drawing of all four](renders/concepts/archive_structure_options.svg)
([PNG](renders/concepts/archive_structure_options.png)) ·
[CAD view of A, C and D with three cards](renders/archive_corner_proposals/inspect_archive_corner_proposals_isometric.png) ·
[Shared parametric builder](archive_corner_proposals.py) ·
[Decisions and SVG-first workflow lesson](notes/cap_comparison.md#archive-r2--four-retaining-forms).

The foot is **64 × 44.8 mm**, pocket **50.4 × 30.3 mm**. Raised guides extend
40 mm above the card floor; open centres retain 18 mm low walls matching the
nominal J body. A 2 mm entrance widens 1.2 mm per side. Window roots and exposed
lips are rounded; the accepted upward recessed grips stay within the foot.
C exposes 62 mm of card across the open centre and 40 mm above the corners.
Full stacks seat upright; sparse cards may lean. No adjustable follower or
sustained-preload card spring is added.

Print **floor down, PETG, .4 mm nozzle/.2 mm layers, two walls, 7% adaptive cubic**.
Each file contains only one base, already placed for printing. Use the existing
[G hood STEP](cap_g_hood_5.step) and [I keys layout](cap_i_grip_keys.step) (use key 3).
Browse on a horizontal desk, insert the bundle square and lift cards vertically.
The user has tested A successfully for the previously discussed browsing and
sparse-card containment concerns, including a single card. With all 15 cards
loaded and G hood fitted, lifting by the hood kept the base attached. Open-box
carrying/inversion and long-term durability are not qualified. The earlier
recommendation to start with C is superseded by the user's successful A trial.

[Functional CAD checks](notes/archive_r2_checks.json) cover actual cards,
8-direction bundle entry, extraction, normal sparse contact, complete I3/J4
joining and G key captivity. The [corner study](notes/archive_corner_support.json)
adds selected yaw/lean challenges. All four block the sampled rigid cases;
this does not prove all escape paths or printed stiffness. A now has a successful
physical-use report: cards remain contained during the reported tests, and the
existing key, latest J (J4) and exact G hood work together. B/C/D have only CAD
and slice evidence. Reference STL slicing does not verify Orca's GUI STEP import.

All four valid bases exported successfully as matching STEP/STL pairs.
OrcaSlicer 2.4.2 completed the diagnostic Q2C/PETG/.4/.2/two-wall/7% slices
with preserved placement, no reported notices and no generated supports in
the automatic-support probes. This matches the agreed starting setup, but is
not the user's actual temperature/flow calibration.

Native paired-export/slice reports:
[A](notes/archive_r2_walled_review.json) · [B](notes/archive_r2_slim_review.json) ·
[C](notes/archive_r2_corner_review.json) · [D](notes/archive_r2_side_guides_review.json).

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A — complete base is the trial | No detached coupon | Pocket constraints and sparse browsing need the complete geometry |
| Final printable object, A | Yes — printed and accepted, reported 2026-10-04 | `archive_r2_walled_15.step/.stl`; existing G hood, key and J4 base | User chose A; archive use, single-card/sparse-card containment, J4 joining and G hood fit work as intended. Full 15-card load stays attached when lifted by the hood. Exact printed artifact hash and actual print settings are not supplied; carrying/inversion and durability remain unqualified |
| Final printable objects, B/C/D | No — user printed only A | Other three R2 STEP/STL pairs above | No physical-use result; retain existing CAD/slice evidence |

[Detailed A print report](notes/cap_comparison.md#archive-r2-a-print-report--2026-10-04).

[Development reflection and measured memory-policy comparison](../../performance/reviews/2026-10-04-152419-archive-reflection-and-memory-policy.md)
records the workflow improvements and historical memory-policy comparison.
[Shared RAM budgeting and admission have since been removed](../../performance/reviews/2026-10-04-163751-shared-memory-controls-removed.md). The complete-input
inspection declaration still enables guarded geometry reuse. Printable geometry
and print status are unchanged by this reflection.

## Requirements to preserve

- Store the cards with their long dimension vertical and notch at the top; the
  closed hood fully covers them.
- For display, keep seated cards upright and aligned even with only a few occupied positions.
  A final downward press is acceptable. The broad clip was liked; the tiny end
  spring gave no useful centering in the earlier PETG print.
- Guide insertion from left/right and front/back so replacing thin cards does
  not require precise alignment with a narrow slot.
- Use printed parts throughout. Seat the hood's lower rim against the base
  (the discontinued quiet revision proposed a TPU seat) while
  retaining a practical grip and deliberate opening motion.
- Support adding modules with modest repeated material and part overhead.
  Occasional separation should remain possible; joined carrying is unqualified.
- Keep the five-card display variants; the archive trial holds a compact stack
  of 15. In the archive, a full stack sits upright, while a sparse remainder may
  lean during desk browsing provided it stays contained.

Reusable form preferences are maintained in the
[design preference reference](../../.codex/skills/cadquery-3d-design/references/user-preferences.md).
Exact dimensions, artifact compatibility and physical results remain here and
in the linked object records. The H connector sample has been printed and rejected
for excessive looseness. Its I replacement keys now work in the printed sample;
J4's complete-base key now works in the reported print, while K4 has the
one-ended stopping-wall problem described above.

The [earlier archive discussion](notes/cap_comparison.md#future-compact-archival-module--recorded-2026-10-04)
and [SVG proposal](renders/concepts/archive_containment.svg) are concept history.
The user rejects panel 1's drawn side construction as a CAD reference; R1's
[actual CAD](notes/development_record.md#archive-r1--rejected-before-printing-retained-history)
superseded it, and R2 subsequently replaced R1. Larger capacity and additional
mechanisms remain undecided. Further hood exploration is ended.

## J4/K4 recessed upward-facing grips — current base trials

**J4:** [STEP](cap_j4_base_5.step), [STL](cap_j4_base_5.stl),
[source](cap_j4_base_5.py). **K4:** [STEP](cap_k4_base_5.step),
[STL](cap_k4_base_5.stl), [source](cap_k4_base_5.py).
Reuse the [accepted G hood](cap_g_hood_5.step) and existing I key 3.
No new hood is required. Bases retain the original **64 × 44.8 mm footprint**
and matching joining pitch. J4 preserves J2's
broad spring and opposing upright rails; K4 preserves K2's corrected dome
follower and opposing rails. Earlier checks preserved each parent's geometry;
they did not qualify K4's key capture at both ends. Use J4 as the preferred
current baseline; K4's reported one-ended stop failure remains unresolved.

The two recesses are 18 mm long, 2.2 mm deep from each X side and open above
a 2 mm floor. Enter from the side through the **3 mm gap below the closed
hood**, rest a fingertip edge on the upward floor and press the base down while
lifting the hood with the other hand. The thick finger body stays outside the
hood. There are no outward ledges. The inner root has a .6 mm radius, the
exposed floor edge .35 mm and plan ends 1 mm; original perimeter rounding is
retained. The grip is intentionally small: reach and skin/nail comfort require
the complete-base trial, not just a detached pocket coupon.

Print floor down in PETG with the established .4 mm nozzle, .2 mm layers,
two walls and 7% adaptive cubic, using **ordinary slicing**. G prints roof down
with ordinary slicing if another is needed. Use J4 with the plain back toward
the broad spring; use K4 with the domed/engraved face toward the shaped follower.
Try one, three and five cards: check upright alignment, entry/removal, actual
K4 dome contact, grip and recovery after dwell. Try opening while modules are
joined, keeping the row supported; carrying remains unqualified.

[Closed appearance](renders/recessed_grip_assembled/inspect_recessed_grip_isometric.png)
contains actual printable parts only. The
[access section](renders/recessed_grip_section/inspect_recessed_grip_section_front.png)
includes an assumed 12 mm wide/2.6 mm thick distal contact edge; its larger outer
body is a reference, not another printed part. [Targeted checks](notes/recessed_grip_checks.json)
cover upward bearing contact, horizontal side approach past the closed hood
and joined neighbour, no outward additions, preserved card/support/catch/key
geometry and four remaining G rim seats outside the recesses. These do not
establish actual finger comfort, card performance or calibrated forces.
[J4 export/slice review](notes/j4_review.json) and
[K4 export/slice review](notes/k4_review.json) retain the final manufacturing evidence.
Both complete bases are now reported printed. Upward recesses are liked and
J4's key works. J4's full-seat tilt remains; K4 is less firm and has a failed
key stop at one end. Further modelling is explicitly deferred. The retained
CAD/slice reports describe geometry/manufacturing checks, not resolutions of
these physical issues.

## Attribution

The [quiet TPU proposal phase](notes/development_record.md#damped-prototype-print-feedback-and-svg-exploration-2026-10-06)
records its separate attribution in the development record. The following attribution belongs to the
historical CAD work.

Primary language model: **GPT-6.1 Sol**. Reasoning effort: **high**. The exact
model and effort are explicitly user-provided, refining the earlier family-only
**GPT-6** record where variant and effort were not exposed. Harness: **Codex**,
shared repository workspace. Provider: **OpenAI**. No subagents. Swatch dimensions and reference
outline derive from the existing user-provided SCAD source; its historical
Gemini attribution remains with that object.

Measured agent effort for the selected historical work is recorded in
[the token and timing notes](notes/agent_effort.md). This supplements creator provenance;
its task and capture limits are explicit.

## Product verification

[verification.py](verification.py) composes the existing shared closed/card/hood/
insert/landing/joining groups and Q1F-local insert screens. Run `./execute.py --threads 2
model/filament_swatch_box_study/verification.py --variant q1f` (or `q1`).
Stdout is always JSON; `--check quiet.hood` focuses a group
while leaving other obligations visible. See the [shared contract](../../product_verification/README.md).

Stable user-intent IDs: `swatch.storage`, `swatch.open`, `swatch.join`,
`swatch.quiet`, `swatch.appearance`, `swatch.upper-fit`. Their provenance links to
the acceptance/feedback sections here. `swatch.insert-connected` is Q1F-only;
`swatch.insert-anchored` follows the separate-jacket architecture;
`swatch.landing-access` follows the prototype soft-seat/grip choice; durability
remains physical UNKNOWN. The reviewed [intent/source inventory](notes/verification_sources.json)
guards silent reclassification/criterion removal and conservative source transfer.
Four beads, a TPU jacket and G hood reuse remain historical design choices.

Q1F CAD PASS, reported joining PASS and noise/coverage/fit FAIL coexist. Q1 is not
inferred printed. `--variant q1f-tpu-hood` surfaces the separate material trial:
noise FAIL; distorted but usable shell observation without inventing appearance
acceptance/rejection. The layer-line cause stays an open hypothesis. Accepted
A/G/I3 loaded-storage evidence is retained within that separate baseline scope.
`replacement-fixture` demonstrates uncovered user requirements and N/A obsolete
insert obligations; it is not a proposed variant. All reports retain the damping
stop directive; none reopens development. Physical settings/hashes remain unknown.

Migration qualification reuses legacy outcomes and existing placement/negative
checks, including wrong hood placement, missing beads and floating card. Geometry,
print exports, historical computational/physical records and slicing are preserved.

Initial verification infrastructure contributor: GPT-6-based Codex; exact model variant/reasoning
effort not exposed; Codex shared-workspace API agent; OpenAI; no subagents. Historical
product attribution above is preserved.

Protected storage intent names the 15-card collection; its current engineering
seating question requires that full fixture.
A smaller source-card population now makes the attempted storage check
INCONCLUSIVE before geometry traversal: a partial fixture cannot qualify the
full collection. This is a verification-input defect, not an inferred physical
capacity failure. Both unchanged source populations satisfy that guard.

The composed `quiet.hood` check shares one actual candidate and returns independent
hood-path, insert-capture/access and landing/grip answers. A failed hood path cannot
falsely mark insert capture FAIL or stop it being checked; a missing landing seat
cannot falsely fail joining. Joined opening belongs to the
joining question, avoiding a redundant cross-target failure claim. The existing
`main()` still composes the same operations into its established report. Historical
reports retain their earlier checker identities and have not been overwritten.

All consequential pre-pair crops now translate known Boolean kernel failures to
INCONCLUSIVE instead of aborting independent requirements. Successfully computed
but absent required diaphragm/landing/key-capture material is FAIL. Neither
outcome changes the historical physical evidence or authorizes renewed development.

<a id="three-directions-for-discussion"></a>

## Earlier designs and technical investigations

These links retain earlier section addresses used by evidence records. The
linked notes explain the historical phase; their old next-step instructions do
not reopen deferred or discontinued work.

<a id="tpu-damping-discontinued-2026-10-06"></a>

- [TPU damping discontinued, 2026-10-06](notes/development_record.md#tpu-damping-discontinued-2026-10-06)

<a id="three-directions-for-discussion--retained-concept-history"></a>
<a id="damped-prototype-print-feedback-and-svg-exploration-2026-10-06"></a>

- [Damped prototype print feedback and SVG exploration, 2026-10-06](notes/development_record.md#damped-prototype-print-feedback-and-svg-exploration-2026-10-06)

<a id="named-assembly-engineering-2026-10-06"></a>

- [Named assembly engineering, 2026-10-06](notes/development_record.md#named-assembly-engineering-2026-10-06)

<a id="quiet-tpu-revision--q1f-with-the-accepted-exterior-2026-10-05"></a>

- [Quiet TPU revision — Q1F with the accepted exterior, 2026-10-05](notes/development_record.md#quiet-tpu-revision--q1f-with-the-accepted-exterior-2026-10-05)

<a id="quiet-tpu-revision--q1-prototype-2026-10-05"></a>

- [Quiet TPU revision — Q1 prototype, 2026-10-05](notes/development_record.md#quiet-tpu-revision--q1-prototype-2026-10-05)

<a id="archive-r1--rejected-before-printing-retained-history"></a>

- [Archive R1 — rejected before printing; retained history](notes/development_record.md#archive-r1--rejected-before-printing-retained-history)

<a id="j3k3-upward-facing-ledges--rejected-before-printing"></a>

- [J3/K3 upward-facing ledges — rejected before printing](notes/development_record.md#j3k3-upward-facing-ledges--rejected-before-printing)

<a id="preserved-j2k2-card-support-revisions"></a>

- [Preserved J2/K2 card-support revisions](notes/development_record.md#preserved-j2k2-card-support-revisions)

<a id="historical-jk-files--preserve-the-rejected-bases"></a>
<a id="v1-single-wall-vase-hood--additional-transparency-trial"></a>

- [V1 single-wall vase hood — additional transparency trial](notes/development_record.md#v1-single-wall-vase-hood--additional-transparency-trial)

<a id="k--existing-dome-shoulder-with-less-seated-spring-bend"></a>

- [K — existing dome shoulder with less seated spring bend](notes/development_record.md#k--existing-dome-shoulder-with-less-seated-spring-bend)

<a id="j--centered-broader-card-panels"></a>

- [J — centered, broader card panels](notes/development_record.md#j--centered-broader-card-panels)

<a id="i--printed-replacement-key-result"></a>

- [I — printed replacement-key result](notes/development_record.md#i--printed-replacement-key-result)

<a id="h--connector-without-a-handle"></a>

- [H — connector without a handle](notes/development_record.md#h--connector-without-a-handle)

<a id="g--retained-modular-five-card-proof"></a>

- [G — retained modular five-card proof](notes/development_record.md#g--retained-modular-five-card-proof)

<a id="f--smooth-exterior-hood"></a>

- [F — smooth exterior hood](notes/development_record.md#f--smooth-exterior-hood)

<a id="e--thin-hood-and-matching-base"></a>
<a id="earlier-thin-hood--e"></a>

- [Earlier thin hood — E](notes/development_record.md#earlier-thin-hood--e)

<a id="historical-matched-prototype--d"></a>
<a id="printed-reference--d"></a>

- [Printed reference — D](notes/development_record.md#printed-reference--d)

<a id="earlier-cap-alternatives"></a>

- [Earlier cap alternatives](notes/development_record.md#earlier-cap-alternatives)

<a id="seating-and-handling"></a>

- [Seating and handling](notes/development_record.md#seating-and-handling)

<a id="print-and-test"></a>

- [Print and test](notes/development_record.md#print-and-test)

<a id="decisions-and-evidence"></a>

- [Decisions and evidence](notes/development_record.md#decisions-and-evidence)

<a id="physical-history-and-print-status"></a>

- [Physical history and print status](notes/development_record.md#physical-history-and-print-status)
