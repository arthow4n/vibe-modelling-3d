# Shared engineering execution

The filesystem is the script interface. `execute.py SCRIPT [ARGS...]` preserves
script stdout/stderr and exit codes. `evaluate_model.py` remains the CAD interface.
Both use the same execution, scheduling and trace facilities. No HTTP service,
cloud collector, serialized user functions or arbitrary-script output cache.

## Architecture contract (version 1)

Requests are bounded JSON messages over a private local Unix socket, with a
unique run ID, strategy, absolute source/cwd, argument list, input identity,
resource budget, deadline and trace context. Output streams travel separately
from concise result metadata. The coordinator starts on demand, admits independent
jobs against CPU/memory budgets, observes clients and workers, and idles out.
Native work runs in owned process groups. Disconnect, deadline and cancellation
terminate owned descendants; ambiguous dispatch is never retried automatically.
The fallback starts a conventional isolated process using the same lifecycle.

Three strategies share this interface: isolated (ordinary scripts), preinitialized
(fresh child of a compatibility-tested preload host), persistent (repository CAD
operations retaining immutable geometry under an explicit closed-input contract).
No arbitrary script executes repeatedly in a shared mutable interpreter.
Source/dependency/environment changes invalidate compatible infrastructure.
Worker recycling bounds jobs, lifetime and resident memory.

Geometry reuse is opt-in because existing trusted model scripts may read arbitrary
files, clocks or environment and write side effects. `--reuse` declares deterministic
construction and complete inputs; extra non-Python inputs use `--dependency`.
All repository Python sources, adjacent Python modules, declared inputs, lockfile,
worker implementation and process environment are content-identified. Unknown
inputs require fresh execution. Validation results carry their originating identity;
reused stages are explicitly marked, never represented as fresh computation.
Managed outputs are staged, identity-checked and atomically published with destination
ownership. Model-written side effects are outside that transaction.

Resource leases cover external tasks and script budgets; nested operations inherit
and divide their parent's budget rather than creating uncontrolled parallelism.
Solver-specific thread/evidence settings remain explicit. Independent tasks may
use the common scheduler; dependent study levels retain their stopping rules.

## Performance evidence

Automatic lightweight records live under ignored `.execution/`: compact run
summaries, OTLP JSONL traces, resource samples and optional profiles. Version 1
uses the OpenTelemetry SDK and protobuf OTLP trace encoder, serialized as standard
JSON messages, one ExportTraceServiceRequest per line. Trace context propagates
through the shared process environment. No environment values or script output
are stored in traces; arguments are fingerprinted. Per-run files avoid concurrent
append corruption. Retention is bounded by age and count. Committed
`performance/benchmarks/` contains reproducible bounded benchmark history, not
unrestricted raw diagnostics. Tracing is best effort and cannot fail a calculation.

Full command reference, measured policies and limitations are finalized as the
implementation is qualified. `performance/IMPLEMENTATION.md` records milestones.

## Running scripts

```sh
./execute.py model/object/experiment.py argument
./execute.py --cwd model/object --timeout 120 model/object/experiment.py
./execute.py --strategy preinitialized --preload cad model/object/check.py
./execute.py --profile cpu model/object/experiment.py
./execute.py --profile allocations model/object/experiment.py
./execute.py --isolated model/object/experiment.py
```

Options precede the script; following tokens are its arguments. Isolated execution
is default. Preinitialized execution is opt-in: import timing/state of the common
scientific/CadQuery dependency set differs from a pristine interpreter. Every
user script still gets a fresh child. Both preload labels use the same qualified
import-only host (scientific dependencies are included by CadQuery). Gmsh and
solvers are never initialized in that host. The host is imported with one native
thread; jobs apply their explicit `--threads` budget. Ordinary jobs default to
one thread and 2048 MiB of process-tree RSS. Use larger explicit budgets when
needed; oversize requests fail before execution. This is process isolation,
not a sandbox.

`--isolated` bypasses the coordinator for compatibility diagnosis, using the same
traced lifecycle. Coordinator startup failure also falls back *before dispatch*;
an ambiguous dispatched job is never automatically replayed. Exit codes preserve
script behavior; timeout is 124, interruption is 130, signals map to 128+signal.
File descriptors carry actual input/output streams; output isn't stored in traces.
Profiling artifacts remain local. Environment values and arguments aren't logged.

`ENGINEERING_CPUS`, `ENGINEERING_MEMORY_MB`, `ENGINEERING_JOBS` configure the
coordinator capacity. `ENGINEERING_TRACE=0` disables detailed spans for overhead
measurement; compact run summaries remain. `ENGINEERING_DATA` selects local
performance storage. No normal engineering task needs to inspect these records.

## CAD iterations and incremental outputs

```sh
./evaluate_model.py model/object/object.py
./evaluate_model.py model/object/object.py --views isometric,front
./evaluate_model.py model/object/object.py --export --slice
./evaluate_model.py model/object/object.py --reuse --dependency model/object/input.json
```

No views, exports or slices are produced by default. Ordinary evaluations use a
fresh child of the import-only CAD host; user modules and globals aren't shared.
`--isolated` selects the conventional process. Explicit views, errors, native
reports and exit codes remain compatible. Each report separates dependency load,
construction, selection, validation, export format and individual view durations.

`--reuse` declares that geometry construction is deterministic, has no required
side effects, and depends only on repository/adjacent Python sources and declared
inputs. Declare *every* external/non-Python input with repeated `--dependency`.
Do not use it for unknown inputs, clocks, random state or required model-written
side effects. Two bounded idle workers can retain geometry; they recycle after
100 jobs, 60 seconds idle or input/environment changes. Unchanged geometry and
validated artifacts carry explicit reuse flags and content identities. Outputs
are staged and published atomically only after current-input checks under
exclusive destination ownership; an old revision cannot replace newer exports.
Cached artifact bytes are digest-verified, so tampered outputs are restored from
valid artifacts, never claimed as verified in place. Cache size/count is bounded.

## Concurrent agents, scheduling and recovery

The default shared CPU capacity is **50%** of affinity/cgroup available cores.
`ENGINEERING_CPUS=75%` or `ENGINEERING_CPUS=8` changes it; `--threads 50%` (the
command default) allocates half that shared capacity. Integer thread counts are
also accepted. Admission gives simultaneous jobs disjoint CPU sets on Linux.
OCCT and BLAS receive the thread count; external native processes inherit CPU
binding through `taskset`, so libraries ignoring OMP limits still stay within
allocated cores. Process-tree memory budgets and a default maximum four jobs
bound admission. Import-only preload remains single threaded for safe forking.

Independent scripts can use `execution.batch.ScriptTask` and `execution.batch.run`:

```python
from execution.batch import ScriptTask, run
answers = run([
    ScriptTask('mesh_a', 'model/object/check_a.py'),
    ScriptTask('mesh_b', 'model/object/check_b.py'),
    ScriptTask('compare', 'model/object/compare.py', depends_on=('mesh_a', 'mesh_b')),
])
```

Scripts stay ordinary files. Dependencies wait for successful upstream work;
failed prerequisites produce `dependency_failed`. Declare output paths when
jobs share destinations. Nested batches divide their parent's admitted CPU set
and launch isolated children inside that lease; they do not recursively acquire
capacity or deadlock. Conditional numerical refinements retain QuestionStudy's
existing sequential acceptance/stopping rules.

Concurrent coding agents use the same private coordinator without administration.
Managed CAD destinations have cross-process ownership locks and staged publication;
identical declared geometry/artifact jobs serialize around the identity and reuse
completed work. Arbitrary scripts keep responsibility for their own side effects.

A watchdog stops orphan process groups and observed detached descendants after
abrupt coordinator death. The next command starts a replacement. Digest-verified
artifact caches survive; in-memory geometry is reconstructed. Durable `jobs/`
metadata records queued/running/terminal states without argument or environment
values. `python -m execution.history --incomplete` lists recoverable work. A queued
or running record whose owner died is evidence of interruption, not completion.
`execute.py --restart RUN_ID SCRIPT [ARGS...]` explicitly restarts matching
script inputs; it does not pretend to resume a partially executed Python function.
Never automatically replay unknown side effects. Physical-analysis saved-field
recovery and identity-checked mesh/evidence reuse remain the checkpoint APIs;
an incomplete native solve cannot become successful evidence through recovery.

Slicing uses immutable input/profile snapshots. Binary/deployment/configuration
identities cache version discovery and opt-in completed reviews. Primary slices
already using the required auto-support policy serve as their own probe. Explicit
independent probe settings can run alongside the primary, with separate logs and
verified effective settings; failures preserve the primary evidence and request
review. For explicit renders plus slicing, slicing starts at STL completion while
CAD rendering continues. Traces show the actual overlap rather than summed work.
