# Requirements and functional decisions

Read when interpreting a new object, mechanism or ambiguous physical feedback.

## Requirements clarification

Reuse the user's known dimensions, printer, material and assembly preferences.
Before detailed CAD, use available requirements for a cheap concept screen and
choose the [next useful deliverable](#adaptive-development-and-the-next-deliverable).
Explain the approach, consequential assumptions and proposed print setup; for a
visual-only phase, defer settings that cannot affect its decision. A choice or
authorization already made in the conversation counts as agreement. Honor
explicit delegation without asking again.
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
complete the phase autonomously, subject to the
[feedback and continuation rules](#feedback-and-autonomous-continuation).
A named fit parameter is not proof that the assumed dimension is correct.
For an existing collection, a measured stack or mating item can cheaply settle
capacity when available; otherwise document the source dimensions and practical
allowance without blocking authorized modelling on a measurement.

## Adaptive development and the next deliverable

First identify which unresolved choice could make the product undesirable or
unworkable, and what evidence would change that choice. Resolve high-impact
uncertainty before work that depends on it. Consider total development, feedback
and print cost, not just CAD build time. Record the next decision, useful evidence
and intended deliverable briefly in existing notes; no new phase schema is needed.

| Task and remaining uncertainty | Appropriate next investment |
| --- | --- |
| Straightforward, well-specified object; little subjective or mechanical uncertainty | Direct complete implementation with applicable CAD, FDM and delivery checks. No preliminary variants, intermediate approvals or coupons by default. |
| Consequential silhouette, proportions or style remain open | A small rough visual comparison before detailed implementation; normally two or three meaningful directions. |
| New mechanism or critical mating behavior | Establish a coherent whole-product concept, then qualify the critical interface with the cheapest adequate checks or representative experiment before dependent full-product work. |
| Both form/use and mechanics remain uncertain | Resolve useful form and normal interaction first, then critical interfaces, then complete the product. |
| Established product with one isolated uncertainty | Preserve the accepted architecture and successful evidence; investigate the affected interface or relationship without restarting product design. |

During initial agreement, recommend the most useful next deliverable: one finished
printable object, one rough complete concept, a few rough visual variants, an
interface sample, a partial-product prototype, or the full product using an already
qualified interface. A request for an object does not automatically require
end-to-end detailing, nor does it automatically require staged discussion.
Use known requirements and authorization to choose; ask only for a consequential
decision that cannot reasonably be resolved within them.

## Levels of investment

Move to a more expensive representation only when it can answer the next question
and current evidence justifies that investment. Skip levels that add no useful
evidence; combine them for simple objects. These are neither five reports nor five
approval gates. A rough model can be the correct final deliverable for a phase.

| Representation | Purpose and sufficient detail |
| --- | --- |
| Concept representation | A short physical description, established reference or sketch that explains the intended experience and architecture; cheap fit/load math can reject impossibility here. |
| Rough complete geometry | Dimensionally meaningful overall form, actual contents or held-item envelopes, major components, openings, approximate proportions and intended motion. A few parametric primitives can suffice. |
| Critical interfaces and representative experiments | Only details that decide feasibility: targeted CAD checks, local geometry, simple mechanics, physical samples or justified numerical studies. |
| Detailed complete product | Finish parametric geometry, necessary verification, manufacturing choices, useful renders, final slicing and matching exports after concept and critical interfaces are sufficiently established. |
| Physical validation | Print the appropriate next sample or complete product; observe real fit, use, appearance and handling, then update object evidence and transferable lessons. |

For CAD-driven fit or assembly questions, prefer simple real parametric CAD to
detailed meshes or attractive illustrations that cannot establish dimensions.
Keep low-detail geometry easy to revise; do not add final fillets, decorative
features, elaborate mechanisms or print-ready exports merely to make a rough
review look finished. Finish/export only the printable specimens agreed for an
experiment phase; rough visual studies do not require slicing.

## Feedback and autonomous continuation

Before a substantial increase in commitment, ask whether the evidence resolves
the decision that investment depends on. Seek focused feedback or stop at a useful
intermediate deliverable when a consequential choice remains unresolved and:

- it is subjective and requires the user's undelegated judgment;
- the next stage costs substantially more and present evidence cannot justify it;
- or a representative small experiment could materially reduce the risk of that
  commitment and its result is needed to choose the design.

Present concrete rough evidence or a reviewable sample and name the decision or
observation needed. Do not ask the user to approve an abstract plan when cheap
independent work can make the choice reviewable. Do not refine dependent mechanisms,
simulate them or finish manufacturing while awaiting concept feedback. If the
agreed phase ends at a rough study or sample, complete that deliverable and stop
there; its existence does not authorize the next phase. An already authorized
next phase can proceed once its dependency is resolved, without renewed approval.
Continue independent authorized work while an answer is pending.

Proceed autonomously when requirements and concept are established, uncertainty
is minor, or adequate evidence supports a reasonable choice within delegated
scope. Do not ask at every level or repeat answered questions. Explicit autonomous
end-to-end implementation normally authorizes routine choices and completion,
with honest reporting of consequential assumptions and remaining physical limits.
It does not establish a physical result or justify major investment in a doubtful
concept. Stop only for a new decision outside that scope or an unjustified
commitment; explain the unresolved dependency and why proceeding would waste work.
The oversized joint/load agreement below still applies.

## Inexpensive visual and form exploration

Identify a consequential design-space choice; variants must be able to change a
real decision. Unspecified visual style in an appearance-driven object is a reason
to explore even without an explicit variants request. A clear reference or an
already adequate straightforward architecture may remove that need. Neither
“always three concepts” nor “always finish one concept” is a general rule.

Normally compare two or three rough alternatives that differ in silhouette,
proportions, open space, support arrangement or interaction as relevant. Share
dimensions, functional constraints, reference contents and builders where useful;
avoid duplicated detailed engineering. Sketches, references, silhouettes, volume
studies or simplified CAD are sufficient when they expose the actual differences.
Screen rough fit and print feasibility, then stop exploring when the choice is
adequately informed. Compare before expensive simulation, manufacturing refinement
and print-ready exports.

Useful SVG proposal sketches are valid design-phase deliverables. Retain their
editable SVGs in the object's `renders/concepts/` directory, with PNG previews
when useful, and link them from the existing decision record. Commit and push
completed proposal work through [the normal Git workflow](../../../../AGENTS.md#git-workflow-and-handoff)
even while concept selection or user feedback is pending; final CAD or a printable
object is not required for this handoff. Label schematic assumptions and unresolved
fit/mechanics, and distinguish superseded sketches from current proposals. Keep
only useful comparisons; this does not require sketches for every model or CAD,
exports or slicing to accompany a drawing. Use direct SVG and existing rendering
tools when adequate; add a drawing helper only for demonstrated repeated work.

Choose limited views to answer specific questions: proportions and overall form,
contents in place, hand/tool approach, major component relationships, meaningful
open/closed/operating states, or understandable normal use. Use comparable scale
and context, noting dimensions when separately framed renders are auto-fitted.
Surface detail alone may not distinguish visual directions. No final textures or
perfect presentation are required. Assess objective conflicts and explain
subjective tradeoffs; never substitute an automated aesthetic score for the user's
preference. Use the feedback rules above to decide whether to hand off or continue.
If the deciding uncertainty is printed texture, finish or feel, renders cannot
settle it; choose a representative physical comparison instead.

## Product architecture gate

Before developing a hinge, snap, latch, detent, release button or similar feature,
establish the specific user problem it solves. Also apply this gate to functional
multi-part or moving products. Use the normal decision record, before detailed
interfaces, tolerance studies, FEA or final slicing. First ask:

- What happens if the mechanism is omitted? Is the simpler product already adequate?
- What practical improvement does it deliver, and could a familiar, simpler physical
  arrangement deliver the same benefit?
- Is that benefit worth the added parts, material, assembly, tolerance sensitivity,
  failure modes and analysis work?

Judge **total product simplicity**, not just individual parts: printed-part and
purchased-fastener counts, assembly steps/tools, opening/closing actions, one- or
two-hand operation, printing/support complexity, adjustment and tolerance
sensitivity. Is the whole object proportionate to its task? A locally elegant
mechanism can still make a poor product. Prefer an ordinary arrangement that works
when added mechanics provide no compelling benefit. Having `SnapFitQuestion`,
FEA, IPC or other tools available is never a reason to invent a mechanism.

Distinguish routine operation from occasional assembly or separation. A permanent
handle or projection for a rare operation needs a benefit worth its effect on
normal grip, appearance and material use. Check simpler release motions before
adding a control, and make their direction clear in the assembled view or
explanation. The [G/H connector feedback](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#h--wider-connector-without-a-handle)
illustrates this tradeoff; its CAD release path does not establish printed effort.

Use the adaptive strategy above. This gate establishes product value before
mechanical investment, not a requirement for every spacer or simple bracket to
produce an intermediate review. For an established product, reuse the accepted
concept and revisit only relationships affected by the change. Passing a rough
self-review is insufficient when consequential subjective choices remain
undelegated: stop at the reviewable concept before doing the dependent engineering.

For the worthwhile architecture, answer these in ordinary physical language:

- What does the user actually do, and where does the stored/held/supported item sit?
- What is each major component's single primary job? Which actual surfaces support
  the item, guide movement, and establish its final seated position or stop?
- Which feature prevents unintended removal/opening, and how does the user undo it?
- What must touch, and what must remain clear?
- What simple sequence takes the normal open/unassembled state to working/closed,
  then through intentional release back to open?

Name consequential mating geometry: “this face seats on this face,” “this rail
constrains this direction,” “this hook sits behind this shelf,” “this gap allows
this motion,” or “this stop carries the closed-position load.” If the responsible
mating geometry cannot be named, resolve the architecture before simulating that
function. Bounding-envelope fit or generic absence of collision is insufficient.

Build low-detail **complete geometry** as soon as possible: the actual object,
contents/held item, all major moving parts, and assembled/open states. A local
mechanism coupon answers mechanics, not whole-object architecture. Cheap math may
reject an obviously infeasible concept earlier; do not use it to skip this gate.

For a closure, temporarily subtract the latch/snap: does the rest still align,
guide, seat and stop correctly? If retention disappeared, would the object remain
coherent and usable, merely unable to stay closed under disturbance? One mechanism
carrying alignment, guidance, stopping, structural support and retention is a
complexity warning that needs a concrete reason. Prefer geometry that guides, a
hard surface that seats/stops, enclosure that contains, retention that retains,
and release that releases. Multifunctional parts are allowed when justified.

Identify a small set of meaningful states along an explicit path: open/unassembled,
initial alignment, partial engagement, mechanism engagement, maximum required
flexure if relevant, seated/working, intentional release and open again. At each,
name which required relationships are established and which forbidden contacts
remain clear. Use deterministic CAD for interface facts where possible; this
requires neither a general motion planner nor a separate review artifact.

Before expensive mechanics, inspect a useful rough assembled/open view with realistic
contents. Explain how the user loads, accesses, browses where relevant, transports,
opens and closes the actual object: fingers, support, movement and regripping.
Add views only for distinct unanswered questions. Ask whether the central task is
improved enough to justify construction and operation. Awkward proportions,
handling requiring too much explanation, poor central-task performance or
accumulating compensating reliefs/guides/windows/shields/stops are stopping
conditions: reconsider or abandon the concept before further engineering.

For consequential subjective qualities (appearance, proportions, intuitive handling,
whether the object is worth owning), present the rough object for human review
when those choices have not been delegated, using the feedback rules above.
Automated self-assessment and valid CAD cannot supply that feedback. Explicit
delegation permits autonomous judgment but still requires willingness to reject
a poor concept.

Sunk CAD, tests, simulation or slicing never protects an architecture that fails
its purpose. Reopen the product choice even late; prefer deleting unnecessary
complexity over adding code to defend it. Separate product value from tool
validation: use simulation for a consequential uncertainty in an otherwise
worthwhile design. If an unnecessary mechanism creates the need for extensive
simulation, consider eliminating it first. Keep numerical benchmarks as independent
engineering experiments; a product project must not become a disguised framework
benchmark. A coupon or solver pass cannot settle whole-product value.

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

For force-loaded seated contact against explicit rigid mates, use
[`ContactQuestion`](../../../../physical_analysis/README.md#force-loaded-contact-questions).
Use `StructuralQuestion` for contact-free loads and `SnapFitQuestion` for a
specified passage/return operation. Prefer the existing combined master surface
for several obstacles sharing a slave region; do not duplicate overlapping pairs
without a concrete reason. Retain failed contact/mesh outcomes separately from
simple load screens and physical validation.

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

Before selecting a mechanism, state the intended task and consequential context:
what is accessed, which hand or surface supports the object, where the operating
hand acts, and the sequence of movement/regripping. Distinguish tasks that need
different layouts, such as frequent selection versus occasional bulk removal.
Use known preferences and document delegated assumptions; a simple object can
need only a sentence in its existing record.

For containers, establish the protection requirement before choosing openings:
dust exclusion, spills, impact and retention imply different closures. Reuse
known preferences; discuss consequential uncertainty when design choices have
not been delegated. Under autonomous scope, ordinary protective storage should
start with a covered cavity and overlapping closure unless ventilation or open
access serves the stated task. Finger cutouts and mechanism slots must not
silently create paths into the stored contents. Keep necessary snap travel or
grips outside a continuous inner enclosure where practical. A covered cavity or
labyrinth seam is dust-resistant geometry, not evidence of airtightness or an
ingress rating. Verify the actual closure and openings in CAD; physical sealing
requires suitable tests. Resolve access within that protection requirement,
rather than treating convenient removal as permission to leave holes. The user's
default for ordinary storage here is a fully covered cavity that excludes basic
dust and sheds incidental spills; do not silently substitute an open organizer.
Do not claim a watertight seal from covered geometry alone.

As soon as rough complete geometry exists, review the assembled object and its
normal handling sequence before detailed mechanism refinement or expensive
simulation. Assess whether local features form a coherent, usable object:
proportions, rim/guide transitions, openings, grips and exposed mechanisms. A
contact shape selected for solver robustness still needs deliberate integration
into the product; a successful local analysis does not justify its exterior form.

Before adding a finger cutout, compare the normal grasp with and without it,
including how much of the actual contents already projects above the rim. Remove
a cut that does not enable a needed reach or motion; extra openings can reduce
containment and introduce contact corners without improving access. For a useful
cut, review its final rim junctions through the
[edge-treatment guidance](parametric-and-edges.md#edge-treatment).

When operation moves substantial weight toward or beyond a freestanding object's
table support, screen tipping before refining the mechanism. Include relevant
empty, sparse and full contents distributions and critical opening/withdrawal
poses; state any stabilizing hand. Compare the gravity line with the supported
footprint, including operating forces when consequential. CAD centroids can
screen shape, but solid-volume weights do not predict low-infill printed masses:
use measured/slicer-estimated component masses or explicit mass sensitivity
assumptions. Keep the check and remaining physical observations with the object.
The [swatch cap comparison](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#comparison-at-handoff)
illustrates a gravity screen that motivated a rear foot; its printed stability
remains unqualified.

Check whether protruding catches or unprotected flexible arms could snag, receive
unintended handling loads or obstruct a grip. Consider recessing or protecting
them when useful, while preserving contact travel, access and manufacturability.
Make insertion and opening understandable from the grip and geometry. Coordinate
edge treatment and transitions; asymmetry or an exposed mechanism can be
appropriate when it serves the intended use. Do not impose symmetry, concealed
mechanisms or decoration as universal requirements.

For a grip intended to separate parts, identify which part each hand contacts
and the required force direction on each part. Check the accessible surface
normals in the closed assembly: an underside scoop can help lift a part while
providing no downward geometric purchase to hold it against an upward pull.
If operation relies on friction or wrapping fingers onto another face, state
that dependency rather than claiming a positive grip from the recess alone.
A printable ramp and a visible cutout do not establish useful hand-force
direction. Reversing a ramp also needs an access check with the other part fitted.

The user's default in this repository is to conceal mechanisms in the assembled
object where practical, leaving understandable, modest controls for operation.
Prefer covers, internal interfaces or protected recesses over exposing the whole
flexure or catch for convenience during analysis. Inspect both the working
mechanism and the final covered appearance; an inspection pose is not the
product's intended appearance. Discuss a consequential visibility/access tradeoff
when autonomy has not been delegated, and choose/document it when it has. This
preference does not require hiding a feature whose exposure serves the task.

Choose the cheapest evidence for the remaining handling question; these are
available methods, not three mandatory stages:

| Method | Establish | Limit |
| --- | --- | --- |
| Task walkthrough and useful views | Supporting/operating contact locations, motion direction, access, surrounding space and understandable operation | A plausible sequence does not establish comfortable handling |
| Targeted CAD checks with reference envelopes or poses | Clearance, reach or extraction along the stated path and sampled poses | Access for an assumed envelope is not a validated human grasp or comfort result |
| Physical handling of a suitable mockup or print | Actual grip, coordination, friction, effort and tactile response in the tested task | A mockup only establishes the behavior it represents; results depend on the tested user/setup |

Reuse clear views and component builders. Add object-owned inspection geometry
only when it answers a question; identify display-only hands, held items and
supports. If line drawings obscure depth, choose a clearer camera or shaded CAD
view when available. Better presentation does not repair awkward geometry.
Style variants are conditional on the unresolved choice; no new rendering tool
or separate review file is required.
Human review of undelegated consequential choices follows the architecture gate;
this is not a repeated approval of routine details.

For a consequential access uncertainty, start with a simple finger/thumb or tool
envelope and selected poses, documenting dimensions, their source/assumption,
approach path and intended contact. Check unintended obstructions rather than
treating deliberate grip contact as a failure. If a pose fails, consider plausible
alternative poses before rejecting the design. Do not infer comfortable skin
contact, grip friction or acceptable human effort from clearance or mechanism FEA
alone.
Keep task-specific poses and checks with the model; extract shared operations
only after a real consumer demonstrates their value, without introducing a
general hand simulator. Translate unresolved assumptions into the
[physical observation plan](physical-experiments.md#recommend-a-first-print-without-blocking-modelling).

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
For an asymmetric held item, derive its reference geometry in its source frame
and apply one documented physical rotation/translation to the whole item. Check
front/back, feature location and handedness against that source before tuning a
mate. Reconstructing a recess beside an independently rotated outline can create
a reflected item that cannot be inserted in the illustrated pose. Rendering and
contact assertions using that same invented reference cannot expose the error.
Include a wrong-face or mirrored-item negative check when that failure would
change engagement. When alignment relies on a spring pressing onto a rigid
datum, verify opposing support spans the load region or explain the alternative
restoring constraint; collision-free placement alone does not establish a stable
attitude. Keep these checks tied to the relevant item and contact pairs.
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

For a joint intended to stay connected, distinguish entry clearance from seated
play. Name what removes that play and holds the parts together: interference with
compliance, a wedge, spring preload, a fastener, or a positive catch. A clearance
key can limit large motion while still rattling or falling out; collision witnesses
alone cannot qualify it. Before exporting a retention sample, screen whether the
actual seated contacts can supply force in the accidental-release direction. A
friction-only fit with a gap and no external normal load has no designed holding
force and must be revised before printing. Use
[`elastic_friction_grip`](../../../../physical_analysis/README.md#friction-only-retention-screen)
for that cheap rejection; positive preload is necessary for this route but does
not by itself establish useful force. Do not substitute more clearance for a
working retention feature or blame printer precision without evidence.
Use the effective preload after the assembly closes, settles or takes up guide
play; interference in an artificially separated pose can disappear during use.

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
