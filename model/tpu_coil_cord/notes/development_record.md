# First compact coil experiment

The user requests one short, real 3D helix in TPU, compressed directly after
printing, with an eye at each end, finger-scale coil diameter and an emphasis on
strong recoil and extension capacity. Hand separation is acceptable. A flat
zigzag is explicitly rejected. A thickness comparison is a later phase.

Selected geometry: 8 mm mean radius, 4 × 3.2 mm hexagonal section, 1.2 mm flat
lands, 3.6 mm pitch and six turns; full revolved end rings share the profile.
This avoids extra projecting eyes and keeps each attachment hole open. Ring-to-
helix overlap intentionally consumes part of each terminal turn. No spacers,
extra assembly or sacrificial tethers are included. There is no designed preload
or initial tension: recoil comes from elastic deformation of the thick solid
TPU section, and must be tested. Strong force is a user goal, not a measured
property of this sample. Safe extension cannot be inferred from cord arc length.

An initial top-ring union was invalid where a revolved periodic seam coincided
with the helical endpoint. The coil, ring and bottom union were independently
valid. Rotating only the circular upper ring's seam by 90 degrees made the final
union valid without changing the intended ring geometry. This is local CAD
construction evidence, not a new general design restriction.

The final evaluator report owns source/export/slice identity and effective
settings. Isometric and front images were opened: true helix, closed end rings,
open bore, and compact proportions match the requested architecture. The final
paired exports use the evaluator's absolute STL tessellation and identical
upright placement. Orca 2.4.2 accepted the centered plate, gave no filtered
notices, and generated no support in its automatic-support probe.

The trial process derives from the existing solid TPU profile, with three walls
and supports/brim/ironing explicitly off. TPU filament and Q2C printer profiles
are shared existing sources; exact paths and effective settings are in the
native report. No hardware, load, printed material modulus, strength, extension,
release allowance or fatigue behavior is calibrated.

Targeted CAD checks sample material at the helical centerline and empty gaps
halfway between successive turns at six angles on each of three middle turns.
Material controls ensure that an absent/misplaced coil cannot pass the void
witnesses. Bore-center witnesses cover both eyes. These samples do not prove
continuous printed clearance. Actual primary layers at Z0.2, Z5.4 and Z22.0 mm
are plotted to inspect initial contact, a middle-turn underside and the upper
ring approach. Blue means deposited TPU; orange would mean a Bridge-labelled
path; whitespace is unfilled area. Toolpath roles and witnesses are retained
in `targeted_checks.json`; source reproduction is `inspect_sample.py` with the
native report's retained Orca run directory. This diagnostic deliberately
rejects absolute-E or relative-XYZ commands after the first layer marker rather than silently misreading it.

Finish line for this phase: one valid, exported, visually reviewed compact
helix with both attachment eyes, a TPU smoke slice and clear physical-test
instructions. Printability, hand release and recovery cannot be digitally
proved here. The next decision depends on the physical trial, not additional
simulation or speculative thickness variants. Review at handoff found no
new transferable printed-material lesson or shared-tool change justified.

The selected-layer image was opened after generation. It shows a closed annular
first layer, a C-shaped helical section with several ordinary paths at Z5.4,
and an annular upper-ring approach at Z22.0. Primary extrusion roles include
Overhang wall but no Bridge role. All 18 paired material/clearance witnesses
passed. An initial parser guard rejected G91 commands in the printer's startup
purge routine; the diagnostic now begins at the first layer marker, after the
startup returns to G90/M83. The generated result is from that corrected reader.


## First physical feedback and next iteration

User report (2026-10-25): the first sample was printed and works reasonably well.
Freeing the turns leaves rough/unclean surfaces; recoil is less bouncy/strong than
wanted. The user used an effectively unlimited wall count, producing practically
solid material. Other actual settings, exact hash, force, extension, dwell and
permanent set are unknown. The first design is accepted as an understandable
experiment, not rejected wholesale. Preserve its source, exports and original
slice evidence as the printed control. The next task is stronger pullback and
cleaner turn separation; horizontal printing is a proposed route, with autonomous
exploration/selection explicitly authorized. Retain a compact real 3D spring and
both end attachment loops; no flat zigzag substitute.


The second phase selected a horizontal rounded-house winding with thicker
5.2 mm cord, four turns, 0.8 mm nominal sideways gaps and outboard end frames
joined through rounded foot tabs. The [R2 decision record](r2_decisions.md)
contains the concept comparison, research, abandoned spline/union attempts,
final native/path evidence and physical comparison instructions. The
[historical R1 record](r1_baseline.md) preserves its original engineering detail;
R1 source and exports remain unchanged. No physical R2 result is inferred.


## R2 physical feedback and R3 authorization

User has printed R2. R1 felt practically better; R2 felt too thick. The user
rejects the additional outboard end rings and the nonuniform house-shaped
outline, preferring a round winding whose outline is consistent around its axis.
No measured force/recovery, surface-cleanup comparison, actual R2 wall count or
other print settings were supplied. Do not infer those results from the fact of
printing. R2 is superseded as the next trial; preserve its geometry and evidence.

R3 is explicitly authorized: horizontal printing, a round helix similar to R1,
terminal loops naturally merged into the last turns rather than outboard rings,
much tighter gaps than R2, and approximately 70 mm overall compressed length.
The user believes the printer can handle substantially tighter gaps. This is a
request to test them, not a calibrated printed minimum. Restore R1's section
rather than increase stiffness again. No further thickness comparison or material
change is needed for this phase.


The user subsequently specifies approximately 15 mm outside diameter for R3,
including the terminal loops. Set the shared cylindrical outside envelope to
15.0 mm; the 3.2 mm cord leaves an 8.6 mm nominal bore. This latest instruction
supersedes the earlier approximately 20 mm coil diameter. Length remains
70.2 mm nominal and the gap remains 0.15 mm.


R3 delivers a 70.2 mm-long horizontal round helix with 15 mm outside diameter,
3.2 mm cord, twenty turns and 0.15 mm axial CAD gaps. Integral closed terminal
turns remain within the same envelope. The [R3 decisions](r3_decisions.md) record
construction corrections, exact user criteria and final scoped evidence. CAD,
paired exports and the supports-off slice completed; the support probe proposes
support inside the round bore, so sag/release remain physical trial questions.
R3 has no physical print report. R1 and R2 sources and exports remain unchanged.
