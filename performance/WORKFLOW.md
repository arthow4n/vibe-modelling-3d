# Local workflow performance analysis

The analyzer combines local Codex metadata with the existing schema-1 summaries
and OTLP spans through `execution.history`, plus optional filtered native Codex
telemetry. It does not collect new execution
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
.venv/bin/python performance/workflow.py --telemetry-only --telemetry .execution/workflow-analysis/otel-LOCAL-CAPTURE --timeline
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
a `ttft_ms` field. In the pinned [client implementation](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core/src/client.rs),
this clock starts inside the stream-mapping task after transport setup and stops
at the first `OutputItemAdded`. Preserve that meaning as a stream-to-first-item
delay; it is neither full request-to-first-token latency nor visible-text speed.
The completion log lacks a response ID and full response duration. Poll durations
and transport histograms must not be substituted for response duration or joined
to rollout usage by mere adjacency.

Logs and traces have separate exporters. The pinned [sampling implementation](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core/src/session/turn.rs)
has `stream_request`, `receiving_stream` and event-specific `handle_responses`
spans; the completion span carries usage and reasoning effort. Their parent/child
relationships are a concrete candidate for associating a client-observed request
operation with completion and usage. Qualify exported boundaries on the installed
transport before implementing this association. The whole sampling span also
includes tool-future draining, so its duration is not response duration. Do not
assume the separately emitted `ttft_ms` log joins to that span tree.

Other interfaces answer different questions:

| Interface | Useful observations | Remaining limit |
| --- | --- | --- |
| Ordinary rollouts | Turn timing, persisted model items, usage, tools, configuration snapshots and notices supported by the adapter. | No qualified per-request start/completion pair; cannot recover missing boundaries retrospectively. |
| Native OTel logs/traces | Transport attempts/errors, stream waits, completion usage/configuration; trace structure may associate client request-operation timing. | Export/correlation must be qualified; native `ttft_ms` has the narrower scope above. Aggregate metrics cannot reconstruct individual responses. |
| [Hooks](https://learn.chatgpt.com/docs/hooks), including [plugin-bundled hooks](https://developers.openai.com/plugins/concepts/plugins) | Session/turn, tool, interruption and compaction lifecycle observations. | No documented model-request start/completion hooks. Packaging hooks in a plugin does not add those boundaries. |
| [App-server](https://learn.chatgpt.com/docs/app-server) | Live turn/item events and assistant/reasoning deltas for a connected client. | Arrival time is client-observed output timing; no documented per-request lifecycle pair or visible-text token count. This is not a passive observer of an existing CLI session. |

There is also a separate upstream [local rollout trace](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/rollout-trace/README.md),
enabled by `CODEX_ROLLOUT_TRACE_ROOT`. Its [inference events](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/rollout-trace/src/inference.rs)
have correlated start/completion/failure/cancellation identifiers, model/provider
and response usage payloads. Writer wall-clock timestamps include payload-write
overhead; they describe client-observed inference intervals, not isolated server
compute. Stream deltas/first-token events are not retained by this producer.
The installed 0.160.0 binary contains the trace-enabling/event strings, but this
route has not been runtime-qualified here; even the README's `trace-reduce`
command is absent from its debug help. This is source evidence, not a supported
analyzer input.

That diagnostic path writes full requests, responses, tool data and paths before
recording event references. The inspected producer has no numerical-only mode.
It does not meet this investigation's approved-field retention policy; filtering
after recording would not fix that. Do not enable it as a latency workaround.
The upstream Rust [request-contributor/interceptor API](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/ext/extension-api/src/model_request.rs)
is host-registered code, not a documented installable plugin hook; using it would
require a custom Codex host/build outside this workflow's scope.

Native telemetry could improve transport-attempt and reconnect diagnosis. Exact
request latency/throughput would require qualification of complete request/stream
boundaries, TTFT scope and response association for the installed transport. Those
are not established by the current rollouts or a generic telemetry configuration.
The original rollout baseline did not justify an additional collector. A subsequent
explicit request authorized machine-wide local native capture for ordinary Codex
and Remote Control launches; the optional setup below implements that scope.
For a concrete request-latency investigation, the smallest supported next experiment
is an explicitly started, bounded loopback OTel capture of both logs and traces:

1. Use a numerical/configuration allowlist before storage, discard prompts, tool
   data, credentials and unrestricted attributes, and pseudonymize only the
   structural correlation keys needed for joins. Store normalized records beneath
   `.execution/workflow-analysis/` with the existing retention/size limits. No raw
   request logging or third-party forwarding is permitted.
2. Configure `otel.exporter` and `otel.trace_exporter` separately for loopback
   OTLP HTTP/gRPC endpoints through launch overrides or user configuration; project
   telemetry configuration is ignored. `otel.log_user_prompt=false` alone does not
   remove tool-result snippets. Merely enabling an exporter does not provide a
   local file receiver, and a generic collector's defaults are not this allowlist.
3. Check one-request, multi-request, tool-separated, retry and interrupted cases.
   Require a unique structural association between the request operation,
   completion, usage and configuration; never match by temporal adjacency. Report
   coverage and unassociated attempts, and keep a separate scope for the native
   stream-to-first-item delay. Test export completeness and observer overhead.
4. Extend the existing adapter only for measurements the capture establishes.
   Stop the capture and remove its launch overrides afterward; ordinary engineering
   must consume no telemetry-capture resources. Literal generated-token timing,
   server scheduling and backend compute remain unavailable unless independently
   reported. An honest coverage gap is a complete analysis result.

### Optional machine setup and future clones

Native capture is a **machine installation**, not part of a Git clone or ordinary
CAD evaluation. On a new machine, a moved checkout or a different coding agent,
check whether the native receiver and supported adapter are available. Explain
the scope and obtain the user's choice before installing/changing machine defaults.
Modeling, execution history and rollout-only analysis work without this option.
For another agent, qualify its supported instrumentation instead of configuring
Codex or assuming these fields apply.

For an authorized Linux/systemd user setup, after `uv sync --locked`:

```sh
.venv/bin/python -m performance.telemetry --install
systemctl --user is-active codex-workflow-telemetry.service
systemctl --user restart codex-remote-control.service
```

Installation adds only a managed `[otel]` block in `$CODEX_HOME/config.toml`
(normally `~/.codex/config.toml`), a local control file beneath the ignored analysis
directory and a user service pointing at this checkout's locked Python environment.
Existing unmanaged OTel settings require a deliberate merge rather than overwrite.
The helper verifies receiver readiness before enabling native export. It installs
a `Wants`/`After` drop-in when `codex-remote-control.service` exists, but does **not**
restart that service: doing so disconnects active Remote Control sessions.
The user should restart it after handoff; ordinary running CLI processes likewise
need a restart. Rebooting with the user's persistent service manager also loads
the setup. No special Codex launch flags or per-model activation are needed.
Project telemetry settings are ignored by Codex; installing only repository files
cannot enable this. After moving/cloning the checkout, rerun the authorized setup
to update the service's interpreter, working directory and storage root.

The receiver accepts authenticated OTLP HTTP JSON or protobuf on **127.0.0.1**,
filters before writing, never forwards/upload events, and records only numerical
timing/usage, narrowly recognized model/effort/version values, fixed enums and
pseudonymous structural correlation keys. Prompts, bodies, tool arguments/results,
errors, accounts, paths and arbitrary attributes are discarded in memory. Turning
off prompt logging is an additional native setting, not the retention filter.
The native metrics exporter is disabled in this managed configuration.

The explicitly enabled service remains available for all Codex work on this
machine, including non-modeling sessions; it does not run analyses or computation.
Each bundle stops/rotates after eight hours, 16 MiB or 100,000 records; at most
20 bundles remain. Request bodies are bounded to 4 MiB, connections time out,
and files are private/Git-ignored. Idle operation performs no repeated disk writes.
Rotation/export loss can leave incomplete span trees and must retain coverage
warnings. The service restarts automatically after reboot/login according to the
user service manager; headless boot requires an already approved persistent user
manager (`loginctl show-user "$USER" -p Linger`). Do not change that policy silently.

```sh
# Remove managed Codex defaults and stop/disable the receiver; restart Codex afterward.
.venv/bin/python -m performance.telemetry --disable
# Diagnose local receiver startup without printing Codex configuration or source data.
systemctl --user status codex-workflow-telemetry.service
journalctl --user -u codex-workflow-telemetry.service -n 20
```

`performance.telemetry --duration 600` remains a foreground-only alternative for
a bounded experiment; exporter configuration is then a separate explicit choice.
There is no launcher wrapper or private model-traffic interception.

### Qualified native observations

Installed 0.160.0 was exercised prospectively with a small multi-request turn
separated by a shell tool. Both sampling operations exported a `stream_request`
child and a completion `handle_responses` child under the same sampling/receiving
tree, with completion usage and request effort. The completion's `receiving`
child ends when the event reaches Codex core. This supports **derived client
request-operation duration** from `stream_request.start` to that receipt, plus
`output_tokens / operation_duration`. It includes client preparation, network and
scheduling; it is not isolated backend compute or exact wire-send timing.
The parent sampling/receiving spans can include later tool draining and are not
used as response-duration substitutes. Output includes reported reasoning tokens.

The installed export did not retain event-kind labels on non-completion
`handle_responses` spans, despite the source's `otel.name` recording. Individual
text/reasoning-delta receipt timing is therefore **unsupported**, not inferred from
generic stream polls. Native log `ttft_ms` retains its stream-mapping-to-first-item scope and is reported separately,
without joining it to a request or using it as a generation-rate denominator.
Warmup completions can appear among native completion logs; those logs are not a
generation-request count. Literal request TTFT, generation-only/visible-text
throughput, exact wire-send duration and backend compute remain unavailable.

The adapter currently qualifies these boundaries for 0.160.0 only. Unknown versions,
missing/ambiguous parents, conflicting duplicate spans, missing timestamps and
unfinished attempts keep missing metrics and warnings. Export order is irrelevant;
relationships come from span/parent IDs, not adjacency. Model is configured sampling
identity and backend implementation remains unverified. Missing effort stays unknown.

Ordinary analyzer commands automatically inspect retained native captures for the
**selected rollout sessions**, using pseudonymized explicit session metadata keys.
They never add native usage to rollout token totals. Explicit `--telemetry` may
select up to 20 bundles; `--telemetry-only` permits analysis of those chosen bundles
without rollouts/executions and declares that broader scope. Aggregate parsing is
bounded to 100,000 records. Modeling mode still requires milestone evidence and
selected session associations; a telemetry-only capture is not task acceptance.
Local reports include native coverage, configuration, tokens, slowest operations
and transport-attempt observations. Perfetto retains these request intervals
separately. Measured-turn attribution unions tools first, then native request
operations, recorded model items and compaction, so overlap is not counted twice.

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
