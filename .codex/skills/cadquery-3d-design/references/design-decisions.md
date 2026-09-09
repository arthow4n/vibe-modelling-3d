# Requirements and functional decisions

Read when interpreting a new object, mechanism or ambiguous physical feedback.

## Requirements clarification

Reuse the user's known dimensions, printer, material and assembly preferences.
Honor an explicit request to proceed autonomously: choose a reasonable mechanism
and document assumptions instead of asking for routine preference decisions.
Otherwise ask only when an unresolved requirement would materially change fit,
function, usability or manufacturing. Continue independent work while awaiting
an essential answer; do not mistake elapsed time for an answer.

Useful questions establish the intended use, critical interfaces, loads and
whether required hardware or assembly is acceptable. Explain what to measure
and why; do not expect the user to specify every printing detail. Do not assume
access to purchased parts merely because the user has a printer.

When a mechanism choice needs user input, recommend one feasible approach and
briefly explain the meaningful tradeoff. When the user has delegated the choice,
select it directly within known constraints. State the interpreted use, print
approach and consequential assumptions before building. Revisit clarification
only if new evidence reveals a material conflict; a named fit parameter is not
proof that the assumed dimension is correct.

## Functional design

Design functional objects around behavior and interaction, not only shape. Before creating geometry, reason about what must be held, supported, guided, blocked, connected, protected, or constrained; how an item enters or is installed; what retains it after insertion; what prevents accidental movement or release; how it is intentionally removed or adjusted; and what normal forces or disturbances it should tolerate.

Check whether the user can still grab, access, operate, plug in, unplug, or otherwise manipulate the relevant object. Account for required clearance, friction or retention, and flexibility where relevant. Identify obvious everyday failure modes.

For holders, docks, clips, mounts, adapters, organizers, and similar objects, reason through this sequence:

```text
How does the item enter?
How is it retained?
What prevents accidental release?
How is it intentionally removed?
Can the user still access or operate it?
```

A visible slot, opening, hook, or retaining feature is not enough if the held object can fall through, the opening blocks installation, retention is ineffective, or the user cannot reach the object. Avoid designs that require threading a long or attached item through a closed hole when it should be installable in place.

## Critical and vibe dimensions

Separate dimensions that control function from dimensions chosen mainly by visual judgment:

* **Critical dimensions** materially affect fit or function, such as cable diameter, device thickness, shaft diameter, mounting spacing, shelf or desk thickness, insertion clearance, retaining throat/opening, and mating diameter. Ask for these explicitly, infer them conservatively when reasonable, or expose them as named model parameters.
* **Vibe dimensions** do not materially affect function or printability, such as decorative curvature, non-critical taper, visual balance, and cosmetic transitions. External proportions and corner radii belong here only when they do not affect fit, strength, bed contact, or support requirements. Choose and refine these visually as needed.

Critical functional geometry takes priority over cosmetic refinement.

## Translate subjective feedback into a physical question

“Tight” can mean hinge wobble, movement when closed, resistance to accidental
opening, friction during movement, or deliberate release effort. Explain only
the relevant distinctions; ask what happens during use rather than requiring
engineering terminology. Reuse preferences already established.

Trace the load-bearing contact during insertion, seating, attempted opening and
intentional release. Check whether contact blocks motion or cams the parts apart.
Compute engagement from both mating surfaces in a common coordinate frame:
moving both surfaces can leave overlap unchanged. A visible hook, larger tooth,
or collision-free closed pose does not establish positive retention. Where
useful, check that locked movement intersects the catch and released movement
clears it; distinguish rigid motion checks from elastic deformation.

Resolve a known manufacturing defect on a fit-critical surface before offering
another trial that depends on that surface. Disclosing a likely defect does not
make it an informative experiment. Consider orientation, geometry or part
separation within the user's assembly constraints; explain any new tradeoff.

## Deterministic motion and interface checks

Measure actual geometry in a common coordinate frame where feasible: mating
sizes, local wall/gap thickness, undercut, interference and clearance. A bounding
box or nominal parameter alone cannot establish a local gap or retaining contact.
For motion, include the relevant geometry pairs, axis/path, endpoints and intended
contact or exclusions. A shell-only sweep does not check the removed latch;
rigidly translating a latch clear does not establish its elastic release behavior.

Keep a simple model-specific sweep when it is reliable. Extract a reusable helper
only when repeated calculations justify it; do not force unlike mechanisms into
one abstraction. Report range, sample step or method, intersection tolerance,
geometry pair, and any detected collision or sampled minimum clearance/pose.
Use “none detected at sampled poses,” not continuous-motion proof, for a plain
coarse sweep. Zero intersection volume alone does not establish positive clearance.

If a clear/colliding pair brackets contact, refine numerically to useful precision
(e.g. 75–80° to approximately 77.4°), then render a diagnostic pose only if needed.
Bisection locates that transition; it does not exclude earlier narrow collision
intervals. When between-sample contact could change the decision, use adaptive
sampling with a justified clearance/motion bound or a swept-volume/continuous
check. Do not claim a global minimum from sampled distances. Improve coverage
only as far as the required clearance and decision warrant, not arbitrary precision.

## Actuation effort and cheap mechanics

For latches, clips, detents, cams, flexures and over-center mechanisms, geometric
engagement and release are necessary but do not establish intended effort.
Distinguish closed play, retention force, movement friction, insertion effort and
deliberate release effort. Treat “firm enough for a bag, comfortable with one
thumb” as a functional requirement. Where useful, choose and record a provisional
force or torque range at the actual finger contact, based on use and delegated
preferences. Words such as light, firm or near-locking have no universal numeric
scale. Record the target as an assumption, not an achieved measurement.

Trace the load path and user leverage: torque = force × perpendicular moment arm.
For tangential finger force, F = torque / finger radius. A strong internal detent
can feel light through a long lever. Inspect retaining contact, required release
displacement, preload, contact angle and friction before enlarging a tooth.

For a roughly rectangular, slender cantilever under a transverse end load, a
cheap small-deflection estimate can reject obviously weak, stiff or high-strain
concepts before slicing/printing. Use effective flexible length L, width b,
bending thickness t, end displacement δ and assumed modulus E:

```text
I = b*t^3/12
k ≈ 3*E*I/L^3
F_spring ≈ k*δ
peak root strain ≈ 3*t*δ/(2*L^2)
```

With lengths in mm and E in N/mm², k is N/mm and force is N; strain is dimensionless.
Record the material/modulus source or explicit assumption, boundary conditions
and useful uncertainty range. These are simplified predictions: printed
anisotropy, root stress concentrations, attachment compliance and large deflection
limit applicability. Compare strain with a defensible material/process allowance;
do not silently assume bulk properties or keep thickening an overstressed arm.

Stiffness scales with b, t³ and 1/L³. All else equal, changing 2.2 mm leaves to
2.8 mm predicts about 2.06 times the stiffness, but also increases strain at the
same displacement. This motivates a physical stiffness comparison, not a claim
of doubled release force. Contact, undercut, preload, friction and finger leverage
can dominate release; beam spring force is not complete latch actuation force.

Use simulation only when a consequential question exceeds simple mechanics,
for example interacting or curved/tapered flexures, large deformation or
contact-dominated release. Full nonlinear FEA is not a routine stage. If future
reusable tooling is justified, prefer a small question-oriented interface such
as `evaluate_flexure` or `check_motion` returning assumptions, scope, estimates
and limitations over a collection of raw solver APIs. No new solver is required
by this guidance. Physical calibration remains necessary for actual feel and wear.
