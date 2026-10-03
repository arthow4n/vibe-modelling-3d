---
name: workflow-performance-analysis
description: Investigate coding-agent session latency, Codex token usage, repeated tool activity and engineering computation bottlenecks together using local session metadata and existing execution history. Use for requested performance analysis or an authorized reflection investigation, not ordinary model iterations.
---

# Workflow performance analysis

This skill owns measurement of agent activity alongside engineering executions.
[Engineering execution](../engineering-execution/SKILL.md) owns resource admission,
workers, tracing, profiling, benchmarks and computational correctness.
[Engineering reflection](../engineering-reflection/SKILL.md) owns lessons, preferences,
engineering decisions and where reusable process guidance belongs. An analysis
request alone does not authorize broad algorithm, worker or modeling changes.

Use [the local analyzer and publication contract](../../../performance/WORKFLOW.md)
for commands, supported Codex formats, accounting limits and privacy checks.
Do not inspect session history after ordinary commands or generate routine reports.

## Choose the investigation

**Mode A — latency:** a session, response, command or operation felt slow.
Compare observed model/turn activity, tools, admission, initialization and other
waiting; investigate the largest measurable contributor first. An engineering
productivity assessment is unnecessary. Missing request boundaries leave request
latency unavailable: turn time outside tools is unattributed, not inference.

**Mode B — modeling workflow:** assess the work required to reach an established
engineering milestone, such as checked initial geometry, resolved interference,
a validated printable variant, a qualified simulation or a correction after
physical feedback. Establish the outcome and its limits from existing object
records and checks first. Select explicit sessions and a bounded period using
the documented modeling mode; retain evidence references and the association
basis locally. One task can span sessions; one session can include several tasks.
The analyzer records the analyst's evidence-backed assertion, not acceptance.
Do not attribute all selected activity to the milestone merely by time overlap.

For either mode, distinguish measured observations, plausible interpretations,
actions and unknowns. Tokens, turns, edits, revisions, failed operations,
equivalent calculations, reuse and validation activity describe effort; none is
a productivity score. Repeated verification/exploration can be necessary. Seek
reduced time or unnecessary agent effort while preserving required correctness,
manufacturing verification and physical evidence. A proposed change needs an
expected benefit and a test that could establish it; analysis does not authorize
implementing an optimization.

1. Establish the question, repository, period and source scope. Prefer a completed
   session or a bounded recent selection; active files are only snapshots. Exclude
   related forks/inherited histories from multi-session totals. Explicit selection
   is required for ambiguous repository ownership.
2. Discover local sessions by recorded working directory; inspect metadata only
   for unrelated sessions. Reuse `.execution/` or `ENGINEERING_DATA` through
   `execution.history`. Keep private identifiers and source records local.
3. Check availability, parser quality, usage method, open calls/turns and trace
   coverage before interpreting totals. Run execution-only analysis if agent
   records are missing. Unknown fields/formats are missing evidence, not zeros.
   Preserve Codex version, metric scope/quality and measured/eligible counts.
   Native turn first-token delay is not request TTFT or visible streaming speed.
   Initial turn configuration is not independently verified request/backend
   identity. Keep changed/ambiguous configuration unknown. Never pair cumulative
   tokens with session/turn time to manufacture throughput or context occupancy.
4. Run the deterministic analyzer for timing unions, reported token categories,
   tool counts, execution stages, queue/startup, worker warmth and recorded reuse.
   Prefer unique response usage; do not add repeated cumulative or per-turn totals.
   Input/cache and output/reasoning subsets are not independent additive totals.
5. Review correlation strengths. Exact structured run IDs establish a relationship;
   a unique containing tool interval is only plausible. Concurrent candidates are
   ambiguous. Stage sums and nested tools cannot be added to session elapsed time.
   Unattributed intervals are not model reasoning time.
6. Identify material observations before suspected causes or remedies. Repeated
   identical inputs can be justified verification; high token usage alone is not
   inefficiency. Compare only sufficiently similar contexts. Metadata does not
   establish intent or explain why work was repeated.
7. For the largest decision-relevant uncertainty, use existing history/benchmarks
   first. Invoke engineering execution for targeted profiling or matched measurements
   only if they can change a conclusion. Avoid expensive runs to fill report cells.
   Private content inspection, if necessary, is a separate narrowly scoped inquiry.
8. Retain the concise local report and useful supporting artifacts beneath the
   ignored execution-data root. Record findings, interpretations, missing evidence
   and any justified next investigation there; preserve the native measurements.
   Answer the question and achieved result, time/token contributors, largest
   supported delays, necessary work, testable improvement and remaining gaps.
   Inspect native telemetry only if rollouts lack decision-relevant measurements;
   qualify its scope/correlation before proposing instrumentation. Do not enable
   export, add a collector or copy unrestricted telemetry for theoretical coverage.
   Use the workflow's optional-telemetry guidance to distinguish OTel, hooks,
   app-server and raw rollout tracing; a plugin cannot supply missing lifecycle
   hooks, and raw tracing has no qualified numerical-only retention mode.
9. Publish only meaningful reusable findings or a useful measured baseline. Author
   a concise draft from approved aggregate fields using the six sections in the
   publication contract. Reviews preserve evidence, not new standing instructions.
   Route supported engineering/process lessons through engineering reflection and
   computational lessons through engineering execution; avoid duplicated guidance.
10. Run the publication checker and deliberately read the draft for privacy and
    factual support before creating a tracked review. The scanner is a secondary
    safeguard, not an anonymity guarantee. Never publish session IDs, prompts,
    command arguments, tool outputs, raw events/traces or diagnostic attachments.
    Creation does not commit/push; follow the repository Git workflow separately.

No worthwhile recommendation is a valid result. State the supported measurements
and limits; do not invent a bottleneck or optimization benefit.
