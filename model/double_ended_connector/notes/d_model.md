# D — captive threaded barrel connector

This is the first of the requested sequential CAD models. D replaces each open
mouth with a screw-driven sleeve. Turn a sleeve four turns toward the middle to
expose the mouth; reverse four turns to cover the fixed nose again. The other end
stays closed. Neither attached loop turns with the sleeve.

## Files and views

The [STEP](../d_barrel_gate.step) and [STL](../d_barrel_gate.stl) contain the eight
parts separated in their print orientations. [Entry point](../d_barrel_gate.py),
[parametric geometry](../d_design.py), [local thread helper](../lock_geometry.py).
Do not print an assembled pose as one fused object.

- [Assembled, both closed](../renders/d/d_barrel_gate_inspections/closed.png).
- [Assembled, one open](../renders/d/d_barrel_gate_inspections/open.png).
- [Assembly order](../renders/d/d_barrel_gate_inspections/assembly.png).
- [Section through the real model](../renders/d/d_barrel_gate_inspections/section.png).

The first model is larger than the rough sketch: approximately 62 mm long,
23 mm wide including barrels, with thicker screw bosses only near the middle.
The slim 4 mm-thick spine and 3.6 mm-diameter free nose are designed around the
nominal 7.6 mm cord bore. This is not an assumed fit to every key ring.

## How to assemble

1. Thread one barrel onto each separate stem from its small keyed-root end.
   The barrel's wider cavity faces the stem's integral keeper shoulder. Turn
   the barrel to its retracted position before fitting the frame.
2. Lay both stem/barrel units into the lower frame half's keyed sockets. The
   small root grooves align with the socket ribs; these block stem withdrawal.
3. Fit the upper frame half along the split plane, closing those sockets.
4. Install the two printed thumb screws through the clearance side into the
   threaded frame bosses. Hand tighten; do not crush the seam.
5. Turn each barrel independently between its open and closed stops. Nothing
   is removed for daily use.

The eight parts are two frame halves, two stems, two barrels and two hand screws.
This deliberately changes the schematic five-piece proposal. A split frame with
integral half-stems would still require the stems to cross the barrel walls
while assembling; the CAD approach check rejected it. Separate keyed stems let
sleeves be installed axially first and the finished units captured afterward.
No component needs stretching, snap assembly or a tool.

## What holds it closed

Each barrel has a four-millimeter threaded skirt and a wider upper cavity.
The keyed stem supplies guidance and screw travel. An integral keeper
shoulder stops the skirt advancing beyond the stem tip; a base shoulder limits
retraction. The closed sleeve overlaps the free nose, physically covering the
mouth. The base, thread and nose support it; no spring provides retention.

A two-millimeter pitch gives eight millimeters of travel in four turns. The
nominal radial allowance is 0.22 mm, with 0.12 mm flank allowance. These are
trial design choices, not measured PLA/PETG calibration. Thread friction and
resistance to back-out under rubbing or shaking remain unmeasured.

## Print and evidence

Print all separated pieces as supplied. Suggested experiment setup: PLA or PETG,
0.4 mm nozzle, 0.2 mm layers, solid parts, 5 mm brim for small parts, supports off
initially. Frame halves
lie on their split faces; barrels stand upright with an open bore; hand screws
stand on their heads. Outer grips are recessed and exposed circular lips have
0.35 mm chamfers/rounds. No print-in-place joints need breaking free.

The split gives the frame halves a flat bed face; the stems stand on their
keyed roots, so their threads rise vertically. Internal sleeve threads still have
short sloping flanks: actual thread quality and dimensional fit need the trial.
The seam and two small printed frame screws are prototype load paths, not a
rated connection. The central block leaves 1.85 mm nominal material above and
below each root socket. This object has no established carrying capacity.

CAD criteria and motion checks: [source](../d_checks.py). The checks distinguish
helical running clearance, axial obstruction, assembly approach and solid screw
cores from the physical questions of effort, vibration, wear and strength.
Final native export/slice evidence is linked by the current object README.

| Item | Print status | Artifacts | Remaining physical checks |
| --- | --- | --- | --- |
| D complete prototype | Unknown | `d_barrel_gate.step`, `d_barrel_gate.stl` | Thread fit, hand access, frame seam, both-end pull/twist, unloaded shaking and wear |
| Final rated connector | N/A | None | Experimental mechanism comparison only |

## Provenance

Primary model: GPT 6.1, F4 Medium as supplied by the user; runtime identity and
reasoning effort are not independently exposed. Codex CLI, OpenAI. Original local
geometry; the coarse solid-core trapezoidal helix follows the repository's
existing printed-thread construction approach, not a claim of transferred fit.

The reference slice uses the Q2C 0.4 mm printer and Generic PETG filament from
[the maintained Orca reference profiles](../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/),
with the existing [solid coarse-fastener process](../../dental_travel_case/notes/printed_fasteners/profiles/process.json)
(0.2 mm, four walls, 100% rectilinear fill, 5 mm brim, supports off).
[Process attribution and licence](../../dental_travel_case/notes/printed_fasteners/profiles/ATTRIBUTION.md)
remain with that profile. PLA is an intended alternative, not a separately sliced
or physically qualified material in this increment.

Final digital review: CadQuery 2.8.0 reports valid geometry; both paired exports
and all four native inspection views completed. The shared verification report
passes the CAD obligations and leaves hand use and shaking UNKNOWN. OrcaSlicer
2.4.2 accepted the centered solid-PETG layout with no filtered notices. This does
not qualify PLA, physical fit or a particular GUI STEP importer.

The automatic support probe requests review: [actual support-location plot](d_support_review.png),
[parsed diagnostic](d_support_review.json), [reproducing source](review_d_slice.py).
Orange in that plot is proposed support, gray is primary-slice extrusion. Proposed
support appears at the frame's screw/socket regions, inside the barrel skirts,
and around the external screw/stem threads and keeper shoulders. Support reaches
Z16.6 mm below the highest keeper shoulder. That 30-degree-threshold probe does
not prove necessity or easy removal. The trial keeps supports off to avoid
mating-thread cleanup; check flanks, small shoulders and socket/hole roofs after
printing. The slice is acceptance with a reviewed support warning, not a claim
that every overhang prints cleanly.
