# S16 damping liner for the printed sunglasses case

The **revised curved-corner liner** uses three air pockets around each rounded
bend, in addition to the straight-wall channels. Print
[sunglasses_case_liner.step](sunglasses_case_liner.step), or its matching
[STL](sunglasses_case_liner.stl). The plate contains **two identical TPU cups**,
one for each half of the already printed [accepted E case](../sunglasses_case/notes/printing_and_design.md).
[Print entry](sunglasses_case_liner.py) · [Parametric builder](design.py).

![Retained solid corner left; current revised corner right](renders/corner_study/corner_study_top.png)

## Intent

User instructions, 2026-10-16: S16 and S12 were both printed and work; S16 is
preferred over S12/I22 and feels good compared with I30/original 4 mm I. Record
that preference and a reusable lesson, then adapt S16 to the already printed
sunglasses case, which the user confirms has enough interior room. The
[original physical report](../tpu_damping_box/README.md#s16--s12-print-feedback--2026-10-16)
qualifies the sample profile, not this new accessory's fit or quietness.

The user then held off before printing after noticing the solid corners, asked
for investigation, and explicitly authorized updating the model and recording
that **future adaptations must check corners**. The current revision implements
that correction. The accepted rigid case and its source/exports are unchanged.

## Geometry and adaptation

Target cavity: **158 × 78 × 63 mm**, 7 mm inner corner radius. Each cup remains
**157.6 × 77.6 × 30.8 mm**, with a 6.8 mm outer corner radius and 0.2 mm nominal
allowance per side. The correction removes material only inside the corner cores;
it preserves the installed envelope, opening and shell clearances.

| Feature | Dimension |
| --- | --- |
| Shell-side backing / air core / contents-side skin | 0.4 / 0.8 / 0.4 mm |
| Total floor and wall sandwich | 1.6 mm |
| Straight ribs / pitch / nominal open channel | 0.9 / 4.4 / 3.5 mm |
| Corner pockets | Three curved vertical pockets per bend; 12 per cup |
| Corner ribs | Radial, minimum nominal 0.9 mm chord at the inner core radius |
| Corner sector pitch | 30°, about 3.14 mm along the core centreline |
| Solid top closure of wall channels | 0.4 mm |
| Rounded opening edges | 0.2 mm radius |

Floor ribs run along the short direction; first-skin bridges cross them.
Wall and corner ribs run vertically. Both skins remain continuous through the
rounded bends. The floor/wall junction, short pattern remainders, rib roots and
top cap remain solid locally. There is no claim of identical compliance at every
point or calibrated acoustic transfer from the S16 sample. No labels cut the
thin skins; the two inserts are interchangeable.

Each backing reserves **0.2 mm** for tape against the rigid panel. Each cup ends
**0.5 mm below the rigid mating rim**, leaving **1 mm between liner rims** when
closed. This narrow seam band remains unlined to avoid pinching. The remaining
rounded interior is nominally **154.4 × 74.4 × 59.4 mm**, including the tape
allowance. This is available geometry, not a measured glasses envelope.

## 20 mm bottom-panel sample — ironing comparison

User-requested test piece: [bottom_sample.step](bottom_sample.step) ·
[matching STL](bottom_sample.stl) · [source](bottom_sample.py).
This is a **20 × 20 × 1.6 mm** crop from the centre of the actual liner bottom,
with the same **0.4 mm backing / 0.8 mm ribbed air core / 0.4 mm contact skin**.
It includes the full bottom-panel sandwich, rather than just the first print
layer. Backing faces the bed; the glasses-contact skin faces upward for ironing.
No labels, added edge frame, side walls or corner geometry change the test area.
Cut edges expose the channels so their condition can also be inspected.

Print the **same file twice**, using the liner's [TPU print setup](#printing-and-manufacturing-review)
and supplied unrotated orientation. Keep material, plate, temperatures,
flow and other process settings the same. Use ironing **off** for one print
and ironing on the **top surface** for the other, using the ironing settings you
want to assess. Mark which is which after removal rather than changing the CAD
surface. The supplied reference smoke slice is the **ironing-off baseline**;
it does not select or qualify ironing temperature, flow, speed or spacing.
Ironing evaluates the upward contact face; the bed-facing underside's texture
is a separate observation.

After cooling, compare the central top area's visible lines, smoothness, ridges,
flatness and any nozzle drag. Check the exposed channel edges for sag/fusion and
whether the top skin remains intact. Prefer the finish you find better only if
it preserves the sandwich; a smoother but damaged/fused skin calls for adjusting
or omitting ironing before using it on the full liner. No printed comparison has
been reported yet. This coupon omits corners, walls, adhesion, glasses fit and
full-panel toolpath length/cooling; it qualifies a small flat surface comparison,
not complete-box damping or necessarily the full panel's finish.

[Native sample receipt](notes/bottom_sample_final.json) covers source association,
paired exports and reference slicing. [Local path review](notes/bottom_sample_paths.json)
checks the retained channels, substantial rib tracks and transverse first contact
skin. The sample deliberately keeps the cut edges sharp in CAD to preserve the
exact crop; it lies flat on its full backing, and its only short unsupported
features are the existing channel roofs and short cut-edge skin overhangs.

Baseline review: valid CAD and paired STEP/STL exports; OrcaSlicer **2.4.2**,
supplied TPU triplet, centred without rotation, **no keyword notices**, ironing
off. Estimated **0.54 g / 10 min 16 s** per sample, not measured. The local path
check passed **12 open-channel samples**, **9 rib sections** with at least two
substantial tracks, and the first contact-skin bridge direction. The automatic
probe proposes support in the shallow channels at **Z 0.8–1.0 mm**; primary
supports remain off, with the native `review_required` signal retained. These
short roofs reproduce the liner's supported 3.5 mm spans; the cropped edge has
only a short remaining skin projection. Trapped support would defeat the air
channels. Printed sag and ironing quality remain unknown. STL slicing does not
verify GUI STEP import. The full liner's existing geometry and exports are
unchanged by this added sample.

## Installation

1. Print the supplied layout, backing down and openings up. Remove strings and
   clean the contact faces before placing glasses inside.
2. Dry-fit each cup in an open half. It should seat without buckling and stay
   below the rigid rim.
3. Use small strips of **thin removable double-sided tape, at most 0.2 mm total
   installed thickness**, under the flat backing, particularly for the lid cup.
   Start near the perimeter; avoid thick foam tape and adhesive in the channels.
   Select tape compatible with the actual TPU/shell; adhesion is untested.
   The design does not rely on an unqualified friction fit.
4. Close the empty box gently and check the latch. Then check the actual glasses
   for clearance and compare contact noise. Check that the lid insert stays in
   place after repeated opening. No case reprint or new fasteners are needed.

## Printing and manufacturing review

Use TPU (Generic 95A is the reference assumption), **0.4 mm nozzle, 0.10 mm layers
including first layer, Arachne, two requested walls**, 100% material fill.
The channels are CAD voids. Reuse the S16 reference
[process](../tpu_damping_box/profiles/tpu-closed-process.json),
[filament](../tpu_damping_box/profiles/tpu95a.json) and
[Q2C printer](../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json).
The successful sample's actual settings and TPU brand/hardness were not reported;
these profiles are diagnostic references, not recovered settings or calibration.

Keep **supports off**, both thick bridge options **off**, bridge directions
**180°**, and the supplied unrotated layout. Each 0.4 mm vertical skin is
intentionally one bead; the ribs need multiple substantial paths. Horizontal
skins have four 0.1 mm layers. The floor roofs span at most 3.5 mm between ribs;
wall and curved-corner cap regions bridge the narrow 0.8 mm core with support
from adjacent ribs/skins. Trapped support would be inaccessible. The primary
unsupported slice and automatic probe are reviewed separately; physical sag,
spreading and channel survival remain unknown.

The **157.6 × 161.2 × 30.8 mm** layout, including 6 mm between cups, fits the Q2C
270 × 270 × 256 mm envelope. Broad uninterrupted bottom skins give bed contact
and flat tape backing. Rounded opening edges and corners retain the accepted
outline. Vertical ribs grow from the existing floor/wall junction; the corner
change introduces no detached wall starts.

## Verification

[Product verification](verification.py) uses the shared CLI with explicit
`s16-retrofit` selection. [Current receipt](notes/verification.json) distinguishes
CAD coverage from actual fit, adhesion, glasses clearance and subjective
quietness, which remain physical/subjective **UNKNOWN** until reported.
[Checks](checks.py) cover profile, connected cup, residual cavity, installation,
closed fit, sampled opening and the new corner obligation. The original solid
corners must fail the same coverage checker; a shifted insert must fail the
shell collision criterion. Hinge travel is sampled every 10° and insertion at
0, 0.5, 5, 20 and 35 mm above seating; these are sampled rigid checks.

Corner CAD witnesses check air at 15°, 45° and 75° at three heights in each bend
(**36 air and 72 skin locations**), plus **24 radial-rib locations**. The retained
solid-corner baseline is a negative control. [Corner comparison](corner_study.py)
now uses these same production builders; [native view receipt](notes/corner_view.json).
No duplicated experimental corner builder selects the printable geometry.

[Final evaluator receipt](notes/final_review.json) owns final source association,
paired exports, tool identities, profile selection, placement and slice status.
[Path receipt](notes/path_review.json), [floor/support preview](renders/path_review.png)
and [corner paths](renders/corner_paths.png) cover straight and radial sections,
multiple rib tracks, first corner caps, floor bridges and bridge extrusion height.
These are slicer metadata, not measured deposited polymer. STL slicing does not
verify Orca GUI STEP import or physical damping.

Current checks: profile, corner coverage (including the solid-corner negative
control), nominal fit and sampled motion all **PASS**. Physical use and quietness
remain **UNKNOWN**. The final native evaluator reports valid geometry and
successful matching STEP/STL exports. OrcaSlicer **2.4.2**, supplied TPU triplet,
centred compound without rotation: slice completed with **no keyword notices**.
Diagnostic batch estimate: **63.95 g / 28 h 10 min 4 s**, not measured.

The revised slice retains **72 corner air-gap sections**, minimum **0.782 mm**,
**48 corner rib sections** with at least two substantial tracks, and **24 first
corner-cap sections** at Z 30.5 mm. Existing straight-region checks also pass:
18 floor-channel samples, 48 wall-gap sections (minimum 0.799 mm) and 30 rib
sections with at least two tracks. Bridge extrusion height is 0.10 mm. The
reviewed corner preview shows the separate curved skins, radial rib joins and
cap coverage. These local witnesses do not guarantee deposited gap survival.

The automatic probe still proposes trapped support interfaces only in the floor
channels at **Z 0.8–1.0 mm**, with none proposed at the new corner caps. The
primary slice keeps supports **off**: floor bridges cross the 3.5 mm inter-rib
gaps, and the new cap paths close the narrow curved core. The native
`review_required` signal is retained with this reviewed rationale, rather than
being relabeled as unconditional print qualification. Actual bridging needs a
print report.

Reproduce from the repository root:

```sh
./execute.py --threads 1 model/sunglasses_case_liner/verification.py --variant s16-retrofit
./evaluate_model.py model/sunglasses_case_liner/sunglasses_case_liner.py --views none --slice --slice-keep-run --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json --slice-process model/tpu_damping_box/profiles/tpu-closed-process.json --slice-filament model/tpu_damping_box/profiles/tpu95a.json --report model/sunglasses_case_liner/notes/final_review.json
./execute.py model/sunglasses_case_liner/review_paths.py
```

## Corner coverage investigation — 2026-10-16

The first liner (`60784df`) had hollow straight walls but solid rounded bends.
The user's preprint concern led to the curved-core study (`ab43b48`). The
[original corner FAIL](notes/corner_coverage_solid.json) and
[initial CAD study](notes/corner_study.json) are retained as historical evidence;
that study's `production_files_changed=false` describes the exploration phase.
The user then authorized incorporating the curved core into the printable model.
The previous successful straight-wall slice did not qualify corner coverage.

Solid corners remove air-core deflection space at diagonal contacts. This does
not establish zero damping in solid TPU or quantify acoustic improvement. Future
S16 transfers must check all distinct contact regions, particularly curved
corners, in both CAD and sliced paths. Sample approval alone cannot qualify a
larger liner's complete coverage. This lesson is recorded in
[print planning](../../.codex/skills/cadquery-3d-design/references/print-planning.md#functional-process-co-design)
and the [reusable evidence index](../../.codex/skills/cadquery-3d-design/references/reusable-model-lessons.md).

## Print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | Unknown — no bottom-sample print report | `bottom_sample.step/.stl`; 20 × 20 × 1.6 mm | Requested ironing off/on surface comparison; no result yet. Original approved S16 samples remain scoped to the damping-box fixture. |
| Final printable object(s) | No — user reported holding off before correction | Revised `sunglasses_case_liner.step/.stl` | Curved-core correction requested; actual fit, adhesion, quietness, skin integrity and wear remain untested. Existing rigid case is printed and accepted. |

## Attribution

Primary language model: GPT-6-based Codex; exact model variant and reasoning effort
not exposed. Harness: Codex shared-workspace API agent. Provider: OpenAI. No
subagents. Uses the existing accepted E case and user-approved S16 profile;
their historical attribution remains in their respective records.
