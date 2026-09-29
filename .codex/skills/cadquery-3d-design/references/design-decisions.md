# Requirements and functional decisions

Read when interpreting a new object, mechanism or ambiguous physical feedback.

## Requirements clarification

Reuse the user's known dimensions, printer, material and assembly preferences.
Before detailed CAD, use available requirements for a cheap concept screen and
present viable deliverable and process options when they have not yet been agreed.
Recommend an approach, explain its consequential assumptions and print setup,
and establish whether this phase delivers a full model, samples before a selected
full model, or samples only. A choice already made in the conversation counts as
agreement. Honor explicit delegation of routine choices without asking again.
The oversized-assembly joint/load agreement below still applies. Ask only when
an unresolved requirement would materially change fit, function, usability or
manufacturing. Continue independent work while awaiting an essential answer;
do not mistake elapsed time for an answer.

Useful questions establish the intended use, critical interfaces, loads and
whether required hardware or assembly is acceptable. Explain what to measure
and why; do not expect the user to specify every printing detail. Do not assume
access to arbitrary purchased parts merely because the user has a printer, but
prefer the user's on-hand screw and nut assortment (listed in `AGENTS.md`) when
fasteners are needed. Discuss during planning whether the user prefers a fully
printed design or if using this stock hardware is acceptable; if the user
explicitly requests full autonomous implementation, use best judgment and using
this stock hardware is permitted.

When a mechanism choice needs user input, recommend one feasible approach and
briefly explain the meaningful tradeoff. When the user has delegated the choice,
select it directly within known constraints. State the interpreted use, print
approach and consequential assumptions before building. After agreement,
complete the phase autonomously; revisit the decision only if new evidence
reveals a material conflict or the agreed physical observation is needed.
A named fit parameter is not proof that the assumed dimension is correct.
For an existing collection, a measured stack or mating item can cheaply settle
capacity when available; otherwise document the source dimensions and practical
allowance without blocking authorized modelling on a measurement.

## Pre-CAD concept screen

Use rough, stated assumptions to answer consequential questions before detailed
geometry. As relevant, calculate a fit stack, mating-surface engagement,
clearance or release travel, full-size assembly path, oriented part envelope,
or a structural load and deflection estimate. Compare alternative concepts at
the level needed to reject one; avoid detailed calculations that cannot change
the choice. If a concept fails even an optimistic bound, revise it before CAD
or a print trial. List what needs actual modelled geometry, such as local weak
sections or motion interference, and what needs a physical print, such as
friction, spring force, sag or feel. Confirm concept estimates with measured CAD
sections and interfaces only where those measurements change the decision.

An assembled object may exceed the repository's practical printable envelope;
do not reject the request for size alone. If it must be divided into printable
parts, discuss and agree on the joint requirements before finalizing the split.
Establish the loads and directions the joints must withstand, whether separation
is acceptable, permanent versus demountable assembly, permitted fasteners or
adhesives, assembly access, and the consequence of failure. Recommend a concrete
joint approach with its strength, printing and assembly tradeoffs. A locating
feature, friction fit, dovetail or simple connector is not automatically a
structural joint. If the user delegates the joint design after establishing the
required loads, assembly permanence, permitted hardware or adhesive, and failure
consequences, choose the details and document the assumptions. Do not substitute
guessed loads for the required agreement on an oversized assembly.

## Structural load paths and joint screens

For a structurally important part or split assembly, start with a dimensioned
sketch or parameter table before detailed CAD. Derive service and foreseeable
handling cases from intended use, including support and grip positions. Estimate
reactions, bending in each direction that puts a different seam face in tension,
shear, torsion and withdrawal. Estimate required section size and joint or
fastener capacity with stated material allowances. Set provisional limits for
sag and joint rotation from intended use, then estimate whether the concept
meets them. Compare those demands with plausible joint dimensions and print
layer direction; vary uncertain loads, properties and load sharing. Reject a
concept that fails even an optimistic bound before spending time modelling it.

At the same stage, calculate the full-size insertion travel and swept space for
the proposed assembly sequence. Check whether the parts can be aligned, held,
fastened and released with available hand and tool access. A short fit coupon or
collision-free rigid path does not establish that the full assembly is practical.

Once the geometry exists, measure likely weak sections from evaluated CAD,
including reliefs, holes, thin skins and attachment roots. Recalculate the
relevant bending, stiffness, bearing, fastener seating, thread or catch and edge
tear-out screens using the actual assembled load path. Credit friction, a butt
seam, preload or shared contact only when the design and stated assumptions
support it. Record boundary conditions, print orientation, infill,
material-property source and allowance; check sensitivity where uncertain. A
positive geometric lock, clean slice or successful fit test does not establish
strength. A passing calculation is conditional evidence, not a certified load
rating or a substitute for physical validation.

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

## Whole-object form and handling

As soon as rough complete geometry exists, review the assembled object and its
normal handling sequence before detailed mechanism refinement or expensive
simulation. Assess whether local features form a coherent, usable object:
proportions, rim/guide transitions, openings, grips and exposed mechanisms. A
contact shape selected for solver robustness still needs deliberate integration
into the product; a successful local analysis does not justify its exterior form.

Check whether protruding catches or unprotected flexible arms could snag, receive
unintended handling loads or obstruct a grip. Consider recessing or protecting
them when useful, while preserving contact travel, access and manufacturability.
Make insertion and opening understandable from the grip and geometry. Coordinate
edge treatment and transitions; asymmetry or an exposed mechanism can be
appropriate when it serves the intended use. Do not impose symmetry, concealed
mechanisms or decoration as universal requirements.

Use the smallest adequate visual review: an existing clear view can suffice for
a simple object. For an assembly, choose closed/open or use-context views only
where they answer different questions. If line drawings obscure depth, use a
clearer camera or shaded CAD view when available. Better presentation helps
diagnosis but does not repair awkward geometry. This review does not require
style variants, a new rendering tool or a user approval gate.

Resolve consequential integration problems early and revisit only affected
questions after substantial changes. Protect critical fits, flexure dimensions
and print orientation during visual refinement; changes to contact, attachment
stiffness or supporting geometry require their affected checks. Keep the brief
decision in the object's existing record instead of creating a separate review
report. Continue autonomously within the authorized design scope.

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

Connect local flexible-motion evidence to the surrounding assembly. A cam/arm
fixture may omit guides, reliefs, root support and shell flexibility. Where an
unmodelled collision could change function, check the relevant deformed envelope
or saved poses against surrounding CAD, or record that integration gap. A head
clearance check does not cover the whole beam. A fixed root is not automatically
conservative for both strain and operating force; qualify the quantities it
screens rather than claiming complete assembly validation.

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

Define both acceptable deliberate operation and resistance to accidental release
from intended use. A qualitative acceptance condition is sufficient when no
numerical target is justified; autonomous scope allows choosing and documenting
it. Easy opening and positive geometric obstruction alone do not establish
adequate retention. Screen engagement and effort at consequential clearance
extremes, including guide play and alignment, before refining nominal force.
Do not apply every tolerance combination when only one could change the decision.

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

For rounded detents, use the shared circular-cam spring screen during concept
selection when its assumptions fit; it can expose sliding-force or guide-play
issues before a costly solve. Treat failure of a screen's applicability criterion
as a limit on its evidence, not permission to report a precise force. Use the
[contact-study guidance](../../../../physical_analysis/README.md#plan-a-contact-study)
when deformation and contact remain consequentially coupled.

Use simulation only when a consequential question exceeds simple mechanics,
for example interacting or curved/tapered flexures, large deformation or
contact-dominated release. Full nonlinear FEA is not a routine stage. If future
reusable tooling is justified, prefer a small question-oriented interface such
as `evaluate_flexure` or `check_motion` returning assumptions, scope, estimates
and limitations over a collection of raw solver APIs. No new solver is required
by this guidance. Physical calibration remains necessary for actual feel and wear.
