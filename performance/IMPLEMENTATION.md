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
- CPU/job admission and native thread budgets share the coordinator. Large
  native objects stay in their owner; independent external work may overlap.
- Process-group/descendant cleanup, no automatic replay after uncertain dispatch,
  atomic managed outputs and source identity guards protect result ownership.

## Ordered progress

1. Inspection: evaluator, slicing, all three physical backends, question studies,
   mesh reuse/recovery, motion, manufacturing and field extraction reviewed.
   Existing IPC thread benchmarks retained. Host is WSL2, 16 logical CPUs;
   Gmsh requires the documented local runtime library path.
2. Architecture: above contracts chosen; detailed interface follows in execution/README.md.
3. Baselines: retained cold/warm subprocess measurements from `f984a0b`; optional
   native tools checked rather than assumed.
4–6. Tracing, coordinator and qualified initialization: implemented and pushed.
7–9. CAD, verified incremental artifacts and resource-aware slicing: implemented
   and pushed; explicit render/export/slice contracts preserved.
10–11. Physical backends and measured computational kernels: implemented and
   pushed; native completion and quality requirements unchanged.
12–13. Agent interface, instructions and focused execution skill: implemented
   and pushed, with reliability refinements in final verification.
14. Frozen-source integration and regression verification: **145 passed, 3 skipped**
   in 237.30 s, including native CalculiX/FEBio and coordinator/native death tests.
15. Final cold/warm, observability and scheduling benchmarks: complete, retained
   with matching baseline/final fixtures and core dependency versions. See README.md.

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

### Physical-analysis integration milestone

Scheduling commit `7e6b8ce` pushed. CalculiX, FEBio and IPC now share resource
leases, trace context, native subprocess ownership and cancellation while
preserving separate isolated workers, mesh reuse, saved-field recovery and
backend quality/completion checks. Removed an unused CadQuery import from the
CalculiX extraction worker; dependency versions come from installed metadata.
Default IPC CPU selection follows portable shared capacity; explicit settings remain.

A WSL wall-clock correction exposed unsafe PID birth checks based on wall time.
Linux watchdog identity now uses `/proc/PID/stat` boot ticks. Ten repeated flexure
solves and a repeat native regression passed; 41 tests passed across execution,
CalculiX, FEBio and numerical kernels. Failed earlier concurrent runs are retained
as diagnosis, not accepted engineering evidence. Result resource provenance is
preserved when merging successful native answers.

### Measured computational kernels

Physical integration commit `641dc2a` pushed. Batched quadratic-surface traction
uses the original three-point quadrature, signed shape weights and normalization,
with bounded 4096-face chunks. Curved/shared-node regression agrees within 1e-12.
Median 2000-face integration fell from 0.324 s to 0.0166 s (19.5×).
Reusable Tet4 reference inverses reduce 1000-frame extraction from 0.102 s to
0.0617 s; strain definition and inversion rejection are unchanged. G-code reading
now streams. Bounding boxes skip only strictly separated motion booleans;
exact minimum distances and all possible intersections remain native checks.
Separated 81-pose screen: ~0.82 s baseline versus ~0.69 s final.

Rejected: SciPy cKDTree mapping measured 0.0229 s against existing VTK 0.0184 s,
so the established VTK path stays and SciPy was removed. No custom compiled/JIT
kernel is justified by these measured workloads. Focused execution/evaluator,
slicing, kernels, motion and manufacturing validation: 59 passed.

### Automatic reuse and workflow consolidation

Kernel commit `487da7b` pushed. Artifact reuse now derives from validated actual
BREP bytes, including state-sensitive model output, rather than requiring an
agent decision. Construction side effects still execute. A versioned per-model
closed-input declaration enables geometry reuse on ordinary calls; `--fresh`
overrides all controlled reuse. Slices reuse complete identity-verified evidence
by default. CPU partitions also split actual affinity for concurrent native slices.

Added CAD memory configuration, quiet locked-environment bootstrap, installed
metadata/runtime invalidation, pruned complete repository Python identities,
pre-dispatch native qualification with clean-spawn fallback, bounded traces/raw
records and grouped history/Perfetto analysis. Updated AGENTS.md, CadQuery/Orca
skills and physical documentation; added the validated engineering-execution skill.
Full repository test directory, frozen production source: **129 passed, 3 skipped**
in 220.89 s. Skips are unavailable optional native IPC execution; CalculiX/FEBio,
CAD and Orca orchestration were exercised. `pytest` without a test-directory
restriction imports object-owned modeling experiments, so qualification used
`pytest tests` and did not treat those CAD scripts as tests.

### Reliability and startup qualification

Workflow commit `b20f35f` pushed. Linux subreaper ownership now catches rapid-exit
children even when they detach before resource sampling. Tracing/cache storage
failure preserves calculations; repository output locks stay shared across clients
with different trace destinations. Run summaries merge source/resource provenance
without retaining full CAD reports, diagnostics or output. Coordinator configuration
changes invalidate capacity. Repository test discovery excludes object-owned CAD
experiments. Full regression: **134 passed, 3 optional native IPC skips**.

A final candidate benchmark exposed excessive recompilation caused by globally
bypassing dependency bytecode. Replaced it with fresh loaders only for editable
repository/adjacent source, preserving normal cached bytecode for locked dependencies.
The import-only host also preloads tracing dependencies without starting threads;
compatibility qualification remains mandatory. Full repeated regression again:
**134 passed, 3 skipped**. Candidate benchmark retained to document the rejected
startup policy; final measurements follow after the verified mesh-index integration.

The final ownership audit additionally tests coordinator SIGKILL while native code
holds the GIL, both in script workers and external execs. Linux parent-death signals
must follow the long-lived creating thread: the standard-library forkserver now
starts lazily from the coordinator main thread. Starting it in a short-lived request
thread killed persistent geometry owners; relying only on Python watchdogs left
GIL-blocked work running. Both rejected variants were caught by regression tests.
Focused corrected verification: **53 passed**. Saved reports now recheck source
identity after slicing and use the same destination locks as managed artifacts.

Ownership/import/automatic-mesh milestone `0efef63` and reproducible workflow/policy
harness `1e0bb06` were pushed. Final abandoned-child coverage adds repository/owner
birth tags: a replacement reaps detached arbitrary subprocesses after supervisor
SIGKILL without replaying user code. Focused verification: **54 passed**.

Final ownership change `e8777d5` pushed. Final frozen regression: **145 passed,
3 unavailable native IPC skips** in 237.30 s. Baseline and final fixture/package
identities match; all benchmark exits succeed. Fresh beam displacement matches
exactly. Warm default evaluation: 2.866→0.462 s; explicit complete render/export/
slice workflow: 3.907→0.530 s; physical solve: 8.632→7.221 s. Independent scripts
3.344→2.291 s; one-core sequential versus four-core concurrent slice pair
1.954→0.823 s. Measured small-fixture pipeline overlap is 0.524 s.

Retained limitations: isolated tiny-script latency increases with shared execution
and observability; detailed tracing adds ~0.134 s on the trivial fixture. Cold
native initialization and changed expensive geometry/solves remain bottlenecks.
The default four-core allocation captures most measured numerical speedup and
leaves capacity for other agents; memory defaults stay conservative. Bounded JSON
history and two representative timelines are committed; raw traces remain local.
Additional isolated/preinitialized native SIGSEGV smoke checks returned 139 and
recovered; locked environment and focused skill validation passed. The disposable
original-source baseline checkout was removed after recording its evidence.

## RAM-control removal — 2026-10-04

Shared RAM reservations, per-job limits, capacity controls and memory-based idle
cache reclamation have been removed, including their APIs, CLI options, fixtures
and dedicated tests. Earlier entries describe historical implementations. CPU/job
admission, cancellation, timeout, process ownership and passive RSS records remain.
