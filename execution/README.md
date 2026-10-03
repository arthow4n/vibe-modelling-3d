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
