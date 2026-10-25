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


## R3 failed partial print and R4 authorization

The user canceled R3 mid-print: adjacent spiral lines were merging and the print
lifted from the bed. The user names Cura 3D and attributes insufficient adhesion
to that setup, but actual temperatures, brim, bed surface, speed, exact printed
hash and root cause are unknown. Record Partial / failed rather than complete
print success; no recoil or maximum-extension result is available.

R4 is authorized to increase the turn spacing a little and change the shape to
provide more bed contact. Perfect circularity is explicitly relaxed. The user
requires symmetry in at least two axes, preferably more. Interpret this as the
outer transverse profile: four identical flats give two mirror axes plus four
quarter-turn-equivalent resting sides. A chiral helix itself is not mirror
symmetric. Retain about 7 cm length, about 15 mm size, thinner cord, horizontal
placement and integral ends. Existing R3 geometry/evidence remain historical.


R4 delivers nineteen turns with 0.40 mm axial spacing, 71.6 mm overall length,
and four identical 0.5 mm outer trims. The 15 mm maximum envelope becomes 14 mm
across flats. Native contact checks give about 10 mm² per sampled middle foot
and 200.8 mm² total bed-plane contact; native gap is about 0.398 mm. The
[R4 decisions](r4_decisions.md) retain exact evidence and print limitations.
The supports-off reference slice completed, with bore supports still proposed
by the automatic probe. There is no physical R4 result. R3 remains Partial /
failed, with its original source, exports and reports preserved.


## R4 physical feedback and R5 short-sample authorization

User printed R4 and says the idea can work, but turns still stick and cause print
defects. They request substantially more spacing while retaining reasonable
compression. They find the current outer-only clipped circular tube strange and
want matching flat/faceted inner and outer outlines, with overhang-friendly
geometry. An eight- or sixteen-sided outline and a faceted swept cord section
are explicitly acceptable. No explicit R4 adhesion result, force/recovery data,
actual settings, material batch or printed hash was supplied; do not infer them.

The next authorized deliverable is one short approximately 20–30 mm sample to
reduce print/revision effort. The approximately 70 mm version remains a future
intent, explicitly deferred until the geometry/printing experiment works. Keep
the existing symmetry, approximately 15 mm transverse size, horizontal printing,
solid TPU and integral attachment ends. R4 is superseded; preserve its source,
exports and native evidence as historical data, not successful separation proof.


R5 delivers one 25.2 mm short sample: five octagonal winding circuits with
1.2 mm nominal gaps, an eight-faced chamfered cord section and closed terminal
turns within the same envelope. Both inner and outer walls have native flat
facets in all eight directions. The [R5 decision record](r5_decisions.md) holds
construction and manufacturing evidence. Local native gap is about 1.190 mm;
sampled middle feet have about 9.28 mm² planar contact. CAD, paired exports and
the supports-off reference slice completed; the automatic probe still proposes
roof supports, so bridge quality and clean separation require printing. There
is no R5 print report. No long R5 geometry/export is supplied; the 70 mm user
intent remains explicitly deferred.


## R5 physical acceptance and connector exploration handoff

User reports having printed R5 and says it is okay. Record the sample as Yes /
accepted as okay, preserving this subjective scope. No specific force, extension,
adhesion, recovery, wear, exact settings or printed hash was provided. The new
message refers to the earlier cord as PETG, whereas the design and earlier
instructions called for TPU; actual material for the accepted print is not
independently confirmed. Do not use this report as printed-material calibration.

The user defers further cord modelling, including the approximately 70 mm version.
A separate two-ended connector is now requested at SVG concept stage, linking
the printed terminal loop to an existing key ring or similar loop. It should
open without spinning an attached ring/cord, be stable closed on both ends and
work as a rigid PLA/PETG mechanism without springs or elasticity/friction-fit
retention. Fully printed is preferred; existing hardware is allowed if needed.
The user delegates generic reasonable sizing rather than measuring a key ring.
Connector proposals are owned separately in `model/double_ended_connector/`.

## R6 return to circular geometry with flat contact

The user reopens cord work and requests a circular alternative to R5's octagon,
retaining flat printing contact to test whether edges can be eliminated. One
25.2 mm short TPU sample is delivered, with five circular winding circuits,
3.2 mm round cord, 1.2 mm nominal gaps, a 15 mm round envelope and two opposing
0.5 mm exterior trims. Bore diameter is nominally 8.6 mm, print height 14 mm.
Terminal loops remain closed and integrated in the winding envelope. The two
flat boundaries are intentional; other transverse faces are round. R5 remains
accepted and unchanged; the ~70 mm version remains deferred.

Valid CAD and matching STEP/STL exports passed the existing selected-profile
Orca slice, with supports off and no filtered notices. The automatic probe
still flags curved-roof support; actual paths and model views were opened.
Local contact is 10.01 mm² per sampled middle foot, local gap 1.192 mm; 36
material/gap/bore witnesses and 101 bridge midpoints pass their scoped checks.
No physical R6 result is inferred. Full reasoning, settings and experiment
limits are in [R6 decisions](r6_decisions.md), with the preserved prior summary
in [R5 baseline](r5_baseline.md).

## R6 design rejection and R7 profile correction

The user rejects R6 before printing: flat contact was intended to come from a
flat-sided swept section, continuously on the inner, outer and end-facing sides,
rather than isolated shaving of round swept cord. Mark R6 No / rejected in this
record and the root catalog; its native reports remain historical digital evidence,
not a physical failure. The rejected instructions are preserved in
[R6 historical record](r6_rejected.md), explicitly marked do not print.

R7 uses a 3.2 × 3.2 mm rounded-square profile with R0.6 corners and 2 mm straight
lands, on a true circular winding. Nominal diameter 15 mm, bore 8.6 mm, five
circuits, 4.4 mm pitch, 1.2 mm nominal gaps and 25.2 mm length retain the short
trial's scale. No clipping is used to flatten the exterior. The actual local
section is inspected separately from the complete circular end view. Horizontal
first-layer sections and paths replace R6's inappropriate shaved planar-area
criterion. The printing setup remains solid TPU / 0.4 mm / 0.2 mm, supports and
brim off; actual adhesion and round roof printing remain physical experiments.

Direct periodic-surface unions repeatedly returned incomplete geometry despite
validity. An overlap-supplement attempt preserved middle material but left much
of the first eye absent; a suspicious half-foot in the actual first-layer plot
triggered full terminal checks. It was corrected before handoff by retaining the
complete right half and joining its 180-degree-rotated copy on the axial midpoint.
The source now guards complete terminal perimeters, and local review checks the
flat-sided material around both eyes as well as the winding. Detailed diagnosis
and final evidence belong to [R7 decisions](r7_decisions.md).

The user's explicit profile preference is recorded with its cord-specific scope
in the design preferences. A concise reusable CAD lesson now covers complete
functional-material witnesses after periodic unions. Neither is a universal
TPU tolerance or boolean algorithm recommendation.
