---
name: articulated-human-interaction
description: Investigate articulated hand/arm contacts and sampled access paths against CAD using established MyoSim anatomy and explicit setup/collision assumptions. Useful for consequential control, recess or service access; geometric reach cannot answer physical comfort or force questions.
---

# Articulated human interaction

Use established **MyoSim anatomy** for ordinary product-level analysis when a
suitable model exists. The qualified example is product-local V3 rear release
access in [human_interaction.py](../../../model/analysis_phone_stand/human_interaction.py).
Read its [current evidence and limitations](../../../model/analysis_phone_stand/README.md#articulated-release-access)
before adapting it. There is no shared anatomical registry or grasp framework.

State a consequential question: contact through an opening, approach/withdrawal,
or held contact during mechanism motion. Declare the candidate, requested surface,
setup, obstructions and decision the result could change. Ordinary dimensional
clearance may need only CAD; effort, friction, comfort and fatigue need other
qualified analysis or physical evidence.

## Import and inspect anatomy

Inspect the installed `myo-sim` distribution and maintained source before choosing
a model. `myo_sim.load_spec('myoarm_r')` supplies right arm, all five digits and a
passive torso scaffold; a hand/finger model is appropriate only if the question
actually excludes arm placement. Do not substitute guessed lengths, joint axes,
limits, couplings or hand envelopes merely for convenience. Preserve imported
geometry and distinguish visual bones, muscle wrap geoms and collision skin.
If available anatomy is technically unsuitable, demonstrate that limitation before
choosing an alternative. Synthetic geometry is useful for isolated numerical
fixtures and controlled comparisons, with its scope explicit.

Record package/version, source/asset digests, bodies, joints/ranges, equality
constraints, collision masks and explicit pairs. The example's `audit()` describes
these and its supplemental pair coverage. MyoArm has 38 hinge coordinates and 11
active affine shoulder equalities. The local solver eliminates these exactly and
intersects master bounds with dependent limits. `mj_forward` does **not** project
arbitrary qpos onto equalities. Its index DIP is independent; never carry the old
synthetic DIP/PIP coupling into this model. Unsupported constraint topology must
be qualified or handled by a suitable constrained solver before use.

Kinematic use is legitimate: the example disables actuation, prescribes qpos and
never integrates dynamics. Muscle/tendon presence does not qualify force, strength,
fatigue or physiological effort. Imported anatomy is not a measurement of the user.
Keep torso/shoulder placement and coordinate transforms separate from anatomy.

## Own the product scene and contact

Start consumers locally. Use authoritative CadQuery builders/configurations to
derive selected collision representations and surfaces; keep units/transforms
explicit. The example rotates the whole reference anatomy about Z and translates
its neutral humerus origin to an unmeasured shoulder reference, without scaling.
CAD portions are conservatively boxed: holes/rounding are filled; this may reject
real free space. A single convex mesh hull can seal an opening. Include relevant
setup obstacles and declare missing support hands/accessories.

Target a **skin surface**, not just a nearby marker. The example uses the imported
index ellipsoid's +local-Z pole and normal against the CAD rear button face;
`IFtip_r` is retained as a descriptor, not presumed to be the contact skin. Allow
only the declared pad/patch contact with named numerical tolerances. Other finger,
arm or product penetration remains forbidden. These tolerances are screens, not
user requirements or universal ergonomic thresholds.

Audit self-collision separately. Imported MyoArm skin masks have `conaffinity=0`
and only four torso/arm pairs are explicit. No simulator contacts does not establish
anatomical nonpenetration. The example directly queries native signed distances,
adds selected cross-digit/nonadjacent and finger/arm pairs, and lists exclusions.
Forearm/metacarpal composites and a proximal middle/ring proxy overlap are excluded
without resizing geometry. The latter has a retained [finite collision audit](../../../model/analysis_phone_stand/audit_myoarm_collision.py).
Do not blindly enable all pairs or interpret these exclusions as validated anatomy;
palm gaps, adjacent/composite overlaps and hand/torso coverage remain limitations.

## Solve, then independently validate movement

MuJoCo supplies FK/distances; SciPy bounded multi-start least squares searches
independent imported coordinates. Inspect multiple initializations and posture,
joint margins, contact/normal errors and named collision witnesses. Solver
termination is neither necessary nor sufficient for acceptance. Penalty residuals
can settle just outside a hard screen; the example's optimization buffer does not
change final acceptance. One discovered cluster does not establish uniqueness.

Separate endpoint reach from pre-contact approach, prescribed press, maintained
contact and withdrawal. Check nonlinear FK between solved states, including limits,
couplings, forbidden collisions and requested-contact scope. The example samples
at <=2° independent-joint and <=0.5 mm mechanism increments. These are sampled
paths, not continuous guarantees; optimizer trial iterates are not a movement path.
The start is only 40 mm from contact; withdrawal holds the button released.

Preserve regressions: valid MyoArm endpoints can hide a middle-finger/floor collision
on withdrawal. Historical invented-anatomy fixtures retain desk-sweep and held-press
counterexamples in [synthetic tests](../../../tests/test_synthetic_human_interaction.py).
They protect numerical semantics and must not become default product anatomy.
Do not delete obstacles, shrink skin or loosen screens to make a path pass.

## Scope evidence and improve from real work

A found witness supports only the declared finite model/screens. No witness is
normally INCONCLUSIVE, not physical impossibility. Missing/stale evidence is UNKNOWN;
malformed attempted receipts are INCONCLUSIVE; programming errors remain errors.
Keep physical operation UNKNOWN until measured. No digital PASS overrides user rejection.

Choose sensitivity around actual uncertainty. The example varies shoulder rearward
placement with anatomy unchanged; old uniform-scale outcomes remain historical.
Scaling is not physiological personalization or a population percentile.

Run through `./execute.py`. Keep concise diagnostics plus replayable states and
source/asset/tool/setup/search/collision identities with the product. The local
[verification adapter](../../../model/analysis_phone_stand/verification.py) independently
replays against current CAD and rejects old synthetic receipts. Stored PASS flags
or optimizer counts cannot supply PASS. Compose ordinary `product_verification`
questions; shell success only means a trustworthy command report, not product readiness.
No new scheduler, cache, score or evidence database is needed.

Future agents may improve this skill when real engineering work establishes a
reusable lesson, confirmed failure mode or qualified capability. Link its consumer
and applicability limits. Do not add speculative methods or universal human design
thresholds. Extract shared code only when concrete consumers or demonstrated
correctness needs justify it; additional contacts, measured profiles and force
analysis still need their own qualification.
