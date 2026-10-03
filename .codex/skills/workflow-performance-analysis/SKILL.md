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
