# Where to put the opening grips

**Start with the cap band centred 50 mm above the seam and the body band
30 mm below it.** This is a dimensional proposal for the selected smooth,
0.7 mm deep × 20 mm wide full-wrap shape. The anatomical search has not
established a usable grasp, so these positions are **not ergonomically validated**.
There is no reason to hold up the visual comparison while searching indefinitely.

[Placement comparison — editable SVG](grip_human/placement_comparison.svg)
([PNG](grip_human/placement_comparison.png)) shows where the fingers would find
each band, which half stays supported, and which direction the cap moves.
The [shape/profile comparison](wall_comparison.md#continuous-band-and-shallow-profile)
still owns the choice of depth, curved ramps and interior-space cost.

## User direction

The user selected recessed saddles over the other grip ideas, then accepted
exploration of a shallow smooth band wrapping around the box. They requested
anatomical investigation of its location and recorded visualizations. They
specified **upright/diagonal opening because the toothbrush must not fall out**.
Accordingly, the lower hand supports the body and the upper hand lifts the cap.
This study includes upright and 25° diagonal arrangements, never horizontal use.
These statements preserve user intent; the numerical screens below are agent
choices, not user acceptance criteria.

The existing seam finger notches remain scheduled for removal in a later CAD
revision. No production source, STEP or STL is changed by this study.

## Placement comparison

All dimensions are axial millimetres from the closed-case seam. Each band spans
10 mm on either side of its centre; the band goes around faces and corners.

| Candidate | Cap centre / extent | Body centre / extent | What changes in use |
| --- | --- | --- | --- |
| Near | +40 / +30…+50 | −15 / −25…−5 | Close together; cap recess overlaps the existing backing blend and starts at the sleeve end |
| Balanced, provisional | +50 / +40…+60 | −30 / −40…−20 | Keeps the recess beyond the joint structure without pushing the cap band toward its far end |
| Separated | +65 / +55…+75 | −50 / −60…−40 | More room between grip centres, but the cap band ends only 15 mm before the closed end |

The internal sleeve ends at +30 mm. The existing exterior catch-backing blend
ends at +39 mm. Thus the balanced cap band starts 10 mm beyond the sleeve,
but **only 1 mm beyond the backing blend**. This is nominal geometric separation,
not a tolerance or wall-flex guarantee. Centres are 55, 80 and 115 mm apart;
these distances alone do not tell us whether actual hands crowd each other.

A full wrap lets the person choose a face or corner and rotate their grip.
That is the reason for exploring it; it does not prove traction. A shallow
recess still depends on skin compliance, surface friction and squeeze force.

## What the human model actually checked

The local experiment imports MyoSim 0.2.3 **myohands**, including both native
hands, all digits and original collision skin. It preserves 46 native hinge
coordinates/ranges, holding the six wrist coordinates neutral and searching
40 finger coordinates plus rigid position/orientation of each hand. Hands are
not resized or remodelled. Rigid hand placement deliberately excludes shoulder,
elbow and wrist posture comfort; it is not a population or user-specific model.
Earlier fixed-shoulder attempts gave no usable grasp and cannot establish
that the person's arm cannot reach the box.

The consequential question is whether thumb and index skin can contact each
half's band with distinct contact directions, while other skin avoids the
opposite half and the two hands avoid each other. Other fingers may rest
against their own half. The setup places the seam 1,150 mm high and 350 mm
forward; these are unmeasured reference coordinates, not a prescribed posture.
No muscles are actuated and no dynamics are integrated.

The product representation derives from the authoritative thin-case builder:
74.2 × 51.2 mm main exterior, 6 mm corners, 174 mm body length to seam,
90 mm cap, 30 mm sleeve. Rounded rectangles are represented by native boxes
and cylinders, with half-millimetre axial subdivisions along the band.
The profile is conservatively overbounded between stations; the actual
rounded corners remain available for contact. Interior and old finger-notch
voids are filled, so skin cannot pass through the shell. Existing exterior
backing pads are conservatively boxed through their full blend length.
Contents, local skin deformation and shell deformation are not simulated.

Contact position error must be at most 0.30 mm, normal error at most 15°.
Thumb/index contact normals must differ by at least 60° and contact points by
at least 20 mm; these are distinct-contact screens, **not force closure**.
Forbidden pairs require 0.20 mm clearance. Resting contact with one's own
half permits at most 0.05 mm numerical penetration. Native signed distances
check nearby pairs; conservative AABB lower bounds exclude certainly distant
pairs. Collision masks alone are insufficient, so selected cross-digit,
nonadjacent-digit and all between-hand pairs are explicitly queried. Adjacent
skin/composites and the known proximal middle/ring proxy overlap are excluded
and named in the audit. Palm proxy gaps and exclusions limit this screen.

The baseline planned four deterministic starts using bounded least squares,
up to 220 evaluations for each warm and final stage. **Two starts completed;
both failed the screens. The agent stopped further solver tuning during the
next start; no interrupted state is treated as completed evidence.** This is an
incomplete planned search and an inconclusive placement investigation, not an
exhaustive failure proof. Saved completed configurations are
independently replayed. The lowest-cost failed pose is a diagnostic illustration,
never an accepted grasp. The same native posture is rigidly translated to the
three band positions and rotated upright/diagonal: those are **placement replays,
not six independent grasp searches**. Rotation is geometrically equivalent in
this local scene without arm constraints or gravity.

**Result: zero accepted completed baseline starts, and all six placement/
orientation replays INCONCLUSIVE.** In the selected failed pose, the index
contacts miss the target skin-to-wall position by roughly 14.6 mm—about the
width of a small fingertip—and their normals face poorly toward the wall.
That is a failed numerical grasp, not evidence that a person cannot hold the
box. No opening path is qualified from those endpoints. The layout comparison
therefore supplies the provisional location; the anatomy result does not rank it.

If an endpoint passes, the recorder samples the first 6 mm cap lift every
0.5 mm with the cap hand following it and all finger joints held fixed.
Without an accepted endpoint, no opening path is qualified. Approach, complete
cap removal, contents retention, snap-release force, comfort, wet fingers,
friction, durability and population coverage remain unqualified.

## Recorded evidence and reproduction

- [Native hand projections: near](grip_human/pose_near.svg),
  [balanced](grip_human/pose_balanced.svg),
  [separated](grip_human/pose_separated.svg). Read their status labels:
  unsuccessful attempts do not show a feasible handhold. Red points are
  actual requested skin points; orthographic overlaps alone do not prove collision.
- [Search, anatomy audit and independently replayed states](grip_human/study.json).
  The record includes source/asset/tool identities, joint axes/ranges, masks,
  named collision pairs/exclusions, diagnostics and all searched configurations.
  The historical `q_rad` key holds mixed parameters: 40 finger radians, then
  right and left wrist XYZ in object-local millimetres and world rotation vectors
  in radians. The receipt declares that layout explicitly.
- [Shared verification report](grip_human/verification.json) preserves the
  inherited product requirements as well as this grip question. Existing
  printable-model evidence is not promoted to qualify the band concept.

Run from the repository root:

```sh
./execute.py --threads 1 model/dental_travel_case/grip_human_study.py
./execute.py --threads 1 model/dental_travel_case/grip_human_record.py
./execute.py --threads 1 model/dental_travel_case/grip_placement_diagram.py
./execute.py --threads 1 model/dental_travel_case/verification.py --variant grip-band-placement
```

The final command uses the existing shared CLI and recomputes native acceptance;
stored PASS flags cannot supply a result. Missing/stale evidence is UNKNOWN;
malformed attempted evidence or a finite search without a witness is INCONCLUSIVE.
No witness does not mean the box is impossible to hold. Meaningful regressions
cover native geometry preservation, mirrored contacts, palmar-side selection,
rounded-corner access, rigid placement replay and false/stale receipt promotion.

## Contact-side audit and lesson

Early adaptation of the phone-stand fixture's +local-Z ellipsoid contact was
unsuitable for this grasp. Native mirrored-left ellipsoid axes reverse their
outward sign. More fundamentally, those flattened ellipsoids are on the
extensor-facing side; geometric outwardness is not palmar skin semantics.
Those preliminary attempts are rejected and supply no placement evidence.

The corrected targets use the **native distal capsule barrel on the flexor
side**. A finite perturbation of the native DIP/IP coordinate and imported
FDP2/FPL tendon length identifies the shortening direction; the corresponding
native segment motion selects the flexor-facing capsule normal. Thumb motion
is negative and index motion positive in both native hands. This uses tendon
geometry to identify a side, never tendon force or physiological strength.
Regression tests retain the mirrored-axis and flexor-side counterexamples.
The earlier phone-stand result retains its original geometric contact scope.

Another early proxy filled the rounded corners and restricted contacts to flat
face middles. That could wrongly exclude corner grasp space, so the current
scene preserves the real rounded outline and targets the whole perimeter.
Neither correction is permission to shrink anatomy or remove real obstacles
until a search passes. The specialist skill now routes these checks before
adapting a new grasp.

The practical stopping point is a readable location comparison plus a truthful
finite human-model result. No further solver campaign or print is queued by
this note. Balanced placement remains a starting proposal for a future CAD/
physical comparison, rather than claiming that simulation selected an optimum.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | Rough SVG/native-hand study only | No new sample authorized for this phase |
| Final printable object(s) | N/A for this study | Existing production pairs unchanged | Band traction/comfort and loaded upright opening remain untested |

Primary language model: GPT-6, exact runtime variant and reasoning effort not
exposed. Harness: Codex, shared local repository. Provider: OpenAI. No subagents.
MyoSim source/assets remain in the installed package; package hashes and version
are recorded, with its original licensing/attribution retained. No anatomy assets
are copied into this repository. Historical model attribution remains in
[the current comparison record](wall_comparison.md#handoff-lesson-and-attribution).
