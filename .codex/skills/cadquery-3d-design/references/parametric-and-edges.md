# Parametric construction and edge treatment

## Maintainable parametric design

Strongly prefer parameterized construction so the model is easy to maintain and revise when the user changes dimensions or requirements. Aim to make most major geometry respond to a small, understandable set of inputs rather than requiring edits throughout the construction code.

* Group clearly named, user-editable parameters near the top of the source, with units and brief comments where useful. Cover main dimensions, interfaces, thicknesses, clearances, repeated-feature counts and spacing, and meaningful edge treatments when likely to change.
* Define each independent dimension once. Derive dependent dimensions, feature positions, patterns, and symmetry from those inputs so a size change propagates consistently. Keep deliberate fixed dimensions, such as hardware interfaces or printability limits, independent where appropriate; do not blindly scale everything.
* Keep nominal dimensions and fit allowances distinct. Explain non-obvious relationships, and add simple checks for invalid combinations such as a wall thicker than the available space or a retaining opening larger than the item it must retain.
* Choose readable construction and feature selection that can tolerate expected dimension changes. Avoid scattered magic numbers, duplicated dimensions, and brittle assumptions about edge ordering where practical. When modifying an existing model, update its parameters and relationships before adding one-off geometry overrides.
* During review, check that a likely user request—such as changing width, device thickness, or hole spacing—can be handled through a small number of parameter edits. Evaluate an alternate configuration only when a credible dependency failure would change the design or documented adjustment range; restore and re-evaluate the requested configuration before final exports. State any known range restrictions; one alternate build does not prove every combination works.

Do not parameterize every incidental coordinate or introduce a general-purpose configuration framework without a benefit. Fixed local details are acceptable when they improve readability and are unlikely to need independent adjustment. Prioritize useful editability of the main design over parameter count.

## Components and shared parameters

Use multiple Python files when separating components or shared dimensions makes a model easier to construct, inspect, change, or debug. A single file with small builder functions is also appropriate; do not split files merely because an object contains several features.

* Keep one clear main entry point, such as `<object_name>.py`, that builds the final object from its components. Component modules may provide builder functions returning geometry; avoid triggering exports or unrelated work on import. Keep modules, parameters, evaluation entry points, and derived artifacts inside `model/<object_name>/`.
* A shared `parameters.py` or similarly named configuration module can hold the editable dimension table, units, and fit allowances. Give shared interfaces one source of truth and derive component dimensions from it; avoid copied parameter tables, circular imports, and mutable global state. Document the file the user should edit to change dimensions.
* Define component coordinate origins and assembly placements clearly. Build and evaluate a component independently with the shared CadQuery command when that makes a difficult feature easier to inspect. Ensure evaluation entry points expose geometry in the form the tool expects, and verify local imports work through the command without relying on an interactive session. A parameter-only module is not a geometry evaluation target.
* Bring components together early enough to check alignment, clearances, retention, interference, and the installation/removal sequence. Independently valid parts do not prove the assembled object works. Re-evaluate affected components and the final main entry point after changing shared parameters.
* Distinguish code organization from physical part separation. Separately built features intended as one printed part must form the intended connected solid. Parts intended to remain separate need individual printable exports and documented assembly placement; review each part's print orientation as well as the assembled fit. Splitting source files alone is not a reason to add physical joints.

When one evaluation needs identical copies or several crops of the same component,
build that component once and derive translated copies or intersections from it.
For example, a two-ended connector sample can crop both ends from one actual
base instead of calling the complete base builder for each end. Keep distinct
parameter configurations separate and avoid mutating shared geometry. Reuse is
local to that evaluation; it does not need a persistent cache or replace checks
against the complete assembly when a crop omits an insertion blocker.

For variants of one object, keep repeated applicable CAD checks in an object-owned
helper taking the actual builders/geometry and expected interface values. Thin
entry points add their differences rather than copying complete check scripts.
Preserve each assertion's purpose and scope; sharing code does not qualify a new
variant without running its affected checks. Do not build a general test framework
for one object's fixtures.

### Assembly representation

For new or substantially revised multipart engineering, recommend native
`cq.Assembly` with the [assembly geometry API](../../../../assembly_geometry/README.md)
when checks, inspection or print layouts share named components/poses, or when
explicit pair/path diagnostics materially help the investigation. Choose this
representation before organizing placements and checks. Keep authoritative
geometry builders and operating relationships in the object; an object-owned
factory can share them across configurations and variants. Deterministic
placements need no constraint solve.

Opt out when an existing local check already gives adequate evidence, a simple
one-off needs only shapes/functions, or the API cannot represent the required
behavior without obscuring it. For an otherwise applicable multipart task,
briefly state the reason and retained evidence in the existing object record;
no separate checklist or permission is needed. This recommendation does not
require migrating unchanged models. `check_pair()` can provide explicit criteria
without an assembly snapshot.

The API captures positioned geometry, qualifies a bounded set of native constraint
solves and evaluates declared pair/path intent. The object still chooses actual
references, required contacts, exclusions, thresholds and path coverage. Keep
analysis masks/envelopes distinct from physical components; a useful negative
case can expose a check that accepts a missing support or retaining feature.
Use positioned component shapes with existing physical questions, with explicit
supports, loads and contact assumptions. The implementation documentation owns
[contracts and remaining gaps](../../../../assembly_geometry/README.md#remaining-gaps-and-extension-decisions).

## Edge treatment

For everyday objects, sharp CAD edges are not finished geometry by default. Actively decide whether exposed edges should be filleted, chamfered, or intentionally left sharp. Consider edges touched by fingers or hands, insertion openings, cable slots, clips and retaining features, handles and grips, corners likely to catch on clothing or nearby objects, parts that slide against another object, mating and alignment features, exposed corners that may chip or feel unpleasant, and 3D-printed transitions that create unnecessary stress concentrations. Visible and touchable exterior corners should usually receive intentional edge treatment unless a sharp edge is functionally required.

Prefer a **fillet** when the part is touched frequently, a softer ergonomic transition or molded/product-like appearance is desirable, reducing stress concentration is useful, or a curved transition improves handling or insertion. Prefer a **chamfer** when helping one part enter another, guiding insertion or alignment, breaking a sharp edge with minimal geometry, creating a lead-in around holes, slots, pegs, sockets, or mating interfaces, or when a flat bevel better matches the intended mechanical form. Do not mechanically fillet every edge; choose treatment based on function and visual intent.

Keep edge treatment proportional to the feature. Avoid huge radii that change intended dimensions, tiny cosmetic fillets that add complexity without value, fillets that interfere with mating surfaces or reduce retention lips, clip engagement, or required clearances, and chamfers that unintentionally enlarge openings or weaken thin walls. Preserve fit, retention, and mating geometry first, then apply edge treatment around it.

For handheld objects, assess broad corners, finger-contact rims and protruding mechanisms together. A tiny edge break can remove mathematical sharpness while leaving an uncomfortable overall shape; judge the scale of the treatment against how the object is gripped and carried, not merely whether fillets exist.

For openings cut through a rim, review the final inner and outer junctions in
plan and a relevant side/section view. A circular scoop or rounded face lip can
still terminate in an abrupt inward corner where it meets another surface;
rounding the cutting profile alone does not qualify those junctions. Remove an
unnecessary opening before spending effort blending it. For a needed opening,
make the finger-contact path continuous through the junction, preserving the
functional lead-in and remaining wall.

Review edge treatment in the chosen print orientation. A fillet on a bottom edge can reduce bed contact and introduce a difficult overhang; use a suitable chamfer or retain the bed-contact edge when appropriate. Recheck thin walls and lead-ins after edge treatment so smoothing does not make them unprintable.

## Fillet and chamfer failure handling

If a fillet or chamfer fails because of topology or an excessive radius, do not repeatedly retry arbitrary radii. Identify the problematic edge or radius, reduce the radius or apply the treatment selectively, and preserve the successful main geometry. Do not redesign a sound model solely because a cosmetic fillet fails.

Localize the selection before changing treatment: face boundary selections may
include tangent seams that need no edge break. Connected rim/window lips may
also need one combined fillet operation, because an earlier fillet changes the
topology required by the next. Inspect the selected edge types and adjacency;
exclude smooth seams and treat the intended sharp junctions together when
appropriate. The [R2 rim fixture](../../../../model/filament_swatch_box_study/archive_corner_proposals.py)
uses that approach. This is a diagnosis option, not a guarantee for every fillet.
