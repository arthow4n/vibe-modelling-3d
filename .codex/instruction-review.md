# Instruction consolidation review — 2026-10-05

Documentation-only review against repository revision `95c8dc9`. No product
geometry, exports, runtime implementation, dependency locks or historical model
attribution changed. This record explains the refactor and validation; it is not
another instruction entry point or a recurring required report.

## Ownership and preservation

The substantive review covered AGENTS.md, all five repository skills, all design
references, execution/physical-analysis documentation, root workflow/licensing
links and relevant performance routing. Implementation checks covered evaluator
selection, export tolerances, stage/report status, support probing and reuse;
bootstrap, input identities, artifact ownership and resource defaults. Existing
code contracts, rather than proposed architecture, determined technical wording.

| Original guidance | Current owner and disposition |
| --- | --- |
| Purpose, autonomous scope, product value, correctness and evidence integrity | [AGENTS.md](../AGENTS.md): universal constraints retained; phase procedures routed. |
| Printer envelope, nozzle/layers, filament choices, walls/infill, precise-printer caveat and complete hardware inventory | [User preferences](skills/cadquery-3d-design/references/user-preferences.md#printer-manufacturing-and-available-hardware): moved without changing numerical defaults or any of the 14 stock size/quantity entries. Setup agreement and consequential-change rules retained. |
| Standard assembly tools, protection and concealed-mechanism defaults | Same preference record: moved from design skill/reference, with explicit scope and links back to handling methodology. |
| Core modelling sequence and comprehensive TODO checklist | [Design skill](skills/cadquery-3d-design/SKILL.md): consolidated into adaptive investment, timed reference retrieval, intent-based review and phase completion. Checklist removed, not relocated as another mandatory procedure. Its applicable obligations remain in the named references. |
| Product architecture, form exploration, feedback, handling, fit/load screens, oversized joint/load agreement and retention | [Design decisions](skills/cadquery-3d-design/references/design-decisions.md): preserved with section-level entry points before consequential decisions. Existing agreements and delegation still apply; no new approval gates. |
| Parametric construction, edges, repeated variant checks | [Construction reference](skills/cadquery-3d-design/references/parametric-and-edges.md): retained; object-owned check reuse moved here from AGENTS.md. |
| Manufacturing co-design, actual paths, solid-analysis mismatch and material/process uncertainty | [Print planning](skills/cadquery-3d-design/references/print-planning.md): consolidated; settings cannot establish calibrated modulus/strength/fatigue/strain or isotropy. |
| Stage responsibilities and limits | Core evidence rules plus design skill's question-based evidence table and specialized owners. No mandatory sequence; no routine bounds/solid counts, STEP reimports, STL audits or G-code fit reconstruction. Exception criteria retained in core. |
| Evaluation/export/render/report procedure | [Execution documentation](../execution/README.md#cad-evaluation-and-exports): moved beside implementation; same selection, placement, paired exports, absolute meshing, status/exit semantics, path rules and historical-exporter update requirements. Long tool-specific JS example replaced with concise operation guidance and a shell example. |
| Slicer settings, placement and support interpretation | [Orca skill](skills/orca-slicer-printability/SKILL.md): retained specialized review. Duplicate user defaults/export explanation replaced by links; duplicated option table and profile examples replaced by CLI help and one existing-export example. Diagnostic mismatch, profile-derived limits, support-removal review, STL/GUI STEP distinction and final per-layout smoke check retained. |
| Numerical questions, studies, convergence, diagnostics and retained evidence | [Physical-analysis documentation](../physical_analysis/README.md#use): existing API contracts preserved. Failure classification moved from core to the saved-result diagnostic entry point. Existing study guidance owns resolution, backend qualification, force/strain measures and finite-edge witnesses. |
| No invented deadlines, locked environment, native isolation, identity and output guards, evidence reuse and unknown-side-effect recovery | Core invariants retained; detailed commands and automated safeguards remain in execution/API documentation. No new manual checker duplicates their guarantees. |
| Reflection, consumer-driven extensions and qualification | [Reflection skill](skills/engineering-reflection/SKILL.md#put-the-result-in-its-owning-source): extension procedure consolidated; concrete consumer, in-scope implementation, specific blockers, benchmarks and demonstrated benefit preserved. No routine API audit or new framework. |
| Profiling/recovery versus agent-session measurement | [Execution skill](skills/engineering-execution/SKILL.md) routes relevant technical sections; [workflow performance skill](skills/workflow-performance-analysis/SKILL.md) retains measurement, privacy, per-object attribution and optional-machine-setup procedures. Duplicate performance-attribution detail removed from reflection/core in favor of routing. |
| Object records, transferable lessons, physical feedback and print status | Existing object directories, [bounded evidence index](skills/cadquery-3d-design/references/reusable-model-lessons.md) and [physical experiments](skills/cadquery-3d-design/references/physical-experiments.md) remain authoritative. Print results, unknown settings, successful interfaces, rejection-before-print versus physical failure, immediate readiness/root-index correction and standard status block preserved. |
| Attribution, licensing, completion and Git | Core retains actual/unknown provenance, historical attribution, requested-work staging, whitespace review, automatic commit/push on current upstream and truthful delivery status. |

Removed speculative future wrapper names from the mechanics reference in favor
of the already implemented question/study API. No substantive historical design
lesson was deleted. Physical experiments, hinge example, reusable-evidence index
and performance skill remain structurally unchanged because their distinct
responsibilities and scoped evidence already fit the desired architecture.

## Routing validation

Walkthroughs evaluated what each task retrieves and when, not just whether its
links exist. They do not claim completed products or measured task performance.

| Scenario | Expected necessary route and decision | Unrelated work avoided |
| --- | --- | --- |
| Straightforward printable tray | Core → design skill → printer defaults/applicable precedent → construction and print planning → evaluator/Orca details at export/slice → brief handoff reflection. Complete directly when requirements are clear. | No mandatory alternatives, mechanism review, coupon, contact study or performance history. |
| New multipart snap-fit product | Design skill → preferences → architecture gate and rough whole-object use before interfaces → named contacts/states, motion and retention screen → representative physical experiment or numerical question only for unresolved consequential behavior. | No mechanism refinement or expensive analysis used to justify product value; no automatic full-product completion beyond an agreed sample phase. |
| Independent structural/contact analysis | Core → physical-analysis Use → study sequence → applicable question/study API; saved-result diagnostics if failure. Explicit loads/material/manufacturing, quality and decision tolerances; benchmark qualification separate from product acceptance. | No product-design review for an independent tool study; no full performance audit or alternative solver by default. |
| Physical-print failure | Core → reflection → physical-feedback/failure sections → correct object readiness/status and root index; preserve observation separately from hypothesized cause. | No automatic redesign, simulation, tolerance calibration or coupon matrix. |
| Execution-performance investigation | Core → execution skill → relevant history/schema, capacity, profiling or recovery details. Agent-token questions additionally route to performance skill. | No whole-product review, full design references or model export/slice. |
| Established-product revision | Design skill and current object record → affected relationships, construction and manufacturing; preserve successful interfaces and retained evidence, rerun affected final checks. | No full architecture restart, unrelated sweeps, historical-print invalidation or repeated physical experiment without changed conditions. |

## Validation and limits

All five skill folders passed the skill-creator `quick_validate.py` validator.
A temporary audit checked Markdown local targets/heading anchors in repository
skills, changed documents and incoming links to changed documents: 289 local
link/anchor checks passed with no broken targets. Stable core anchors used by historical model and
performance records were retained. The audit script is disposable validation,
not a new repository framework. Git whitespace checks passed.

One independent blind review, given no intended conclusions, compared the working
instructions with HEAD and exercised all six routes. It found no blocking
technical-contract loss and identified one scope regression and two discovery/
duplication concerns. All were addressed:

- Restored “ordinary storage” after relocation had inadvertently narrowed the
  protection default to “ordinary protective storage”; explicit open-tray requests
  still override it.
- Added a direct conditional link from physical-analysis Use to saved-result
  failure diagnosis before input/backend changes or another solve.
- Consolidated printer precision/clearance/calibration guidance in the printer
  section; the joining paragraph retains seated-connection preference and H failure
  evidence, linking to the general rule. This had also been found in local review.

Measured initial-entry text (whitespace-separated words): AGENTS.md decreased
from 6,186 to 1,321; the design skill from 2,368 to 1,190. These measure relocated
and consolidated text, not latency, token savings, engineering quality or total
scenario reading. Specialized documents grew where they now own moved content.
No matched end-to-end agent-performance benchmark was run; improved retrieval is
an architectural expectation supported by routing review, not a measured speedup.
No CAD, solver or slicer runs were needed for documentation-only changes.

Some short reminders intentionally remain at caller/owner boundaries: evidence
limits, deadline links, pairing/status and setup agreement. They protect discovery
without duplicating inventories or full procedures. Large design/analysis
references remain intact with direct section routes; splitting them into more
skills/files was not justified. Runtime defaults remain in code/help, diagnostic
profile facts in the Orca skill, and user starting preferences in their record.
