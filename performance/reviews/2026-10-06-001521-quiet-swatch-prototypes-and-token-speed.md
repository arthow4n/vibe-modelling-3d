Scope: Requested reflection on the quiet filament swatch box proposals, Q1 prototype and Q1F revision through repository revision `7c8f7bb`, reviewed 2026-10-06. Eight completed modelling or clarification turns are selected by reviewed whole-turn ownership; the subsequent reflection investigation is excluded. This is selected effort, not lifetime cost or billing. Detailed selections and source evidence remain local.

Measurements: Completed-response usage is deduplicated before attribution. Cached input is included in input; reasoning is included in output. Uncached input is their valid difference. Input includes reused conversation and source context.

| Selected work | Responses | Input | Cached input | Uncached input | Output | Reasoning output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Q1 proposals, clarification and full prototype | 55 | 6,995,086 | 6,791,424 | 203,662 | 57,371 | 24,625 |
| Read-only exterior clarification | 2 | 419,615 | 414,208 | 5,407 | 1,508 | 1,034 |
| Q1F matching exterior and retained hood | 35 | 3,232,134 | 2,989,440 | 242,694 | 39,262 | 18,116 |
| Selected total | 92 | 10,646,835 | 10,195,072 | 451,763 | 98,141 | 43,775 |

Native timing is a separate captured sample, never added to the usage table. Rates summarize each request's own output divided by its own client-operation duration, including reasoning. All current sampled operations identify configured `gpt-6.1-sol`, high effort, Codex CLI 0.160.1; backend identity is not independently verified.

| Captured work | Operations | Operation union, min | Median output tokens/s | P90 tokens/s | Median duration, s | P90 duration, s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Q1 (partial construction sample) | 26 | 15.20 | 26.19 | 35.64 | 28.20 | 66.20 |
| Exterior clarification | 1 | 0.15 | 25.28 | unavailable | 9.22 | unavailable |
| Q1F | 33 | 18.03 | 32.71 | 41.90 | 22.74 | 72.40 |

The [earlier archive sample](2026-10-04-165521-archive-token-speed-and-request-timing.md) measured 80 operations at median 20.78 output tokens/s, P90 26.42. Q1F's median is about 57% higher in this comparison. Tasks, request sizes, contexts and captured periods differ; this is not a controlled speed benchmark or evidence of a service-side cause.

Recorded completed-turn interval union is 52.42 minutes: Q1 31.05, exterior clarification 0.93 and Q1F 20.43. These include tools and waiting. Native whole-turn duration and timestamp intervals disagree in six selected turns; both are retained locally, and turn intervals are not inference-rate denominators. The native whole-turn duration for Q1F is 19.07 minutes.

Retained execution history covers 31 selected runs: 22 completed and nine failed attempts. Failures exposed geometry or check defects during development; this count does not represent nine rejected products. Execution interval union is 10.29 minutes and tool interval union 11.30 minutes. These overlap native request activity and must not be summed into total elapsed time.

| Computational stage | Calls | Summed stage work, s | Stage interval union, s |
| --- | ---: | ---: | ---: |
| Script execution (including geometry sweeps) | 13 | 774.26 | 608.14 |
| CAD construction | 16 | 83.02 | 83.02 |
| Rendering | 12 | 62.19 | 62.19 |
| Paired exports | 12 | 1.04 | 1.04 |
| Orca review, including probes | 7 | 85.39 | 67.75 |

These nested stages overlap each other. Queue durations also overlap concurrent work; their summed 251.37 seconds are not additional elapsed time. The longest observed queue was 78.01 seconds, while full geometry checks were running. Exact causal allocation is unavailable from the retained associations.

Findings: Preserving the accepted exterior was feasible by budgeting the rigid wall, separate TPU insert, guide protrusions and hood clearance together. Q1F preserves the card pocket and accepted G hood in CAD. Port cuts initially separated the sleeve into two pieces; seating bands and matching base channels restored one connected insert. Connectivity and assembly clearance therefore need distinct checks. The thin local rigid crests and the TPU installation remain physical-test questions.

The independent expanded installation envelopes answer geometric clearance only; they do not represent a connected elastic deformation or calibrated 95A strain. CAD and slicer acceptance do not establish quieter closure, insertion force, retention, creep or durability. The next useful product evidence is an assembled print compared with the accepted box during real handling.

Context review found one unnecessary duplicate full geometry sweep launched while an unchanged sweep was still running, after adding a cheap connectivity assertion. Other reruns followed substantive geometry or travel-check corrections. No precise recoverable-time claim is made for the duplicate because work overlapped. Script sweeps were the largest retained computational stage; export conversion was negligible here.

The timing analyzer initially rejected 0.160.1 because its gate accepted only 0.160.0. The three relevant producer files are byte-identical between those releases: [turn sampling](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/core/src/session/turn.rs), [client stream](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/core/src/client.rs) and [session telemetry](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/otel/src/events/session_telemetry.rs). Actual 0.160.1 captures also pass the structural boundary checks. This was an analyzer compatibility issue, not evidence that the model ran slowly.

Implications: The recent sample is faster than the earlier slow archive sample under the stated client-observed metric. It cannot identify backend generation speed, visible-text streaming speed, literal request TTFT, or the reason for the difference. Product confidence should come from physical handling, while future digital work should reuse unchanged completed or running evidence.

Changes or recommendations: The analyzer now directly qualifies 0.160.0 and 0.160.1, accepts canonical patch versions within the qualified major/minor family only when existing structure and timing checks pass, and marks patch-based qualification explicitly. Other version families remain unavailable pending qualification. No collector configuration or runtime installation changed. The object record and bounded reusable-model lessons now preserve the envelope/connectivity lessons, and the object's effort record links this supplement. Existing sequential-refinement guidance covers the duplicate-sweep lesson; no additional scheduler or routine performance inspection was added.

Verification and limitations: Focused telemetry, attribution and workflow regressions passed: 124 tests. Qualified captures contain one size/rotation limit and one active snapshot; Q1 is partial, and Q1F has 33 measured operations versus 35 usage observations. Completed-turn usage has complete field coverage within the selected scope. Native tokens are not extrapolated or added to usage totals. Source selections, contextual commands, identifiers and raw captures remain private. This report was deliberately reviewed for factual support and privacy before publication. No CAD, export or slice reruns were needed for these analyzer and documentation changes. Q1 and Q1F remain unprinted; the previously accepted archive and hood observations retain their original scope.
