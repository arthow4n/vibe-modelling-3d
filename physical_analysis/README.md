# Physical questions from CadQuery

A small, solver-independent case API with a working Gmsh → CalculiX backend.
Source geometry stays in CadQuery. Callers describe named parts, material
assumptions, supports, total surface forces, translations and explicit contact
pairs. The backend owns meshing, solver input, execution and result extraction.
It supports any number of named parts/pairs; it is **not** a general mechanism,
joint/dynamics, plasticity or printed-material simulator.

## Setup

`uv sync --locked` installs the editable Python package and pinned Gmsh binding.
Install CalculiX and Gmsh's native library dependencies on the host, for example
on Ubuntu 24.04: `sudo apt install calculix-ccx libxft2 libglu1-mesa`.
`CALCULIX_COMMAND` can name an alternative executable (a path, not shell syntax).

This development environment has no passwordless sudo. Ubuntu packages were
instead downloaded with `apt-get download` and extracted with `dpkg-deb -x`
under `~/.local/opt/physical-analysis`. The backend recognizes that prefix, or
`PHYSICAL_ANALYSIS_RUNTIME`, and adds its `usr/lib/x86_64-linux-gnu`, `blas` and
`lapack` subdirectories to the isolated worker's library path. No native binaries
are stored in Git. Required packages here were calculix-ccx, libspooles2.2t64,
libarpack2t64, liblapack3, libblas3, libgfortran5, libopenmpi3t64 and their Ubuntu
runtime dependencies, plus libxft2. A system installation is simpler elsewhere.

Run `uv run --locked python -m physical_analysis doctor` to check both tools;
run `uv run --locked pytest -q tests/test_physical_analysis.py` to qualify them.
Missing tools are failures, not silently skipped benchmarks.

## Use

```python
import cadquery as cq
from physical_analysis import AnalysisCase, Region, PETG_SCREEN

beam = cq.Workplane('XY').box(40, 8, 2, centered=False)
case = AnalysisCase('tip_load', nonlinear=True)
case.add_part('arm', beam, material=PETG_SCREEN, mesh_size_mm=1)
case.fix('arm', Region.plane('x', 0))
case.apply_force('arm', Region.plane('x', 40), force_N=(0, 0, -0.1))
answer = case.run('notes/tip_load_run_01').require_completed()
print(answer.metrics)
```

All coordinates are assembly coordinates, in mm. Forces are N, stress and
modulus are MPa. `Region()` means the entire part; `Region(lower, upper)` is a
box. Plane regions select a coordinate plane. Constraints select nodes; surface
loads/contact select **complete exterior quadratic triangle faces** inside the
region. Empty selections fail. Partition a CAD face when a small load patch
needs exact boundaries; a box cutting through triangles approximates that patch.
Total force is integrated over the selected surface, not multiplied by node count.

`fix(part, region)` fixes all three displacement components.
`constrain(..., displacement_mm=(0, None, None))` fixes only x.
`prescribe_motion(..., displacement_mm=(None, None, 1))` ramps z to 1 mm while
leaving x/y free. It translates a selected region, not a hinge rotation.
A fully prescribed part behaves as a moving obstacle; otherwise an explicit
material and sufficient supports are required. Do not overconstrain a flexure's
free face unless that is the actual loading fixture.

```python
case.contact('spring', Region.plane('z', 2),
             'obstacle', Region.plane('z', 2.1), penalty_N_mm3=60000)
```

Contact uses frictionless penalty contact. The default
`discretization="node_to_surface"` preserves existing cases; the optional
`discretization="surface_to_surface"` integrates over contacting faces and is
qualified by the compression benchmark and conditional storage-box studies.
The [CalculiX 2.21 manual](https://www.dhondt.de/ccx_2.21.pdf) cautions against
node-to-face contact with quadratic elements. Surface-to-surface contact enabled
the revised box's pass-over studies after exploratory node-contact timeouts;
geometry also changed, so this is not an isolated formulation comparison.
Both choices require an explicit penalty stiffness.
In CalculiX 2.21, node-to-surface normally updates the pairing during Newton
iterations, freezing it from iteration nine to improve convergence;
surface-to-surface updates it once at the start of each increment and keeps it
fixed during that increment ([manual, §7.22 and §10.4](https://www.dhondt.de/ccx_2.21.pdf)).
Surface-to-surface can accumulate large total travel, but each increment must
resolve changes at edges and curved leads. It is not the same per-iteration
finite-sliding algorithm. Earlier result assumption strings calling every
formulation finite sliding are inaccurate descriptions, not evidence of that
capability. Keep those historical results and reassess consequential motion
resolution instead of silently relabelling their predictions.
Check engagement, penetration, force balance, mesh sensitivity and penalty
sensitivity before using its numbers. No geometry is silently adjusted to close
gaps. Loads retain one proportional static ramp. A translation can instead follow a
piecewise-linear progress curve in the same nonlinear step:

```python
case.prescribe_motion('obstacle', displacement_mm=(-8, 0, 0), name='drive',
                      progress=((0, 0), (.5, 1), (1, 0)))
```

Each pair is normalized time and multiplier of the reference translation.
Times must increase from `(0, 0)` through time 1; the curve can reverse or pause.
This example drives 8 mm and returns, retaining contact/deformation in one solve.
It is a quasi-static path, not elapsed seconds, dynamics or a fatigue cycle model.
The solver samples converged increments; a progress knot is not guaranteed to be
an output frame. Check actual motion, contact passage and increment sensitivity.
During a pause the projected motion force is zero; reaction vectors still report
holding forces. At a knot the signed projection uses the incoming segment.
Multiple steps, rotations, friction, rigid-body joints, contact activation changes
and self-contact remain unsupported.

## Plan a contact study

Before solving, name the design decision, relevant quantities and acceptable
uncertainty. Separate passage, strain, recovery and operating-force targets;
they need not require the same precision. Use the cheapest analytical force
screen first when applicable, including consequential guide/fit extremes.

For a new operation, first obtain and inspect one complete representative path:
actual motion, contact passage, reaction history, strain location, penetration
and return. Check travel-increment resolution before spending on mesh/penalty
studies when narrow contact events or force peaks could be under-resolved.
Then compare mesh and contact settings at adequate travel resolution, varying
one factor where practical. Revisit coupled sensitivities if a change alters the
contact sequence; no study order guarantees convergence. Do not treat all runs
sharing a coarse increment as independent evidence of a resolved force peak.

For fixed-mesh controls, use `case.run(new_directory, mesh_from=existing_run)`.
This performs a new solve on the saved nodes/elements; it does not reuse old
predictions. Source input/case hashes must match their result provenance, and
ordered part names, fixture BREP hashes and mesh-size settings must match the
new case. Geometry or mesh changes are rejected; material, constraints, contact
and increments are compiled afresh. The original mesh input/case are copied
into the new run and retained by the evidence helper. This avoids assuming
that remeshing with the same requested size creates an identical mesh: the
lift-box study exposed different node positions with unchanged geometry,
settings, mesher version and adapter. Compare mesh-refinement runs separately.

Choose relative or absolute change criteria against the decision before repeated
refinement. A small absolute force change may leave the same first-print decision
while failing a percentage criterion; record the failure and conditional force
range, rather than renaming it convergence. Stop when additional precision cannot
change the next action, keeping unresolved numerical limits separate from
material/friction uncertainty. Existing `studies.compare_results` reads completed
results without rerunning a solver. Local-fixture completion does not establish
whole-assembly compliance or collision clearance.

## Result contract

`completed` means the solver finished the entire normalized load interval,
required nodal/integration-point fields exist and force imbalance at every saved
increment is below 1% (normalized by the larger of applied force, summed reaction magnitudes
and 1 N). It does **not** mean the design is adequate. `status`, `errors` and
`warnings` distinguish failures, timeouts and completed solves with notices.
`require_completed()` raises on incomplete analyses. Partial solves never return
successful metrics. Peak forces are reaction-vector magnitudes per constraint
region, including only its prescribed DOFs; history retains signed components
and per-frame force imbalance.
Overlapping constraint regions may report the same reaction in both regions;
force balance deduplicates constrained node/DOF pairs.

The parser accepts CalculiX's fixed-width numbers with omitted `E` markers in
three-digit exponents, preserving tiny elastic-return fields. If extraction
fails after a completed solve, the private worker's `--postprocess-only` recovery
can reuse its saved mesh and fields in the configured native environment. It
requires a byte-identical regenerated input, checks the saved solver completion
log and reruns field/quality checks; it neither remeshes nor launches a solver.
Recovery records its provenance and leaves the original input/log intact.
Keep the original artifacts; this is not an importer for arbitrary solver decks.

Strain is the maximum absolute principal mechanical strain at integration
points across saved increments, with the part, element and integration point.
It is neither engineering shear strain nor a promise of elastic recovery.
The named material strain limit is an explicit screening assumption. Sharp
fixed edges can create mesh-sensitive singularities. Inspect/converge the
quantity relevant to the design rather than treating a peak as a universal
failure criterion. Displacement includes prescribed rigid travel.

`observe(part, region, name='tooth')` adds signed displacement minima, maxima
and means for a feature. History includes these observations and the signed
reaction projected along each prescribed translation and its current progress
direction. `peak_motion_force_N`
is the corresponding actuation-force magnitude; it excludes orthogonal holding
reactions. `check_strain_limits()` returns per-part conditional screening results.
At a stationary plateau in a progress curve, the motion-direction force is zero
because there is no current travel. A press-and-hold release still needs holding
effort: read the relevant axis of its recorded `reactions_N` across that plateau,
not only `peak_motion_force_N`. All reaction components remain available.

Choose driver contact faces for the intended load transfer. For a normal press
actuator, including its side faces can add unintended vertical restraint;
an engineering block is not a model of skin or grip. Conversely, include real
cap edges that cross the snap during motion. Keep these fixture choices and
their omitted physical behavior with the object.

Contact penetration above the explicit `penetration_limit_mm` (default 0.05 mm)
rejects the result with `status='quality_failed'`, retaining diagnostic metrics.
Choose a tighter limit when fit requires it. Unknown solver parameters fail
instead of being accepted as warnings. Other warning messages include context.

Each new run directory owns `case.json`, geometry BREP snapshots, solver input,
raw `.dat` results, logs, increment status and `result.json`. Existing directories
are never overwritten. Hashes, mesh sizes, tool versions and boundary selections
are retained. Runs have a wall-clock timeout covering meshing and solving; the
worker and solver process group are stopped together. Gmsh's global state is
isolated per run, so independent callers can run concurrently.
Caller interruption also stops that isolated process group, records an
`interrupted` result, and re-raises `KeyboardInterrupt`. Retain it as incomplete
evidence if useful; cancelling a superseded design must not leave its solver
running in the background.

The worker streams full result fields one increment at a time, retaining a
compact history. This bounds full-field memory independently of increment count;
the compatibility `parse_dat` helper still collects frames when called directly.
The lift-off study exposed a silent worker failure after a completed solve with
nearly 1 GB of text fields. A worker failure now reports its exit code even when
its log is empty. Recovery can re-extract the saved solve; it must still satisfy
the input-identity and completion checks above, and does not repair contact quality.

Before meshing, moving pairs of fully prescribed whole-part translations receive
a sampled CAD clearance screen. Their relative progress knots are subdivided
to at most 0.25 mm relative travel per interval. An overlap above 1e-7 mm³ returns
`invalid_rigid_motion` without launching the solver; the case, fixtures and
`rigid_driver_clearance.json` remain available. This catches collisions between
rigid drivers that would otherwise be ignored when contact is defined only to
the flexible part. No sampled overlap is not continuous-path proof. Partial
region constraints, deformable parts and static relative pairs are excluded;
contact/deformation still needs its own analysis. The lift-off box motivates
this check: a press actuator must withdraw before a cap window passes it.

The default PETG material is an explicitly assumed homogeneous solid, **not a
model of two walls and 7% infill**. Use geometry that represents the load-bearing
section, a documented conservative effective material, or an appropriate solid
print. Calibrate against physical tests before claiming real force or strength.

## Locate a contact-quality failure

Before launching another solve, use the saved result, input and raw fields:

```sh
uv run --locked python -m physical_analysis.diagnostics /tmp/box_run model/box/notes/contact_locations.json --rigid-parts lid_catch release_pad
```

`physical_analysis.diagnostics.contact_frames(run, fractions=None,
rigid_parts=())` defaults to the saved frame with greatest reported penetration.
Pass `--fractions .29 .75` or an explicit Python sequence for other saved frames.
The isolated adapter reads the original C3D10 mesh, pairs CDIS/CSTR rows in output
order, groups repeated element/face identifiers without mistaking them for unique
integration points, and returns pressures, gaps and ten deformed quadratic-face
samples. Optional named rigid parts use their saved BREP and actual recorded
uniform translation to report signed sample distances: positive outside,
negative inside. Input/case identity is checked against result provenance;
changed fixture snapshots, missing frames or deforming comparison parts fail.

Native contact gaps and sampled CAD distances answer different questions.
Matched master faces and actual contact quadrature coordinates are not present
in these fields; face samples do not prove absence of intersection. A discrepancy
helps locate a suspect projection, edge transition or mesh approximation. It
does not erase a failed quality screen or prove a solver defect. Keep the report
with the model, including its limits. The helper is read-only and needs raw DAT
fields still present in the original run; compact archives omit those fields.

## Retain analysis evidence

Use `physical_analysis.evidence.retain_run(run, destination)` or:

```sh
uv run --locked python -m physical_analysis.evidence /tmp/box_run model/filament_swatch_box/notes/analysis/new_trial
```

The destination must be new. The helper preserves result history, assumptions,
failure status and provenance; copies the case and increment record; and retains
available input, logs, selected regions and all fixture BREPs as deterministic
gzip files. Artifact links name only files actually copied. Bulky raw fields are
excluded; replay instructions come from the backend. Failed/timeout runs can be
retained without claiming completion. This archives an existing CalculiX run;
it launches no solver, changes no source run, and does not replace original raw
fields needed for postprocess-only recovery. Older object archives remain valid
historical records even when they contain fewer artifacts.

Reused-mesh runs also retain `mesh_source.inp.gz` and `mesh_source_case.json`.
Unpack the mesh-source input as well as the run input before postprocess-only
recovery; source identity is still checked. `mesh_from` expects an existing run
with uncompressed input/case/result files, not a compressed archive directly.

Keep object-specific metrics, acceptance conditions and plots with their model.
Do not copy this file-retention implementation or hand-maintain a second history
table; derive summaries from retained results and link them from the decision
record.

## Evidence and extension

This API is an evolving foundation. Agents may improve it autonomously when a
real modelling task exposes a reusable need, following the repository's
[shared-tool guidance](../AGENTS.md#improve-shared-tools-from-concrete-needs).
Use simpler CAD checks or analytical screens when they adequately answer the
question; neither using nor expanding this API is a goal in itself. Keep
model-specific fixtures with their object, and bring reusable analysis behavior
into this package with an exercised consumer and appropriate numerical evidence.

Acceptance tests cover beam bending/refinement, displacement-controlled flexure,
contact onset and an open gap, contact penalty sensitivity, contact-driven flexure, force balance,
invalid regions, conflicting constraints, ignored solver parameters, excessive penetration,
feature observations, surface-contact compression/open gap, a contact load-and-return
cycle, missing solver, timeout and stale-run
protection. Benchmarks qualify these analysis types, not every nonlinear model.

The implementation follows the [CalculiX 2.21 manual](https://www.dhondt.de/ccx_2.21.pdf)
and [Gmsh API documentation](https://gmsh.info/doc/texinfo/). Tetrahedral midside
node ordering is explicitly converted to C3D10 ordering. Loads integrate
quadratic surface shape functions. CalculiX 2.21 contact `.dat` output uses
negative normal CDIS for overlap in the compression benchmark; penetration is
reported as `max(0, -CDIS_normal)` and tested against pressure/penalty.

Add a backend by implementing `run(case, directory) -> AnalysisResult`. Reject
unsupported case features explicitly. Add a numerical benchmark before exposing
a new analysis type; keep solver keywords out of object scripts. Future joint
networks and material laws should extend the case contract only when a concrete
model needs them. The [swatch box](../model/filament_swatch_box/README.md) exercises a rounded
contact-driven pass-over and reopening with mesh/contact/increment sensitivity;
its numerical result is conditional on frictionless elastic solids and a locally
clamped root. Sharp-tooth pass-over remains unqualified: the phone-stand
experiment did not converge, and its failed result is retained with that model.
The current process isolation targets POSIX hosts.

`physical_analysis.screening.rectangular_cantilever` provides a cheap beam and
buckling rejection screen before meshing. `physical_analysis.studies.compare_results`
compares named metrics from already completed runs without launching new solves.
Convergence of force does not imply convergence of a local strain concentration.

For a mechanical assumption that depends on actual sliced solidity or support
placement, `physical_analysis.manufacturing.orca_linear_paths(path)` yields
linear deposited segments with Orca's width/role metadata. The sliding box and
lift-off box use this narrow reader for local feature reviews. It requires
absolute XYZ, relative E and linear layer moves; incompatible modes fail.
Keep geometry registration, section choices, support access and decisions with
the object. This does not replace Orca's layout acceptance, predict polymer
properties or justify routine G-code inspection of ordinary walls.

For the lift-off and upright boxes' repeated local fill question,
`section_coverage(paths, x_mm=..., z_mm=..., span_mm=(y0,y1))` clips and unions
the recorded-width extrusion strokes on one Y section, excluding support and
brim roles. It returns filled/uncovered widths, internal gaps and intervals.
The planar capsule approximation includes parallel segments and finite rounded
ends; it does not measure deposited polymer. Select consequential sections and
interpret them in the object, without inferring modulus, isotropy or bonding.

`physical_analysis.screening.circular_cam_detent` screens two rigid circular
profiles against a linear transverse spring, returning pass-over travel and peak
frictionless sliding force from an explicitly supplied stiffness. The swatch box
uses it to interpret increment-sensitive numerical reaction forces. It omits
head rotation, spring-axis shortening, guide compliance and friction; stiffness
and printed material properties require separate assumptions/evidence. An
independent sampled-angle projection qualifies the analytical maximum. It does
not replace nonlinear contact analysis when those interactions matter.
