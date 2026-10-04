Scope: Retrospective token usage and captured request timing for all 14 current model directories, reviewed 2026-10-04 at base repository revision `29ae1eb`. Nineteen repository-associated source sessions yield 20 reviewed milestone/accounting scopes. Selected work spans 2026-09-05 through 2026-10-04; original sessions can extend beyond a model milestone. Source CLI versions are 0.153.4, 0.154.0, 0.155.1, 0.157.1, 0.159.0 and 0.160.0. This is selected retained effort, not exhaustive lifetime cost, accepted-design-only cost or billing. Original creator provenance and print evidence are preserved.

Measurements: 2,472 unique completed-usage observations are allocated across 190 selected recorded turns. In those selected sources, 179 additional usage observations remain unassigned because they belong to excluded shared/reflection work or lack reviewed turn ownership. Unique response-to-turn ownership supplies accounting; overlapping allocations and inherited selected response histories are rejected. All four reported token categories have complete field coverage for the allocated observations. Cumulative legacy counters are not summed into these response counts.

The table covers direct construction/checks/revisions, except the swatch row, which measures Codex integration of a supplied design. Input includes carried request context; cached input is an input subset. Reasoning is an output subset. Uncached input and separate shared/follow-up phases are available in each linked object record.

| Current object / selected construction scope | Input tokens | Cached input tokens | Output tokens | Reasoning output tokens |
| --- | ---: | ---: | ---: | ---: |
| [sunglasses_case](../../model/sunglasses_case/notes/agent_effort.md) | 31,748,694 | 29,619,456 | 209,293 | 84,191 |
| [macbook_charger_holder](../../model/macbook_charger_holder/notes/agent_effort.md) | 5,378,414 | 5,225,856 | 20,574 | 2,822 |
| [dental_travel_case](../../model/dental_travel_case/notes/agent_effort.md) | 7,342,521 | 6,873,472 | 46,596 | 16,713 |
| [glove_drying_insert](../../model/glove_drying_insert/notes/agent_effort.md) | 4,369,078 | 4,151,808 | 41,871 | 16,858 |
| [vaseline_container](../../model/vaseline_container/notes/agent_effort.md) | 1,122,446 | 1,059,712 | 7,054 | 767 |
| [corner_flow_test](../../model/corner_flow_test/notes/agent_effort.md) | 1,679,636 | 1,630,208 | 12,700 | 3,255 |
| [filament_archive_swatch (integration only)](../../model/filament_archive_swatch/notes/agent_effort.md) | 2,353,709 | 2,248,576 | 23,519 | 6,717 |
| [vaseline_transfer_spatula](../../model/vaseline_transfer_spatula/notes/agent_effort.md) | 2,759,197 | 2,660,352 | 26,245 | 15,329 |
| [storage_tray](../../model/storage_tray/notes/agent_effort.md) | 1,802,062 | 1,679,744 | 10,438 | 1,504 |
| [faceted_storage_tray](../../model/faceted_storage_tray/notes/agent_effort.md) | 5,398,481 | 5,063,296 | 28,617 | 4,628 |
| [book_reading_plate](../../model/book_reading_plate/notes/agent_effort.md) | 22,373,042 | 20,397,952 | 224,967 | 115,490 |
| [postcard_display](../../model/postcard_display/notes/agent_effort.md) | 3,413,192 | 3,220,096 | 21,585 | 4,085 |
| [analysis_phone_stand](../../model/analysis_phone_stand/notes/agent_effort.md) | 43,139,985 | 40,201,984 | 403,869 | 221,953 |
| [filament_swatch_box_study](../../model/filament_swatch_box_study/notes/agent_effort.md) | 87,665,609 | 81,281,920 | 895,384 | 481,346 |

The swatch-box total separates into 713,412 display output tokens and 181,972 archive output tokens. The archive row exactly reproduces the earlier bounded archive usage: 181,972 output including 100,405 reasoning. Retained rejected revisions/specimens count toward those phases; removed predecessor products are excluded.

| Separate associated scope | Input | Cached input | Output | Reasoning output |
| --- | ---: | ---: | ---: | ---: |
| vaseline_transfer_spatula: follow_up — Print feedback and compact SVG concept alternatives | 2,246,422 | 2,134,656 | 47,781 | 35,015 |
| postcard_display: follow_up — Wave print report | 112,531 | 12,288 | 294 | 0 |
| analysis_phone_stand: mixed — Initial phone stand and physical-analysis foundations | 9,745,870 | 9,340,416 | 92,279 | 38,624 |
| filament_swatch_box_study: mixed — Model-linked shared-tool and workflow investigations | 31,178,865 | 29,580,032 | 259,719 | 128,895 |
| filament_swatch_box_study: follow_up — Archive A print and loaded-hood feedback | 2,827,980 | 2,775,168 | 8,190 | 2,245 |

Native timing uses one explicitly selected retained capture bundle per relevant source, preserving the existing 100,000-record parse bound. These are boundary-qualified samples of identified phases, not exhaustive or randomly sampled task records. Each operation needs a structural session/completion join and complete containment in exactly one selected recorded turn. Bundle size/rotation limits, unfinished trees and cross-boundary operations reduce coverage.

| Captured object phase | Selected operations | Operation union, min | Native sample output | Native sample reasoning | Median output tokens/s | P90 tokens/s | Configured sampling identity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| vaseline_transfer_spatula: follow_up | 26 | 14.72 | 47,004 | 34,499 | 48.86 | 54.90 | gpt-6-luna, xhigh |
| analysis_phone_stand: direct | 53 | 57.79 | 72,143 | 54,757 | 21.41 | 27.85 | gpt-6.1-sol, high |
| filament_swatch_box_study: direct | 35 | 32.31 | 44,257 | 26,729 | 21.30 | 27.41 | gpt-6.1-sol, high |

The selected source bundles contain 55 phone-stand candidates (53 qualified/included), 37 swatch-study candidates (36 qualified, 35 within selected archive turns) and 28 spatula follow-up candidates (27 qualified, 26 within selected turns). These are capture candidate counts, not complete session request counts. Request-operation time runs from client operation entry to receipt of the associated completion and includes client preparation, transport, scheduling and model response time. Medians/P90 are per-operation output-token ratios; native usage is never added to rollout totals. Reasoning is already included in output. The durations are not isolated server compute, and the rates are not visible-text speed.

The [earlier archive timing supplement](2026-10-04-165521-archive-token-speed-and-request-timing.md) preserves a different 80-operation sample with median 20.78 tokens/s and about 79 minutes of request-operation union. It is complementary historical evidence, not added to the current 35-operation sample. Missing request timing for earlier phases remains unavailable; recorded turn time is published separately in object notes and includes tools/waiting.

Findings: Object-level attribution is possible using explicit reviewed turn ownership, without charging complete mixed sessions to a model. The source parser now retains private ownership keys in memory and exposes only generalized turn indices in normalized output. Contextless starts can shift these indices, so a context-only list cannot safely index a selection. Missing/ambiguous response owners stay unassigned.

Interpretation: The figures describe the effort toward each documented milestone, including rejected model iterations and necessary validation. They cannot establish whether effort was wasteful. The initial phone-stand foundation thread is inseparable from reusable API construction and is kept mixed. Standalone model-linked tooling/reflection turns in the swatch thread are also separate. The original swatch’s Gemini creation cost is unavailable; its measured Codex import work must not be mislabeled as creation. The spatula’s later SVG concepts and print feedback do not describe its original printable build.

Implications: The model index now makes measured agent effort discoverable alongside creator provenance. Selected output totals, cache reuse, uncached input and known timing coverage can inform a future matched investigation. Larger input counts include repeated conversation/context; they do not count newly created CAD text. Different phases, models, efforts and capture coverage prevent a model-speed or productivity ranking. No lifetime inference time can be recovered by dividing total tokens by a sample rate.

Changes or recommendations: Added the local reviewed-manifest consumer `performance/attribution.py` over the existing usage/native adapters, with allocation guards, source/evidence fingerprints and explicit bounded telemetry selection. Added object-owned `notes/agent_effort.md` records and index/instruction links. Updated the workflow-performance-analysis and engineering-reflection skills, the performance workflow contract and AGENTS provenance routing to attempt object attribution during requested investigations. Ordinary modelling does not acquire a routine history-analysis requirement. No new telemetry collection, model benchmark or CAD/solver computation is required.

Verification and limitations: Focused synthetic attribution and existing workflow/native-telemetry regressions passed: 102 tests. They cover ownership independent of usage timestamps, contextless-start indexing, mixed-work partitioning, duplicate/inherited response/turn scopes, source fingerprints, legacy partial counters, missing categories, private-key normalization and native sample boundaries. The real consumer attributes 19 selected sources without overlapping response allocations, reproduces the earlier archive token window and preserves unmapped usage. Public notes and this draft were checked for structure/privacy and deliberately reviewed against aggregate evidence. Source selection bases, source locations/identifiers and native records remain ignored. Other sessions, later print-feedback records outside the selections, deleted predecessors, another harness’s creation and unretained captures are outside these numbers. No CAD, exports, slices or physical checks were rerun. Backend inference time, literal request TTFT and visible/generation-only speed remain unavailable.
