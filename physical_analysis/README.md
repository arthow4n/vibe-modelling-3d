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

Contact uses frictionless node-to-face finite sliding with an explicit penalty stiffness.
Check engagement, penetration, force balance, mesh sensitivity and penalty
sensitivity before using its numbers. No geometry is silently adjusted to close
gaps. All loads/motions share one proportional static ramp. Multiple steps,
rotations, friction, rigid-body joints and self-contact are unsupported.

## Result contract

`completed` means the solver finished the entire normalized load interval,
required nodal/integration-point fields exist and the final force imbalance is
below 1%. It does **not** mean the design is adequate. `status`, `errors` and
`warnings` distinguish failures, timeouts and completed solves with notices.
`require_completed()` raises on incomplete analyses. Partial solves never return
successful metrics. Peak forces are reaction-vector magnitudes per constraint
region, including only its prescribed DOFs; history retains signed components.
Overlapping constraint regions may report the same reaction in both regions;
force balance deduplicates constrained node/DOF pairs.

Strain is the maximum absolute principal mechanical strain at integration
points across saved increments, with the part, element and integration point.
It is neither engineering shear strain nor a promise of elastic recovery.
The named material strain limit is an explicit screening assumption. Sharp
fixed edges can create mesh-sensitive singularities. Inspect/converge the
quantity relevant to the design rather than treating a peak as a universal
failure criterion. Displacement includes prescribed rigid travel.

`observe(part, region, name='tooth')` adds signed displacement minima, maxima
and means for a feature. History includes these observations and the signed
reaction projected along each prescribed translation. `peak_motion_force_N`
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

Acceptance tests cover beam bending/refinement, displacement-controlled flexure,
contact onset and an open gap, contact penalty sensitivity, contact-driven flexure, force balance,
invalid regions, conflicting constraints, ignored solver parameters, excessive penetration,
feature observations, missing solver, timeout and stale-run
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
model needs them. Sharp-tooth pass-over remains unqualified: the phone-stand
experiment did not converge, and its failed result is retained with that model.
The current process isolation targets POSIX hosts.

`physical_analysis.screening.rectangular_cantilever` provides a cheap beam and
buckling rejection screen before meshing. `physical_analysis.studies.compare_results`
compares named metrics from already completed runs without launching new solves.
Convergence of force does not imply convergence of a local strain concentration.
