# S16 liner for the printed slim dental travel box

Two TPU cups cushion the contents of the existing **264 × 74.2 × 51.2 mm narrow
M1**. The body insert follows the internal catch guards and continues through the
overlap sleeve; the cap insert begins above the sleeve. The rigid box is unchanged.
This accessory does not repair the box's reported pull-apart retention failure.

Primary print interchange: [STEP](dental_travel_case_liner.step), matching
[STL](dental_travel_case_liner.stl), [Python entry](dental_travel_case_liner.py),
[parametric design](design.py). The delivered compound contains both inserts,
openings up, with the cap at X +82 mm. Preserve their positions and orientation.

![Cutaway of the long body and short cap inserts](renders/assembled/inspection_isometric.png)

## Intent

On 2026-10-16 the user requests a sound damping liner for the recently printed
slim dental travel box, following existing instructions. When asked about the
already tight packing, the user explicitly chooses **“Use the full S16 liner;
there is room.”** This authorizes the accessory; it does not reopen the stopped
rigid-box redesign. The [printed-box report](../dental_travel_case/notes/m1.md)
remains authoritative for the shell and closure.

The starting profile is the user's [preferred printed S16](../tpu_damping_box/README.md#s16--s12-print-feedback--2026-10-16):
**0.4 mm backing + 0.8 mm air core + 0.4 mm contact skin**, with **0.9 mm ribs**.
This is a starting architecture, not physical approval of this larger liner.

## Geometry and coverage

Nominal lateral installation allowance is **0.2 mm per side**. Both ends reserve
0.2 mm for thin attachment material. Ordinary lower-body lined space is
**66.6 × 43.6 mm**. The sleeve's lined opening is **61.5 × 38.5 mm**, with
**51.5 mm local width between the lined catch guards** near the centre of the
depth. These are nominal sectional dimensions, not a rectangular packing volume.
The narrower regions follow the actual M1 source. The user confirms space for the liner; no measured model
of the combined toothpaste, brush and floss is invented.

The body insert occupies assembled Z **2.2–185.6 mm**; the cap insert
Z **186.4–261.8 mm**, leaving a **0.8 mm seam gap** clear of the rigid overlap.
The body and cap print heights are consequently **183.4 and 75.4 mm**.
End tapers preserve clearance from the rigid R2 interior end blends.

Ribs follow the perimeter normal, including rounded bends and the concave catch
guard notches. Their spacing is at most 4.4 mm, tightened slightly to distribute
the final remainder. Different perimeter patterns meet through 0.4 mm solid
connecting bands. The floor perimeter/root frame, end blends, opening caps and
short transition regions remain locally solid. The sloping guards and sleeve
transition do not have identical compliance to ordinary flat walls. No claim
of uniform cushioning or decibel reduction follows.

The liner's sleeve corners use **R3 mm** instead of following the shell's tight
R1.45 mm cavity bend. This rounds farther inward and leaves room for a real
corner core. An initial smaller-radius draft left one corner completely occupied
by a rib; the corrected design checks every curved bend, including the sleeve.
Coverage is checked on this geometry rather than inherited from straight-wall
samples. Both skins are retained; exposed
open-backed structures are not substituted. No identification recess cuts a skin;
the long body insert and short cap insert are visually distinct.

## Installation

1. Remove strings, inspect both contact skins and clean the inserts before use.
2. Install each insert with the rigid halves separated. Gently collapse/fold the
   TPU walls to pass the narrow mouths, then unfold and seat them. A rigid axial
   drop-in route is not claimed: the body bottom is wider than its sleeve mouth.
3. The indented walls of the body insert align with the existing internal catch
   guards. Never tuck material inside the catch channels or under the hooks.
4. If retention is needed, use small strips of compatible removable double-sided
   tape, **at most 0.2 mm installed thickness**, under the end backing. Do not use
   thick foam tape or fill the air cores with adhesive. Actual adhesion is unknown.
5. Close the empty case gently, check both releases and inspect for pinching.
   Then load the actual contents and compare ordinary carrying noise. Remove or
   adjust an insert that buckles, prevents seating or obstructs a release.

The cups are removable for cleaning and drying. Printed TPU surface cleanliness,
moisture retention and adhesive compatibility are unqualified; no sterilization
or watertightness claim is made. The liner adds no new drainage holes to the
existing closed case. Contents can still strike one another, and seam noise or
the existing closure's movement may remain audible.

## Printing and evidence

TPU 95A is the stock starting assumption; brand and calibrated properties are
unknown. Use the Qidi Q2C and 0.4 mm nozzle. Two walls and 100% rectilinear fill
apply to the modeled material; CAD voids create the air core. The reference
smoke setup uses the local [0.2 mm closed-skin TPU process](profiles/tpu-s16-0p2-process.json),
[TPU filament](../tpu_damping_box/profiles/tpu95a.json) and
[Q2C printer](../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json).
It retains Arachne and thin bridges from the research process and uses
**0.2 mm layers**, including the first layer. The user confirms all earlier
liner prints also used 0.2 mm despite the 0.1 mm instructions; see the
[shared correction](../tpu_damping_box/README.md#actual-liner-layer-height-correction--2026-10-16).
Each horizontal skin
has two layers, and the 0.8 mm core spans four layers. This setup needs its own
gap/path review; the research's 0.1 mm evidence is not transferred. It is a
diagnostic setup, not recovered settings from the user's prints.

Print the full end backings on the bed, openings upward, supports **off**.
Trapped core supports would alter the cushioning. End transitions grow outward
gradually; inward guard ramps, thin skins and narrow sleeve bends require actual
TPU print inspection. Floor roofs bridge between the substantial ribs; the
delivered orientation and process direct their first roof paths across the ribs.
Keep scale at 100%. Opening lips stay flat to preserve the thin skins; they sit
inside the rigid mouths. The narrow flexible lip is intentionally unlettered and has
small plan-view corner radii in the sleeve; it is internal to the rigid box.

The user's [50% ironing-flow preference](../sunglasses_case_liner/README.md#ironing-flow-print-feedback--2026-10-16)
is a starting trial for the upward floor contact face. The reference process has
ironing off. Ironing cannot smooth the vertical walls; if used, inspect the skin
and air channels afterward. Do not confuse ironing flow with normal extrusion flow.

[Verification entry](verification.py) uses the shared command with explicit variant:

```sh
./execute.py model/dental_travel_case_liner/verification.py --variant slim-m1-s16
```

CAD fit is distinct from flexible installation, adhesive retention and actual
quietness. Those physical/subjective questions remain UNKNOWN until feedback.
STL smoke acceptance does not establish Orca's separate GUI STEP import.

The [current verification receipt](notes/verification.json) reports CAD PASS for
all three groups: installed fit/catch movement/sampled cap withdrawal; preserved
flat S16 profile and connected cups; air coverage through every curved bend,
including the small sleeve corners. A deliberately displaced liner is rejected
by the same collision criterion. The [cutaway receipt](notes/inspection.json)
and inspected image show the stepped body, guarded regions and separate cap.
These checks do not establish a rigid insertion path or physical fit.

The [final native receipt](notes/final_review.json) confirms valid geometry and
matching STEP/STL exports. OrcaSlicer **2.4.2**, supplied 0.2 mm TPU triplet,
centred without rotation: primary slice completed with **no keyword notices**.
Estimated pair: **80.50 g / 21 h 58 min 37 s**, not measured.

The [actual path review](notes/path_review.json) and
[headless preview](renders/path_review.png) cover **56 wall/core regions**, including
each curved bend and the guard detours; minimum sampled skin separation is
**0.577 mm** against a local 0.5 mm criterion. Sampled ribs retain at least
**two substantial tracks**. Six floor-channel witnesses remain open; first contact
skins cross the ribs. Native bridge heights are approximately **0.2 mm**.
These are path metadata, not measurements of sagged or compressed printed TPU.
Other insert outlines may appear in the preview where both share a print layer.

The automatic probe proposes **support interfaces only at Z 1.0 mm**, within
the shallow floor channels. No support remains proposed up the guard/sleeve
walls after correction. Primary supports stay off: the floor roofs intentionally
bridge the rib-bounded 3.5 mm channels, and trapped support would fill the core.
The native `review_required` flag is retained with this inspected scope;
actual bridge quality and channel survival remain physical checks.

An [initial 0.1 mm slice](notes/initial_0p1_review.json), before the guard-ramp
correction, completed with a floating-region notice and automatic support signal.
It estimated **43 h 54 min / 84.07 g**. The inner guard cut began abruptly and
created an unsupported initial ledge; the current cutter extends the same
diagonal beyond the cavity so the inner skin starts gradually. The taller
application also motivates reviewing 0.2 mm layers instead of inheriting the
research's requested 0.1 mm diagnostic setting. The user subsequently confirms
all actual liner prints already used 0.2 mm. This historical receipt does not cover
the delivered geometry or setup; no print of that draft was reported.

### Toolpath reader correction

The initial local bridge-height scan expected an extrusion token starting with a
digit. Orca 2.4.2 emitted valid compact values such as `E.89832`, so that scan
collected no bridge heights; its combined assertion misleadingly suggested a
height violation. The corrected reader accepts both compact and leading-zero
forms and separates missing samples from excessive height. This was a reader
failure, not evidence of thick bridge extrusion. Material paths use the shared
`orca_linear_paths` parser; the additional scan reads its missing height metadata.

## Print status

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test pieces | N/A — no new coupon required | Existing S16 research has separate physical approval | Sample approval does not establish application fit or noise reduction |
| Final printable objects | No print reported | `dental_travel_case_liner.step/.stl` | Flexible installation, actual contents fit, closure clearance in print, attachment, skin/channel integrity and quietness untested |

## Attribution

Primary language model: GPT-6 family (exact runtime identifier and reasoning
effort not exposed). Harness: Codex shared-workspace agent; provider OpenAI.
No subagents. Uses the existing M1 shell dimensions and local S16 design evidence;
geometry authored for this accessory. The derived process retains AGPL-3.0;
see its [changes and attribution](profiles/ATTRIBUTION.md) and the upstream
[Orca/Qidi attribution](../tpu_damping_box/profiles/ATTRIBUTION.md).
