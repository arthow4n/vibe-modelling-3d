# Surface isolation — architectures beyond changing the ties

[Object record](../README.md) · [Printed B approval and earlier D investigation](b_surface_concepts.md)

**Current question:** how can the internal damping structure affect the printed
object-facing surface much less? The user finds D's tie rearrangements
insufficient as the main answer. This investigation changes the manufacturing
sequence, component boundary or support path instead. B08/B16 stay approved;
no new printable models or presets are made in this SVG-only phase.

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

[Overview SVG](../renders/concepts/surface_isolation_overview.svg).
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

**Prioritize E1 and E2 for discussion.** They change how the visible face is
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
| E1–E4 and corner concept | N/A — SVG investigation | Six new SVGs, preview images | Discuss architecture; no printable models or exports |
| Final application liner | N/A — not designed in this phase | None new | Existing application failures remain unresolved |

Attribution: primary language model GPT-6 family; exact runtime identifier and
reasoning effort not exposed. Harness: Codex shared-workspace CLI/API agent;
provider OpenAI. No subagents. User supplies the correction, black-TPU report,
thickness freedom and corner requirement. This phase authors the architectural
investigation and vector drawings; cited sources explain process considerations,
not validation of these proposals. No third-party diagrams or meshes copied.
