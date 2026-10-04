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
jobs against CPU threads/job slots and idles out. RSS sampling is diagnostic.
Native work runs in owned process groups. Disconnect, deadline and cancellation
terminate owned descendants; ambiguous dispatch is never retried automatically.
The fallback starts a conventional isolated process using the same lifecycle.

Three strategies share this interface: isolated (ordinary scripts), preinitialized
(fresh child of a compatibility-tested preload host), persistent (repository CAD
operations retaining immutable geometry under an explicit closed-input contract).
No arbitrary script executes repeatedly in a shared mutable interpreter.
Source/dependency/environment changes invalidate compatible infrastructure.
Worker recycling bounds idle-worker count, jobs and lifetime. The coordinator idle
timeout starts after the last request completes and does not expire while handlers
are queued. A long active job does not consume the subsequent idle allowance.

Geometry reuse requires a closed-input declaration because trusted model scripts may read arbitrary
files, clocks or environment and write side effects. `--reuse` declares deterministic
construction and complete inputs; extra non-Python inputs use `--dependency`.
All repository Python sources (excluding virtual environments/generated caches), adjacent Python modules, declared inputs, lockfile,
worker implementation and process environment are content-identified. Unknown
inputs require fresh execution. Validation results carry their originating identity;
reused stages are explicitly marked, never represented as fresh computation.
Managed outputs are staged, identity-checked and atomically published with destination
ownership. Model-written side effects are outside that transaction.

The same contract applies to deterministic inspection entry points with reference
contents, not only printable outputs. Declare their complete inputs too when
they have no required side effects; choosing a different render destination
does not require constructing the same inspection geometry again.

Finish repository Python edits before launching any CAD batch, including
inspection or benchmark qualification. Even a benchmark docstring changes the
current conservative identity. The current
input identity conservatively includes all repository Python, so even editing an
unrelated check while CAD is queued or running can invalidate publication. Work
on non-Python documentation or review completed evidence during that batch instead. If the
guard rejects a job, freeze Python edits and rerun that affected request; retained
content-verified exports/renders can still be reused. The J4/K4 grip revision hit
this guard when its check script was edited during final evaluation; freezing
edits recovered the affected outputs without changing the geometry.

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

See [performance evidence](../performance/README.md) for measured policies and
limitations; `performance/IMPLEMENTATION.md` records implementation milestones.

## Running scripts

```sh
./execute.py model/object/experiment.py argument
./execute.py --cwd model/object model/object/experiment.py
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
50% of shared CPU capacity. CPU requests exceeding capacity fail before execution.
Admission uses CPU threads and job slots. RSS is sampled for performance records;
it does not reserve capacity or stop jobs. There are no shared RAM budgets,
memory-limit options or memory-pressure watchdogs. Process isolation is not a sandbox.

Ordinary scripts, CAD evaluation, slicing, native analyses, diagnostics and
recovery run **without automatic computation deadlines**. Do not invent a cap
from expected duration or add one as a precaution; follow the
[repository deadline rule](../AGENTS.md#shared-engineering-execution).
Optional timeout arguments implement explicit user-requested deadlines.
Native compatibility probes, tool discovery and benchmark computation also have
no agent-selected runtime ceilings.

At the user's request, coordinator connections allow **60 seconds per handshake**,
replacement allows **30 seconds** for the old socket to disappear, and new
coordinator startup allows **120 seconds** of retries. These are generous service
connection allowances, not measured computation limits. After dispatch, the
connection waits without a timeout. Idle retirement and post-termination cleanup
waits retain their separate lifecycle roles.

`--isolated` bypasses the coordinator for compatibility diagnosis, using the same
traced lifecycle. Coordinator startup failure also falls back *before dispatch*;
an ambiguous dispatched job is never automatically replayed. Exit codes preserve
script behavior; timeout is 124, interruption is 130, signals map to 128+signal.
File descriptors carry actual input/output streams; output isn't stored in traces.
Profiling artifacts remain local. Environment values and arguments aren't logged.

`ENGINEERING_CPUS` and `ENGINEERING_JOBS` configure coordinator CPU capacity and
job-count limit. `ENGINEERING_TRACE=0` disables detailed spans for overhead
measurement; compact run summaries remain. `ENGINEERING_DATA` selects local
performance storage. No normal engineering task needs to inspect these records.

When investigating queue waits, inspect CPU/job blocking and initialization.
Historical memory-policy measurements remain in the performance reviews;
RAM reservation and limit controls have been removed.
For sequential scripts on the current single-thread CalculiX/Gmsh route, use
`--threads 1`; requesting four threads reserves four cores even while that
native worker uses one. Parallel batches and other backends need their own
budgets. If the user explicitly requests a deadline, an outer command limit
includes admission wait and all sequential study levels; an optional native
limit applies to one isolated worker. Neither is enabled by default.

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

Validated actual BREP content (excluding export triangulations), implementation,
runtime and export/render settings identify controlled artifacts automatically,
even when construction must run freshly. Dynamic model inputs therefore change
artifact identities; required model side effects still execute. Complete slice
reviews also reuse automatically by input/profile bytes, placement and tool identity.
`--fresh` forces new construction, exports, renders and slices; retained diagnostics
with `--slice-keep-run` always perform a new slice.

For deterministic models, declare complete inputs once beside the source:

```json
{"schema_version":1,"deterministic":true,"inputs":["settings.json"]}
```

Name it `object.execution.json` for `object.py`. Paths are relative to the source;
files/directories and the declaration itself enter the content identity. Subsequent
ordinary evaluator calls automatically use compatible geometry. Undeclared inputs,
randomness, clocks and required construction side effects cannot use this contract.

`--reuse` also declares that geometry construction is deterministic, has no required
side effects, and depends only on repository/adjacent Python sources and declared
inputs. Declare *every* external/non-Python input with repeated `--dependency`.
Do not use it for unknown inputs, clocks, random state or required model-written
side effects. Two bounded idle workers can retain geometry; they recycle after
100 jobs, 60 seconds idle or input/environment changes. Unchanged geometry and
validated artifacts carry explicit reuse flags and content identities. Outputs
are staged and published atomically only after current-input checks under
exclusive destination ownership; an old revision cannot replace newer exports.
Saved reports also acquire destination ownership and recheck source identity
after slicing, preserving a newer report when source changes during review.
Cached artifact bytes are digest-verified, so tampered outputs are restored from
valid artifacts, never claimed as verified in place. Cache size/count is bounded.

## Concurrent agents, scheduling and recovery

Tests or investigations that change coordinator configuration, including
`ENGINEERING_DATA`, must use a unique `ENGINEERING_INSTANCE` before connecting.
Otherwise compatibility checking can replace the default coordinator and
interrupt unrelated active jobs. The physical-analysis mesh-cache test uses this
existing namespace mechanism; its cache assertions still run through real native
solves. A separate instance has its own admission accounting, so keep such
qualification workloads small rather than treating it as extra shared capacity.

The default shared CPU capacity is **50%** of affinity/cgroup available cores.
`ENGINEERING_CPUS=75%` or `ENGINEERING_CPUS=8` changes it; `--threads 50%` (the
command default) allocates half that shared capacity. Integer thread counts are
also accepted. Admission gives simultaneous jobs disjoint CPU sets on Linux.
OCCT and BLAS receive the thread count; external native processes inherit CPU
binding through `taskset`, so libraries ignoring OMP limits still stay within
allocated cores. CPU threads and a default maximum four jobs bound admission;
actual memory use is recorded diagnostically. Import-only preload remains single
threaded for safe forking.

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
abrupt coordinator death. On Linux, kernel parent-death signals additionally stop
native jobs that hold the Python GIL; the preload host is created by the long-lived
coordinator main thread. Owned external tools use an exec shim with the same
parent-birth guard. The next command starts a replacement, which also reaps
repository-tagged arbitrary subprocesses whose
recorded supervisor PID/birth identity has died, including detached children.
Digest-verified artifact caches survive; in-memory geometry is reconstructed. Durable `jobs/`
metadata records queued/running/terminal states without argument or environment
values. `python -m execution.history --incomplete` lists recoverable work. A queued
or running record whose owner died is evidence of interruption, not completion.
`execute.py --restart RUN_ID SCRIPT [ARGS...]` explicitly restarts matching
script inputs; it does not pretend to resume a partially executed Python function.
Never automatically replay unknown side effects. Physical-analysis saved-field
recovery and identity-checked mesh/evidence reuse remain the checkpoint APIs;
an incomplete native solve cannot become successful evidence through recovery.

Slicing uses immutable input/profile snapshots. Binary/deployment/configuration
identities cache version discovery and completed reviews automatically. Primary slices
already using the required auto-support policy serve as their own probe. Explicit
independent probe settings can run alongside the primary, with separate logs and
verified effective settings; failures preserve the primary evidence and request
review. For explicit renders plus slicing, slicing starts at STL completion while
CAD rendering continues. Traces show the actual overlap rather than summed work.

## Analysis and local data schema

```sh
.venv/bin/python -m execution.history --last 30
.venv/bin/python -m execution.history --last 200 --stats
.venv/bin/python -m execution.history --compare RUN_A RUN_B
.venv/bin/python -m execution.history --incomplete
.venv/bin/python -m execution.history --run RUN_ID --perfetto /tmp/timeline.json
```

Load the timeline in Perfetto's trace viewer when investigating overlap. These
commands inspect retained evidence and never rerun calculations. Compare identity,
status, cold/warm strategy and tool/environment context before interpreting latency.
Native computation can dominate cProfile's calling function; external sampling
such as py-spy or solver facilities is an optional targeted investigation, not a
normal-run dependency.
`lifecycle.wait` attaches its sampled summary as `execution_resources` to
`TimeoutExpired`. Physical-analysis native results preserve it in provenance;
the exception and failed status remain unchanged. Missing samples stay null.

| Local directory | Version 1 representation |
| --- | --- |
| `runs/` | One atomic JSON summary per run: identity, source and repository-Python hashes, lock hash, strategy, status, actual wall/observer CPU and RSS, worker/resource fields where observed. |
| `traces/` | OTLP ExportTraceServiceRequest JSONL with hex trace/span IDs, actual timestamps, parent IDs, PID/thread identity and operation attributes. |
| `resources/` | Schema 1 columns plus bounded samples: Unix nanoseconds, sampled process-tree RSS and live-tree CPU seconds. Short-lived processes can be missed; CPU is a sampled lower bound, not an exact integral. Summed RSS includes shared pages; unavailable samples stay null. |
| `profiles/` | Optional cProfile pstats or tracemalloc snapshots. Python allocation profiling does not measure native allocations. |
| `jobs/` | Durable request hashes and owner birth identity, queued/running/terminal status; unknown side effects are never replayed. |
| `cache/` | Digest-verified controlled bytes and their complete identity, independent of execution reuse. |

Repository output locks and staging stay under `.execution/` independently of
`ENGINEERING_DATA`, so trace-storage failure cannot corrupt computation or split
concurrent-agent output ownership. Optional cache writes fail safely.

Normal summaries/raw groups retain 500 runs for 14 days, protecting files younger
than one hour from concurrent cleanup; abandoned groups also expire. A trace file
is capped at 4 MiB with a `.truncated` marker. Resource sampling is capped at 2000
samples per script. Controlled caches keep at most 200 entries/256 MiB per
namespace; coordinator logs rotate at 2 MiB. Raw data stays Git-ignored. Deliberately
commit only bounded summaries, small representative trace snapshots and benchmark
history; tools never commit evidence automatically. No arguments, environment
values, script output or exception messages are stored in normal trace evidence.

Run summaries can also retain `artifact_reuse`: existing evaluator decisions for
geometry, export/view counts and slice status, with no paths or new cache semantics.
Absence in older records means unreported. Effective request budgets and bounded
`admission` observations now retain capacity, first blocking occupancy, wait status
and work seconds attributed to CPU/job slots. Older memory/resident-memory
blocking records describe the removed reservation policy.
Reasons can overlap and their sums are not elapsed time. Native leases carry a
`resource.admission` span with the measured queue duration and effective budgets;
its full span also includes connection/protocol overhead.

`execution_inputs_sha256` is a comparison fingerprint of actual options, resource
budgets and compatibility inputs. It does not authorize output caching. Older CAD
`arguments_sha256` fields represent an empty outer argument list and do not
establish matching view/export/fresh requests. Treat those groups as candidates
only. Comparison fingerprints still do not control machine load or validate task
necessity. `queue_seconds` measures resource wait;
the `coordinator.admission` span encloses both waiting and admitted execution, so
its duration must not be interpreted as queue time.

Native preload is checked before user dispatch: the import-only host must have
one thread, and two fresh children must complete matching native Boolean/validity
checks. An incompatible stack selects clean spawn workers. Dependency/runtime
content changes replace the coordinator and invalidate compatible worker state.
Gmsh and solvers remain isolated regardless of the CAD preload check.

The coordinator/watchdog and affinity implementation target Linux (including
WSL) and local POSIX environments. Native process birth identity on Linux uses
boot ticks so wall-clock corrections do not falsely terminate live work.

Physical backends automatically find candidate unchanged meshes through the existing
backend-specific identity guards. The cache stores references, not a competing mesh
format. Geometry, mesh settings, backend implementation and dependency identity
must match; copied input snapshots are rechecked. Stale/deleted references compute
freshly. `ENGINEERING_REUSE_MESH=0` requests fresh meshing for qualification. Every native solve and its quality/evidence checks still execute. Reports
identify automatic mesh reuse and original input hashes. Explicit `mesh_from`
retains its existing strict failure behavior; completed question-study evidence and
saved-field recovery retain their separate identity/completion requirements.

Combined coding-agent/execution investigations use the
[local workflow analyzer](../performance/WORKFLOW.md), which reuses these summaries
and OTLP spans read-only. Ordinary execution requires no session inspection.
