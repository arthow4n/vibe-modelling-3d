Scope: Retrospective agent effort for `analysis_phone_stand`, reviewed 2026-10-04 against object records at repository revision `29ae1eb`. These are selected retained work scopes, not exhaustive lifetime cost or billing. Task associations were reviewed from the relevant source conversation and object evidence. Source selections, fingerprints and detailed numerical evidence remain local.

Measurements: Unique completed-response usage, selected by explicit response-to-turn ownership; no proportional allocation. Cached input is included in input, reasoning is included in output, and uncached input is their valid difference. Input includes carried conversation/context; it is not newly authored model text.

| Selected work | Scope | Usage observations | Input | Cached input | Uncached input | Output | Reasoning output |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial phone stand and physical-analysis foundations | mixed | 87 | 9,745,870 | 9,340,416 | 405,454 | 92,279 | 38,624 |
| Hardware adaptation and compact V2/V3 development | direct | 368 | 43,139,985 | 40,201,984 | 2,938,001 | 403,869 | 221,953 |

The union of recorded complete turn intervals below includes tools and waiting. It is a separate wall-time observation, never inference time or a rate denominator.

| Selected work | Recorded turn union, minutes |
| --- | ---: |
| Initial phone stand and physical-analysis foundations | 52.67 |
| Hardware adaptation and compact V2/V3 development | 322.00 |

Qualified native timing uses a deliberately selected single retained capture bundle for the relevant source, a bounded snapshot of the phase. Structural session/boundary joins and unique whole-turn containment support task association. The bundle has a recorded size/rotation limit; these are samples, not full-phase request censuses. Rate medians/P90 summarize each operation’s own output-token count divided by its own client-operation duration.

| Captured phase | Operations | Operation union, min | Native sample output | Native sample reasoning | Median output tokens/s | P90 tokens/s | Configured sampling identity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Hardware adaptation and compact V2/V3 development | 53 | 57.79 | 72,143 | 54,757 | 21.41 | 27.85 | gpt-6.1-sol, high |

Native completion usage is a separate sample and is never added to rollout totals. The duration includes client preparation, transport, scheduling and response time; reasoning is already an output subset. Backend compute, literal request TTFT, generation-only/visible-text speed and total lifetime inference time are unavailable. Timing for other phases in this record is unavailable.

Findings:

- Initial phone stand and physical-analysis foundations: Initial digital prototype retained historically; V1/V2 rejected before printing.

- Hardware adaptation and compact V2/V3 development: V1/V2 rejected; V3 digital and conditional mechanics checks retained, unprinted.

The initial foundations thread jointly built the reusable analysis API and a phone-stand consumer, so it remains `mixed`. Direct later construction also contains incidental shared-API work that cannot be split within a turn. Rejected earlier revisions are included in their respective recorded phases; these numbers are not the marginal cost of accepted V3 alone.

Implications: These figures describe observed agent effort toward the stated outcomes. They do not score product usefulness, engineering quality, wasted work, pricing or model efficiency.

Changes or recommendations: Keep this bounded record linked from the existing object instructions and root model index. Future requested investigations should use [per-object effort attribution](../../../performance/WORKFLOW.md#per-object-effort-attribution), updating scope and evidence when a new phase is analyzed. Ordinary modelling does not require routine history inspection.

Verification and limitations: The catalog attribution uses 19 repository-associated source sessions across 14 current object directories; raw turn/response keys stay private and normalized labels are ordinal only. It rejects duplicate turn allocation and overlapping selected response histories. All categories in the table have complete field coverage for the selected usage observations. Source CLI versions for this record: 0.159.0, 0.160.0. Native boundaries are qualified for 0.160.0 only. General tooling, unselected turns, unmapped usage and unavailable predecessor/other-harness records are outside these figures. Historical usage counters can differ from completed unique-response accounting; the latter is used here. Digital and physical outcomes come from the existing object records, not performance metrics. Focused attribution/workflow regressions passed; CAD, exports, slices and print-status conclusions were not re-evaluated.
