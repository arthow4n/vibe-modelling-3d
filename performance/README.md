# Execution performance evidence

[Execution commands and contracts](../execution/README.md) describe the working
system; [implementation history](IMPLEMENTATION.md) records decisions and commits.
Benchmark summaries are versioned JSON in `benchmarks/`; unrestricted runtime
evidence stays in ignored `.execution/`.
Benchmark computations, native compatibility probes and tool discovery use no
automatic runtime ceilings. Follow the
[repository deadline rule](../AGENTS.md#shared-engineering-execution).

For requested agent-session and execution investigations, use the
[local workflow analyzer](WORKFLOW.md). Raw sessions, normalized histories and
combined timelines stay local; concise privacy-reviewed findings may be preserved
in flat `reviews/` using the publication contract.

## Reproduction

Run from the repository root after locked environment synchronization:

```sh
.venv/bin/python performance/benchmark.py --final --label final --output performance/benchmarks/final.json
.venv/bin/python performance/policies.py --output /tmp/policies.json
.venv/bin/python performance/kernels.py --output /tmp/kernels.json
.venv/bin/python performance/motion_benchmark.py --output /tmp/motion.json
```

The workflow harness measures the complete subprocess interval, using three runs
per workload. Each final workload has its own empty controlled cache and private
coordinator: first execution is cold initialization; subsequent median is warm.
The OS page cache is not flushed. Original revision `f984a0b` supplies baseline
commands and default four-view behavior. Fixture/tool/core dependency versions
must match before interpreting differences. Do not run heavy tests simultaneously.

To reproduce the original baseline, create a checkout of `f984a0b`, copy the
current `performance/benchmark.py` and `performance/fixtures/` there, synchronize
its original locked environment, and run the harness without `--final`. Optional
solvers and Orca must be available in both environments. Each successful physical
benchmark still performs a fresh native solve; warm runs can reuse verified meshes.

## Final command latency

Final production/harness revision: `e8777d5`; original source revision: `f984a0b`.
Both use CPython 3.12.14, CadQuery 2.7.0, OCP 7.8.1.1.post1, NumPy 2.5.3,
Gmsh 4.15.2 and VTK 9.3.1. The host is WSL2/Linux with 16 logical CPUs and
approximately 8 GiB RAM. Default shared CPU capacity is 8; per-command default
is 4. The policy run admitted 2873 MiB of shared memory. Orca 2.4.2, CalculiX
2.21 and FEBio 4.13.0 were exercised; native IPC was unavailable.

Seconds below include interpreter/CLI, scheduling and result delivery. First-run
values are single observations; warm values are medians of two subsequent runs.
They describe these fixtures, not universal speedups.

| Workflow | Original first | Original warm | Final first | Final warm |
| --- | ---: | ---: | ---: | ---: |
| Small NumPy script, isolated | 0.503 | 0.149 | 0.646 | 0.510 |
| Ordinary CAD script, preinitialized final mode | 4.438 | 2.180 | 2.328 | 0.360 |
| Evaluator, geometry only | 2.291 | 2.231 | 2.435 | 0.480 |
| Default evaluation (original four views; final no views) | 2.982 | 2.866 | 2.482 | 0.462 |
| Two explicit views plus STEP/STL | 2.844 | 2.818 | 2.929 | 0.484 |
| Exports plus slice/support review | 3.278 | 3.261 | 3.674 | 0.553 |
| Four explicit views, exports and slice/support review | 3.822 | 3.907 | 4.127 | 0.530 |
| Fresh CalculiX beam solve | 8.652 | 8.632 | 7.446 | 7.221 |

Declared unchanged geometry gives 0.333 s warm command latency. Import-preinitialized
NumPy alone gives 0.354 s warm latency; this small script does not benefit over
the original bare command. Every beam result is **0.3277944687855075 mm**, including
the fresh baseline and final solves. No numerical tolerance or quality threshold
was relaxed. Warm CAD exports/views/slices reuse identified prior artifacts/evidence;
geometry construction still runs unless the complete-input declaration permits reuse.

Final CAD worker sampled peak RSS is approximately 246–266 MiB; isolated NumPy
workers are approximately 40–43 MiB. These are sampled process RSS, include shared
pages and are not total-system peak memory. Source, lock, fixture, package and
resource provenance is retained in [baseline](benchmarks/baseline_verified.json)
and [final](benchmarks/final.json) summaries. Initial baseline and rejected startup
candidate remain bounded historical evidence alongside them.

## Resource and observability policies

[Policy measurements](benchmarks/policies.json) use ordinary files and the shared
scheduler, with three repetitions for computational experiments and five for tracing.

| Experiment | Comparison | Median seconds |
| --- | --- | ---: |
| Trivial script | Detailed tracing disabled / enabled (summaries in both) | 0.288 / 0.422 |
| Three 2400×2400 matrix products | 1 / 2 / 4 / 8 allocated cores | 4.172 / 2.417 / 1.777 / 1.535 |
| Two independent matrix scripts, 4 cores each | Sequential / concurrently admitted | 3.344 / 2.291 |
| Fresh primary/support slices | 1 core sequential / 4 cores with concurrent lanes | 1.954 / 0.823 |
| Fresh CAD/render/slice pipeline | 2048 MiB CAD budget / measured 512 MiB fixture budget | 1.918 / 1.365 |

Four cores give most of this numerical fixture's benefit; eight cores improve
single-job latency modestly while reducing room for concurrent agents. Keep the
portable 50% default and allow explicit workload budgets. These historical
measurements used a 2048 MiB CAD default. Subsequent smaller-budget trials and
unreserved admission comparisons are retained in the
[archive reflection and memory-policy review](reviews/2026-10-04-152419-archive-reflection-and-memory-policy.md).
Those RAM controls and their fixtures have since been removed; current admission
uses CPU threads and job slots only. The timings describe the historical policy.
[The retained Perfetto timeline](traces/pipeline.perfetto.json) contains **0.524 s**
of actual render/primary-slice overlap. [The cold complete OTLP snapshot](traces/complete.otlp.jsonl)
preserves hierarchical command, worker and native stages across processes.

Detailed tracing costs about 0.134 s on a trivial script, largely SDK/import
startup. This is a material relative overhead for tiny isolated work and a small
absolute cost for engineering operations; it is not hidden as a speedup.
`ENGINEERING_TRACE=0` retains compact records while disabling detailed spans.
Cold native initialization and large exact CAD/solver computations remain
bottlenecks; result reuse cannot help changed inputs. Conservative repository-wide
Python identity also invalidates declared geometry after unrelated source edits.

## Qualified kernels and rejected approaches

The original quadratic-surface traction quadrature is batched, not approximated:
2000-face median 0.324 s to 0.0166 s. Prepared Tet4 reference inverses reduce
1000-frame strain extraction from 0.102 s to 0.0617 s. Conservative motion bounds
skip strictly separated booleans; exact distances and possible intersections
remain exact. G-code input streams instead of loading the entire file.

Existing VTK mapping outperformed the investigated SciPy spatial index (0.0184 s
versus 0.0229 s), so no competing index or SciPy dependency remains. Global
dependency-bytecode bypass increased startup costs; fresh editable-source loaders
retain locked dependency bytecode instead. Gmsh remains isolated despite passing
a narrow forkserver experiment. No measured kernel justifies Numba, Cython, Rust
or another worker framework.

## Verification scope

Final frozen-source regression: **145 passed, 3 skipped in 237.30 s**. Qualification
runs on Linux/WSL2 with CPython 3.12, CadQuery/Open Cascade, Gmsh,
OrcaSlicer, CalculiX and FEBio. Optional native IPC/PolyFEM execution is unavailable;
its orchestration, field extraction, quality and recovery guards are tested with
retained fixtures and automated coverage. Linux affinity/parent-death behavior
has not been qualified on other operating systems. This is process isolation,
not a security sandbox.
Additional isolated and preinitialized SIGSEGV smoke runs both returned 139 and
subsequent execution recovered successfully; [verification evidence](benchmarks/verification.json)
records these outcomes. Locked environment checks required no changes, and the
focused execution skill passed its schema validator.

History analysis requires no rerun:

```sh
.venv/bin/python -m execution.history --last 200 --stats
.venv/bin/python -m execution.history --compare RUN_A RUN_B
.venv/bin/python -m execution.history --run RUN_ID --perfetto /tmp/timeline.json
.venv/bin/python -m execution.history --incomplete
```

Inspect history during dedicated performance/recovery work, not routinely during
model iterations. Raw records retain 500 runs/14 days, with per-file/sample/cache
bounds documented in the execution reference. No tool creates Git commits.


The [archive token-rate and request-timing supplement](reviews/2026-10-04-165521-archive-token-speed-and-request-timing.md)
adds the retained sample's median 20.78 output tokens/second (including reasoning)
and separates client-observed response time from unavailable backend inference
time. It reuses the prior snapshot rather than benchmarking current service speed.

## Historical memory-policy studies

Performance reviews retain measurements of the former RAM admission policy.
Shared execution now admits by CPU threads and job slots only. RAM reservation,
per-job limits, pressure watchdogs and their benchmark fixtures have been removed.
RSS remains a passive measurement for requested investigations. The
[removal review](reviews/2026-10-04-163751-shared-memory-controls-removed.md) records the decision and qualification.
