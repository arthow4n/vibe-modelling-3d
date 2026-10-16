# Phone stand V3 — mechanics, access and execution investigations

[Current product, assembly, printing and status](../README.md) ·
[V2 rejection/history](../HISTORY_V2.md) · [V1 history](../HISTORY.md)

These investigations answer different questions. A local mechanics or kinematic
PASS does not qualify the unprinted product. The README owns current product
instructions; the records here preserve fixtures, results, failures, assumptions,
commands and contribution attribution.

- [Mechanics and verification](#analysis-and-verification): why the fork and lock
  changed, numerical outcomes, quality and manufacturing limits.
- [Current MyoArm release access](#articulated-release-access): imported anatomy,
  setup sensitivity, contact/collision exclusions, replay and physical UNKNOWN.
- [Timeout investigation](#timeout-investigation-requested-by-the-user): what was
  meshing failure, useful slow progress, admission wait or cancellation.
- [Historical synthetic access](#historical-synthetic-release-access): the earlier
  invented anatomy and counterexamples, retained for regression/history only.

Runtime versions and test totals below describe their recorded milestones.
They are not current installation requirements: consult [pyproject.toml](../../../pyproject.toml)
and [uv.lock](../../../uv.lock). In particular, the synthetic study's argument
against importing anatomy was superseded by the current MyoArm correction.
Neither the historical suggestions nor the remaining evidence gaps authorize
additional product work.

## Analysis and verification

[Geometric and static checks](../check_v3.py) cover component interference, sampled
rotation/release/insertion, bidirectional angle capture, pin capture, cable and
ring envelopes, and full-product pressure centres. The solid PETG density
assumption is 1.27 g/cm³; geometry mass is used specifically for tipping.

The provisional service screen combines a **2 N upper-screen press with 0.5 N
sideways force**, and separately a light **0.5 N outward disturbance**. An
additional **2 N outward pull is a diagnostic case and can tip this compact
stand**. It is not promoted into a passing service result. These loads are
chosen screens, not measured user forces. Desk sliding depends on actual feet
and friction, which this static calculation does not establish.

[Engineering fixtures](../analyze_v3.py) use `FlexureQuestion`, `ContactQuestion`
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
| Rigid fit, assembly and sampled movement | [CAD checks](v3_checks.json) pass at all three angles, including portrait/landscape accessory reserves and pin/slot capture. | Nominal geometry; printed play and binding unknown. |
| Compact-footprint tipping | Minimum service pressure-centre margin **18.2 mm**, conditional on 373 g solid stand mass. Required friction reaches about 0.28 in the selected tap cases. | A 2 N outward diagnostic pull tips some poses; desk friction unmeasured. |
| Guided 3 mm release | [Study](v3_analysis/guided_release/study_result.json): peak strain **0.58%**, two-leaf reaction-norm bound **0.28 N**; motion-increment comparison stable. | Mesh refinement not qualified. Contact friction, root play, fatigue and physical recovery excluded. |
| Lock nose and deformable housing | [Study](v3_analysis/current_guide/study_result.json): baseline strains **1.16% / 0.35%**, maximum displacement **0.204 mm**; refined nose strain **1.34%**. Mesh and penalty comparisons meet the specified 20% tolerance. | Idealized rail/housing restraints, frictionless contact; all are below the provisional 1.5% strain screen. |
| Full cradle | [Native result](v3_analysis/stiff_cradle/result.json): maximum deflection **0.904 mm**, peak strain **0.189%**. | Fixed pivot neighbourhood, one baseline; excludes hinge play and rotor-pocket compliance. |
| Final exports and slice | [Core](v3_final_review.json): valid CAD, paired STEP/STL, completed Orca 2.4.2 slice on Qidi profile. Support signal reviewed in the [current print setup](../README.md#print-setup-and-remaining-physical-checks). [Feet](v3_feet_diagnostic_review.json): exports and support-free diagnostic slice. | Feet slice uses PETG, not TPU qualification. Separate GUI STEP import was not checked. |
| Solid-section assumptions | [Actual toolpath sections](v3_solid_sections.json): sampled leaves, nose, guide, cradle standoff and ledge are filled to within 0.007 mm in the width-based path screen. | Local paths support the solid approximation, not isotropic material properties. |

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

## Articulated release access

The current foundation is **MyoSim MyoArm**, loaded from the locked standalone
`myo-sim==0.2.3` distribution as `myoarm_r`. The right arm and hand are appropriate
because rear-release access depends on whole-arm placement and other digits, not
just an isolated index. The library includes a passive torso scaffold, shoulder
girdle, humerus, ulna/radius, wrist/carpals, metacarpals, thumb and four fingers.
The [maintained source](https://github.com/MyoHub/myo_sim) and
[model notes](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/models/arm/README.md)
own anatomy. It is Apache-2.0 licensed; assets are dependencies, not copied into
this product. MyoSim/MyoSuite attribution: Caggiano, Wang, Durandau, Sartori and Kumar,
[MyoSuite, 2022](https://arxiv.org/abs/2205.13600). Imported anatomy is a model,
not a measurement of this user or a guarantee of anatomical accuracy.

[human_interaction.py](../human_interaction.py) owns the product question, scene,
solver and interpretation. MuJoCo 3.15.0 supplies FK and signed distances; bounded
SciPy 1.18.1 least squares remains suitable for this kinematic contact search.
NumPy is 2.5.3 and Python remains 3.13.15. No Mink/QP, MyoSuite task framework,
muscle-force optimizer, shared model registry or new scheduler was needed.

### Imported constraints and setup

All **38 imported hinge coordinates**, ranges, axes and collision sizes are
preserved. Eleven active affine joint equalities couple shoulder-girdle motion;
the solver eliminates them exactly, leaving **27 independent coordinates**.
Master ranges are intersected with dependent ranges, and every submitted state
is independently checked. Both index interphalangeal joints are independent;
the historical invented DIP/PIP coupling is gone. The other digits participate
in the solve, rather than becoming a guessed curled envelope. Imported 63 muscle
actuators and 67 tendons remain in the model; none of those tendons has an active
length limit. Actuation is disabled; dynamics, passive/muscle forces and physiology
are not used or qualified.

CAD/report axes are X across, Y rearward, Z up in mm; MuJoCo uses metres. The entire
unchanged reference anatomy rotates +90° about world Z, then translates its
neutral humerus origin to **(80,500,550) mm**. This is an unmeasured setup reference,
not a fixed humerus during shoulder motion; imported girdle relationships remain
active. The passive torso moves with that scene transform. A local sensitivity
uses shoulder Y=450 and 550 mm, with identical anatomy. No anthropometric scaling
or percentile claim is made. The former shoulder Z=330 mm belongs to the synthetic
history below. At that height the imported passive torso's fixed skin proxies
intersect the infinite desk plane by about 133 mm, before any arm search; the
collision audit retains this setup mismatch. Z=550 avoids that fixed overlap and
provides a reference scene for reach qualification; it is not a typical seated
user claim. Actual torso/desk-edge placement needs separate setup qualification.
Supporting hand, actual ring/cable and soft tissue remain absent.

### Contact and collision qualification

Current CadQuery builders still own every product component and selected 60°
assembly. The previous partitioned conservative boxes, phone envelope, desk plane,
rear button face, prescribed 3 mm stroke and front-slider swept reserve are reused.
Holes/rounding are filled; these boxes can reject real free space. There is no
independent simulator product design or spring-deformed geometry.

Contact uses the **+local-Z surface pole of the imported index skin ellipsoid**
`distph2_coll_2_r`, with its outward normal toward the button. The imported `IFtip_r`
marker is not on this contact skin and is reported separately. Only that pad/patch
may touch the button: 0.25 mm patch error, 10° normal error, at most 0.05 mm native
penetration. All other checked pairs require 0.2 mm clearance. A 0.1 mm optimizer
buffer does not change acceptance. These are numerical screens, not user criteria,
comfort dimensions or anatomical limits.

The receipt audits **36 imported anatomical collision geoms**, **432 human/product
and desk pairs**, and **264 self pairs**, including all four imported torso/arm pairs.
Visual meshes and muscle wrap geoms are not treated as skin. Upstream anatomical
masks use `contype=1`, `conaffinity=0`; no contacts does not imply nonpenetration.
Native signed queries explicitly check selected cross-digit phalanges, nonadjacent
same-digit segments and finger/arm pairs. All 366 excluded pairs are listed.
Same-body, adjacent/composite, palm/wrist composites and hand/torso coverage are
incomplete; the metacarpal capsules do not form complete palm skin.

The imported radius/metacarpal capsules overlap by roughly 1–7 mm at neutral wrist.
A proximal middle/ring proxy pair also overlaps despite disabled automatic contact.
[audit_myoarm_collision.py](../audit_myoarm_collision.py) samples 2,401 combinations
of those fingers' imported MCP ranges; [its receipt](myoarm_collision_audit.json)
finds −15.32 to −0.587 mm signed distance. This is finite representation evidence,
not proof over every pose or physiological validation. Those composite pairs are
explicitly excluded from supplemental self checks without resizing skin. Digit
self-nonpenetration remains a limitation; exclusions are not anatomical PASSes.

### Results and sensitivity

[The new schema-2 receipt](v3_myoarm_interaction.json) records package/source
and asset digests, versions, anatomy audit, setup, collision fixture, screens,
search settings, failed candidates and replayable joint states. Each setup uses
six initializations: imported reference qpos plus five seeded (7301) starts within
all independent ranges. Each solve permits 180 function evaluations. Optimizer
termination never substitutes for independent acceptance.

| Shoulder Y (mm), Z=550 | Accepted endpoints / 6 | Complete interactions / 6 | Interpretation |
| --- | --- | --- | --- |
| 450, nearer | 1 | 1 | Found sampled 40 mm approach, maintained 3 mm press and withdrawal. |
| 500, nominal | 1 | 0 | Approach and press found; withdrawal violates clearance. Access INCONCLUSIVE. |
| 550, farther | 0 | 0 | No accepted endpoint found under this search; INCONCLUSIVE. |

Only one descriptive endpoint cluster was found per successful setup; this is not
uniqueness or exhaustive coverage. The nominal endpoint has 0.166 mm contact error
and 1.44° normal error; its index PIP range margin is about 0.0044°. The nearer
endpoint has 0.0064 mm error, 0.067° normal error and wrist deviation near its
imported lower range. Such margins describe this model, not comfort or easy use.
Position diagnostics use body references: `palm_mm` is the lunate/wrist frame and
`elbow_mm` is the radius origin, not measured surface landmarks.
Setup position materially changes the finite screen; importing anatomy does not
remove placement uncertainty. These outcomes neither reproduce nor invalidate
the old uniform-scale study: they concern different anatomy and setups.

Approach/withdrawal interpolate independent joints; press is solved at 0.5 mm
increments with held contact checked between states. FK/collisions/limits are
sampled at <=2° independent-joint and <=0.5 mm mechanism increments. This is not
continuous-path proof or a route from an arbitrary resting posture. The withdrawal
holds the slider released; spring return and supporting-hand tilt are excluded.
[An additional retained withdrawal counterexample](myoarm_withdrawal_counterexample.json)
was found during solver qualification and independently revalidated after range
correction: both endpoints pass, but an interior middle-finger pad penetrates the
stand floor (minimum sampled distance about −0.237 mm). It remains a regression
rather than a substitute search result. The final nominal run's failure is a
clearance-screen violation, distinct from that penetration witness.

### Evidence integration and reproduction

[verification.py](../verification.py) preserves the existing `stand.adjustment` intent
and physical-operation question. Current variants are `v3-60-nominal`,
`v3-60-shoulder-near`, and `v3-60-shoulder-far`. It replays joint states and sampled
transitions against current CAD/anatomy; stored acceptance flags/counts cannot
supply PASS. Source/asset/tool mismatch or a historical synthetic receipt gives
UNKNOWN; malformed attempted metadata gives INCONCLUSIVE. Finite unsuccessful
search is INCONCLUSIVE. **Integrated physical operation remains UNKNOWN** for
all variants. A complete computational witness does not establish effort, grip,
friction, binding/return, comfort, fatigue, safety or actual user/population access.
The shared CLI still exits 0 for trustworthy reports regardless of these outcomes.

```sh
./execute.py --threads 1 model/analysis_phone_stand/human_interaction.py --output model/analysis_phone_stand/notes/v3_myoarm_interaction.json
./execute.py --threads 1 model/analysis_phone_stand/audit_myoarm_collision.py
./execute.py --threads 1 model/analysis_phone_stand/verification.py --variant v3-60-nominal
./execute.py --threads 1 model/analysis_phone_stand/verification.py --variant v3-60-shoulder-near
uv run --locked pytest -q tests/test_human_interaction.py tests/test_synthetic_human_interaction.py tests/test_product_verification.py tests/test_product_verification_cli.py tests/test_product_verification_entrypoints.py
```

The [living skill](../../../.codex/skills/articulated-human-interaction/SKILL.md) now
requires looking for applicable established MyoSim anatomy, auditing imported
constraints and collision coverage, and keeping synthetic fixtures out of default
product evidence. It can improve through demonstrated product lessons. The whole
implementation remains product-local; no second consumer justifies shared plumbing.
No product CAD, STEP/STL, manufacturing placement or historical evidence was changed.
V3 remains unprinted and physically unqualified. Useful next work would measure
setup, qualify remaining self-collision coverage, and test physical two-hand operation;
additional contacts or force analysis need separate questions and qualification.

Qualification passed a **208-test** broader run covering human/synthetic, product
verification/CLI/entrypoints, assembly geometry and execution, plus the final
**16 human regressions** and focused imported-constraint check. The explicit
MyoArm study, 2,401-state audit, nominal/near CLI replay, historical-view smoke
command, dependency check and skill validator completed. Independent skill
forward-testing replayed all three setup outcomes. No CAD exports or slices were
rerun for this analysis correction.

Correction attribution: GPT-6-based Codex (exact runtime variant/effort not exposed),
Codex shared-workspace API agent, OpenAI; independent skill forward-test by a Codex
subagent without model/effort override. Earlier attribution remains historical.

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

[Selected automatic execution records](v3_timeout_execution_records.json)
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
[repository workflow](../../../AGENTS.md#shared-engineering-execution) prohibits
inventing these deadlines. Historical timeout records retain their original
inputs and status; elapsed times are observations, not future limits.
Use one CPU thread and fresh output directories:

```sh
./execute.py --threads 1 model/analysis_phone_stand/analyze_v3.py release model/analysis_phone_stand/notes/.execution/release_new --study
./execute.py --threads 1 model/analysis_phone_stand/analyze_v3.py guide model/analysis_phone_stand/notes/.execution/guide_new --study
```

Assess whether computation answers a useful question from its progress and
evidence. Taking longer than expected alone does not justify terminating it.

## Historical synthetic release access

**Historical evidence from e0b4009, before the MyoSim correction.** The invented
anatomy, scale sensitivity, results and figure below remain scoped to that model.
They are not the current anatomical foundation and do not transfer to MyoArm.
The current adapter/CLI uses the MyoArm receipt described above. The original full
study source remains in Git; [synthetic_human_interaction.py](../synthetic_human_interaction.py)
is retained only for numerical regression/replay of these counterexamples.

The [original product-local study](https://github.com/arthow4n/vibe-modelling-3d/blob/e0b4009/model/analysis_phone_stand/human_interaction.py) asked whether an assumed
arm/palm/index model can contact the **rear centre of the release button**, approach
from 40 mm behind it, maintain contact through its prescribed 3 mm stroke, and
withdraw while released. This is a useful pre-print question because clear solved
endpoints can hide a colliding hand transition. V3 was selected over the already
successful jar/case and the discontinued swatch damping direction: it has an
unprinted, consequential press-and-tilt interaction. No product was redesigned.
This investigates only the button hand, not the other hand supporting/tilting the
phone or the complete two-hand operation.

[Retained receipt](v3_human_interaction.json) contains replayable independent
joint states, per-start contact/normal errors, individual joint margins, palm/elbow
positions, named clearance violations and penetrations, press transitions and
first invalid path witnesses. It is an explicit output, not a search-result cache.
[Diagnostic side projection](v3_human_interaction.png) omits X separation;
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

[verification.py](../verification.py) adopts only the existing recorded adjustment
intent, with its [protected inventory](verification_sources.json), because
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

The historical diagnostic figure can still be replayed against unchanged V3 CAD:

```sh
./execute.py --threads 1 model/analysis_phone_stand/view_human_interaction.py
uv run --locked pytest -q tests/test_synthetic_human_interaction.py
```

The former scale variants and their verification outcomes above describe the old
adapter. They are no longer selectable current product evidence. The preserved
schema-1 receipt is explicitly rejected by the MyoArm adapter. No new scheduler,
cache or evidence database was added. [Historical synthetic regressions](../../../tests/test_synthetic_human_interaction.py) preserve
static/path differences, held contact, signed distances with disabled contacts,
the former coupling/limits, constant maximum stroke and authoritative target changes. Product-local code retains geometry,
setup, criteria, solver and replay choices; one consumer has not justified a shared
package. The [living skill](../../../.codex/skills/articulated-human-interaction/SKILL.md)
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
guidance, with no model/effort override; [historical product attribution](../README.md#attribution)
remains unchanged.
