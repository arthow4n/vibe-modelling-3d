# Local workflow performance analysis

The analyzer combines local Codex metadata with the existing schema-1 summaries
and OTLP spans through `execution.history`. It does not collect new execution
metrics, alter caches/workers, call a model, or require a Codex launch wrapper.
The adapter boundary is `performance.sessions.Event` / `Session`; another harness
can provide those metadata objects when there is a demonstrated consumer.

Run from the repository root in the locked environment:

```sh
.venv/bin/python performance/workflow.py --recent 3
.venv/bin/python performance/workflow.py --session /local/path/to/rollout.jsonl
.venv/bin/python performance/workflow.py --recent 2 --timeline
.venv/bin/python performance/workflow.py --execution-only --last-runs 200
.venv/bin/python performance/workflow.py --session /local/path/to/rollout.jsonl --agent-only
.venv/bin/python performance/workflow.py --session "$PERF_SESSION_A" --question 'Which observed activity explains the waiting?' --timeline
.venv/bin/python performance/workflow.py --execution-only --since 2026-10-01T00:00:00Z --until 2026-10-03T12:00:00Z
```

`--session` may repeat (20 files maximum); it deliberately overrides repository
ownership and supports only rollout JSONL, not a UUID lookup. Automatic discovery
reads only headers of unrelated files and requires an absolute recorded `cwd`
within `--repo`. Workspace access lists alone do not establish ownership. Recent
means recorded creation time, not last modification. `--codex-home` overrides
`CODEX_HOME`/the conventional home; it reads its `sessions/` directory only.
Absent sessions are reported and retained executions are still analyzed.

Execution selection is bounded to 500 retained summaries, overlapping selected
session observation windows (not necessarily one task). With no sessions it uses
recent retained history. `--since`/`--until` select overlapping whole sessions and
executions; counters are **not** prorated or restricted to partial turns. Explicit
sessions remain explicit. Choose a narrower explicit session for task accounting.
The configured execution-data root is assumed to belong to the selected repository.
Related forks may replay old events: select independent sessions for combined
usage. Shared response keys across files suppress combined token totals and flag
overlapping accounting scopes. Tool outcomes without structured success status remain `returned`/unknown.

## Engineering milestone investigations

Default `--mode latency` answers a timing question without assessing engineering
productivity. For `--mode modeling`, first read the object's existing record and
required checks to establish an achieved milestone and its limits. Use explicit
sessions (up to 20), an ordered period, evidence references, an outcome and an
association explanation. Replace the example's local paths, period and assertions
with reviewed evidence; the analyzer does not establish acceptance itself:

```sh
.venv/bin/python performance/workflow.py --mode modeling \
  --session "$PERF_SESSION_A" --session "$PERF_SESSION_B" \
  --since 2026-10-01T00:00:00Z --until 2026-10-03T12:00:00Z \
  --question 'What work reached the checked variant?' \
  --milestone 'Printable variant with required CAD and slice checks' \
  --outcome 'Required digital checks passed; physical use remains untested' \
  --evidence model/object_name/README.md \
  --association-basis 'Selected sessions implement and check the documented variant' \
  --timeline
```

Evidence references are existing repository-relative files, with content hashes;
their contents are not copied into normalized metadata. These references preserve
the investigation's evidence identity, not a task database or proof of success.
The question, outcome and association basis are local analyst assertions. Review
them against engineering evidence before drawing conclusions or publishing.

The period bounds execution selection; selected session counters cover whole
sessions, including activity outside the milestone. `sessions_extend_time_bounds`
flags sessions that extend beyond the period. One session may contain several
tasks and a milestone may span sessions. Exact run relationships, timing candidates
and ambiguous executions keep their original strengths. An overlapping execution
does not automatically belong to the milestone. Tool edits are observable activity,
not a count of geometry revisions; failed regression fixtures are not failed designs.
Use the object records to interpret exploration, equivalent calculations, reuse,
verification and physical evidence. Fewer tokens/calls/revisions or shorter time
cannot establish better engineering. Record a concrete improvement only when its
expected benefit and correctness-preserving verification are testable.

## Verified formats and accounting

On 2026-10-03, installed `codex-cli 0.160.0` advertised `codex exec --json` in its
local help. The [official non-interactive documentation](https://developers.openai.com/codex/noninteractive/)
describes that structured interface. It is suitable for prospective integrations;
this implementation reads existing interactive **rollout** files, whose envelopes
and fields differ. Untimestamped exec JSONL is not a supported adapter and must
not be interpreted as a timed rollout. No client hooks or version-specific
environment variables are required.

Repository-associated local rollout headers were observed for CLI versions
0.153.4, 0.154.0, 0.155.1, 0.156.1, 0.157.1, 0.159.0, 0.159.2, 0.159.3 and 0.160.0.
All 49 repository-associated files parsed in the compatibility pass. One thread-total
mismatch, seven legacy counter-reset events and three negative item intervals were
flagged rather than silently accepted. Compatibility is field-driven, not a promise
for all files of those versions.
The parser consumes timestamp/type/payload envelopes and these validated fields:

- `session_meta.cwd`, timestamp, CLI version, structured subagent source and a
  fork marker when available. `turn_context` supplies narrowly recognized model
  names and default/plan mode. No prompts/instructions or workspace values remain.
- `token_usage_record`: unique `(thread_id, response_id)` keys with `usage`, and
  `thread_token_usage` as a cross-check. Input, output, cached input and reasoning
  output are separately reported. `turn_token_usage` is cumulative within a turn
  and is **never summed**. Duplicate responses are discarded, conflicts flagged.
  Missing fields remain unavailable. Thread-total disagreement qualifies coverage.
- Legacy `event_msg.token_count.info.total_token_usage`: nonnegative successive
  differences, excluding first/reset baselines of unknown origin. Repeated values
  contribute zero. `last_token_usage` is not summed because notifications repeat.
  This fallback is explicitly incomplete, especially across resumes/compaction.
  Response records take precedence when present; the two streams are never added.
- `task_started`, `task_complete`, `turn_aborted`, response tool call/output pairs,
  and `item_completed` millisecond intervals. Observed CommandExecution `command` fields
  are argument lists; both those vectors and string-form fixtures are classified
  without retaining their contents. Item and response tool layers remain
  separate in frequency tables; overlapping intervals are unioned for wall time.
  A completion timestamp is not proof that a shell child finished successfully.
- `compacted`, context-compaction items and observable subagent activity. Compaction
  count is from `compacted` records; item intervals are a separate timing layer.
  Resumes without explicit markers and unavailable subagent sessions stay unknown.

In three completed 0.160.0 sessions checked during implementation, unique response
sums equaled final thread totals for all reported categories; legacy totals differed
in two sessions with compaction. They are not interchangeable. This establishes
an observed adapter contract, not billing or model-quality semantics. Cached input
is an input subset; reasoning output is a reported output subset. No price/cost or
"token efficiency" score is calculated.

## Model timing qualification: Codex 0.160.0

The installed CLI and four recent repository-associated rollout schemas were
inspected during this extension. The installed format records per-response usage
and native **turn** duration/first-token delay, but no per-response request-start,
duration, first-token or streaming-delta timing. Qualification is field-driven;
older records remain supported with missing native fields left unavailable.

Semantics were checked against version-pinned upstream sources:
[protocol definitions](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/protocol/src/protocol.rs),
[turn timing](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core/src/turn_timing.rs),
[turn configuration serialization](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core/src/session/turn_context.rs)
and [retry handling](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core/src/responses_retry.rs).
No private records were used as fixtures. A matching version number does not
guarantee every upstream event was persisted by the installed harness.

| Measurement | Evidence and quality |
| --- | --- |
| Response count and usage | Observed unique keyed completed-usage records; failures/incomplete requests without usage are outside this count. Repeated/conflicting records and inherited scopes retain warnings. |
| Usage-record timestamp | Observed persistence timestamp, retained locally; not an exact request boundary or streaming timestamp. |
| Native turn duration | Observed `duration_ms` on completion/abort, based on a monotonic clock; separate from wall-clock interval unions. |
| Turn interval duration | Derived from recorded start/end when native duration is absent; warnings retain negative intervals or substantial native/wall disagreements. |
| Native turn first-token delay | Observed `time_to_first_token_ms` on completion: turn start to first recognized model event. Upstream accepts text/reasoning deltas and eligible output items, including tool/compaction items. It is not necessarily the first generated or visible token, nor request TTFT. |
| Turn configuration associated with usage | Observed initial `turn_context` model/`effort`, matched by explicit turn key. Unique unchanged snapshots only; conflicts, missing keys and identified compaction responses remain unknown. This is contextual initial configuration, not independently verified request model or backend implementation. |
| Request duration, request TTFT, throughput | Unavailable in qualified rollouts. Neither preceding tool completion nor turn start is an exact request start, even with only one completed usage record in a turn. |
| Context occupancy, backend implementation | Unavailable. Cumulative session usage and input-token counts cannot establish actual context occupancy. |
| Error/interrupt/reconnect observations | Observed error and stream-error notices plus completed/failed/interrupted/incomplete turns. Stream-error notices can describe explicit reconnect attempts, but some retries are hidden; full retry count, request attribution and backoff duration remain unavailable. |

Each timing/rate statistic reports eligible and measured counts. `quality` describes
the source observations; `statistics_quality` labels calculated statistics as derived.
Token aggregate records likewise retain category coverage; uncached input is derived
only when both counts exist and cached input does not exceed input. Reasoning is an
output subset. Overlapping response histories suppress combined response counts and
token totals. No timing estimates are currently emitted. Combined turn distributions
are suppressed for histories that share turn keys, while wall-clock interval unions
remain valid and warnings identify the overlap. Median and maximum are
available for small samples; nearest-rank P90 requires ten measured observations.
Groups describe configured turn context, not backend attribution or model rankings.

For qualified, associated request observations the arithmetic is:
`output_tokens / duration_seconds`, and approximate generation throughput is
`output_tokens / (duration_seconds - first_token_delay_seconds)`. The latter requires
a strictly positive denominator; missing/negative/nonfinite inputs and zero
denominators leave the rate unavailable. The pure calculation is tested, but the
rollout adapter has no qualified request timing inputs and does not enable rates.
Output can include reasoning tokens; these formulas do not measure visible text speed.
Visible-text throughput would also need visible text-token counts and genuine
streaming timestamps, which these records do not supply.

The report compares tools, recorded model items, compaction and unattributed time
within measured turns using disjoint interval unions (tools take precedence over
overlapping items, then compaction). Model-item spans are observed item activity,
not request intervals or complete inference time. Native turn statistics are a
separate layer and are never added to those wall-clock unions. Only genuine stored
intervals enter the existing Perfetto timeline; no request intervals are invented.
Slowest turns use generalized selection/turn labels; slowest responses are unavailable.

### Optional native telemetry decision

The [official telemetry documentation](https://learn.chatgpt.com/docs/config-file/config-advanced#observability-and-telemetry)
supports opt-in OTel export. It also describes prompt/tool-result events: disabling
prompt logging alone does not satisfy this repository's numerical-only retention
policy. Nothing in this extension enables export or changes Codex configuration.

Version-pinned [native telemetry](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/otel/src/events/session_telemetry.rs)
records API attempt/status/duration and stream-event timings. Its API duration
encloses an HTTP request operation, not necessarily the complete streamed response.
The [SSE implementation](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/codex-api/src/sse/responses.rs)
times individual stream polls. Completion telemetry has usage/configuration and
a supplied TTFT field, but that log record alone does not establish full request
duration and reliable response-key correlation. Poll durations and transport
histograms must not be substituted for response duration or joined to rollout
usage by mere adjacency.

Native telemetry could improve transport-attempt and reconnect diagnosis. Exact
request latency/throughput would require qualification of complete request/stream
boundaries, TTFT scope and response association for the installed transport. Those
are not established by the current rollouts or a generic telemetry configuration.
No collector, background service or launch wrapper is justified for this baseline.
If a future concrete investigation needs telemetry, first demonstrate the missing
decision-relevant measurement and correlation; use explicitly enabled local-only
collection with an allowlist of numerical timing/usage/configuration, discarding
prompts, tool data, credentials and unrestricted attributes before storage. It must
consume no resources during ordinary engineering work. Unqualified fields stay
unsupported; an honest coverage gap is a complete analysis result.

## Timing and execution evidence

Observed session wall time is the union of first/last record timestamps, not a
measurement of client launch/exit. Active turns include tool time and waiting.
Open tools/turns contribute counts and coverage warnings, not invented durations.
Tool/model item timing describes recorded activity, not all server inference.
Unknown or between-turn time is never labeled reasoning time. Concurrent sessions,
engineering executions and nested spans retain overlap in the optional Perfetto
file, using the existing `execution.history.perfetto_event` conversion.

Run summaries provide actual elapsed, queue, dispatch, status, sampled resources
and geometry-worker reuse where available. A new geometry worker can inherit
initialized imports; it is not necessarily a cold import host. Initialization
spans report that separate cost. Trace spans describe CAD, Python, Orca and
physical-analysis stages; stage sums are work totals and may include parent spans.
Existing evaluator reuse decisions are now retained as bounded `artifact_reuse`
summary counts for geometry, exports, views and slices, without output paths or
changes to cache decisions. Older records do not have this field. Explicit trace
`strategy=reused/fresh` is also reported as observed; absent fields do
not imply fresh work. Warm workers and artifact reuse are different measurements.
Admission observations report effective capacities and reason-specific blocking
work; reasons can overlap. Native resource-lease spans provide the same metadata,
summarized separately because they can be nested inside execution intervals.
Missing historical observations cannot establish a specific limiting resource.
CPU samples are lower bounds and RSS includes shared pages. Dispatch is not full
initialization. Source/lock/repository/argument/strategy identity groups suggest
repetition. New `execution_inputs_sha256` fingerprints also cover actual CAD
options and resource budgets; legacy CAD argument hashes omit those options,
so their groups are candidates only. Neither fingerprint controls machine load. A cache hit alone does not quantify saved time.

An exact run ID extracted only from a structured `run_id` field in a tool return
is a confident relationship; it can refer to an ancestor orchestration call.
Without it, one containing shell item or shell/orchestration/poll response interval (one-second tolerance)
is a plausible timing match. Multiple candidates remain ambiguous; no match remains
unassociated. Raw arguments/outputs are discarded immediately. No mandatory
harness identifier or modification of execution cache identity was necessary.

## Storage and publication

Reports, normalized metadata and timelines stay under
`data_root()/workflow-analysis/` (`.execution/` or `ENGINEERING_DATA`). The original
records are read-only. Analysis names are content-addressed to avoid duplicate
writes; at most 20 analyses remain, each JSON/timeline capped at 16 MiB. Lines are
streamed with a 16 MiB line bound and 100,000 normalized events per session;
truncation is reported. Defaults are repository-local and Git-ignored. A configured
root inside the repository must pass `git check-ignore`; an outside root is local
operator configuration and must not be published. Never stage raw outputs with
`git add -f`, diagnostic attachments or temporary transcript copies.

Publication is separate and optional. Author a short draft from approved aggregate
fields, not unrestricted events. Use these exact section prefixes with substantive
content (continued paragraphs/tables are allowed):

```text
Scope: question, period, conditions, source revision and relevant software.
Measurements: observed numbers and their measurement method.
Findings: observations followed by explicitly labeled interpretations.
Implications: the practical consequence.
Changes or recommendations: supported concrete action and its owning source, or none.
Verification and limitations: tests, coverage, uncertainty and comparisons not established.
```

Do not include usernames/hostnames/home paths, private URLs, session IDs, prompts,
conversation quotations, full commands/arguments, environment values, secrets,
raw stack traces/events, unrelated source snippets or unrestricted diagnostics.
Relevant CPU/RAM budgets, tool versions, revisions and repository-relative technical
references are useful, but a revision/fingerprint is not inherently anonymous.

```sh
.venv/bin/python performance/publication.py .execution/workflow-analysis/review-draft.md
# Read the Markdown deliberately for privacy AND evidence support, then:
.venv/bin/python performance/publication.py .execution/workflow-analysis/review-draft.md --publish-reviewed measured-subject
```

The checker requires the six sections and rejects recognizable sensitive patterns;
it cannot guarantee privacy or validate factual claims. Unexpected source fields
are never copied automatically. Publication only creates a file, never commits or
pushes. Flat `performance/reviews/YYYY-MM-DD-HHMMSS-subject.md` uses local creation
time and exclusive creation; same-second collisions receive a short suffix.
Later reviews should link earlier relevant findings. Reviews preserve evidence;
standing lessons belong in the responsible skills/docs. No review is required
when evidence does not justify a useful baseline or recommendation.
