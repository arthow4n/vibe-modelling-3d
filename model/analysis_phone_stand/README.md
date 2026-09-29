# Physical-analysis phone stand

A complete four-part, press-to-release phone-stand prototype used to develop and
exercise the repository's [physical-analysis API](../../physical_analysis/README.md).
Designed around a **300 g phone, up to 90 × 180 × 14 mm**, at **45°, 60° or 75°**.
The source, matching exports and numerical evidence are complete. Physical fit,
creep, spring recovery and durability remain untested; this is not a tablet rating.

![Assembly with display-only phone envelope](renders/assembled/stand_in_use.png)

## Files and printing

Use [analysis_phone_stand.step](analysis_phone_stand.step) as the primary complete
print layout, or the matching [STL](analysis_phone_stand.stl). Preserve the supplied
part orientations. STEP contains four separate solids; split them into objects
only if needed for individual settings, then preserve their orientations.

| Part | Editable entry point | STEP | STL | Orientation |
| --- | --- | --- | --- | --- |
| Base | [stand_base.py](stand_base.py) | [STEP](stand_base.step) | [STL](stand_base.stl) | Broad base down |
| Toothed support arm | [stand_arm.py](stand_arm.py) | [STEP](stand_arm.step) | [STL](stand_arm.stl) | Broad side down; pivot bore vertical |
| Phone cradle | [stand_cradle.py](stand_cradle.py) | [STEP](stand_cradle.step) | [STL](stand_cradle.stl) | Upright on the seat/bottom edge |
| Spring catch | [stand_latch.py](stand_latch.py) | [STEP](stand_latch.step) | [STL](stand_latch.stl) | Flat underside down |

The shared dimensions/builders live in [components.py](components.py); the complete
layout is [analysis_phone_stand.py](analysis_phone_stand.py).
[inspect_assembled.py](inspect_assembled.py) is an inspection pose, not a print layout.

Print **PETG, 0.4 mm nozzle, 0.2 mm layers, two walls, 100% rectilinear infill**.
Solid infill deliberately replaces the usual 7% starting point so the homogeneous
solid analysis has a useful physical counterpart. Use calibrated filament settings.
The retained [process profile](notes/solid-petg-process.json) and Generic PETG
reference filament used 250°C after the first layer, 245°C initially and an 80°C bed;
these temperatures are reference evidence, not a filament calibration.

OrcaSlicer 2.4.2 accepted the full layout and every individual export on its Qidi
Q2C 0.4 mm profile: **no notices, no automatic supports generated**, with auto-brim
available. See [slice evidence](notes/slices.json). The upright cradle avoids an
unsupported retaining lip; the spring bends along its printed layers. The base's
teardrop pivot roofs and short screw-hole bridges require no supports in this
profile. Edge radii soften the cradle, tab and tooth roots. Actual bridge quality,
layer bonding and fit still need a print. The STL smoke checks do not validate
Orca's separate GUI STEP importer.

## Hardware and assembly

Supply one **M4 × 35 mm socket-head bolt**, one M4 nyloc nut and two M4 washers;
four **M3 × 16 mm countersunk screws**, four M3 nuts and four M3 washers. Nominal
socket tools are 3 mm for the M4 bolt and 2 mm for M3 countersunk socket screws,
plus 7 mm and 5.5 mm nut tools. Check the drive type of the hardware you buy.

1. Insert two M3 screws upward through the base's countersunk underside holes.
   Set the catch on the raised rear mounting pad, with its tooth and broad thumb
   tab pointing toward the front. Add washers and nuts above the catch root.
2. Attach the cradle to the arm using the other two M3 screws from the phone side.
   Their heads must sit flush in the cradle countersinks; washers and nuts go on
   the arm's rear face. Snug the connection without crushing the PETG.
3. Put the toothed arm between the base cheeks and insert the M4 pivot bolt with
   washers outside the cheeks. Retain it with the nyloc nut while leaving the arm
   free to rotate. The design has 0.4 mm axial clearance per side and 4.5 mm bores.
4. Support the cradle by hand, press the front tab down to its stop, set the angle,
   and release the tab into a tooth valley. Use the 45–75° range; valleys are
   spaced 15° apart. Verify engagement before letting go.

**Press, adjust, release.** Do not force the teeth over the catch. Remove the phone
or support its weight while adjusting. The cradle has an 8 mm retaining lip and
an open 20 mm cable notch. The phone lifts out upward along the cradle; it is a
gravity holder, not a clamp for carrying the device around.

## Numerical evidence and its limits

[Current verification summary](notes/verification.json),
[geometry/use checks](notes/geometry.json), and [analysis consumer](analyze.py).

| Question | Conditional prediction | Scope |
| --- | --- | --- |
| Thumb release | 6.49 N at 4.7 mm travel; least sampled tooth clearance travel 2.20 mm | E = 1200 MPa; front-edge press; idealized clamped root |
| Holding contact | Checked to 22.70 N versus 14.64 N service demand; maximum penetration 0.0017 mm | E = 800 MPa; local tangential translation of an actual tooth patch; frictionless |
| Arm/cradle bending | 0.86 mm maximum displacement; 0.37% peak strain | 300 g phone plus conservative 100 g moving-part allowance; E = 800 MPa |
| Release strain screen | 1.40% on the finer mesh versus an assumed 1.5% limit | Local peak remains mesh sensitive; not a converged yielding prediction |
| Hardware bearing screen | 0.77 MPa at the pivot, 2.24 MPa at cradle bolts | Conservative projected areas versus an assumed 7 MPa allowance |

![Predicted release and holding curves](renders/analysis/force_curves.png)

Release force changed 0.07% between 1.5 and 1.1 mm meshes. Holding force changed
0.35% when refining from 2.5 to 1.8 mm and doubling the penalty stiffness.
**Peak strain did not meet the 5% refinement criterion**: it changed about 21%
for release and 8% for holding. The high release value lies near the idealized
clamp edge. Neither the assumed limit nor this elastic material law establishes
permanent set, layer failure, fatigue or long-term PETG creep.

The structure case treats the bolted arm/cradle interface as bonded and fixes a
cut at the gear sector; its displacement excludes hinge play, catch rotation and
joint slip. Contact uses a short straight tangential path, not a complete rotating
assembly solve. The checked force/service ratio of 1.55 is not a certified safety
factor. The moving CAD material volume corresponds to about 87 g at an assumed
1.27 g/cm³, below the 100 g load allowance. The phone centre has an 18.5 mm rear
footprint margin at 45°, before counting stabilizing base weight. A lateral bump,
a shifted phone or a cable pull is outside that static screen.

The full geometry check found no unintended component overlaps at the three
locked poses; arm/base and cradle/base motion was sampled every 2° over 45–75°.
The device envelope seats and lifts out. These geometric checks do not simulate
elastic release or continuous contact.

### What using the API changed

The model exposed an offset-tab twisting problem, a need for feature-specific
motion observations, a misleading total-reaction/actuation-force distinction,
an ignored solver parameter and slow tensor post-processing. Those led to API
fixes and numerical regressions. The catch acquired a wider root and a positive
thumb stop: the retained [overtravel result](notes/analysis/release_overtravel_rejected/result.json)
exceeded the provisional strain limit at 5.3 mm travel.

A [sharp-tooth pass-over experiment](notes/analysis/pass_over_rejected/result.json)
on an earlier fixture failed to converge. It remains explicitly rejected; the
operating design uses deliberate release. All 19 repository tests passed, including solver-backed regression cases.
The supported foundation now covers
loaded solids, prescribed flexure deformation, smooth contact and this local
holding-contact experiment. General rotating multipart mechanisms, friction,
plastic deformation and durability need further backends or validated extensions.

### Reproduce

From the repository root, after the [analysis runtime setup](../../physical_analysis/README.md#setup):

```sh
uv run --locked python model/analysis_phone_stand/analyze.py release /tmp/release_new --mesh 1.1
uv run --locked python model/analysis_phone_stand/analyze.py holding /tmp/holding_new --mesh 1.8 --modulus 800 --penalty 120000
uv run --locked python model/analysis_phone_stand/analyze.py structure /tmp/structure_new --mesh 2.3 --modulus 800
uv run --locked python model/analysis_phone_stand/verify.py
uv run --locked pytest -q
```

Run directories must be new. [Retained cases](notes/analysis/) contain compact
results, parameters, compressed solver input and logs, and increment records.
Decompress a case's `analysis.inp.gz` into a fresh directory and run `ccx -i analysis`
to replay its exact finite-element input. Geometry BREP snapshots and large raw
result fields are not committed; `analyze.py` rebuilds them from current source.
The rejected pass-over deck preserves its earlier geometry independently.
[evidence.py](evidence.py) retains a run, [summarize_evidence.py](summarize_evidence.py)
compares completed evidence, and [plot_evidence.py](plot_evidence.py) rebuilds views.

## First physical trial and print status

The complete stand is the trial; no separate coupon is supplied. First check free
pivot motion and repeated unloaded release/return, then use a supported 300 g
surrogate before putting a phone on it. Report whether the catch fully returns,
holds each angle, takes a permanent set, or drifts under an hour-long load. Record
material, print settings, orientation and actual release effort if measurable.
Check that countersunk heads are flush and the cradle joint does not slip.
If the catch binds, diagnose the contact before changing thickness: thickness
changes both force and strain. Physical feedback is needed before a load claim.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None; full stand is the trial | No separate coupon phase |
| Final printable object(s) | Unknown | `analysis_phone_stand.step/.stl`, `stand_base`, `stand_arm`, `stand_cradle`, `stand_latch` STEP/STL pairs | No print report; fit, release, recovery, holding, creep and durability untested |

## Attribution

Primary model: GPT-6 in the Codex agent environment. The user identified the model
as **GPT-6 Astra with low reasoning effort**; the exact runtime variant and effort
are not independently exposed. Harness: Codex via API. Provider: OpenAI.
No sub-agents contributed. Geometry and analysis integration are repository-owned
work under the root MIT licence. CalculiX and Gmsh remain separately licensed
external dependencies; no solver binaries are included.
