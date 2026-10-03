# Engineering execution implementation

Working branch: `execution-performance`. Baseline revision: `f984a0bda405563e4476c666e392b34fddcd9b14` (full identity
recorded by the benchmark). This record tracks the ordered implementation; native
engineering evidence remains owned by its existing tools.

## Decisions and contracts

- CPython 3.12 and locked uv environment remain authoritative.
- One standard-library local coordinator, one filesystem-oriented command,
  process isolation as the arbitrary-script baseline. No arbitrary result cache.
- OpenTelemetry SDK spans, local versioned OTLP JSONL, bounded ignored raw data,
  committed benchmark summaries. Instrumentation failure cannot fail calculations.
- Reusable initialization is enabled only after native compatibility experiments.
  Stateful CAD reuse requires an explicit closed-input/purity contract; normal
  model execution retains fresh user-module semantics.
- Existing CAD validity, STEP/STL meshing, slice exit 0/1/2, support probe,
  backend identity/recovery/convergence and numerical tolerances are preserved.
- CPU/memory admission and native thread budgets share the coordinator. Large
  native objects stay in their owner; independent external work may overlap.
- Process-group/descendant cleanup, no automatic replay after uncertain dispatch,
  atomic managed outputs and source identity guards protect result ownership.

## Ordered progress

1. Inspection: evaluator, slicing, all three physical backends, question studies,
   mesh reuse/recovery, motion, manufacturing and field extraction reviewed.
   Existing IPC thread benchmarks retained. Host is WSL2, 16 logical CPUs;
   Gmsh requires the documented local runtime library path.
2. Architecture: above contracts chosen; detailed interface follows in execution/README.md.
3. Baselines: in progress; optional native tools checked rather than assumed.
4–15. Pending implementation, regression and final measurements.

Commit identifiers and benchmark findings will be added at subsequent milestones;
Git history is the authoritative commit/push record.

### Baseline and tracing milestone

Baseline commit `d7f8f77`. Corrected benchmark placement to the user's home so
Flatpak sees the actual STL: three complete slices now pass. Baseline medians:
geometry 2.186 s, default four views 2.703 s, explicit two views/exports 2.796 s.
Tracing foundation: SDK + supported OTLP encoder, local JSONL, cross-process
context, hierarchical controlled-operation spans, summaries, retention and
Perfetto conversion. Tracing failure tests and evaluator/slicing regression:
26 passed. Native forkserver compatibility probes are running before lifecycle
selection. No numerical tolerance or evidence policy changed.

### Shared execution milestone

Tracing commit `a2027a1` pushed. Implemented one private Unix-socket coordinator,
automatic locked-environment bootstrap, isolated and fresh preinitialized script
children, real stdio descriptor forwarding, deadlines including queue waits,
resource admission, tree RSS/CPU samples, cProfile/tracemalloc modes, process-group
and detached-descendant cleanup, idle shutdown, runtime-content invalidation and
pre-dispatch fallback. Fresh source imports bypass timestamp-based bytecode.

Compatibility probes: six matching CAD boolean results in each preload mode;
six matching Gmsh meshes (341 nodes). Import-only CadQuery is single threaded
with BLAS/OMP limits. Gmsh remains isolated despite passing this narrow probe.
Focused tests: 18 passed, 3 optional IPC native tests skipped. An earlier full
suite was run while files were being edited and observed an old in-memory module;
its 4 import failures are not regression evidence. Full frozen-source regression
will be rerun at consolidation. No solver quality setting changed.

### CAD/incremental milestone (in verification)

Shared coordinator commit `4204f15` pushed. Integrated CAD through the same
coordinator, fresh import-preloaded children by default, no views by default,
opt-in deterministic geometry owners, digest-verified controlled artifacts,
source/data/environment invalidation, staged revision-guarded publication and
cross-process output locks. Separate construction/selection/validation/export/view
measurements preserve native evidence. Initial warm fresh evaluation ~0.46 s;
unchanged persistent geometry ~0.16 s worker interval plus command overhead.

User steering: use available multithreading with portable percentage/integer
budgets. Shared CPU capacity defaults to 50% of affinity/cgroup availability;
per-job thread allocation defaults to 50% of that capacity. Import-only host stays
single threaded for safe cloning; CAD OCCT/BLAS pools use the job budget.

CAD milestone validation: 33 evaluator/script/slicing regressions passed, followed
by 30 evaluator/script tests including declared-data invalidation, tampered-export
restoration and source-change-during-build prevention. Default builds still run
validity checks; reused validity is identified as prior evidence for the same
closed-input geometry. STEP/STL tessellation settings remain unchanged.

### Scheduling/slicing/resilience milestone

CAD commit `d9b8ab0` pushed. Added portable percent/integer resource budgets,
disjoint CPU sets, borrowed/divided nested budgets, dependency-aware ordinary-script
batches, shared native subprocess lifecycle, runtime alias normalization, durable
job journals and owner-death watchdogs. Slicing snapshots its inputs, caches
content-bound version discovery and optional completed reviews, overlaps explicit
primary/probe work, preserves probe-failure review semantics and starts from STL
completion independently of rendering. Controlled simultaneous artifacts are
serialized by identity; arbitrary scripts are never result-cached or replayed.

Validation: 38 existing/added execution/evaluator/slicing/telemetry checks passed;
21 focused scheduling/slicing/telemetry tests including actual probe overlap and
version invalidation passed. Real Orca 2.4.2 primary/probe completed on the fixture.
Remaining stages: physical integration, measured kernels, dedicated resilience
qualification, instructions, frozen-source regression and final benchmarks.
