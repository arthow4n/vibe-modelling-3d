---
name: articulated-human-interaction
description: Investigate articulated hand/arm reach, contact and sampled access paths against product geometry using explicitly scoped kinematic models. Use for consequential control/recess/service access questions; ordinary dimensional clearance and physical comfort/force questions need other evidence.
---

# Articulated human interaction

The qualified implementation is intentionally **product-local**: V3 phone-stand
rear release access in [human_interaction.py](../../../model/analysis_phone_stand/human_interaction.py).
Read its [question, assumptions and results](../../../model/analysis_phone_stand/README.md#articulated-release-access)
before adapting it. MuJoCo supplies forward kinematics and explicit signed geom
queries; SciPy supplies bounded multi-start IK. There is no shared human-model
registry, anatomical asset, grasp planner or universal clearance/comfort criterion.

## Choose a consequential question

Use this when articulation or posture changes the answer: reach through a recess,
button approach, withdrawal, or maintaining contact while a mechanism moves.
State the actual configuration, allowed contact patch, surrounding obstructions,
setup and what a discovered state or counterexample would change. If a local CAD
gap answers the question, use it. If only effort, friction or comfort remains,
computational reach does not resolve it; retain physical UNKNOWN evidence.

Start another consumer locally. Reuse authoritative CadQuery builders and named
assembly configurations where available. Derive collision portions from those
shapes, or explicitly associate simplified fixtures with the selected source and
parameters. Keep units/transforms explicit. The example partitions actual CAD and
boxes each portion conservatively; holes and rounded edges are filled. A single
MuJoCo mesh hull can seal an access opening. Choose simplification for the question,
not to obtain a passing pose. State missing accessories and setup obstacles.
Do not export a reference human as printable product geometry.

## Declare the model and solve

Separate imported anatomy (none in the example), assumed segment/radius geometry,
setup, joint coordinates/ranges, coupling and numerical search controls. The
example uses independent hinge coordinates, fixed shoulder, arm/palm/index,
curled-other-finger envelope and explicit DIP/PIP coupling; its ranges are model
hypotheses, not clinical limits. Uniform scaling explores a geometry hypothesis;
it does not personalize anatomy or establish a population percentile.

Define a contact point/patch, object outward normal and the modeled pad geometry.
Offset a spherical pad centre by its radius; targeting the surface with its centre
would penetrate it. Allow only the declared pad/patch contact with a named numerical
penetration tolerance. All other human/product pairs remain forbidden. Distinguish
clearance-screen violations from actual penetration. Enumerate self-collision
coverage and intentional same-body/adjacent-joint exclusions; zero simulator
contacts does not establish nonpenetration. The example disables automatic contact
masks and queries its declared pairs directly, including same-world-body obstacles.

Use multiple declared initializations for local IK. Independently evaluate the
returned configuration: finite coordinates, contact/normal errors, joint limits
(including coupled joints), and exact native distances for the declared proxies.
Solver termination is neither necessary nor sufficient for that geometric screen.
The example adds an explicit optimization clearance buffer while leaving final
acceptance unchanged; penalty residuals can otherwise land just below a hard screen.
Inspect failed candidates and near-limit joints instead of hiding them behind counts.
Use a descriptive separation rule for discovered poses; one cluster is not uniqueness.

## Distinguish reach from usable movement

For consequential access, solve a pre-contact state, contact, actuation states and
withdrawal. Validate nonlinear forward kinematics **between** solved states.
The example samples joint interpolation at <=2° independent-joint increments and
<=0.5 mm mechanism increments, checking held contact during the press. This is
sampled evidence, not continuous collision proof. It starts only 40 mm from contact;
it does not establish access from an arbitrary resting posture. Withdraw under an
explicit mechanism state; the example withdraws with the slider prescribed released.

Qualification found clear nominal pre-contact/end poses whose interpolated palm
crosses the desk; endpoint acceptance hid an invalid intermediate state. It also
found a held-contact interpolation penetrating the button despite valid press
endpoints. Preserve [these regressions](../../../tests/test_human_interaction.py).
Do not fix a failed path by deleting the desk, altering hand collision geometry,
or loosening contact limits. Try a justified alternative path/setup or retain
INCONCLUSIVE. Floating-point interpolation at a maximum mechanism stroke must not
manufacture an out-of-range input; retain the constant-stroke regression.

## Interpret, retain and integrate

A PASS means a configuration/path was found satisfying **the declared finite
model and screens**. It does not establish real human feasibility, comfort, safety,
force capability, fatigue or accessibility. No candidate normally means
INCONCLUSIVE under this search, not physical impossibility. Missing/stale retained
evidence is UNKNOWN; malformed attempted evidence is INCONCLUSIVE.

Report contact and normal errors, individual joint margins/posture, palm/elbow
positions, named clearance/penetration witnesses, distinct configurations and path
outcomes. Choose an inexpensive assumption sensitivity that could change the
conclusion. The example changes uniform geometry scale with shoulder fixed; complete
sampled interaction appears only in the smaller hypothesis. Do not rank products
with an ergonomic score.

Run with the existing `./execute.py` boundary and explicit receipt output; no new
scheduler/cache is needed. The example snapshots source/lock digests through
`execution.identity.digest`, verifies they did not change during the study, and
retains concise search diagnostics and replayable joint states. Keep receipts with
the product; inspect source/tool/setup association before transferring evidence.

Where adoption is useful, compose existing `product_verification` questions and
checks. The example's [verification.py](../../../model/analysis_phone_stand/verification.py)
uses the shared CLI and replays saved poses/paths on current CAD rather than trusting
stored PASS/counts. Endpoint and access questions are separate from physical
operation; digital evidence cannot overwrite a user rejection. No new status or
requirements infrastructure is needed. Object records own nuanced intent and history.

## Improve from real work

Improve this shared skill when real engineering work produces a reusable workflow
lesson, confirmed simulator failure, qualified capability, integration pattern or
useful counterexample. Link the consumer and applicability limits. Do not add
universal design constraints or methods merely because they seem plausible.
Extract code only when real consumers or a demonstrated correctness/diagnostic
need earn it; repeated variants of this one product remain local. Further fingers,
measured profiles, anatomical self-collision or force analysis require their own
consumer and qualification before this skill describes them as available.
