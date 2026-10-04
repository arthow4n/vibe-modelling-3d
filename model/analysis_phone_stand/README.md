# Raised open-easel phone stand, revision 2

The current revision implements the user's selected raised open easel, with a
Pixel 7 Pro in its case as the reference and editable generic phone dimensions.
Revision 2 is **rejected before printing**: the user finds it too bulky and
does not want to print it because it occupies too much horizontal desk space,
including the large rear structure and forward-projecting feet. Its files and
analysis are retained as development evidence, not a recommended print. The old
exposed-gear stand was also rejected before printing; its
[discussion and evidence](HISTORY.md) remain historical.

The user authorized autonomous implementation after selecting proposal 1 on
2026-10-04. The architecture review used the complete phone/stand relationship:
raised charging access, broad rear accessory space, positive angle support,
two-handed adjustment and stability. The rear frame and paired prop supply
support outside the ring pocket. A separate keeper prevents the prop lifting
out; springs return the keeper, while solid seats carry ordinary compression.
There is no friction-tightened angle adjustment.

## Rejection before printing and footprint explanation

The user reviewed the implementation and rejects its size. No physical print,
material failure, fit failure or measured tapping response was reported. Earlier
CAD, slice and local numerical checks establish their specific geometry/process
and fixture outcomes; they do not establish a useful desktop product. The
previous complete-prototype print recommendation is withdrawn.

The source chooses a roughly **224 mm wide × 246 mm deep** base. The central
rails are 130 mm across; the rear spring mounts spread to ±112 mm because the
keeper uses long transverse flexures. Rear root position 196 mm, rear guide
position 178 mm and the 120 mm prop package lengthen the rear structure. The
front rail end at Y = −35 mm lies 77 mm ahead of the front pivot at Y = 42 mm.
That forward extension was a chosen support/cable-bay arrangement, not a
calculated minimum for the specified taps.

The static screen tested this chosen footprint with a provisional 0.30 kg phone,
2 N normal upper-screen tap and 0.5 N sideways component, ignoring stand mass.
It found pressure centres inside the selected support rectangle. It did not
optimize the footprint, compare compact architectures, or establish that these
width/depth/front-extension dimensions are necessary. The tap screen covers its
specified loading directions; it is not a universal stability requirement.
Ring and charging clearance informed the raised cradle, but they do not prove
that the complete base must be this large.

The design gave stability margins and low-strain release flexures too much
priority relative to desk footprint. Acceptance of the raised-easel proposal
and permission to extend rear support did not establish acceptance of this final
size. A replacement should revisit the whole support/adjustment architecture
and show its actual desk footprint before detailed mechanism investment. The
Pixel 7 Pro reference, generic case/ring/cable accommodation, hand adjustment,
ordinary-use stability and physical-analysis exercise remain requirements;
the rejected keeper and base dimensions are not requirements. No replacement
geometry is implemented as part of this feedback record.

## Compact replacement discussion — silhouettes only

The latest discussion reconsiders V1's overall visual direction after rejecting
V2's exposed mechanisms and footprint. This is interest in a revised compact
form, not acceptance of V1's existing CAD or evidence that either revision works.
The new requirements still apply: generic Pixel 7 Pro/case fit, portrait/landscape,
broad ring clearance, generous portrait cable space, a few firm viewing angles,
hand adjustment without loosening screws, and meaningful physical analysis.

[Editable SVG comparison](renders/concepts/compact_revision_directions.svg)
([PNG preview](renders/concepts/compact_revision_directions.png)) shows three
candidate forms at a common side-view scale and their target desk footprints
against V1's 80 × 125 mm and V2's 224 × 246 mm bases. These are proposals, not
approved dimensions or printable geometry. The old SVGs remain superseded
appearance/operating records for the rejected products.

| Direction | Target base W × D | Architecture and hand adjustment | Main decision or risk |
| --- | --- | --- | --- |
| A — hooded pedestal | 105 × 140 mm | V1-like single rising support, open fork cradle and low enclosure around a positive angle lock. Support phone, press base release, tilt and let the lock reseat. | Closest visual continuation of V1. Enclosing an indexed lock does not remove its torque, play, tool-access and release-force requirements. No lock geometry is qualified yet. |
| B — compact side pivots | 115 × 135 mm | Short side pods and an open centre. Support phone and release coordinated side locks to tilt. Stock short pivot screws can be considered; no desk adjustment by tightening screws. | Shorter support paths and outboard mechanisms, at the cost of a wider silhouette and paired-lock coordination. |
| C — reseatable cradle | 105 × 145 mm | Open fork carrier plugs into one of three keyed angled seats in a smooth low wedge. Release a small lift-retaining clip, lift the carrier, then insert it into another seat. Seats bear use loads. | Avoids a permanent rotary lock, but adjustment requires lifting/reseating. Removing the phone first may be the comfortable procedure; this is not yet agreed. |

The silhouettes share an 85 × 170 × 13 mm phone assumption, 65° displayed angle,
55 mm illustrative underside clearance and open edge-supported cradle. The
amber side projection reserves 33 mm rear accessory depth; green contact arms
crossing that projection represent outboard contacts, not a central backplate.
Their real lateral positions and the landscape accessory sweep still need
checking. The illustration's 55 mm height is not an established connector/bend
clearance, and the actual phone bottom would move with a real pivot.

A [rough rear-tipping screen](notes/compact_proposal_screen.json) shows the
compactness tradeoff rather than claiming the target footprints stable. For a
0.30 kg phone, the earlier provisional 2 N normal upper tap, constant illustrated
phone location, stand CG at mid-depth, pads 8 mm inward and a chosen 5 mm rear
margin, assumed stand mass would need roughly **185 g for A, 230 g for B and
150 g for C** across the selected angles/orientations. These are conditional
mass targets, not predicted print weights or universal minimum masses. No actual
stand mass/CG, opposite tap directions, sideways stability, desk friction or
lock strength is established. Lower phone height, a different pivot/load layout,
more depth or extra base weight could change the result. No purchase of ballast,
solid-base process or reduction in required tap resistance has been agreed.
The 2 N assumption itself is not a measured user requirement.

A is the preferred starting direction for discussing the user's return toward
V1's form; C is the simpler mechanical alternative if lift-and-reseat adjustment
is acceptable. B trades the central pedestal for side pods. Selection remains
open. Concealing V1's gear alone is inadequate: its solid backing and central
arm must also be changed to preserve the new broad rear clearance.

All options can exercise local structural stiffness, seated contact and
retention/release with existing `StructuralQuestion`, `ContactQuestion`,
`FlexureQuestion`/`SnapFitQuestion` and `QuestionStudy` where the actual fixture
fits those contracts. A/B add pivot-region and lock-load questions; C emphasizes
keyed-seat engagement, clearance, bearing and lift retention. Whole free-joint
assembly response, real thread preload, friction, creep and fatigue remain
outside those qualified fixtures. No new API is justified by a silhouette alone;
concrete gaps should be implemented when a selected product exposes them.

This phase delivers SVG/PNG proposals only. No replacement CAD, exports, slice,
physical trial or approval of a new mechanism is claimed. Existing rejected
sources, exports and native analysis stay historical. The drawing and rough
screen are reproduced by `./execute.py model/analysis_phone_stand/draw_compact_proposals.py`.

## Historical print files and setup

| Plate | Authoritative entry point | Primary export | Secondary export | Process |
| --- | --- | --- | --- | --- |
| Base | [phone_stand_v2_base.py](phone_stand_v2_base.py) | [STEP](phone_stand_v2_base.step) | [STL](phone_stand_v2_base.stl) | PETG, 0.4 mm nozzle, 0.2 mm layers, 2 walls, 7% adaptive cubic |
| Cradle, paired prop, keeper, two guide caps | [phone_stand_v2_mechanism.py](phone_stand_v2_mechanism.py) | [STEP](phone_stand_v2_mechanism.step) | [STL](phone_stand_v2_mechanism.stl) | PETG, 0.4 mm nozzle, 0.2 mm layers, 4 walls, 100% rectilinear |
| Four optional grip feet | [phone_stand_v2_feet.py](phone_stand_v2_feet.py) | [STEP](phone_stand_v2_feet.step) | [STL](phone_stand_v2_feet.stl) | TPU, calibrated filament preset, 0.4 mm nozzle / 0.2 mm layers, solid |

Use the delivered orientations and relative placement. Base rails face the bed;
cradle rear plane, prop's flat arm backs and keeper underside face the bed.
Guide caps and feet lie flat. The keeper's 1.2 mm springs bend in the XY plane.
The separate solid plate supports the homogeneous-solid analysis idealization;
it does not establish isotropic PETG properties or layer bonding. The ordinary
base retains the user's economical settings.

The provided [base process](notes/v2_base_process.json) and
[solid mechanism process](notes/v2_solid_process.json) enable removable automatic
normal supports. Review beneath the keeper roofs, projecting retaining lips,
round prop bar and horizontal nut/pin recesses. These regions are accessible;
remove support carefully from the keeper's retaining undersides and pin holes.
The rear nut counterbores are open for insertion and tools; crossbars sit
above the pivot axes to leave the axial driver approaches clear. The base is roughly
224 × 246 mm: its wider rear spring mounts buy a longer, lower-strain release
spring, and its depth resists taps on the raised phone. Each plate fits the
planned 270 × 270 × 256 mm envelope with likely print aids; actual slice evidence
is reported below. Use your calibrated filament temperatures and speeds.

The feet are compliant press-in parts, with 0.1 mm interference per neck side
and a shallow locating/capture recess. Stand weight bears on their broad pads.
Print these in TPU, not rigid PETG. No calibrated TPU profile is present here;
their PETG diagnostic slice checks geometry/path generation only. TPU-specific
flow, temperature, speed, insertion and desk grip remain unqualified. Omit them
only if the bare base grips the actual table adequately.

## Assembly and adjustment

Hardware comes entirely from the user's Jula assortment. Use an 8 mm nut
driver or spanner for the M5 nuts, 5.5 mm for the M3 nuts, and a driver matching
the supplied screw heads:

- Four M5 × 30 mm screws and eight plain M5 nuts: two lower pivots and two
  prop-to-cradle pivots, each with one captive nut and one inner jam nut.
- Two M3 × 10 mm screws and two M3 nuts for the keeper's spring roots.
- Two M3 × 12 mm screws and two M3 nuts for the printed guide caps.

1. Clear support from recesses, holes and retaining faces. Insert the four M3
   nuts into the underside base recesses; they sit above the table surface.
2. Lay the keeper on the base with the button at the rear. Tighten its two M3 ×
   10 mm root screws. Fit the two printed caps over the guide posts using M3 ×
   12 mm screws. Tighten against the posts, which preserve 0.3 mm slider headroom;
   the screws must not clamp the moving keeper.
3. Insert the first M5 nuts into the cradle's inner hex pockets. Install the
   cradle in the front cheeks and the paired prop at its upper pivots using
   M5 × 30 mm screws from outside. Leave each pivot free to rotate with small
   axial play; do not tighten until the printed cheeks grip the cradle. Hold
   the screw while tightening the second inner nut against the first to lock
   the thread setting. Verify rotation again. Nominal hole diameter is 5.4 mm,
   axial gap 0.25 mm, and minimum nominal thread projection beyond both nuts
   is 3.85 mm. CAD checks include a 12.5 mm outside-diameter nut driver
   approaching each inner jam nut; verify your actual driver and hardware fit.
4. Press the four TPU feet into the underside pockets. Confirm each broad pad
   seats against the base and does not rock.
5. Support the cradle, press the rear button toward the phone and seat the common
   prop bar into a pair of V seats. Release the button; check that both ends are
   seated and the central keeper roof blocks lifting.

The three screen angles are **50°, 65° and 75° above the table**.
[This operating drawing](renders/concepts/v2_adjustment.svg)
([PNG](renders/concepts/v2_adjustment.png)) shows the interaction. Use one hand
to support the cradle. With the other, press the rear button approximately
7 mm forward, lift the rear bar clear of the catches, reposition, lower into
the new pair of seats and let go. Screws stay assembled during adjustment.
Removing the phone first is the easiest initial trial; then check whether loaded
adjustment is comfortable. Do not rely on the keeper to support an unseated prop.

## Phone, ring and cable space

[v2_components.py](v2_components.py) owns the named dimensions and builders.
The design envelope is **170 × 85 × 13 mm**; width/height are conservative design
assumptions rather than measurements of the user's case. Lower ledges and front
lips retain the phone, with separate rear contacts at ±37 mm. They leave the
centre port open. The frame's front is 36 mm behind the phone's rear plane.

CAD checks use a broad 33 mm deep accessory envelope: portrait X ±30 mm,
10–125 mm above the phone bottom; landscape X ±85 mm, 10–60 mm above the bottom.
These include the reported roughly 30 mm hanging reach and a modest allowance
around the roughly 2 mm mounting base. Both sideways landscape offsets are
covered. The unknown ring outline still prevents a universal compatibility claim;
keep the ring inside these zones or revise the parameters. Camera protrusions
are left in the open rear area; no Pixel camera bar is used as a locating feature.

The nominal phone bottom is about 73–87 mm above the table across the angles.
Checks include a 20 mm wide plug extending 30 mm below the phone and a broad
front cable-turn bay 45 mm high. The actual cable's plug/bend requirements remain
a physical check. Portrait and landscape reference entry points are inspection
only and are excluded from print exports.

## Evidence and physical-analysis scope

The [nominal geometry checks](notes/v2_geometry_checks.json) cover forbidden
interference at all three seats, both phone/accessory orientations, charging
space, pin/nut access, sampled keeper release and raised-prop repositioning.
They establish the checked rigid poses, not printed tolerance or continuous
elastic movement. [Static screens](notes/v2_statics.json) use a provisional 2 N
normal tap plus 0.5 N sideways at an upper off-centre screen location. They
ignore stand weight, conservatively, and screen pressure-centre tipping margins
inside the narrower central support rectangle. Desk sliding is a separate
friction requirement, which is why TPU feet are included. No arbitrary tapping,
impact or safety-rated load is claimed.

[analyze_v2.py](analyze_v2.py) exercises three local fixtures, all with explicit
uncalibrated 800 MPa, Poisson 0.38 homogeneous PETG and a provisional 1.5% strain
screen. This is a sensitivity assumption, not a measured property or fatigue limit.

- `StructuralQuestion`: cradle loads from phone weight plus a 2 N upper-screen
  tap, with pivot-boss regions restrained. It includes front-lip reaction for
  the tall portrait phone; it excludes pivot clearance and complete frame dynamics.
- `ContactQuestion`: 5 N upward on the active keeper roof against two stationary
  guide cages. The cages idealize the printed caps and posts as rigid; screw
  preload, thread friction and cap compliance are outside this fixture.
- `SnapFitQuestion`: explicit finger contact, forward release and return.
  This full contact cycle timed out at its 600-second budget; the failed baseline
  stopped all refinements and establishes neither passage nor elastic return.
  `FlexureQuestion` separately tests prescribed button travel as a cheaper
  spring diagnostic; it does not repair that missing contact evidence.

The new shared **ContactQuestion** closes the force-plus-contact question-layer
gap. It reuses existing case/backend, retained-identity and `QuestionStudy`
facilities, preserves unsupported outcomes and shares rigid-mate construction
with `SnapFitQuestion`. Native qualification checks a loaded cantilever closing
a 0.2 mm stop gap, equilibrium and penetration; missing native contact fields
cannot promote an answer. This extends reusable loaded-seat/keeper analysis,
not bolted-joint, rotating-assembly, friction or fatigue simulation. The workflow
guidance to identify and implement justified extensions was already committed
before CAD; no further approval or speculative API framework was introduced.

Qualification: 24 engineering-question tests and 20 physical-analysis tests
passed, including native force/contact fixtures and existing snap consumers.
The coordinator-cache test was also rerun with its isolated instance after
correcting test configuration that had interrupted a product study.

The numerical checks changed the spring and exposed a fixture error. The initial
1.6 mm spring fixture reported 1.80–1.86% strain against the provisional 1.5%
screen, prompting a thinner leaf. Later review found that the restraint extended
onto the narrowed transition; those earlier results remain superseded diagnostics,
not a qualified comparison of the two designs. With the restraint corrected to
the actual full-width root pad, the current 1.2 mm leaf reaches 1.36% at baseline
and 1.35% on the finer mesh, with approximately **2.84 N total ideal release force**.
Mesh and increment comparisons meet the chosen 20% decision tolerance without
changing acceptance. These are local guided-spring results, excluding guide
friction, real thumb contact, printed return and fatigue.

The final M5 cradle baseline predicts **0.63 mm** maximum displacement and
**0.25%** strain under its specified service fixture. No finer study qualifies
this final geometry. A finer mesh of the earlier M4 cradle failed Gmsh's
high-order optimization; that historical result cannot qualify the revised part.
The corrected keeper lifting fixture predicts **1.17 mm** displacement and **0.27%** strain
under **5 N** upward, with **0.0048 mm** maximum penetration and adequate force
balance. Its 2 mm provisional displacement allowance applies to accidental
lift against the keeper, not phone wobble under seated service compression;
positive capture remains, while the V seats carry ordinary use. Doubling the contact penalty changes displacement
by 0.13% and strain
by 0.04%; that comparison is stable. The finer holder mesh timed out at its
600-second budget, leaving mesh sensitivity and overall numerical adequacy
unresolved. These outcomes remain in the native records and do not establish
print validation.

Current native evidence: [guided spring study](notes/v2_analysis/spring_final_m5/study_result.json),
[final cradle baseline](notes/v2_analysis/structure_m5_2048/result.json),
[keeper lifting study](notes/v2_analysis/holding_study_recovered/study_result.json).
The [analysis ledger](notes/v2_analysis/README.md) separates current fixtures,
superseded attempts and unsupported operations.

All three layouts produced valid CAD and matching STEP/STL pairs. OrcaSlicer
2.4.2 completed the [base](notes/v2_base_final_review.json),
[mechanism](notes/v2_mechanism_final_review.json) and
[feet diagnostic](notes/v2_feet_diagnostic_review.json) with no notices.
The PETG plates generate support; the feet diagnostic does not. The
[selected-layer review](notes/v2_support_review.png) confirms accessible support
in underside foot/nut recesses, through the horizontal pivot openings and beneath
keeper roofs/cradle lips. Remove these before assembly, preserving the flat
retaining surfaces. Actual PETG support removal remains untested.

[Actual local path sections](notes/v2_solid_sections.json) fill both 1.2 mm
spring spans and the selected cradle ledge/rear-pad sections within 0.006 mm
of their nominal widths. This supports those local solid idealizations only.
The slice checks the matching STL, not Orca's separate GUI STEP import, and
the feet's PETG diagnostic does not validate a TPU process. Solver completion,
refinement, provisional acceptance and physical limits stay separate.

## Withdrawn first-print trial

The following trial plan predates the product rejection and is retained for
history. It is not a recommendation to print this revision or its keeper coupons.

The original plan was to use the complete stand as the first trial: phone
placement, ring freedom, charging, two-handed adjustment and tipping/grip depend on its full geometry.
A small coupon would omit those interactions while preserving much of the keeper
and guide printing effort. Preserve the delivered orientations and PETG solid
mechanism settings; use TPU feet and the actual phone/cable.

First check unloaded pivot freedom, full keeper return and all three pairs of
seats. Place the phone in both orientations, connect the cable in portrait and
confirm the ring hangs freely. Apply ordinary taps at the centre and corners;
watch phone play, stand sliding and tipping separately. Check release/reseating
with the cradle supported, then repeat after a period under phone weight.
Accept the interface only if it seats both ends, returns without assistance,
blocks unintended lift and remains comfortable. Binding, failure to return,
noticeable tapping motion, cracking or growing play calls for a revised part;
do not compensate by tightly clamping an adjustment pivot. Unknown fatigue and
creep mean a short successful test does not establish durability.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | N/A | No separate coupon | Rejected product does not warrant a mechanism coupon |
| Final printable object(s) | No | `phone_stand_v2_base`, `phone_stand_v2_mechanism`, `phone_stand_v2_feet` STEP/STL pairs | Rejected before printing: excessive horizontal footprint, large rear structure and forward-projecting feet. No physical failure observed; local evidence retained, print recommendation withdrawn |

## Attribution

Revision 2 and ContactQuestion integration: GPT-6 family, Codex API agent, OpenAI;
specific runtime variant and reasoning effort are not independently exposed.
No sub-agents contributed. Historical attribution is preserved in
[HISTORY.md](HISTORY.md#attribution). Source and analysis integration remain under
the repository MIT licence; external CalculiX/Gmsh have separate licences.
