# Compact fully printed phone stand — revision 3

Revision 3 implements compact proposal A: a rounded pedestal, open fork cradle
and concealed positive angle lock. It uses **four printed core parts and one
pin insertion**, with optional printed TPU feet. It is a full-size prototype;
printed fit, return, tapping feel and long-term PETG behaviour remain untested.
V1 and V2 remain rejected before printing.

The reference phone is a Pixel 7 Pro in a bulky case, with **13 mm** total
thickness. The editable checking envelope is 85 × 170 mm and 0.30 kg; width,
height and mass were conservative assumptions rather than user measurements.
The geometry supports other phones through edge contacts and broad open space,
without a fitted camera or ring recess. Recheck changed phone/accessory envelopes.

## Current outcome and next step

V3 is the current full-size prototype, **not a physically validated stand**.
V1's exposed form and V2's desk footprint were rejected before printing. V3 has
nominal CAD/motion checks, conditional mechanics and a reference slice; it has
no user print report. Its 105 × 140 mm base and four solid core parts still
represent a substantial print (reference estimate 436 g with supports, 11 hours).

The next product step is the first full-size physical trial described under
[print setup](#print-setup-and-remaining-physical-checks), if the user chooses to
print it. No further redesign or analysis is implied by the remaining unknowns.
Optional feet have only a PETG diagnostic slice, not TPU qualification.

Two improvements have separate evidence and limits:

- The thin fork failed its deflection screen. Deeper sections behind the phone
  reduced the final baseline deflection to 0.904 mm under the assumed load.
  A contact model allowing both nose and housing to deform directed reinforcement
  to the nose. These are conditional solid-PETG results, not printed load ratings.
  [Mechanics, failures and benchmark evidence](notes/v3_engineering.md#analysis-and-verification).
- Rear-button reach now uses imported MyoSim MyoArm anatomy instead of the earlier
  invented arm/hand. A nearer setup has a sampled interaction witness; nominal
  withdrawal fails clearance and the farther search is INCONCLUSIVE. Setup and
  self-collision coverage remain limited. **Integrated physical operation is
  UNKNOWN for every setup**, including the computational witness.
  [Current access investigation](notes/v3_engineering.md#articulated-release-access).

The separate [timeout investigation](notes/v3_engineering.md#timeout-investigation-requested-by-the-user)
explains meshing failures, interrupted progress, queue waits and retained resource
reporting. It did not turn failed/incomplete calculations into product acceptance.
Detailed evidence, commands and historical environments remain in that record.
Current runtime requirements come from [pyproject.toml](../../pyproject.toml) and
[uv.lock](../../uv.lock); older Python/version lists identify retained runs.

## Files and operation

- [STEP print layout](phone_stand_v3.step) and matching [STL](phone_stand_v3.stl).
  [Entry point](phone_stand_v3.py) and [parametric components](v3_components.py)
  are authoritative. Preserve the supplied four-part arrangement in Orca.
- [Portrait view](renders/assembled/v3/inspect_v3_isometric.png),
  [side view](renders/assembled/v3/inspect_v3_right.png) and
  [landscape/accessory view](renders/assembled/v3/inspect_v3_landscape_isometric.png).
- [Editable adjustment SVG](renders/concepts/v3_adjustment.svg)
  ([PNG](renders/concepts/v3_adjustment.png)). Reproduce it with
  `./execute.py model/analysis_phone_stand/draw_v3_mechanism.py`.
- [Optional TPU feet STEP](phone_stand_v3_feet.step) and [STL](phone_stand_v3_feet.stl).
  Their PETG diagnostic slice does **not** qualify a TPU profile or pad friction.

The base occupies **105 × 140 mm**, with a 10 mm solid lower plate. The pin ends
increase assembled width to about 113 mm. The three angles are **45°, 60° and
75°** from horizontal. They replace the earlier illustrative angle targets;
15° spacing leaves material between the hidden pockets.

To assemble, remove supports and clean contact surfaces, slide the slider/root
pads into the base from the rear, place the cradle in the hood, then insert the
printed pin through the base, both roots, the moving rail slots and cradle. The
same pin limits slider travel; the head and split tail capture it. Do not force
a binding fit. For removal, squeeze the split tail and
withdraw the pin. No stock screw, nut, ballast or glue is needed.

To adjust, support the phone/cradle with one hand, press the rear button forward
to its **3 mm stop**, tilt, then release into a pocket. Confirm full engagement
before removing support. Pocket faces bear the angle load; the folded springs
only return the slider. Adjustment under the phone's full torque can bind the
dog against its pocket; supporting the phone unloads that contact.

## Agreement and architecture decisions

The user authorized autonomous implementation of compact A with fully printed
parts and minimal assembly. PETG, a 0.4 mm nozzle and 0.2 mm layers remain the
basis. Full-size phone loads govern; scaled copies can explore a mechanism but
cannot qualify full-size load, gap, spring or fit behaviour.

Four separate parts permit useful print orientations, accessible mating surfaces
and support removal. Print-in-place construction would introduce floating
bearing surfaces and orientation conflicts. A single pin also captures both
spring roots, avoiding separate root fasteners. The low enclosure hides the
index pockets. The open fork reserves accessory space behind the phone.

A fixed stand would omit the requested angles; reseatable proposal C changes the
selected press-and-tilt interaction. The footprint stays at proposal A's target.
The later stiffness changes add material behind the fork rather than longer feet.
This continues the physical-analysis exercise while aiming at a useful product;
local CAD or numerical passes do not establish product acceptance.

## Fit, cable and ring space

The cradle accommodates portrait and landscape. Split lower ledges leave a
central cable opening. Nominal CAD checks reserve a **20 mm wide plug envelope
extending 30 mm below the phone**, including 18 mm in the screen-normal direction.
The phone bottom is about 63–74 mm above the bare base plane across the angles.
The user's actual connector and bend radius are unknown: test the real cable.

The rear ring reserve is **33 mm deep**, allowing for the reported 30 mm hanging
ring and approximately 2 mm mounting base with a small margin. The portrait
reserve spans 60 mm across and 115 mm vertically; the landscape reserve spans
170 mm across and 50 mm vertically. This is broad accessory space, not a
ring-specific fitted aperture. Outboard pads sit outside or above those envelopes.
The reported camera-case projection is not a calibrated universal camera envelope.
The Pixel reference's camera region lies beyond these support pads; check future
phones rather than assuming their cameras fit the same contacts.

The pivot bore is 8.3 mm for an 8 mm pin (0.3 mm diametral allowance). Pocket
flank clearance is 0.12 mm total; the guide's nominal vertical allowance is
0.1 mm. These have different jobs: insertion/rotation, angular play and guided
bearing. They are unprinted interface assumptions, not measured tolerances.
Gravity seats one flank; reversal can expose joint clearance. A tight, tap-resistant
feel still needs the first physical test.

## Print setup and remaining physical checks

Use PETG, 0.4 mm nozzle, 0.2 mm layers, **four walls and 100% infill** for the
core. The solid base provides mass for the compact tipping screen, while the
mechanism/structure use a conditional solid-material analysis. The user's usual
2-wall/7% setup would change both assumptions. Solid toolpaths do not establish
isotropic PETG properties or layer bonding. The retained process profile uses
Generic PETG temperatures/flow; apply the actual spool's qualified settings.
The reference slice estimates **436 g including supports and 11 hours**. The
solid CAD mass used in statics is 373 g. This remains a substantial print despite
the smaller footprint; lowering infill invalidates that mass/stiffness screen.

The base prints upright, cradle on its side, slider flat in XY and pin on its
flat lower surface. The side orientation gives the fork a continuous cross-section
through the supports and prints the cradle bore vertically. The slider's narrow
folded springs bend in the layer plane. The pin's long split tail provides
assembly compliance; its main pivot section stays solid.

Supports are generated on the core layout. Review their placement and clear the
rotor cavity, guide/root channels and outboard cradle pads before assembly.
The [selected-layer support review](notes/v3_support_review.png) identifies
guide/root-channel interfaces and supports beneath the projecting cradle pads.
They have open rear/side removal routes before assembly; the pin bores are
accessible from their ends. Small guide ceilings, horizontal base bores and pad
starts need careful cleanup; actual PETG removal quality remains unprinted.
Do not leave material in the
moving channels. Optional TPU feet print pad-down and press into four underside
recesses; actual retention and desk grip are unqualified.

For a first full-size trial, check dry assembly, pin capture, full button stroke
and spring return before loading the phone. Then test all angles, portrait and
landscape, the hanging ring, cable insertion and ordinary tapping. Stop if the
lock does not seat fully, if a spring takes a permanent set, or if the stand slips.
Desk friction, print tolerances, wobble, wear, sustained-load creep and warm-room
behaviour require observation. No miniature qualifies those full-size behaviours.

## Rejection before printing and footprint explanation

V1's exposed gear/form and V2's 224 × 246 mm desk footprint were rejected before
printing. Neither rejection establishes a material or print-process failure.
The full [V2 rejection, evidence and proposals](HISTORY_V2.md) and
[V1 history](HISTORY.md) remain available. Revision 3 supersedes their print
recommendations; historical exports and evidence remain deliberately retained.

## Print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | None | No separate coupon: the complete compact prototype represents assembly, ring/cable space and use; miniatures are exploratory only. |
| Final printable object(s) | Unknown | `phone_stand_v3.step/.stl`, `phone_stand_v3_feet.step/.stl` | V3 has no physical print report. Fit, spring return, engagement, cable/ring use, tap wobble, desk grip and creep remain. V1/V2 were explicitly rejected before printing. |

## Attribution

Original repository design developed from the user's requirements and feedback.
No external CAD model was copied. Historic proposals, source and native analysis
are retained with their owning revisions. The reference Qidi/Generic PETG slice
is diagnostic evidence for its exact selected profiles, not the user's printer
calibration.

Measured agent effort for the selected historical work is recorded in
[the token and timing notes](notes/agent_effort.md). This supplements creator provenance;
its task and capture limits are explicit.


## Engineering evidence and earlier investigations

<a id="analysis-and-verification"></a>

- [Analysis and verification](notes/v3_engineering.md#analysis-and-verification)

<a id="timeout-investigation-requested-by-the-user"></a>

- [Timeout investigation requested by the user](notes/v3_engineering.md#timeout-investigation-requested-by-the-user)

<a id="contact-and-collision-qualification"></a>
<a id="evidence-integration-and-reproduction"></a>
<a id="imported-constraints-and-setup"></a>
<a id="results-and-sensitivity"></a>
<a id="articulated-release-access"></a>

- [Articulated release access](notes/v3_engineering.md#articulated-release-access)

<a id="qualification-and-interpretation"></a>
<a id="setup-and-collision-scope"></a>
<a id="evidence-integration-and-reproduction-1"></a>
<a id="historical-synthetic-release-access"></a>

- [Historical synthetic release access](notes/v3_engineering.md#historical-synthetic-release-access)
