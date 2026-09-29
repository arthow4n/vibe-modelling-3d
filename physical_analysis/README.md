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

Contact uses frictionless finite-sliding penalty contact. The default
`discretization="node_to_surface"` preserves existing cases; the optional
`discretization="surface_to_surface"` integrates over contacting faces and is
qualified for the storage-box rounded snap and the compression benchmark.
The [CalculiX manual](https://www.dhondt.de/ccx_2.22.pdf) cautions against
node-to-face contact with quadratic elements. Surface-to-surface contact enabled
the revised box's pass-over studies after exploratory node-contact timeouts;
geometry also changed, so this is not an isolated formulation comparison.
Both choices require an explicit penalty stiffness.
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

The default PETG material is an explicitly assumed homogeneous solid, **not a
model of two walls and 7% infill**. Use geometry that represents the load-bearing
section, a documented conservative effective material, or an appropriate solid
print. Calibrate against physical tests before claiming real force or strength.

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

`physical_analysis.screening.circular_cam_detent` screens two rigid circular
profiles against a linear transverse spring, returning pass-over travel and peak
frictionless sliding force from an explicitly supplied stiffness. The swatch box
uses it to interpret increment-sensitive numerical reaction forces. It omits
head rotation, spring-axis shortening, guide compliance and friction; stiffness
and printed material properties require separate assumptions/evidence. An
independent sampled-angle projection qualifies the analytical maximum. It does
not replace nonlinear contact analysis when those interactions matter.
