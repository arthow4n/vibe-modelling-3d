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

## Analysis and verification

[Geometric and static checks](check_v3.py) cover component interference, sampled
rotation/release/insertion, bidirectional angle capture, pin capture, cable and
ring envelopes, and full-product pressure centres. The solid PETG density
assumption is 1.27 g/cm³; geometry mass is used specifically for tipping.

The provisional service screen combines a **2 N upper-screen press with 0.5 N
sideways force**, and separately a light **0.5 N outward disturbance**. An
additional **2 N outward pull is a diagnostic case and can tip this compact
stand**. It is not promoted into a passing service result. These loads are
chosen screens, not measured user forces. Desk sliding depends on actual feet
and friction, which this static calculation does not establish.

[Engineering fixtures](analyze_v3.py) use `FlexureQuestion`, `ContactQuestion`
and `StructuralQuestion`; planned refinements use `QuestionStudy`. All numerical
material screens assume uncalibrated isotropic E = 800 MPa, ν = 0.38 and a
provisional 1.5% strain limit. These are conditional short-term screens, not
printed strength, fatigue, creep or physical return qualifications.

The new shared API permits **supported deformable mating bodies**. The printed
housing can share strain and load with the lock nose instead of being fixed as
an undeformable obstacle. Explicit supports, loads/materials and per-body strain
screens reuse the existing multipart backend. Rigid-mate identities remain intact.
The first fixture directed reinforcement to the nose rather than the housing;
that is a concrete design consequence. An independent equal-cantilever benchmark
qualifies load sharing, equilibrium, penetration and retained identity. The API
still excludes free rotating joints, friction and screw/thread preload.

The original thin fork exceeded its 1 mm deflection screen under the chosen
phone/tap load. Its bridge, neck and side rails were deepened behind the open
accessory space, and the contact standoffs thickened. The earlier geometry is
retained as failed development evidence. A broad spring attachment avoids an
artificial narrow-tip fixture, and the release stop limits actuation strain.
Pocket depth was reduced to 2 mm while retaining positive engagement and wider
material between pockets.

Final outcomes, with input identities in the linked native records:

| Question | Result | Qualification limit |
| --- | --- | --- |
| Rigid fit, assembly and sampled movement | [CAD checks](notes/v3_checks.json) pass at all three angles, including portrait/landscape accessory reserves and pin/slot capture. | Nominal geometry; printed play and binding unknown. |
| Compact-footprint tipping | Minimum service pressure-centre margin **18.2 mm**, conditional on 373 g solid stand mass. Required friction reaches about 0.28 in the selected tap cases. | A 2 N outward diagnostic pull tips some poses; desk friction unmeasured. |
| Guided 3 mm release | [Study](notes/v3_analysis/guided_release/study_result.json): peak strain **0.58%**, two-leaf reaction-norm bound **0.28 N**; motion-increment comparison stable. | Mesh refinement not qualified. Contact friction, root play, fatigue and physical recovery excluded. |
| Lock nose and deformable housing | [Study](notes/v3_analysis/current_guide/study_result.json): baseline strains **1.16% / 0.35%**, maximum displacement **0.204 mm**; refined nose strain **1.34%**. Mesh and penalty comparisons meet the specified 20% tolerance. | Idealized rail/housing restraints, frictionless contact; all are below the provisional 1.5% strain screen. |
| Full cradle | [Native result](notes/v3_analysis/stiff_cradle/result.json): maximum deflection **0.904 mm**, peak strain **0.189%**. | Fixed pivot neighbourhood, one baseline; excludes hinge play and rotor-pocket compliance. |
| Final exports and slice | [Core](notes/v3_final_review.json): valid CAD, paired STEP/STL, completed Orca 2.4.2 slice on Qidi profile. Support signal reviewed above. [Feet](notes/v3_feet_diagnostic_review.json): exports and support-free diagnostic slice. | Feet slice uses PETG, not TPU qualification. Separate GUI STEP import was not checked. |
| Solid-section assumptions | [Actual toolpath sections](notes/v3_solid_sections.json): sampled leaves, nose, guide, cradle standoff and ledge are filled to within 0.007 mm in the width-based path screen. | Local paths support the solid approximation, not isotropic material properties. |

The earlier pocket-web solve used a 3 mm pocket depth, so it does not qualify
the final 2 mm depth. A simple 30 N / (16 × 2 mm) nominal flank-bearing screen
gives 0.94 MPa; an idealized 2 mm long, 16 mm wide web with a conservative 2 mm
thickness gives about 0.70% strain at E = 800 MPa. These omit edge concentration and
nonuniform engagement. Pocket wear, printed pin retention and full joint load
sharing remain physical checks, not completed assembly FEA.

Shared API verification: **46 tests passed** across engineering questions and
physical analysis; both new deformable-mate fixtures also passed a subsequent
targeted rerun. Current release, guide and cradle records were read through their
question identity guards. Failed development screens, interrupted runs and
timeouts remain distinct from this evidence. Compact archives exclude large
raw fields; full native working directories remain locally under
`notes/.execution/v3_analysis_raw/` for the requested investigation.

## Timeout investigation requested by the user

On 2026-10-04 the user requested a follow-up investigation after the modelling
work: timeouts should be diagnosed and prevented where practical, rather than
accepted as the normal analysis workflow. Keep the retained run/input identities.
The follow-up review distinguishes mesh compilation errors, native nonlinear
iteration cost, matrix/mesh growth, resource/admission wait, extraction cost,
and explicit cancellations. Relevant cases include `release`, `release_leaf`,
`folded_release`, `folded_release_resolved`, `working_leaf`, `reinforced_guide`,
`flat_guide` and the pocket/cradle mesh refinements under `notes/v3_analysis/`.
Failed design strain/deflection screens are a different category from timeouts.
Do not loosen equilibrium, penetration or design limits to make a run appear
successful. Diagnose from the saved logs and automatic execution records, then
qualify any justified solver, fixture or execution improvement separately from
product acceptance.

The bounded investigation after the modelling handoff found:

| Evidence | Finding and action |
| --- | --- |
| `release` and `release_leaf` | Gmsh reports a 1D loop compilation error in under 0.5 s. `folded_release` aborts high-order optimization in about 2.2 s. These are meshing failures, not timeouts. The exact geometric/optimizer cause remains unproved; no permissive mesh-quality workaround was added. |
| `folded_release_resolved` | Refining the full leaf/root/bore fixture produced 96,526 nodes; only one load increment converged by the 300 s deadline. The final fixture keeps the actual working leaf and replaces the stout root continuation with an explicit restraint; 28,775 nodes and the guided baseline finishes in 68 s. Geometry/constraints changed, so this is not a same-input solver speedup. |
| Refined guide, cradle and pocket | Node count grows about 2.2–2.4× from each baseline. Their saved increment records show progress when killed: guide 0.4, cradle/pocket 0.5 of the requested interval. Matrix factorization and nonlinear iterations dominate these logs; no deadlock was observed. The symmetry-reduced current guide completes both refinements. The old cradle's 6.6 mm deflection already decisively failed the 1 mm target; refining it was an avoidable expense. Revise such geometry before further solves. |
| `working_leaf` | The forward/reverse fixture finishes in 282 s with 20 converged increments, 83 logged iterations and four cutbacks. It also fails its design screen. It is slow completed evidence, not a timeout; the final physical guide and 3 mm travel replace the earlier free lateral/5 mm motion assumptions. |
| Execution run `5d93a765…` | A geometry check waits **511.9 s**, then is explicitly cancelled before admission. Two four-core leases occupy the eight-core capacity, although this native route uses one thread. Final commands use `--threads 1`. No global capacity or solver-thread policy changed. |
| Runs `9fda71b9…` and `7c09b4ac…` | Agent-chosen outer caps expire at 600 s. The latter study already spends 109 + 202 s on its first two runs, leaving less than its invented 300 s native cap; the former also waits 16.5 s for admission. These unjustified caps interrupted useful computation and are removed. Historical cancellations remain incomplete evidence. |
| Runs `5b384805…` and `f5ac0b8…` | Each waits about 66 s and is then rejected because the script changed while queued. Freeze Python edits during dispatched work; the identity guard correctly prevents stale publication. |

[Selected automatic execution records](notes/v3_timeout_execution_records.json)
retain the native summaries and identities behind the queue/outer-deadline
findings. The archived solver logs and increment records retain the native
failure/progress evidence. This review is observational; different fixtures and
machine contention prevent a universal timing prediction.

A concrete reporting defect was corrected: `lifecycle.wait` previously discarded
its sampled resources when it raised `TimeoutExpired`, leaving timed-out native
results without the CPU/RSS/elapsed summary available for successful runs. It now
attaches that summary, and the backend preserves it in provenance while keeping
the timeout status and process-group termination. **Six targeted tests pass**,
including real timeout persistence, process termination, interrupted-worker
handling and command recovery. Solver, equilibrium, penetration and material
limits are unchanged. Historical records retain their original missing fields.

The first investigation explains the observed progress and execution failures;
a controlled diagnosis of the original Gmsh loop/high-order failures remains
unsupported. The retained failing inputs are available for separate reproduction.

The user rejected the agent-invented 180/240/300 s analysis caps and the
600/900 s outer-cap policy. **All current stand fixtures now run without a
runtime deadline.** The shared analysis API, CAD evaluation, slicing, diagnostics
and recovery also use uncapped defaults, so removing an object override cannot
silently restore another arbitrary cap. The
[repository workflow](../../AGENTS.md#shared-engineering-execution) prohibits
inventing these deadlines. Historical timeout records retain their original
inputs and status; elapsed times are observations, not future limits.
Use one CPU thread and fresh output directories:

```sh
./execute.py --threads 1 model/analysis_phone_stand/analyze_v3.py release model/analysis_phone_stand/notes/.execution/release_new --study
./execute.py --threads 1 model/analysis_phone_stand/analyze_v3.py guide model/analysis_phone_stand/notes/.execution/guide_new --study
```

Assess whether computation answers a useful question from its progress and
evidence. Taking longer than expected alone does not justify terminating it.

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

## Articulated release access

The [product-local kinematic study](human_interaction.py) asks whether an assumed
arm/palm/index model can contact the **rear centre of the release button**, approach
from 40 mm behind it, maintain contact through its prescribed 3 mm stroke, and
withdraw while released. This is a useful pre-print question because clear solved
endpoints can hide a colliding hand transition. V3 was selected over the already
successful jar/case and the discontinued swatch damping direction: it has an
unprinted, consequential press-and-tilt interaction. No product was redesigned.
This investigates only the button hand, not the other hand supporting/tilting the
phone or the complete two-hand operation.

[Retained receipt](notes/v3_human_interaction.json) contains replayable independent
joint states, per-start contact/normal errors, individual joint margins, palm/elbow
positions, named clearance violations and penetrations, press transitions and
first invalid path witnesses. It is an explicit output, not a search-result cache.
[Diagnostic side projection](notes/v3_human_interaction.png) omits X separation;
the native pair distances, not apparent overlaps in that image, decide collision.

The stack is **MuJoCo 3.15.0 + NumPy 2.5.3 + SciPy 1.18.1**, using the current
Python 3.13 locked environment. MuJoCo supplies forward kinematics and
[signed primitive distances](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mj-geomdistance).
Bounded SciPy least-squares supplies local IK with collision penalties; returned
states are independently checked. [Mink](https://kevinzakka.github.io/mink/api/limits.html)
provides useful differential IK/linearized limits, but another IK/QP/Clarabel stack
was unnecessary for this small fixed-contact question. [MyoArm](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/models/arm/README.md)
has detailed anatomy and muscles; that asset/model complexity has not earned its
place in this initial geometric screen. No imported anatomical data or external
model assets are used. This does not qualify physiological feasibility, muscle
forces or any anatomical accuracy. The assumptions below are repository-owned,
not an anatomical model copied from those projects.

### Setup and collision scope

World axes match `v3_components.py`: X across, Y rearward, Z up, millimetres in
CAD/reports and metres in MuJoCo. The stand is at 60°, with the assumed portrait
phone envelope present, desk plane at Z=0 and a fixed shoulder at **(80,500,330) mm**.
No calibrated user/torso setup, thumb, actual ring, cable or support hand is modeled.
Upper arm/forearm lengths are 280/250 mm with capsule radii 35/28 mm. The palm is
76 × 80 × 28 mm; index segments are 45/25/18 mm with 9/8/7 mm radii and a 7 mm
spherical pad. Other fingers are a fixed curled envelope; their independent
articulation and soft tissue are excluded. These are explicit engineering
hypotheses, not measured user dimensions or population percentiles.

Eleven declared hinge coordinates represent three shoulder rotations, elbow,
forearm rotation, wrist flexion/deviation and index abduction/MCP/PIP/DIP. The ten
independent coordinates determine DIP = 0.65 × PIP. Declared axis-coordinate ranges
are shoulder X/Z ±100°, shoulder Y ±90°, elbow 0–145°, forearm ±80°, wrist flexion
±70° and deviation ±25°, index abduction ±15°, MCP −10–85°, PIP 0–100°, DIP 0–70°.
These Euler/hinge ranges and coupling are **assumptions, not clinical restrictions**.
All returned joints, including the coupled DIP, are checked against them.

The collision fixture calls the authoritative builders for base, placed cradle,
slider, pin and phone. It partitions current CAD at object-local clipping planes
and boxes every portion, preserving whole-component coverage while avoiding a
single hull filling all access space. Bounds here deliberately construct collision
proxies, not another export audit. Holes, recesses and rounded edges are filled;
these conservative boxes can reject real free space. The centre of the button's
actual rear flat face is derived from its CAD portion. The button translates by
the declared stroke; the front slider uses a fixed ±3 mm swept Y reserve instead
of translating its anchored roots. Spring-deformed surfaces are not generated;
this swept reserve is an explicit analysis assumption, not a deformable solve.
CAD source and human-script/lock digests, tool versions, setup, boxes and targets
are retained with each study. Geometry changes require rebuilding/rechecking the
fixture; the regression moves the authoritative slider builder and observes the
corresponding target change.

Eight human proxies are queried against eleven product boxes and the desk
(**96 explicit obstacle pairs**), plus **18 explicit nonadjacent self pairs**.
Queries use native signed distances independently of automatic contact masks;
zero MuJoCo contacts is not the criterion. Same-body/composite and directly
adjacent joint neighbours are excluded because their proxy overlaps are
intentional. Thumb, soft tissue, other-finger articulation, torso and these
exclusions prevent a claim of complete anatomical self-nonpenetration.
The requested spherical pad/rear-centre patch is the sole allowed contact,
with at most 0.05 mm penetration; side/back/button contact is not generally
licensed. Other pairs must retain 0.2 mm clearance. Contact-centre tolerance is
0.25 mm and distal-axis normal tolerance 10°. These are local numerical/geometry
screens, not comfort or ergonomic limits. A declared 0.1 mm optimization buffer
helps avoid penalty solutions just below the unchanged acceptance clearance.

### Qualification and interpretation

Six seeded initializations (7301) each receive at most 180 least-squares function
evaluations per solve. Optimizer termination is neither necessary nor sufficient
for state acceptance. Uniformly scaling human geometry while keeping the shoulder
fixed is a **model sensitivity study**, not physiological personalization.

| Human geometry hypothesis | Accepted endpoints / 6 | Complete sampled interactions / 6 | Distinct endpoint clusters | Interpretation |
| --- | --- | --- | --- | --- |
| 0.9 scale | 2 | 2 | 1 | Declared model finds approach, held press and withdrawal. |
| 1.0 scale | 2 | 0 | 1 | Endpoints found; tested approach/withdrawal cross desk. Full access INCONCLUSIVE. |
| 1.1 scale | 2 | 0 | 1 | Endpoint found; tested approach/withdrawal cross desk. Full access INCONCLUSIVE. |

The nominal candidate's pre-contact and contact poses both pass, yet its sampled
interpolated palm penetrates the desk by about **0.45 mm**. Withdrawal also fails.
A second nominal candidate has accepted initial/0.5 mm press poses but an interior
held-contact state penetrates the button beyond the 0.05 mm allowance. These are
modeled counterexamples to endpoint-only reasoning, **not physical product
failure or impossibility**. Alternative paths, shoulder placement and richer
anatomy were not exhaustively searched. The scale-dependent outcome warns against
transferring one witness to an assumed human population.

Accepted nominal endpoint contact error is about 0.004 mm with 1.10° normal error;
several shoulder, forearm, wrist and index coordinates approach their declared
limits. The smaller model also has near-limit joints. Reported tiny margins are
numerical descriptors, not a claim of easy or comfortable use. A greedy diversity
rule separates representatives by >=30 mm elbow displacement OR >=20° maximum
independent-joint difference; only one cluster was found per hypothesis. That
neither establishes a unique solution nor supplies a population claim.

Approach/withdrawal interpolate joints between independently solved states.
Held press is solved at 0.5 mm stroke increments, then the **nonlinear forward
kinematics between states** is checked. Samples limit independent-joint increments
to 2° and stroke increments to 0.5 mm; contact remains checked during actuation.
These are sampled paths, not continuous-path guarantees. Optimizer trial iterates
may collide and are never interpreted as physical movement; only the declared
transitions receive path evidence. The 40 mm pre-contact
state is a local start, not a path from an arbitrary resting posture. Withdrawal
prescribes the slider held released; spring-driven return is excluded.
A denser 41-point desk-gap plot illustrates the same witness without upgrading
sampling into a proof. There are no dynamics, force, friction, soft contact,
fatigue, comfort, safety or physical-accessibility conclusions.

### Evidence integration and reproduction

[verification.py](verification.py) adopts only the existing recorded adjustment
intent, with its [protected inventory](notes/verification_sources.json), because
kinematic access and physical operation now need separate questions. Other V3 CAD,
mechanical, statics and slice evidence above stays with its existing checks and
records; this is not a mechanical migration of all stand studies. The shared
`product_verification` CLI reports endpoint PASS independently of access
INCONCLUSIVE, while actual integrated operation stays physical UNKNOWN.
The adapter replays retained joint states and sampled paths on **current CAD**;
stored acceptance flags/counts cannot supply PASS. Missing/stale receipt or native
identity mismatch gives UNKNOWN; malformed attempted evidence gives INCONCLUSIVE.
A finite search with no complete witness gives INCONCLUSIVE, not physical FAIL.
Later user rejection cannot be overwritten by these computational questions.

From the repository root:

```sh
./execute.py --threads 1 model/analysis_phone_stand/human_interaction.py --output model/analysis_phone_stand/notes/v3_human_interaction.json
./execute.py --threads 1 model/analysis_phone_stand/view_human_interaction.py
./execute.py --threads 1 model/analysis_phone_stand/verification.py --variant v3-60-nominal
./execute.py --threads 1 model/analysis_phone_stand/verification.py --variant v3-60-scale-0.9
uv run --locked pytest -q tests/test_human_interaction.py
```

Both verification variants exit 0 when their reports complete: nominal has access
INCONCLUSIVE plus physical UNKNOWN; the smaller hypothesis still has physical
UNKNOWN. Shell success does not qualify the product; read the JSON outcomes.
Use `--help` for the shared CLI choices. The explicit study does not
implicitly rerun from verification; no extra cache, scheduler or evidence database
was added. [Semantic regressions](../../tests/test_human_interaction.py) preserve
static/path differences, held contact, signed distances with disabled contacts,
coupling/limits, constant maximum stroke, authoritative target changes and stale,
malformed or forged acceptance receipts. Product-local code retains geometry,
setup, criteria, solver and replay choices; one consumer has not justified a shared
package. The [living skill](../../.codex/skills/articulated-human-interaction/SKILL.md)
teaches this qualified workflow and permits improvements supported by real work.

Qualification also ran the product-verification core/CLI/entrypoint, assembly-geometry
and execution regressions together with the human tests: **178 passed**. The reusable skill validator and
locked dependency check passed. The accidental Python 3.14 working-tree change
was corrected to the committed Python 3.13 contract; final receipts and checks
use that environment, without an environment migration or JSON-contract change.

No CadQuery product source, STEP/STL, print placement or manufacturing settings
changed. V3 remains unprinted/unqualified for actual operation. The most useful
next extensions would compare justified approach waypoints/setup placement and
include the supporting hand or actual accessories. Detailed anatomy, additional
finger contacts or force predictions need an actual consumer and separate
qualification; they are not implemented here.

Capability contribution: GPT-6-based Codex (exact runtime variant and reasoning
effort not exposed), Codex shared-workspace API agent, OpenAI. Independent skill
and implementation review used a Codex subagent under skill-creator forward-testing
guidance, with no model/effort override; historical attribution
above remains unchanged.
