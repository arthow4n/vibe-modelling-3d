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
  and `item_completed` millisecond intervals. Item and response tool layers remain
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

## Timing and execution evidence

Observed session wall time is the union of first/last record timestamps, not a
measurement of client launch/exit. Active turns include tool time and waiting.
Open tools/turns contribute counts and coverage warnings, not invented durations.
Tool/model item timing describes recorded activity, not all server inference.
Unknown or between-turn time is never labeled reasoning time. Concurrent sessions,
engineering executions and nested spans retain overlap in the optional Perfetto
file, using the existing `execution.history.perfetto_event` conversion.

Run summaries provide actual elapsed, queue, dispatch, status, sampled resources
and worker warmth where available. Trace spans describe CAD, Python, Orca and
physical-analysis stages; stage sums are work totals and may include parent spans.
Existing evaluator reuse decisions are now retained as bounded `artifact_reuse`
summary counts for geometry, exports, views and slices, without output paths or
changes to cache decisions. Older records do not have this field. Explicit trace
`strategy=reused/fresh` is also reported as observed; absent fields do
not imply fresh work. Warm workers and artifact reuse are different measurements.
CPU samples are lower bounds and RSS includes shared pages. Dispatch is not full
initialization. Source/lock/repository/argument/strategy identity groups suggest
repetition and narrowly comparable cold/warm groups, but do not control machine
load or all process settings. A cache hit alone does not quantify saved time.

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
