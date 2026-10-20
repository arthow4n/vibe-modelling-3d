# Full-case print comparison: 2 mm and three-line walls

**Current design feedback:** the user prefers recessed saddles and now asks
whether a shallow, smoothly curved [full-wrap band](#continuous-band-and-shallow-profile)
would make the grip easier to use. The [B-family suggestions](#recessed-saddle-variants)
remain the preceding comparison.
They reject the finger notches as an opening aid and intend to remove them,
but defer CAD changes until after the visual exploration. Existing
print files below retain the notches and are available for thickness comparison;
their opening grip is not accepted.

Two complete body/cap pairs are ready for a practical print comparison. The
thick construction is retained. The thin pair has **1.2 mm ordinary walls**;
Orca actually generates **three extrusion strokes across them**, rather than
relying on the nominal nozzle diameter. Both pairs sliced without supports.
Neither has a reported physical result for this comparison.

**Current revision:** both caps have complete finger-slot rounding, and the thin
cap's raised joint backing blends into the shell. See the
[comfort detail drawing](wall_comparison/comfort.svg) and [revision](#comfort-revision).

![Wall sections, actual sliced strokes and material comparison](wall_comparison/comparison.svg)

[SVG](wall_comparison/comparison.svg) · [PNG](wall_comparison/comparison.png) ·
[Previous overlap/force investigation and physical history](short_lap.md)

## Choose a matching pair

| Complete case | Authoritative Python entry | STEP (primary print file) | STL |
| --- | --- | --- | --- |
| 2 mm control, finished cap | [short_lap_case.py](../short_lap_case.py) | [short_lap_case.step](../short_lap_case.step) | [short_lap_case.stl](../short_lap_case.stl) |
| Three-line thin pair | [short_lap_case_three_line.py](../short_lap_case_three_line.py) | [short_lap_case_three_line.step](../short_lap_case_three_line.step) | [short_lap_case_three_line.stl](../short_lap_case_three_line.stl) |

Each export contains the complete body and cap, separated in print placement.
You can select only the cap in your slicer. **Use the thin cap with the thin body**:
their mating surfaces move together. The caps are not interchangeable with the
other version. Printing caps alone can compare flexibility, but testing fit and
retention requires the corresponding body.

## Authorized comparison

On 2026-10-20 the user questioned the material cost of 2 mm walls and requested
three extrusion lines instead, allowing a catch opening if needed. They asked
to retain the current iteration and deliver complete cases for both thicknesses,
so they can choose to print only the cap themselves. They clarified that total
width need not be exact, then selected **the same general outside size with a
matching thin body/cap pair**. These are user directions; 1.2 mm and local pad
dimensions are implementation choices checked below.

The finish line is two usable print candidates, checked for fit and actual sliced
wall construction. No new force or impact simulation is needed to deliver this
comparison. The prior side-hit investigation remains closed and inconclusive;
its results do not establish a safe bag-knock load for either pair.

## What changed and why

| Feature | Preserved control | Thin comparison |
| --- | --- | --- |
| Ordinary body/cap walls | 2 mm | 1.2 mm |
| Body overlap wall | 2 mm | 1.2 mm |
| Cap receiving band | 2.7 mm | 1.2 mm away from pads; 1.85 mm at uncut pads |
| Backing at pocket/runout peak | 2.05 mm | 1.2 mm at pad center |
| Floor and roof | 2 mm | 1.2 mm: six 0.2 mm layers |
| Overlap / bite / nominal guide gap per side | 30 / 0.6 / 0.1 mm | Same |
| Main exterior width × depth × length | 74.2 × 51.2 × 264 mm | Same |
| Maximum width at cap pads | 74.2 mm | 75.5 mm |
| Central sleeve mouth | 64.6 × 41.6 mm | 69.2 × 46.2 mm |

Simply thinning the existing cap would leave only 0.55 mm behind its catch
recesses and the long relief tracks. Instead, two small outside pads add 0.65 mm
per side over a 19 mm blended region, preserving 1.2 mm of backing at the deepest
cuts. They blend back into the shell above and beside the overlap. This avoids cutting long
open slots or adding separate cantilever arms. Between recessed regions a pad
is intentionally thicker than three lines; the whole cap is not uniformly 1.2 mm.
The main thin builder is [short_lap_thin.py](../short_lap_thin.py).

The same small-bite wall-snap profile and recovery track remain. Thinner walls
will flex more easily; their printed holding force, return, rubbing and durability
are unknown. The old conditional 11.22 N pull estimate belongs to the reinforced
control geometry and must not be applied to the thin pair.

## Actual slicing and fit evidence

Both full pairs were sliced with **OrcaSlicer 2.4.2**, Qidi Q2C, 0.4 mm nozzle,
PETG, 0.2 mm layers, three wall loops and 7% adaptive cubic infill. The ordinary
wall is a narrow shell with two boundary contours: the three-loop setting does
not itself mean three lines total across that shell.

The actual paths contain five strokes in the 2 mm wall: two boundary lines, two
inner lines and a center gap-fill line. The 1.2 mm wall contains two boundary
lines and one center gap-fill line. This is **three total lines**, without sparse
infill between them. Boundary widths are 0.42 mm; the middle thin gap-fill line
is about 0.43 mm. Slicer spacing accounts for overlap between bead sections;
adding nozzle diameters is not the width calculation.

| Same-profile full-pair estimate | Control | Thin |
| --- | --- | --- |
| Filament | 183.27 g | 108.54 g |
| Print time | 5 h 0 m 56 s | 4 h 4 m 57 s |
| Saving | — | 74.73 g (40.8%); 55 m 59 s (18.6%) |

These are slicer estimates, not weighed prints. They include the full pair under
this profile. Different settings, caps alone and real printing can differ.

The focused checks passed:

- Thin body and cap fit seated without interference; each end catch independently
  obstructs a 1 mm opening even with ±0.1 mm sideways guide play.
- Sampled axial opening positions have no guide interference; from 6 mm lift
  onward the snap clears. Pushing below the seated position meets the hard stop.
- Individual brush/tube passage gauges clear, recessed grips remain accessible,
  and the actual R4 end surfaces remain. Integrated packing still needs the real
  items; individual gauges do not prove simultaneous loading.
- Actual sampled main body, main cap, sleeve, runout backing and pocket backing
  sections have five control strokes or three thin strokes. The path-width
  approximation leaves under 0.05 mm total uncovered width and under 0.01 mm
  internal gap at each section. These are local fill checks, not calibration of
  deposited polymer, bonding or every curved corner.
- Native evaluation/export succeeded for both revised full pairs. Both
  diagnostic slices and automatic-support probes succeeded,
  with no generated supports and no log notices.

Reproducible local inspection and SVG source:
[short_lap_wall_comparison.py](../short_lap_wall_comparison.py), run with
`./execute.py --threads 1 model/dental_travel_case/short_lap_wall_comparison.py`.
It reads the kept Orca runs identified in the receipts. The committed result is
[checks.json](wall_comparison/checks.json), including source/artifact hashes,
rigid capture/path results and actual section strokes.
Native slice receipts: [control](wall_comparison/control_slice.json),
[thin](wall_comparison/thin_slice.json).

Verification uses the shared interface, with explicit variants:

```sh
./execute.py --threads 1 model/dental_travel_case/verification.py --variant slim-short-lap-three-line
./execute.py --threads 1 model/dental_travel_case/verification.py --variant slim-short-lap
```

The thin plan preserves inherited user intent and physical unknowns while
replacing geometry-dependent evidence. No thick-shell numerical force or impact
claim is inherited. Current reports: [thin](wall_comparison/thin_verification.json),
[control](wall_comparison/control_verification.json).

## Comfort revision

The user visually identified square corners remaining on the cap finger slots,
including their interior edges, and rejected abrupt exterior joint transitions.
This is CAD/appearance feedback, not a print report. Both full-case exports now
include **0.4 mm fillets along the complete inner and outer slot boundaries**,
including the inward corners where the slot meets the open rim. The earlier
0.8 mm rounding in the cutting profile alone did not finish those edges.

The thin cap's backing is now a low, blended swelling: tangent cubic curves
spread its 0.65 mm projection across 3.2 mm ramps on either side, and blend its
upper end back into the cap over 8 mm. The total blended region is 19 mm wide;
the flat middle preserves full backing across the 10.6 mm pocket/track. The
outside open rim is filleted after joining the backing to the shell, removing
the separate square pad lip. Maximum width and central backing thickness are
unchanged. The thicker control has no raised outside pads.

[Before/after slot sections and the new backing section](wall_comparison/comfort.svg)
show the actual CAD. [short_lap_comfort.py](../short_lap_comfort.py) applies the
slot finishing to both print wrappers; the historical reinforced builder is
unchanged. Both bodies are unchanged. The matching guide, bite, seat and release
profiles are preserved and both finished pairs receive the same fit/path checks.
The full pairs have fresh export/slice evidence; earlier force calculations stay
historical and are not promoted to ratings for these revised caps. The old joint
specimen remains historical and does not contain this finishing revision.

The missed step was reviewing only the rounded cutter rather than the final
opening, including its junctions with the rim. Existing edge-treatment guidance
already covers this; the correction is the complete-boundary selection and the
two complementary section views here, rather than another workflow rule. Printed
surface feel still depends on the print; no tactile result is claimed.

## Corner grip exploration

The user questions the practical value of gripping the seam notches when pulling
the halves apart. They request several SVG proposals for exterior friction,
texture or shape, especially around the corners. Removal of the notches is the
intended direction, but they explicitly defer CAD edits until after this visual
exploration. This supersedes refining the old notch as the opening solution; it
is design/use feedback, not evidence of a print or measured opening force.

**[Compare all three directions](../renders/concepts/grip_comparison.svg)** ·
[PNG preview](../renders/concepts/grip_comparison.png)

| Proposal | What the fingers use | Practical tradeoff |
| --- | --- | --- |
| [A — Soft corner ribs](../renders/concepts/grip_a_ribs.svg) | Several low, rounded ribs run across the pulling direction, wrapping each corner | Least change to storage and silhouette; relies substantially on pinch/friction, with some small rib bearing surfaces |
| [B — Shallow corner saddles](../renders/concepts/grip_b_saddles.svg) | A broad depression gives the finger pad a seat and curved slopes to press against | Cleaner, recessed exterior; needs the inner surface moved too to preserve wall thickness, using local interior space |
| [C — Rounded corner shoulders](../renders/concepts/grip_c_shoulders.svg) | A small rounded shoulder above the cap grasp and below the body grasp gives opposing bearing faces | More direct resistance to axial slipping, but more visible exterior swelling; useful grip still depends on finger contact and compliance |

The drawings use the current **74.2 × 51.2 × 264 mm** general proportions and
**30 mm overlap**. They show the closed case, one contact zone for each hand,
opposite pulling directions, corner coverage from the end, and an enlarged axial
surface profile. Existing notches are omitted in the sketches only. Orange
contact marks are schematic finger pads, not an anatomical reach/comfort study.
The thin cap's local snap backing is omitted from these simplified front/end
views; the proposals do not remove or replace it.

For all three, the proposed cap grasp is **35–55 mm above the seam**, just past
the end of the hidden sleeve. The body grasp is **12–32 mm below the seam**.
These are editable starting locations, not measured human-fit requirements.
Putting the cap grasp directly over the sleeve could squeeze the mating walls
together; placing it beyond the overlap aims to reduce that unwanted clamping.
The four-corner treatment provides front and back contact without covering the
center faces or requiring a through-hole. The body and cap shoulders in C face
opposite directions: fingers press the cap shoulder upward and the body shoulder
downward. A texture that only runs along the pulling direction would offer less
geometric opposition to slipping.

**Initial recommendation, superseded by the user's B preference: A.** Low rounded ribs are the smallest change
to the existing thin construction and contents space. B is worth considering if
the recessed appearance matters more, but a 0.6 mm depression must not simply be
cut from a 1.2 mm wall: the wall itself needs reshaping inward and contents/guide
clearance needs checking. C offers a clearer pulling surface if shallow texture
feels inadequate, at the cost of a more pronounced shape. None has demonstrated
grip or a force rating; skin friction, wet hands, wall flex and printed texture
remain unknown.

The illustrated amplitudes are starting proposals: A about 0.4 mm raised ribs,
B about 0.6 mm depression, C about 0.8 mm raised shoulder. All assume the existing
0.4 mm nozzle / 0.2 mm layer PETG direction. Any selected concept will need
smooth blends, preserved minimum wall and snap backing, closed and opening-path
clearance, and a support-aware profile in the existing print orientation. No CAD,
mesh, export, slice or physical test was performed for this sketch phase. The
existing source/export pairs and their evidence remain unchanged.

The editable SVGs are the proposal sources; PNGs are previews. This phase is
complete with the visual comparison; concept selection precedes implementation.
The lesson is local and practical: establish where each hand grips and how its
contact opposes the pull before refining the edges of a recess. Existing
[whole-object handling guidance](../../../.codex/skills/cadquery-3d-design/references/design-decisions.md#whole-object-form-and-handling)
already requires this, so no additional shared workflow rule was added.
Attribution is the same Codex/OpenAI agent context recorded below; no subagents
or third-party geometry contributed. These are unprinted rough proposals with
no printable deliverables (test pieces and final objects N/A for this phase).

## Recessed saddle variants

The user explicitly prefers B over the ribs and shoulders and requests several
different suggestions within that recessed family. This selects a direction for
further visual exploration, not a final saddle geometry or CAD implementation.
The earlier A recommendation is historical. The source and print files retain
the current notches while these sketches are discussed.

**[Compare B1, B2 and B3 — SVG](../renders/concepts/grip_b_family_comparison.svg)** ·
[PNG preview](../renders/concepts/grip_b_family_comparison.png)

| Suggestion | Shape and starting size | Why choose it / what it costs |
| --- | --- | --- |
| [B1 — Oval dimples](../renders/concepts/grip_b1_dimples.svg) | Separate 20 × 10 mm oval pockets, about 0.5 mm deep, on front/back faces near the corners; the corner edge remains plain | A subtle outline and small modified area; requires more deliberate finger placement and remains largely a friction grip |
| [B2 — Long corner saddles](../renders/concepts/grip_b2_long_saddles.svg) | A 30 mm long hollow wrapping about 18 mm around each corner, about 0.6 mm deep, with gentle slopes at both ends | More room to settle or shift the fingers, continuous contact around the edge; reshapes a larger region of the shell and interior |
| [B3 — Directional scoops](../renders/concepts/grip_b3_directional_scoops.svg) | A 24 mm long hollow wrapping about 14 mm around the corner, about 0.6 mm deep; a long soft entrance ramp and a shorter rounded wall facing the pull | A more distinct surface to press against while remaining inside the original outline; the stronger directional feel and local pressure are untested |

The sketches share the existing box proportions, closed seam and 30 mm hidden
sleeve. The grasp centers are **50 mm above the seam on the cap** and **27 mm
below on the body**. Centers are held fixed so different saddle lengths can be
compared fairly. Even B2's nearest cap edge starts 35 mm above the seam, beyond
the 30 mm sleeve; the body saddles stop at least 12 mm below the seam. These
are proposed locations, not verified hand-fit criteria.

B3's cap scoop has its shorter pulling wall toward the cap's far end, where a
finger can push it upward; the body scoop is mirrored so a finger can push it
downward. Both directions are drawn. All concepts retain rounded slopes without
an undercut hook, outward tab or through-hole. The surface profiles are enlarged
separately to explain the shapes; use the listed dimensions, not those enlarged
profiles, to compare physical size. End views distinguish face dimples from
continuous corner wraps. Orange pads are schematic contacts; the thin cap's
snap-backing detail is omitted as in the earlier exploration.

**Recommendation within B: B2 as the starting shape.** Its larger landing area
allows more freedom in where the fingers settle, and the gentle corner wrap
keeps the shape continuous. B1 suits a more discreet appearance. B3 is the option
to explore if a distinct pulling wall matters more than a symmetric, gentle
hollow. These are geometric tradeoffs, not measured comfort or opening-force
results; no variant is claimed to grip better in a physical trial.

All three would move the inner wall with the outside depression, preserving
nominal wall thickness (1.2 mm thin main wall, 2 mm control main wall). Simply
cutting these depressions out of the existing thin skin is not the proposal.
The 0.5–0.6 mm inward shift uses local contents space and needs actual wall-offset,
contents, guide-path and print-orientation checks after a shape is selected.
Rounded transitions and self-supporting slopes remain implementation work.

The editable SVGs and PNG previews complete this visual phase. No model Python,
STEP, STL, slices or verification results were changed, and no print was reported.
All proposed dimensions are adjustable; printed feel and performance remain
unknown. Attribution and the N/A printable-deliverable status for the sketch
phase are as recorded in the preceding exploration. No shared workflow or tool
change is warranted by this preference refinement.

## Continuous band and shallow profile

**Selected placement:** [upright/diagonal opening walkthrough](grip_human.md)
uses cap +55 / body −30 mm band centres. Nominal layout checks pass; placement
selection is complete. Earlier +50/−30 and +50/−27 sketches below are historical.
The precise-hand search is retained as an unsuccessful diagnostic, retired as
a placement criterion. Printed traction/feel remains unmeasured. Production
CAD and exports remain unchanged.

The user asks whether a recess can stay shallow and smoothly curved while still
being useful, and whether wrapping it around the entire box would improve use.
This continues the SVG exploration; no CAD edits or notch removal are authorized
for this phase. The finish line is an understandable comparison of coverage,
depth, slope and interior cost, not an asserted minimum usable grip depth.

- [B4 — Full-wrap band versus corner saddles](../renders/concepts/grip_b4_full_band.svg)
  ([PNG](../renders/concepts/grip_b4_full_band.png)): closed-case placement,
  alternative contact positions, sleeve extent and the narrowed wall section.
- [Three shallow profiles at common scales](../renders/concepts/grip_b4_band_profiles.svg)
  ([PNG](../renders/concepts/grip_b4_band_profiles.png)): a very gentle recess,
  a balanced starting profile and a directional variation. Depth is enlarged
  five times relative to the axial scale, explicitly labeled.

**A full band is a plausible improvement in finding the grip.** Fingers could
land on a face, side or corner rather than having to align with separate pockets.
It is still one band on each half, leaving the seam and overlap region separate.
It does not inherently increase traction at a given contact: pinch pressure,
surface friction, finger compliance and the slope the finger presses against
still matter. Grasp alternatives in the drawing are schematic, not anatomical
fit evidence or multiple simultaneous finger loads.

**Recommended starting exploration: 0.7 mm deep and 20 mm wide axially**, within
a provisional 0.6–0.8 mm depth / 18–24 mm width range. G2 uses two 6 mm smooth
ramps and an 8 mm central landing region. G1 is 0.4 mm deep and 28 mm wide with
10 mm ramps: its long gentle slopes provide less geometric opposition to axial
sliding. G3 keeps the 0.7 mm depth and 20 mm overall width but uses a 10 mm
entry, 6 mm landing and 4 mm return in the cap's pulling direction. Its shorter
return makes a more distinct curved surface to press against. Mirror G3 on the
body for the opposite pull. Depth alone cannot determine usefulness.

The proposed blend is a quintic smoothstep, `10u³ − 15u⁴ + 6u⁵`, between flat
regions: both slope and curvature approach zero at the joins. The profile SVG
samples this geometric curve; it is not a contact or grip-force calculation.
Printed stepping and actual touch remain untested, and the proposed dimensions
are not a proven human-feel threshold.

The band would reshape both outer and inner surfaces while preserving nominal
wall thickness. At 0.7 mm inward displacement on both sides, nominal thin main
interior dimensions locally reduce from **71.8 × 48.8 to 70.4 × 47.4 mm**. This
simple flat-wall dimensional screen is not a qualified full corner offset or
simultaneous contents-packing result. Unlike corner-only saddles, a full band
uses interior room along every face and changes the whole shell section.

The full-band sketch keeps the prior cap/body grasp centers at +50/−27 mm from
the seam. A 20 mm cap band begins 40 mm above the seam, beyond the 30 mm sleeve;
the body band ends 17 mm below it. The wide G1 would begin 36 mm above / end
13 mm below, also outside the nominal overlap. This avoids deliberately placing
the pinch over mating walls, but does not prove that elastic deformation cannot
affect fit or release. Contents passage, constant-thickness corner construction,
wall flex and support-aware slopes remain checks for a selected CAD revision.

The SVGs are editable proposal sources, with visually reviewed PNG previews.
CAD, STEP, STL and existing verification evidence are unchanged. No slice, solver
or physical trial was performed; print-test and final-object deliverables are
N/A for this sketch phase. Existing attribution applies. This is a local grip
design question and adds no shared workflow rule or universal minimum depth.

## Print and compare

Use the same filament and settings for both versions. The exported body stands
on its bottom; the cap stands on its roof. Heights are 204 and 90 mm. Keep that
placement and the diagnostic profile's automatic brim for the tall body. Both
parts fit the selected Q2C layout. The R4 tangent feet and pad tapers were reviewed
for this orientation; the selected support probe generated no supports. The
1.2 mm floor/roof are layers across a closed end, not three horizontal wall lines.
Fit gaps, seams, shrinkage and layer adhesion still depend on the actual printer.
The CLI smoke slice used STL; it does not verify Orca's separate GUI STEP importer.

Compare how the broad walls feel in the hand, whether both bites return after
opening, and whether closing/rubbing/noise are acceptable. Inspect for whitening
or cracks around the pockets. Try the real packed items and ordinary handling.
This direct comparison can decide whether the saved material is worthwhile;
there is no new computational campaign queued before printing. Resistance to
travel-bag knocks and long-term closure life remain physical questions.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | No additional coupon; user requested full cases | Cap-only selection is available in each paired export |
| Final printable object(s) | Unknown | `short_lap_case.step/.stl`, `short_lap_case_three_line.step/.stl` | No print report for these pairs; compare feel, fit, snap return, packed retention and wear |

## Handoff lesson and attribution

Actual toolpaths answered the thickness question directly: three configured wall
loops produced five total strokes in the control shell, while the thin shell
produced three. The catch recess required a local backing decision; it did not
justify keeping every wall thick. This evidence stays local to this geometry and
profile; it does not establish a universal minimum PETG wall or a new mandatory
solver/check workflow. Earlier practical stopping and explanation lessons remain
in [their existing owning records](short_lap.md#practical-stopping-and-explanation-feedback).

Primary language model: GPT-6 (exact runtime model variant and reasoning effort
not exposed). Harness: Codex agent, shared local repository; provider: OpenAI.
No subagents contributed to this comparison. Historical model attribution remains
in [short_lap.md](short_lap.md#attribution). Existing Orca process profile attribution
and AGPL-3.0 licensing remain in [profiles](short_lap/profiles/ATTRIBUTION.md);
no third-party geometry was added.
