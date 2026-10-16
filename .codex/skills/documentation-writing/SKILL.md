---
name: documentation-writing
description: Write or restructure substantial repository documentation so humans can understand current state, engineering changes, evidence and next actions while detailed investigations and historical knowledge remain intact. Apply within the documents affected by the task, not as a routine repository audit.
---

# Documentation writing

Make the present situation understandable without requiring the reader to
reconstruct development history. Preserve the depth needed for investigation.
Use this skill for substantial object records, technical guides, decision
explanations and documentation restructuring. A small factual/link correction
needs only a proportionate edit and validation.

## Establish purpose and authority

Identify the reader's question: choosing a model, printing/using an object,
understanding an improvement, reproducing an investigation, operating an API,
or following agent instructions. Write the entry point for that question.
Inspect the current authoritative record and relevant linked evidence before
summarizing. For consequential rewrites, retain a baseline revision and a working
inventory of decisions, results, limitations and incoming links; this can be
temporary, not another permanent report.

[AGENTS.md](../../../AGENTS.md) owns repository rules. Object records own intent,
physical observations and current decisions; skills own methodology; implementation
documentation owns command/API contracts. [Engineering reflection](../engineering-reflection/SKILL.md)
decides what was learned, whether it transfers and where it belongs. This skill
owns its communication, not that engineering judgment. Link the responsible
owner rather than copy its procedure or establish a competing record.

## Explain the change in terms of its consequence

Start with what the object does or what the reader can now do. For a meaningful
improvement, explain the previous problem or uncertainty, the actual change,
why it was chosen, its consequence, supporting evidence and remaining limits.
Then state the next authorized action, including “none”, a user-deferred fix or
a discontinued investigation when applicable. These are writing questions, not
seven mandatory headings or a required engineering sequence.

For example, explain that a contact simulation formerly held the mating housing
rigid, why housing compliance could affect the lock assessment, and what allowing
both parts to deform changed. Then identify the API/fixture and scoped benchmark;
do not introduce only an unexplained feature name. Keep numerical assumptions,
acceptance thresholds and physical unknowns beside the conclusion they qualify.
Use short tables for genuinely comparable facts; keep investigation narratives
in paragraphs with navigable headings rather than enormous table cells.

## Organize by responsibility and reading depth

- **Current understanding:** the README or existing authoritative current record
  explains purpose, accepted/proposed design, improvements, evidence, unresolved
  issues, next authorized action, deliverables and print/use instructions. Separate
  independent workstreams; one accepted baseline does not make a deferred or failed
  experiment successful. Keep applicable print status and provenance easy to find.
- **Detailed investigation:** use existing object-owned notes/history for extended
  comparisons, calculations, failed attempts, numerical diagnosis and decision
  history. Create a new note only for a distinct purpose that improves navigation.
  Give it a useful title, scope, reading routes and a link to the current record.
  Keep detail near the decision/operation when relocation would harm understanding.
- **Reproducible evidence:** retain fixtures, source, native/structured reports,
  identities, settings and commands in their established locations. Link them from
  the explanation rather than copying their contents into multiple summaries.

Agents are explicitly permitted and encouraged to write extensive meaningful
engineering records whenever useful. There is no arbitrary length limit. Preserve
negative results, rejected alternatives, failed experiments, uncertainty and
unresolved investigations, not just successes. Clear scope and navigation matter
more than word count. Do not mechanically split long files or impose a template
on already readable small records.

## Update without rewriting history into instructions

Revise the current conclusion when evidence changes. Preserve consequential old
reasoning and observations in their owning record, labeling superseded proposals
and old next-step recommendations by phase. Distinguish accepted user decisions
from agent proposals, scope directives from verification results, and observations
from suspected causes. Historical environment versions and test counts describe
retained work; current runtime requirements come from implementation/lockfiles.
Preserve historical attribution and third-party licensing.

Retain requirement IDs, user provenance and explicit criteria, evidence scopes
and verification contracts. A documentation rewrite does not authorize changing
protected snapshots, thresholds, product decisions or code. Keep PASS, FAIL,
UNKNOWN, INCONCLUSIVE and N/A distinct. A CAD or slice pass is not physical
validation; convergence is not engineering acceptance. Old successful interfaces
cannot qualify new variants by association. Do not reactivate abandoned work.

State shared assumptions/instructions once. Replace duplicate explanations with
links, retaining unique facts and useful context. After relocation, repair relative
paths, internal links and incoming references; retain compatibility anchors when
structured provenance or external references depend on them. Do not rewrite
historical evidence artifacts merely to repair a prose navigation path.

## Validate for readers and meaning

Walk through the edited entry point as a new reader: identify the goal, current
state, why a meaningful change happened, what its evidence establishes, remaining
unknowns and what action is authorized. Follow the evidence route and check that
it explains rather than just relocates complexity. Compare consequential claims
and relocated content with the baseline; investigate missing numbers, decisions,
limitations, failed attempts and attribution. Check changed links/anchors and
incoming links, and verify altered command/API wording against its actual owner.

Validate only the authorized scope. Documentation-only edits need documentation
checks, not fresh CAD, solvers, slices or performance studies. Ordinary updates
need no additional checklist, report, audit, score or independent agent review;
use independent review when requested or justified by the task. Follow the existing
Git/handoff rules and report actual verification and remaining limitations.
