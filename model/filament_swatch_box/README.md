# Twenty-swatch archive box

A two-piece PETG tray with a removable sliding lid and an integral printed snap
on the lid. The rounded head passes the body's rounded catch during the last
8 mm of closure, then relaxes behind it. Pulling the lid reverses that operation.
The guides resist lifting; the snap provides a light sliding detent. Intended
for ordinary archive storage, with no transport, drop or sealing qualification.

Print the complete box as the first functional experiment. No separate coupon
is needed for the remaining fit, friction and material questions.

## Files and use

- [STEP](filament_swatch_box.step) is the primary print layout; [STL](filament_swatch_box.stl) is the matching secondary file.
- [Main source](filament_swatch_box.py) selects the layout. Edit the named dimensions and builders in [components.py](components.py).
- [Print view](renders/print/filament_swatch_box_isometric.png) shows the two bed-facing parts; [closed view](renders/assembled/inspect_assembled_isometric.png) shows assembly.
- [Contact-cycle plot](renders/contact_cycle.png), [numerical summary](notes/numerical_summary.json) and [verification record](notes/verification.json) retain the evidence.

Load swatches flat. Start the lid at the open end with the thumb recess and snap
head trailing; slide toward the closed end until the detent passes and the edge
reaches the back stop. Open by pulling at the recessed thumb grip. Do not lift
the lid off the guides. Allow about 95 mm beside the opening to slide it fully
off. The opposed finger scoops expose the upper cards; tip
the open tray gently into your hand to remove the complete stack or the last
few cards. The scoops are narrower than a card, so cards cannot escape sideways.

The box reads `card_width`, `card_height` and `base_thickness` directly from the
[existing authoritative SCAD](../filament_archive_swatch/filament_archive_swatch.scad).
The swatch itself is not duplicated or modified.

| Feature | Current design |
| --- | --- |
| Capacity | 20 × nominal 80 × 50 × 2 mm swatches |
| Storage cavity | 82 × 52 × 44 mm; 1 mm allowance per side |
| Nominal stack allowance under lid | 4.3 mm above the 40 mm stack |
| Body floor / wall including guide foundation | 2.4 / 5.3 mm |
| Approximate closed size | 93 × 66 × 51 mm, including catch |
| Lid / running floor gap | 3.2 / 0.3 mm |
| Finger scoops | Opposed 26 mm openings, reaching 13 mm below the rim |
| Flexible beam | 18 mm straight length, 2.4 mm bending thickness, 3.2 mm height; 0.5 mm root rounding |
| Cams / nominal pass-over | 2.4 mm radius each / 0.8 mm inward bend |
| Closed snap | Contact-free nominally; no intentional sustained spring preload |

The 4.3 mm stack allowance accommodates variation rather than relying on every
printed card being exactly 2 mm. A stack taller than 44.3 mm requires more
`STACK_ALLOWANCE`. `COUNT` adjusts height; this design retains the current card
footprint and snap architecture. Source assertions reject undersized footprints
or a cavity too shallow for the scoops. Fit allowances remain provisional until
an actual box print is reported.

## Manufacturing strategy

Print the body upright, open face up, and the lid flat, recessed grip up, in the
supplied separate layout. Both broad undersides contact the bed. Use PETG, a
0.4 mm nozzle, 0.2 mm layers, four walls and 7% adaptive cubic infill. Use
[the object process](notes/process.json) with the repository's Q2C printer and
Generic PETG profiles. Keep four walls on top surfaces too; the process disables
Orca's single-wall top option and intentional seam gap. The STL smoke slice
covers this layout; importing STEP through Orca's GUI is a separate operation.
Preserve the supplied placement and orientation if splitting the compound there.

The snap bends across Y with its length along X, largely within printed layers.
Continuous perimeter paths fill its narrow section. Four walls also give the
catch/root a more substantial surrounding load path. This is a manufacturing
strategy, not a measured strength multiplier or calibrated isotropic material.
The larger body/roof may retain sparse infill; their stiffness is not included
in the local snap solve.

Orca 2.4.2 accepts the final Q2C 270 × 270 × 256 mm layout, with **no notices
and no support roles in its automatic-support probe**. Earlier slicing exposed
a 0.4 mm guide stem that was not reliably preserved; the final stem is 1.2 mm.
The sloped guide underside and catch pedestal now grow from existing material.
The finger scoops avoid the catch foundation. No supports are requested. Orca estimates 79.7 g of PETG and 2 h 28 min for
the pair under this reference setup; these are estimates, not measured print cost.

[Actual snap paths](renders/print/snap_paths.png) and the recorded 16-layer
section inspection at X = −25 mm show no internal hollow interval in the beam.
Fourteen middle layers and the top layer cover its nominal 2.4 mm width; the
first layer is about 2.11 mm wide because of 0.15 mm elephant-foot compensation
on each side. This path-width approximation supports an effectively solid
section, while leaving bonding, porosity, extrusion accuracy and anisotropy
unmeasured. It does not assign modulus or strain limits to slicer settings.

The retained reference slice uses Generic PETG at 245 °C initially / 250 °C
subsequently, flow ratio 0.95, and the profile's selected Cool Plate at 60 °C.
Its inactive hot-plate values are 80 °C. Use calibrated temperatures, flow and
bed adhesion for the actual filament/plate. The exported STEP/STL are the print
deliverables; diagnostic G-code is not supplied as a printer job.

## Engineering evidence

[verify.py](verify.py) checks the conservative solid card envelope against the
real cavity. It checks the rigid lid, excluding the flexible snap, from −92 to
0 mm at 2 mm intervals: no collisions at sampled poses. It separately checks
zero seated interference, a positive snap overlap during crossing, guide
retention at 1 mm upward movement and the back stop at 0.5 mm overtravel.
The actual lid relief clears a circular head through 1.1 mm inward movement and
±0.15 mm axial drift. A separate check confirms positive snap obstruction even
with 0.4 mm sideways play against the guide; a 0.45 mm shift hits the guide.
This includes the head's inward projection, which a
straight-beam gap check missed. These are geometry checks, not elastic motion
proofs or a continuous swept-volume claim.

The cheap cantilever screen, with explicitly assumed E = 1200 MPa, predicts
1.82 N transverse spring force and 0.89% root strain at 0.8 mm bend. It excludes
root-pad compliance, cam geometry and friction and therefore is not the sliding
operating force. The shared circular-cam/linear-spring screen predicts about
0.42 N sliding force when centered, and 0.15 N at the guide's sideways limit.
This is an order-of-force cross-check, not proof that the numerical force has
converged. The beam's 7.5 length/thickness ratio fails the helper's strict slenderness
rule; these analytical estimates remain rough screens. Root compliance and
interacting deformation/contact require the nonlinear analysis below.

[analyze.py](analyze.py) uses the shared `physical_analysis` API. It fixes the
actual arm's root pad and moves the actual body cam relative to it, −8 mm to
close and +8 mm to reopen, in one retained-state analysis. The beam displacement
is not prescribed. The mating cam drives its deformation through finite-sliding
surface-to-surface contact. The fixture assumes rigid guides/body cam and a
locally clamped lid root; it omits full enclosure compliance and guide friction.
Its centered registration demands the full 0.8 mm bend; actual sideways guide
play can reduce the bend and detent force. The centered strain result screens
the larger bend along this intended path; it does not cover forced off-axis
handling. Force remains a conditional local prediction.

All solids use an **uncalibrated** homogeneous, isotropic, linear-elastic PETG
screening assumption: E = 1200 MPa, Poisson ratio 0.38 and a provisional maximum
absolute principal mechanical strain screen of 1.5%. These values are assumptions
inherited from the repository's screening approach, not filament measurements,
a fatigue limit or a guarantee of recovery in printed PETG.

| Study | Mesh (mm) | Penalty (N/mm³) | Max path increment (mm) | Close / open peak (N) | Peak strain |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 1 | 6000 | 0.4 | 0.560 / 0.611 | 1.13% |
| Finer mesh | 0.7 | 6000 | 0.4 | 0.559 / 0.611 | 1.08% |
| Double penalty | 1 | 12000 | 0.4 | 0.560 / 0.612 | 1.13% |
| Smaller increments | 1 | 6000 | 0.2 | 0.443 / 0.459 | 1.09% |
| Smallest increments | 1 | 6000 | 0.1 | 0.395 / 0.397 | 1.08% |

Across the completed studies the cams pass, contact ends in the closed pose,
and reopening passes them in reverse. The head returns to within 10⁻⁶ mm of its
initial position under the elastic assumptions. Peak strain occurs at the rounded
beam root near X = −16 mm, Y = 26.4–26.6 mm. Maximum reported penetration is under
0.003 mm against a 0.02 mm rejection threshold; force balance is checked at every
saved increment and remains far below the 1% threshold. Mean head bend is about
0.8 mm; nodal motion including head rotation stays inside the checked relief.
Out-of-plane head motion stays below 0.001 mm: the cams pass by bending the snap
in-plane rather than escaping over their ends.

Mesh refinement changes peak sliding force by about 0.1% and peak strain by
4.6%; doubled penalty changes them by under 0.2%. Reducing path increments from
0.4 to 0.2 to 0.1 mm lowers the peak sliding
force from 0.61 to 0.46 to 0.40 N. The last change is 0.062 N (16%), failing the
recorded 10% force-stability screen, while strain changes by only 1.1%. The exact
force peak is therefore **not increment-converged**. A conditional 0.4–0.6 N
centered prediction is useful for the hand-effort decision, not a precise
operating-force claim. Further numerical refinement is unlikely to change the
light-detent conclusion; actual guide play, friction and material remain the
larger unresolved functional questions. The evidence supports a first complete-box
trial; actual retention and effort need that print.

The exploratory node-to-surface run timed out and is retained as
[rejected evidence](notes/analysis/node_contact_rejected/result.json), with its
original geometry and input. Its longer/thinner arm and coplanar cam ends differ
from the final design; it is not a controlled contact-formulation comparison.
The revised smooth cams solve with the optional surface formulation. A separate
shared compression/open-gap benchmark qualifies force and penetration reporting.

The box exposed reusable needs: surface-to-surface contact, a reversing
translation progress curve without resetting the nonlinear state, complete
parsing of CalculiX's omitted exponent markers in tiny return residuals,
and a cheap circular-cam force screen to interpret increment-sensitive reaction
forces. Result quality now checks force balance throughout the operation. The fine-increment
solve originally finished but its result extraction failed; the repaired parser
reprocessed the original mesh/input and recorded that recovery. The byte-identical
input guard prevents silently attaching old fields to a changed case.
The shared numerical suite has 15 passing tests. No additional solver/backend
was introduced. Multiple steps, friction, plasticity and creep remain unsupported.

## Remaining uncertainty and first print

- **Numerical:** a local clamped-root/rigid-guide fixture; sampled contact extrema and increment-dependent forces. The measured studies qualify this rounded snap and do not qualify arbitrary snap architectures or sharp-tooth pass-over.
- **Material/process:** uncalibrated modulus and strain allowance, layer bonding, porosity, shrinkage, seam texture, friction and global lid/body flexibility. Dense paths improve the solid-section approximation without establishing printed material properties.
- **Physical:** fit of the actual 20-card stack, convenient handling, perceived/measured operating force, snap recovery, wear, binding, permanent set and behavior after remaining closed.

For the first complete-box print, record the artifact hash/revision, printer,
filament brand/material, actual nozzle/layers/walls/infill, orientation, temperature
and flow settings. Try all 20 cards and several opening/closing cycles before
relying on retention. Record force in N if measurable, otherwise light/good/too
stiff; inspect recovery, wear and any whitening or cracks. Repeat after leaving
it closed for a day and report the dwell time and any change. Keep observations
against the tested revision so later material/printer calibration can use them.

If guides bind, identify the rubbing surface before adjusting `RUNNING_GAP` or
rail clearance. If the snap is too light or stiff, change the cam/beam parameters
and rerun the contact/strain and slice checks. Wall count alone is not a calibrated
stiffness adjustment. Update this record and the root model-index status together
when physical feedback arrives.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None | Complete box is the first functional trial. |
| Final printable object(s) | Unknown | `filament_swatch_box.step`, `filament_swatch_box.stl` | No print report; verify capacity, fit, force, recovery, wear, set and closed dwell. |

## Reproduction

From the repository root:

```sh
uv run --locked python model/filament_swatch_box/verify.py
./evaluate_model.py model/filament_swatch_box/filament_swatch_box.py --slice --slice-process model/filament_swatch_box/notes/process.json
uv run --locked python model/filament_swatch_box/analyze.py /tmp/swatch-new-cycle --cycle --mesh 1 --penalty 6000 --max-increment .00625
uv run --locked python model/filament_swatch_box/summarize_evidence.py
```

Use a new directory for every analysis. The summary reads retained results and
launches no solver. [evidence.py](evidence.py) follows the phone-stand retention
pattern: compressed solver input, fixture BREPs, logs, case, increments and result
history are kept in `notes/analysis`; large raw fields can be reproduced by
replaying the compressed input. See [shared API documentation](../../physical_analysis/README.md)
for native setup and limitations. The closed inspection source is
[inspect_assembled.py](inspect_assembled.py); it is not the bed layout.

## Attribution

Primary language model for completion: **GPT-6.1 Sol**, reasoning effort **high**,
as explicitly reported by the user during the continuation. Material contributor:
**GPT-6 Astra**, reasoning effort **low**, for the initial concept, CAD and shared
contact/progress implementation, also as reported by the user. GPT-6.1 Sol
completed clearance/process review, result extraction, evidence and delivery.
Harness/agent environment: **Codex shared-workspace agent**. Provider:
**not separately exposed**. No sub-agents were used. The prior swatch's Gemini attribution remains
with its existing object and is preserved.
