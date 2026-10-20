# Surface isolation — architectures beyond changing the ties

[Object record](../README.md) · [Printed B approval and earlier D investigation](b_surface_concepts.md)

**Current question:** how can the internal damping structure affect the printed
object-facing surface much less? The user finds D's tie rearrangements
insufficient as the main answer. This investigation changes the manufacturing
sequence, component boundary or support path instead. B08/B16 stay approved;
no new printable models or presets are made in this SVG-only phase.

## Current route — print-first correction

The user subsequently finds these suggestions insufficiently grounded in
printability and requests one piece ideally, two acceptable, with no complicated
assembly; they confirm up to two cup pieces plus the usual lid pad. The **current comparison is [P1/P2, including print sequence and complete
liner counts](print_first_concepts.md)**. E1 is reworked there with an integral
floor core and one lid pad. E5/E6 are retired from the active shortlist for their
whole-liner part/retention burden, not a claimed failed print of their individual
parts. P1 is three pieces including the pad; P2 is two pieces but requires eight
folds. Both costs are exposed before any CAD choice. **Latest correction: P1 is set
aside for depending on upright thin TPU walls despite prior physical failures;
P2/folding is also rejected for poor printability when adapting to other models.
Neither remains an active proposal.** B08/B16 remain approved.

The following E sections preserve the earlier proposal and its reasoning;
their former next steps and shortlists are superseded by that review.

## Historical shortlist and repaired explainer — 2026-10-21

The user finds the earlier blue/green encoding unclear and cannot see how E1
provides deformation space between the cups. They find E2/E4 unconvincing and
are strongly doubtful about E3. **E2/E4 are dropped from the active shortlist;
E3 is set aside.** This is concept feedback, not a physical test or a claim that
the mechanisms were disproven. E1 remains interesting, not approved for modelling.
The latest “fix and implement” request is implemented as the ongoing SVG
explainer phase: new explanatory drawings and two new suggestions, no new CAD.

[Current overview SVG](../renders/concepts/surface_isolation_overview.svg) ·
[E1: two cups and attached springs](../renders/concepts/surface_isolation_separate.svg) ·
[E5: separate corrugated insert](../renders/concepts/surface_isolation_wave.svg) ·
[E6: hollow tube cushions](../renders/concepts/surface_isolation_tubes.svg).

### Read the colours as actual parts

All TPU would be **black** in the real print. The colours identify physical roles,
not different filaments, material hardnesses or arbitrary decorative surfaces:

| Drawing appearance | Physical meaning |
| --- | --- |
| Blue | The separately printed smooth **inner TPU cup**, touching the contents |
| Dark grey | The **outer TPU cup**, backed by the existing rigid container |
| Orange | **Flexible TPU spring material** in the gap; attached to the outer cup in E1, a separate insert in E5/E6 |
| Pale grey | The **existing rigid test box**, supporting the outer cup |
| White | **Empty space** into which springs can bend/flatten; the white bore in a tube is also empty |
| Red arrows | An impact or assembly direction; not a material |
| Orange diagonal hatching in the assembly view | Location of the spring region; not a solid orange slab. Individual springs are drawn in the close-up. |

The whole-container side cut establishes which cup is inside which. The close-up
then looks **down** through a wall, showing the spring before and during a local
impact. Arrows, part labels and the legend repeat in every drawing. Drawn motion
is deliberately exaggerated, not computed deformation. The content proxy is a
small circle labelled “nut”, not a new container component.

### Where E1's damping space is

**Nut → inner cup → flexing TPU springs → outer cup → existing rigid box.**
The two cups do not occupy the same wall position. There is a real gap between
them, partially occupied by curved spring loops. When a local inner panel is
pushed outward, those loops bend into the remaining white space. The rigid box
backs the outer cup; the drawing does not require the whole inner cup to slide
sideways as a rigid body. TPU flexing is intended to cushion the impact and
dissipate some energy. Empty air alone is not the intended damper and no sealed
pneumatic chamber is assumed.

E1's orange loops are part of the outer cup, with their tips contacting the inner
cup after assembly. They are **not bonded to the inner cup**, and the inner cup
is printed independently with no cell junctions beside its visible surface.
The new cartoon shows engaged tips before the impact. The earlier 0.2 mm take-up
budget was an unselected example; actual fit/preload and travel are still open.
Rim retention must preserve panel movement. Solid corner lands stay in the cup
parts and can carry stiffer local loads; they do not imply welding the two cups
into a full-thickness solid corner across the assembly clearance.

The hatched region beneath the inner floor marks a needed elastic floor pad,
not unsupported floating clearance. The lid needs a matching elastic stack.
Their detailed core geometry and retention remain to be designed; this wall
explainer does not claim a complete tested assembly. Springs can still bottom
out, rub or indent a panel after assembly, so print separation is not a guarantee
of unchanged surface texture under use or useful damping.

### Two new suggestions within the two-cup arrangement

E5/E6 retain the part relationship the user finds interesting. They change the
actual spring mechanism and manufacturing boundary, rather than rearranging
B's dots or returning to the set-aside E2–E4 architectures.

**E5 — plain cups with an independent corrugated TPU insert.** Both cups print as
unstructured shells. A third spring piece sits in their wall gap. Folds flex and
may slide under the inner panel's load, with end/free space for that motion.
This removes core junctions from the print of **both** cups, unlike E1's sprung
outer cup. The cups could be kept constant while separate inserts are compared.
The upright wall insert can have a constant XY section and print from its lower
edge. Its retention, fold buckling, end motion and friction are open;
floor/lid require corresponding separate modules. The drawn folded shape is a
qualitative proposal, not an inextensible-sheet solution or predicted stroke.

**E6 — plain cups with retained hollow TPU tubes.** Round, open-ended tubes sit
between the cups. A tube wall can flex while the round section flattens toward an
oval; its bore and the spaces between neighbouring tubes allow movement. The
illustrated shapes are qualitative. Leave lateral space for bulging and use
outer retention to control rolling/migration, without welding tubes to the inner
cup. Print tubes upright with open ends; floor tubes can be reoriented after
printing and may need a separate tray. Ends remain vented: this proposal uses
flexing TPU walls, not compressed sealed air. More pieces, friction, eventual
wall contact and variable collapse force are unresolved costs.

These are new discussion proposals, not print-ready variants or claims of
better quietness. Ordinary Classic slicing, solid corner lands and unconstrained
thickness remain applicable. Tube diameter/wall, fold thickness, part capture,
corner clearance, floor/lid integration and all spring stiffnesses remain open.
No custom toolpath, supports trapped inside a sealed tube, glue or new material
is assumed.

**Next discussion:** whether the explained E1 arrangement makes sense, and whether
an attached loop, independent fold insert or hollow tube is the more useful
spring to develop. No automatic promotion to CAD or a print recommendation.

## Clarifications that govern this exploration

- Wall and overall lining thickness are **not constrained**. The old 1.6 mm
  sandwich is a printed reference, not an upper limit for these concepts.
- The material is normal **black TPU**. The principal defect is a visible surface
  pattern, with occasional apparently random bumps. Translucency is explicitly
  not the user's issue; opacity, colour changes and hiding see-through infill
  are excluded as explanations/solutions here.
- The user wants corners solid for a reasonable distance to avoid print defects
  around the turn. Solid corner components and a gradual transition into the
  active region are part of the proposals, not an optional late cosmetic edit.
- Ordinary Classic slicing without Arachne remains required. Multi-part concepts
  are proposals with explicit assembly costs, not an assumed accepted replacement.

**Finish line for this phase:** compare genuinely different ways of separating
surface production from core production, show corners and full-object assembly,
and identify the trade-off that would decide the next design. No numerical
surface-quality or damping rating can be inferred from a diagram.

## What the existing evidence supports

The [retained B paths](b_existing_routes.json) already show a closed contact
contour through a tie layer. They also show more disconnected internal chains
on tie layers than between them. That is evidence of nearby path changes,
not proof that those changes caused the reported surface pattern. Fewer chains
alone cannot qualify a smooth black TPU surface, which is the user's correction
to the D investigation.

Possible causes include local deposition/pressure changes beside ties,
differential cooling/shrinkage, and changes in line texture or sheen. Bumps
could be related or separate. These remain hypotheses; there are no defect
photos, path-to-defect registration or measured surface profiles. “Visible” does
not automatically mean “raised”, and black material does not identify which
process mechanism is responsible.

Orca's [wall/surface documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_wall_and_surfaces#print-infill-first)
describes how attached infill can push a wall and affect its finish. B's ties
are explicit CAD geometry, so that guidance does **not** prove an infill setting
is the cause here. It motivates questioning a shared thin facing/core boundary.
[Klipper's pressure-advance guidance](https://www.klipper3d.org/Pressure_Advance.html)
also distinguishes corner/layer-change behavior and nozzle/filament-dependent
calibration. Neither source provides a calibrated prediction for these prints;
no firmware change or new tuning preset is made.

**Method choice:** a topology/print-sequence comparison is useful now. A static
TPU FEM calculation would answer an assumed deformation problem, not predict
visible extrusion texture or sheen. The necessary process inputs are missing;
no solver study is justified for this decision. Existing path evidence is
retained without rerunning its slices. Later physical inspection must compare
the same surface under the same oblique lighting and separately check by touch.
This is a surface study, not another phone dB optimization.

## Four distinct approaches

**Earlier exploration — superseded shortlist.** E2/E4 are now dropped and E3 is
set aside. Their descriptions below preserve the reasoning and limits; they are
not current recommendations. The original four-way overview is retained in Git
`11e7b49`; the live overview now shows E1/E5/E6.
All views are schematic, not to scale or actual future toolpaths. Illustrative
thickness budgets show the design freedom; none is a selected requirement or a
minimum. All retain a compliant region, unlike the rejected fully solid C liner.
A thicker face can still harm damping; the presence of an air core is no guarantee.

### E1 — print the smooth inner cup separately

[Detailed SVG](../renders/concepts/surface_isolation_separate.svg).
Make a uniform, unstructured inner cup and a separate outer spring carrier.
The visible cup is printed on its own; the carrier's cell boundaries, starts and
travels cannot occur beside that cup's surface **during its print**. Nest them
after cooling and capture them at the rim/floor perimeter with the existing
container/lid concept. No adhesive or local face weld is assumed.

A possible carrier has continuous vertical C-shaped spring channels: their XY
section stays constant through the upright region and grows from a supported
base. This avoids assuming that one-sided B tie stubs can bridge from a backing
into empty air after removing the inner skin. The spring geometry is unqualified
and need not reproduce S16's directly bonded ribs. Floor posts can grow vertically
from the separate carrier backing before assembly, with no printed roof over them. Keep the carrier pattern
subordinate to the independently printed face, rather than optimizing dot count.

Illustrative stack: 0.8 mm carrier backing + 2.0 mm spring region + 0.2 mm fit
take-up + 1.6 mm contact cup = about 4.6 mm. Fit allowance and preload need later
selection; tips may engage only after take-up. Solid lands extend around the
printed cup's corners, with a tapered transition into uniform wall thickness.
The carrier also has solid corner components; assembly clearance is still a gap,
not a claim of fused full-thickness corner material.

**Cost:** two cup components and two matching lid-stack components instead of
one cup/pad pair; insertion and capture become extra interfaces. Upright layer
lines and an ordinary seam still exist on the inner cup. In use, spring contacts
could still indent it or change damping. Independent printing removes the
manufacturing connection, not every possible mechanical influence afterward.

### E2 — print the contact faces flat, then assemble the walls

[Detailed SVG](../renders/concepts/surface_isolation_flat.svg).
Print wall tiles with their object-facing sides against the build surface.
Complete a continuous solid facing thickness first, then grow open ribs/posts
on the back in later layers. Put those tiles into a separate carrier, which
provides the continuous outer backing and solid corner rails. The floor and
lid face use the same process. The core is closed by assembly, not a printed
roof over its air spaces.

**The change:** the nozzle is not printing a vertical contact face beside tie
junctions in the same layer. The face is bed-supported when it is made, and the
core features start above an already continuous plate. The [Prusa support guide](https://help.prusa3d.com/article/support-material_1698)
identifies splitting/reorientation as a way to change manufacturing constraints;
this specific tile architecture and its surface benefit remain our proposal.

Example stack: 1.6 mm solid facing tile + 2.0 mm open core + 0.8 mm carrier backing.
The plate transfers its own finish; a smooth result depends on the appropriate
build surface and first-layer process, not an automatic promise of gloss.
Later cooling can still deform a tile. This does not require ironing vertical
faces, custom G-code, Arachne or gluing foam into the liner.

**Cost:** six face tiles plus carrier and lid backing, approximately eight
printed components. Corner joints and capture rails must keep contents away
from gaps or exposed hard backing. Solid corner rails are assembled afterward;
there is no container corner to turn around during a wall tile's flat print.
This is the strongest change in face-manufacturing orientation, with the largest
assembly burden. A folded one-piece net is not assumed: bending a thick sandwich
would introduce an additional unqualified hinge and corner-sealing problem.

### E3 — support the inner cup only at its boundaries

[Detailed SVG](../renders/concepts/surface_isolation_boundary.svg).
Use a separately printed smooth cup whose load path reaches the outer carrier
through solid corner lands, rim and floor perimeter. Leave a clear, vented space
behind the broad faces: no dots, ribs or spot contacts directly behind those
panels. The broad face acts as a diaphragm under an impact and can eventually
contact a continuous backing stop. Corner supports are built into the contact
cup where they affect its own printed corner; outer corner spacers complete the
assembled load path.

This differs from E1: E1 keeps compliant support beneath the broad face; E3
moves that support to its boundaries. It removes local support attachment sites
rather than just moving fewer of them around. Both parts are printed separately;
otherwise a broad suspended floor could require a poor full-span bridge.
The inner floor prints directly on the bed and is then set on the carrier's
perimeter support. The separate lid face is handled similarly.

Illustrative space: 1.6 mm contact face + 2.0 mm free motion gap + 0.8 mm backing.
No hermetic air spring is assumed; a concealed vent route would need design.
Corner lands deliberately consume some damping stroke locally.

**Cost:** bowing, wrinkling, floor sag, abrupt bottoming and corner-transmitted
sound are real open risks. A face thick enough to stay smooth may be too stiff
for useful damping. Layer lines and seams remain. This is an exploratory support
architecture with less confidence in function than E1, not a recommended print.

### E4 — a generous continuous face buffer, in one piece

[Detailed SVG](../renders/concepts/surface_isolation_buffer.svg).
Keep a monolithic hollow liner, but place the core behind a substantially thicker
uniform object-facing wall. For example, allocate 1.6 mm to that face, 2.0 mm to
a compliant core and 0.8 mm to the shell-facing backing: about 4.4 mm overall.
The 1.6 mm face offers room for multiple ordinary-width paths instead of B's
0.5 mm facing. The [wall-order documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_wall_and_surfaces#walls-printing-order)
explains that some orders need at least three actual walls; the physical space
must exist before considering such an order. These are lane-space illustrations,
not a guarantee of a particular Classic path count.

**The change:** separate the core boundary from the visible surface with a wide
continuous material region. Keep solid corner lands and taper the core's return
away from them. This is a buffer, not true isolation: the core remains bonded to
the same part and its local heat, shrinkage or deposition effects can still reach
the face. Thickness freedom makes this a reasonable comparison control, but it
is the weakest architectural departure here. A uniform buffer is not a mandate
to make the whole lining solid like C.

**Cost:** more TPU, reduced cavity if the shell stays fixed, more bending
stiffness, and unknown damping. It might merely reduce the pattern amplitude.
Core and horizontal roof bridging still need the later ordinary slicing review.

## Corners — new requirement and current-source answer

[Corner comparison SVG](../renders/concepts/surface_isolation_corners.svg).
The R2 A/B code cuts a continuous square annular wall core;
[`support_checks.py`](../support_checks.py) explicitly expects air at the corner
core witness. Its 0.5 mm outside skins turn the corner, and floor/rim caps add
material, but there is no dedicated full-thickness solid corner land extending
along both adjacent walls. A's frame islands do not change that corner policy.
C is solid throughout. This answers the current A/B question from authoritative
source and retained evidence without creating new CAD.

For a future monolithic design, fill the whole corner sandwich over a length
**g along each adjacent face**, then taper into the active core over a transition
**t**. A discussion starting range is g = 4–6 mm and t = 2–3 mm; these are agent
examples, not selected limits or a proven prevention distance. Taper in the
horizontal plan and keep the profile consistent through the upright height, so
the transition is not a sudden vertical feature start. Keep tie/cell junctions
outside the solid land and its transition. Floor and rim junctions also need
continuity, rather than protecting only a mid-height section.

For E1/E3, build solid corner regions into the inner cup itself where possible;
post-assembly outer blocks alone cannot repair a defect created while printing
that cup. For E2, each tile prints flat and corner capture occurs in separate
solid rails. Exact joins, retained clearances, sharp-edge treatment and support
access remain design questions. No existing STL or STEP is changed.

A filled corner can avoid a local hollow-core transition at the turn, but it
also gives a stiffer impact path and moves the transition elsewhere. It cannot
guarantee the corner seam, flow or cooling defect disappears. The later test must
check the turn **and the end of the land**, not just a nicer broad-face photo.
On a small fixed box, large lands may occupy much of a face. With an unchanged
34 mm envelope, a 4.4 mm lining leaves a 25.2 mm nominal clear width, versus
30.8 mm in B. Keeping the test shell fixed reduces the cavity; enlarging it changes the
comparison fixture. That choice stays open in this diagram phase.

## Suggested direction and evidence boundary

**Historical recommendation, superseded by the current shortlist above:** prioritize E1 and E2 for discussion. They change how the visible face is
manufactured, not merely the number or placement of ties. E1 is the cleaner
whole-container arrangement with a separate plain cup; E2 gives the strongest
change in face orientation at the cost of many pieces. E3 is an alternative
mechanical architecture to challenge direct face support. E4 is a useful
one-piece buffer control, not the main answer to the user's request for a
creative departure. None is already approved or claimed to outperform B.

Later, after selection, the decisive checks would be ordinary Classic retention
of the selected facing and core, corner/transition behavior, manageable part
capture, and a physical comparison of black surface texture under fixed oblique
light. Damping, indentation, insertion survival and bottoming must be compared
separately to approved B08/B16. Changing thickness is allowed; losing useful
damping remains unacceptable. No automatic toolpath metric promotes surface
quality, and no new CAD, smoke slice or physical result exists for E1–E4.

| Item | Print status | Artifacts | Next action / limit |
| --- | --- | --- | --- |
| Approved B08/B16 | Yes — unchanged baseline | Existing R2 pairs | Retain approval; reported surface marks remain unresolved |
| D1–D3 | N/A — SVG concepts | Earlier D diagrams | Inadequate as the main solution; not disproven secondary experiments |
| E1, E5 and E6 | N/A — SVG discussion | Repaired E1 explainer and two new core mechanisms | Explain parts, gap, deformation and assembly; no CAD or physical qualification |
| E2/E4; E3 | N/A — superseded concepts | Earlier SVGs retained with status labels | E2/E4 dropped; E3 set aside after user doubt; not physical failures |
| Final application liner | N/A — not designed in this phase | None new | Existing application failures remain unresolved |

Attribution: primary language model GPT-6 family; exact runtime identifier and
reasoning effort not exposed. Harness: Codex shared-workspace CLI/API agent;
provider OpenAI. No subagents. User supplies the correction, black-TPU report,
thickness freedom and corner requirement. This phase authors the architectural
investigation and vector drawings; cited sources explain process considerations,
not validation of these proposals. No third-party diagrams or meshes copied.

Explainer-repair attribution, 2026-10-21: same primary model/environment/provider
fields as above; exact identifier/effort not exposed. User supplies the rejection
of the earlier explanation and tentative interest in E1. This phase authors the
role-labelled, before/impact SVGs and the E5/E6 mechanisms. No new CAD, exports,
print settings or physical results.
