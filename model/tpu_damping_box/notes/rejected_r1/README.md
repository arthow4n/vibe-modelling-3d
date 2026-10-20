# Rejected R1 support batch — historical evidence

The user rejected this batch before printing because walls disappeared in their slice.
The old custom profiles below are not current print instructions. [Current R2 record](../../README.md#ordinary-classic-repair--r2).
Original source and exports are pinned to commit `8f1e611`; R1 native/custom-profile receipts remain beside this file.

## Four printable support pairs — 2026-10-20

The user accepts A/B's visual explanations, requests complete inserts **with
matching lid pads and permanent markings**, and selects A at 1.6/2.0 mm and B at
1.6 mm with two distinctly different tie sizes. Spoken “16 / 20” means
**1.6 / 2.0 mm** in the S16 context. Tie dimensions are delegated engineering
choices. All sets reuse the existing rigid experiment body, lid and fasteners;
no replacement rigid box is needed.
The user reiterates **no Arachne** during implementation: Classic is a requirement
for all four delivered experiments, not a fallback preference.

| ID | Nominal lining | Support geometry | Primary STEP | Matching STL / Python |
| --- | --- | --- | --- | --- |
| **A16** | **1.6 mm** | 0.3 mm skins/parallel rails, 0.6 mm cross-links, 0.4 mm square openings | [A16 pair](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_A16.step) | [STL](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_A16.stl) · [Python](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_A16.py) |
| **A20** | **2.0 mm** | Same rail/link widths, 0.8 mm square openings | [A20 pair](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_A20.step) | [STL](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_A20.stl) · [Python](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_A20.py) |
| **B08** | **1.6 mm** | 0.8 × 0.8 mm ties across a 0.8 mm gap | [B08 pair](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_B08.step) | [STL](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_B08.stl) · [Python](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_B08.py) |
| **B16** | **1.6 mm** | 1.6 × 1.6 mm ties across the same 0.8 mm gap | [B16 pair](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_B16.step) | [STL](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_B16.stl) · [Python](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_B16.py) |

Each file contains **one cup and its matching lid pad**, both backing down;
keep the positions/orientation when importing. Labels are recessed **0.2 mm**
into the shell-facing underside, using 12 mm bold monospaced text (over 8 mm
actual capital height). They leave 0.2 mm continuous cup backing beneath the
recess and 0.4 mm pad backing. Both contact surfaces stay flat. B08/B16 name
the **tie size**, not their total thickness.

### Dimensions, support choices and print setup

All cups keep the established **34 × 34 × 34 mm** external envelope and
**0.2 mm per-side clearance** inside the existing shell. Nominal clear cavities
are **30.8 mm cube** for A16/B08/B16 and **30.0 mm cube** for A20. The thicker
A20 therefore changes nut travel too; the shake comparison is not an isolated
material-property measurement. Pads have **0.2 mm per-side pocket clearance**:
33.0 mm square for A, 32.8 mm for B.

The stated lining thickness is the installed geometric sandwich. Pads include
an extra **0.2 mm axial squeeze allowance**, giving printed pad thicknesses
**1.8 mm / 2.2 mm**, with their shell-facing backing 0.6 mm thick. This replaces
S16's historical 0.1 mm pad allowance with one whole 0.2 mm layer; squeeze force
is uncalibrated. Cup pad-seat height is 32.4 mm for the 1.6 mm sets and 32.0 mm
for A20. Existing rigid rim stops still set the closed box height.

**A:** four 0.4 mm lines across a 1.6 mm wall would leave no opening inside the
square. Therefore both A variants use **0.3 mm upright skins and parallel rails**:
between frames, the skin/core/skin is 0.3 / 1.0 / 0.3 mm (A16) or
0.3 / 1.4 / 0.3 mm (A20); alongside each frame rail, each skin locally becomes
0.6 mm. Frames repeat at **4.4 mm pitch** and have square openings 0.4/0.8 mm.
Their **cross-links are 0.6 mm wide**, giving rectangular outside sections
**1.0 × 1.6 mm / 1.4 × 2.0 mm**. Classic omitted A16's original 0.3 mm and
trial 0.4 mm cross-links while retaining apparently plausible rails alongside
both skins. Widening those links to 0.6 mm restores the actual cross-gap paths;
the final path check explicitly covers them on all four walls. Both A variants
use the same link width. The square-opening frame intent is preserved, but
the outside of the upright frame differs from the original square schematic.
This remains an experiment with single-path skins/rails, not an already stronger
S16. Narrow supplemental gap-fill paths are not counted as replacement skins.

A's horizontal skins stay **0.4 mm / two layers**. Their hidden frame rails
are **0.2 mm tall** to match the layer grid, with 0.3 mm cross-web widths and
the same 0.4/0.8 mm square air openings in a vertical section. These bottom/pad
frames have rectangular outside sections because vertical and horizontal line
dimensions differ. Both wall and floor frame openings remain square. The floor
supports continue along Y; upper skins bridge across X.

**B:** both skins stay **0.4 mm** and the gap **0.8 mm**. At the same 4.4 mm
pitch in wall length and height, ties have either 0.8 × 0.8 or 1.6 × 1.6 mm
attachment faces, hence **four times the nominal attachment area** in B16.
Their centres are identical, so larger ties also reduce the clear spacing from
3.6 to 2.8 mm. Each tie spans the gap but is separate from the ties above/beside
it. The bottom/pad uses spaced square posts with the same footprint sizes.
First-row centres are 3.2 mm above the bed, then every 4.4 mm: their undersides
are intentional bridges anchored on the two wall skins. This compares support
amount, bond area and span together; it is not a strength prediction.

Use **TPU, 0.4 mm nozzle, 0.2 mm layers including the first, Classic**,
100% rectilinear material fill, and **supports off**.
The CAD air cores remain empty; material fill does not fill those voids. Use
the same spool for all comparisons. Supplied processes:
[A](../../profiles/rejected_r1/tpu-support-a-process.json), [B](../../profiles/rejected_r1/tpu-support-b-process.json),
with the existing [TPU filament](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/profiles/tpu95a.json) and
[Q2C printer](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json).
A uses 0.3 mm nominal wall/solid widths (0.4 mm first-layer width); B uses
0.4 mm. A requests two perimeter loops; B requests **one perimeter plus solid
material fill** inside thicker regions. The initial two-loop B16 slice left a
0.086 mm unfilled slit through the tie centre because opposing inner perimeters
did not meet. Removing the second loop lets solid paths join across that region;
thin skins still use their single perimeter. Gap-fill filtering is disabled for
B; gap-fill filtering is also disabled for A. This B process change applies to
both tie sizes and keeps Classic throughout.
Both use thin bridges, 25 mm/s wall/material limits, 15 mm/s bridges,
no seam gap, no brim and no ironing. Ironing is omitted to focus this phase on
support integrity. B uses automatic bridge directions so all four wall normals
can be bridged; A retains X-directed floor/pad bridges. The 9 mm³/s filament cap
remains a preset limit, not measured attainable flow.

Do not combine A and B under one unchanged process. The two A files can share
the A process and the two B files the B process; the delivered individual layouts
own the smoke-slice evidence. The presets are inspectable experiment settings,
not recovered settings for the earlier damaged dental print.

### Verification and useful comparison

[Parametric builders](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/support_design.py) keep the existing fit interface, core
patterns and placements together. Native CadQuery assemblies name each printed
part. Existing shape/witness checks remain adequate for the straight insertion
path, so the optional assembly-snapshot API is not added. Square bed edges and
contact/rim edges deliberately preserve thin skin sections and the established
fit; the 0.4 mm top core cap closes the wall gap beneath the pad seat.

CAD checks cover the shell and pad installation path, all six contact skins,
outer skins, empty cavities, label recesses/backing, open frame interiors,
separation of B ties in height, posts, between-support channels and corner air
regions. An initial frame builder used overlapping, unfused rail boxes as boolean
cutters; despite an apparently valid cleaned final shape, these intent checks
found false material and missing skins. Frames are now constructed as single
closed rings before core subtraction. This is why CAD validity alone is not the
acceptance criterion for these experiments.

Final native receipts: [A16](support_A16_final.json),
[A20](support_A20_final.json), [B08](support_B08_final.json),
[B16](support_B16_final.json). All four final pairs are valid CAD with
successful matched STEP/STL exports and completed **OrcaSlicer 2.4.2 / Classic**
slices under the supplied profiles and default whole-layout centering.
The [path review](support_path_review.json) associates current builders,
profiles, shared path reader, exports and G-code, and checks all four wall faces,
frame cross-links/openings, B tie presence/absence, horizontal air/roof coverage,
corner gaps and bridge metadata heights (at most 0.2 mm). Its declared 0.06 mm
local path-rounding allowance is an engineering screen, not a printed tolerance.

![Actual label and support paths](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/renders/support_path_review.png)

The slice receipts retain **review_required=true**: all four report internal
floating regions and the automatic-support probes generate proposals. The
[headless probe view](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/renders/support_probe_review.png) places the ordinary
proposals beneath floor/pad roofs in enclosed cores (the three 1.6 mm cup
floors at Z 1.0 mm; pads at Z 1.0–1.2 mm, or 1.2–1.6 mm for A20). A20's cup
proposals span Z 0.8–31.4 mm and include the upright frame channels below their
top caps. These regions
are not accessible for removal. The supplied print process leaves supports
**off**, retaining the intentional bridge experiment; the warnings are not
removed or recategorized as physical success. CAD provides anchors on both
ends of the panel roofs, frame closures and short B ties; actual TPU sag/bonding
is still unqualified. STL slicing also does not verify Orca GUI STEP import.

![Display-only cutaways, left to right A16, A20, B08, B16](https://github.com/arthow4n/vibe-modelling-3d/blob/8f1e611/model/tpu_damping_box/renders/assembled/support_inspection_isometric.png)

The B08 section review exposed a numerical-reader boundary: after recentering
and rotating bed coordinates, an exactly tangent 0.4 mm path could fall about
1e-14 mm outside a strict bounding comparison. The shared reader now applies
its existing 1e-10 mm interval tolerance consistently to those comparisons.
Its nine focused tests pass, including translated tangency and a genuinely
separated negative control; this numerical tolerance does not fill real gaps
or explain away the earlier 0.086 mm B16 defect. Geometry and slices did not
need changing for this reader correction.

Verification receipts: [A16](support_verification_A16.json),
[A20](support_verification_A20.json), [B08](support_verification_B08.json),
[B16](support_verification_B16.json). Run the shared contract, e.g.
`./execute.py model/tpu_damping_box/verification.py --variant A16`.
CAD/path/Classic questions are separate from physical installation/damping
questions; unresolved physical and separate finish-study coverage remains UNKNOWN.
Existing requirement IDs/provenance are preserved, with the four-pair and
Classic instructions added to the shared intent inventory.

Physical comparison should first check **as-printed inner/outer skin continuity,
corners, floor junctions, label readability and bridge bonding**, then gently
insert/remove each complete cup and matching pad in the same shell. Record any
new tears, layer splits, skin/tie detachment or loss of shape, and when they first
appear. A pair with damage is rejected for application transfer even if it feels
quiet. If intact, use the same nut, grip and repeatable gentle/firmer X/Y/Z shake
motions against the printed S16 reference; record sharp ticks, bottoming and
recovery as well as overall quietness. Reuse the existing screws/nuts and tighten
only to seat the rigid rim; do not force an unexpectedly resistant insert.

These complete small inserts preserve the fixture fit, wall height, floor/wall
junctions, restraint and assembly handling that flat coupons omit. They are the
requested economical integrated test; neither more CAD nor a flat coupon can
establish installation survival or subjective damping. A promising result selects
a support architecture/thickness for further development, not a universal minimum
or automatic approval of the much taller dental liner. Exact spool properties,
printed gaps, insertion forces, long-term fatigue and dental-scale transfer remain
unknown. F0–F7 surface-finish coverage remains separate and untested.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Four complete support-test pairs | No — rejected before printing, 2026-10-20 | `support_A16`, `support_A20`, `support_B08`, `support_B16`, each `.py/.step/.stl` | User reports missing sliced wall paths for all four and declines printing. Ordinary Classic compatibility not accepted. Earlier custom-profile evidence remains narrow; physical behavior untested. |
| Final application liner | N/A — experiment phase | None new | Existing dental failure remains unresolved; no transfer approval |
