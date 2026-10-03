# First local workflow baseline: admission delays and accounting

Scope: Two completed, independent Codex parent sessions observed from
2026-10-02 07:25:20 UTC through 2026-10-03 19:26:52 UTC. Analysis performed
2026-10-03 with CLI 0.160.0 and CPython 3.12.14 on Linux/WSL2; execution records
reported 16 available CPUs. Analyzer implementation: `20afea5`, with history compatibility fix `2a3b254`
(base `a829e39`); the largest
queue observations used execution revision `9b80a389`. Historic per-job CPU/memory
budgets were not retained. The 443-run snapshot was retained before implementation regressions rotated
older native records; a post-commit recent-session analysis also completed.
This is a bounded historical baseline, not a controlled
benchmark or a comparison of agent quality.

Measurements: The snapshot selected 443 retained executions and 871 unique
response-usage records. Response sums matched final thread totals in each selected
session. Twelve compactions and 19 repeated legacy cumulative snapshots were
observed. The selected records reported:

| Token category | Count |
| --- | ---: |
| Input, including cached input | 101,186,955 |
| Cached input subset | 93,661,696 |
| Output, including reported reasoning | 1,036,144 |
| Reasoning output subset | 548,140 |

Recorded active-turn intervals unioned to 52,181 s; observed tool intervals to
14,027.156 s; retained engineering execution intervals to 1,843.979 s. These
intervals overlap and cannot be added. Retention prevents treating engineering
coverage as complete across the whole session period.

Queue measurements existed for 198 runs: 760.476 s of summed queue work, median
0.0000238 s, maximum 198.488 s. Nine model-source runs exceeded one second,
accounting for 758.729 s of that work. The five largest waits were 198.488,
162.407, 159.969, 112.786 and 33.502 s. None had an initialization span. In the
largest case, command duration was 208.944 s, worker duration 10.188 s, and the
CAD worker trace started 198.749 s after command start.

Findings: Resource admission materially delayed those particular CAD calls;
the trace and summary agree on the distinction from initialization. The retained
records do not establish which capacity limit caused the waits. Across the
selected snapshot, 32 initialization spans totaled 72.497 s (median 1.878 s).
Sixty-four successful script calls under one second had median latency 0.301465 s,
but 58 were generated test fixtures, so this is not a normal modeling baseline.
Forty-eight repeated identity groups included 117 additional executions; intentional
regression checks prevent interpreting those counts as avoidable work.

Legacy cumulative usage differed from response totals in two separately checked
completed sessions with compaction. Response-level accounting is the supported
basis when present; summing both streams would be incorrect. Recorded reasoning
items describe activity intervals, not all model latency or the cause of remaining
time. High token usage alone does not establish inefficiency.

Implications: Diagnose queue wait, initialization and computation separately before
proposing kernel or worker changes. The `coordinator.admission` span encloses both
waiting and admitted execution; its duration is not queue time. Historic artifact
reuse was unreported in these summaries, so this baseline cannot quantify cache
benefits. Concurrent session windows also make 418 timing-only associations
plausible and 25 ambiguous; none is claimed as an exact tool relationship.

Changes or recommendations: Added the local analyzer and its focused skill,
with response deduplication, interval unions and explicit coverage limits.
[Execution documentation](../../execution/README.md) now explains admission-span
semantics. Existing evaluator reuse decisions are retained as bounded summary
fields for future analysis; cache behavior is unchanged. A two-call deterministic
fixture smoke check recorded fresh/cold geometry at 2.339168 s followed by
reused/warm geometry at 0.242738 s. This combines multiple effects and does not
establish an isolated cache speedup. Any investigation of historic budget contention
or broader optimization is separate work. Existing matched benchmark evidence
remains in [performance documentation](../README.md).

Verification and limitations: The 82-test adapter, privacy, history and affected
execution/evaluator suite passed. After the final missing-cross-check fixture,
33 focused tests passed; all three skill validators and their local links passed.
Compatibility parsing covered 49 repository-associated files from nine observed
CLI versions between 0.153.4 and 0.160.0. One thread-total mismatch, seven legacy
counter-reset events and three negative item intervals were flagged across that
broader compatibility set. They were absent from the selected response-accounting
scope. The six-section publication check and deliberate privacy/factual review
were applied; automated scanning does not guarantee anonymity. Raw records,
normalized histories, traces and reports stay local. Missing budgets, bounded
retention, nested test operations and timing-only associations limit causal claims.
No computational acceleration or unnecessary agent verification is claimed.
