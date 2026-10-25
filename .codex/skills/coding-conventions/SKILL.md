---
name: coding-conventions
description: Implement or review repository Python code and engineering interfaces with explicit intent, shared command contracts, controlled side effects and scoped evidence. Use before interface decisions and during code review; improve the convention when a concrete coding failure exposes a gap.
---

# Coding conventions

Apply these conventions to implementation and review. The user's task determines
the mode and authorizes changes; this skill adds no permission to redesign a
product or edit files during an explicitly read-only review. [AGENTS.md](../../../AGENTS.md)
owns repository workflow. Engineering criteria and physical observations remain
object-owned; this is not a geometry style guide or a new verification framework.

## Make consequential choices explicit

Inspect the actual callers and owning records before choosing an interface.
A default is consequential when omission changes which design, material, evidence
category, acceptance criterion or publication action the caller receives.

- Require named variants/candidate builders. Reject unknown
  selections before building or writing; an `else` branch must not map a typo to a
  valid design. A fixed-purpose entry point can pass its named design explicitly.
- Declare evidence categories explicitly in records. A generic `Question` needs
  its category supplied; a fixed-purpose strain check declares its own analytical
  scope. Do not add a category argument with only one possible value.
- Require acceptance limits and comparison tolerances, and retain the applied
  values beside the result. Numerical stability, provisional design screens and
  physical qualification remain different claims. Do not choose a threshold just
  because the current candidate passes it.
- Require materials for deformable bodies, including mates made of the same
  material. A rigid proxy's material is irrelevant to its prescribed mechanics;
  do not demand unnecessary inputs for that branch.
- A conditional input may use `None` for absence, but the applicable operation must
  reject absence before computation. For example, description-only manufacturing
  assumptions need no coverage threshold; actual path acceptance does.
- Keep routine operational defaults when they preserve the engineering question,
  are bounded by the owning contract, and are visible where consequential. Render
  resolution, running all declared checks, algorithm controls and identity-checked
  reuse do not need to become compulsory arguments merely for uniformity.

Runtime deadlines implement explicit user requests only. Otherwise propagate
`None`; do not invent seconds based on expected cost, solver difficulty or a
precaution. Connection, service retirement and cleanup allowances have separate
lifecycle meanings under [execution](../../../execution/README.md).

Validate configuration names and types at their boundary. Avoid permissive
`**kwargs`, global overrides, truthiness fallbacks or missing-field defaults that
silently discard a requested choice. Missing attempted evidence must not become
zero, success or a plausible physical fact. Follow the owning result API for
FAIL, UNKNOWN and INCONCLUSIVE; programming/configuration errors fail clearly.

## Use shared boundaries and control side effects

Use the existing common adapter rather than inventing per-product flags, output
formats, schedulers or caches. Every adopted product verification entry point
must follow [the shared command contract](../../../product_verification/README.md#running-during-iteration):
explicit variant selection, declared check IDs, JSON stdout for results and handled
errors, stderr diagnostics, and 0/1 command exit codes. Completed reports exit 0
even with FAIL, UNKNOWN or INCONCLUSIVE evidence; command failures exit 1. Read
JSON for engineering outcomes and failure reasons.
Other established tools retain their owning execution contracts; changing one is
an explicit compatibility change, not a local workaround.

Add a command option only when an actual caller needs to choose its behavior.
Expose declared choices through the shared helper; do not make agents guess names.
Focused checks may save computation but must leave omitted coverage visible.
Diagnostic slice profiles must be identified as diagnostic. Supplied printer,
process and filament profiles form one explicit setup; do not fill a partial setup
with unrelated reference defaults. A slice receipt is not print qualification.

A mesh hash matching its slice receipt only associates those two artifacts.
Before reporting manufacturing evidence for a revised candidate, also establish
that its paired exports came from the current builders using the owning native
publication/source-association guards. Otherwise an unchanged old mesh and old
receipt can falsely pass after a model edit. The [M1 revision](../../../model/dental_travel_case/notes/m1.md#verification)
uses a conservative association in its existing verification inventory.

Geometry construction and inspection must not implicitly export, overwrite notes
or publish artifacts. Use the explicit evaluator/export boundary. Obtain paths
from supplied source context or an explicit argument; do not guess another checkout
using an author's hardcoded home directory. Retain nuanced Markdown observations
and historical numerical records; changed interfaces do not authorize rewriting
them into current success.
Validate managed outputs against source and declared file/directory inputs before
publication, including dynamically discovered image names and report paths; a
successful computation must not overwrite the input that identified it.

Reusable visual recipes use [cad_inspection](../../../cad_inspection/README.md)
and the evaluator's managed boundary. Keep anchors/criteria object-owned, names
explicit and factories lazy. Share current configurations/native check answers
rather than duplicating transforms or labeling new geometry with old results.
Display cuts never feed engineering assertions. Camera, frame, section, component
selection, annotations and diagnostics affect image identity; add no separate
cache or implied product PASS from image generation.
For checked-pose replay, preserve every unselected component's world placement,
including descendants of a moving geometry-bearing node. Adopt prescribed display
poses separately from the source's solved constraint declarations; do not imply
that replay re-solved or still satisfies those constraints.

When adding optional fields to identity-bound requests, normalize historical
omission to the precisely equivalent unset value at the comparison boundary.
Keep explicit values in the identity and test legacy reuse plus rejection of
changed settings. Optional curvature controls once broke retained question
evidence because old parts omitted the two fields that new requests wrote as
`None`; compatibility belongs in canonicalization, without rewriting archives
or ignoring the new settings. The [retained-evidence contract](../../../physical_analysis/README.md#standard-question-studies-and-retained-evidence)
owns that normalization. Required physical inputs must still be present.

## Implement and qualify

Trace affected callers and update them together. When removing a consequential
default, initially pass the previous value explicitly so changing the interface
does not silently retune the criterion. Keep object choices local and compose
existing checks; shared abstractions must earn their maintenance cost.

Test behavior that could defeat the guard: omitted/invalid selection, missing
criterion, partial configuration, unrequested writes, or a calculation that cannot
support its claim. Test the real entry boundary as well as the helper. Preserve
accepted geometry/artifacts and scoped evidence; document a reviewed source
association when a harmless refactor changes a fingerprint. Never update hashes
alone to make an unrelated design inherit physical success. Run affected checks;
do not launch slices or solvers just for an instruction or interface refactor.

Derive geometry selections from the selected variant's dimensions and verify
that they cover the intended feature. A nonempty partial selection can silently
renormalize a total force over the wrong area while the solve converges. The
[dental retention review](../../../model/dental_travel_case/notes/m2.md#consistent-comparisons-and-numerical-limits)
caught an old 8 mm selector on a widened 9 mm catch; actual native load area and
whole-land CAD coverage exposed the defect. Test that coverage when dimensions
or selection logic change, rather than asserting only that some faces exist.

Qualify output readers against actual producer output, including valid numeric
shorthand. The [dental liner review](../../../model/dental_travel_case_liner/README.md#toolpath-reader-correction)
encountered Orca extrusion tokens such as `E.89832`; a leading-digit-only reader
silently collected no bridge heights. Prefer the owning parser where it covers
the field, and distinguish missing parsed evidence from a failed engineering
criterion. Do not diagnose excessive bridge height from an empty collection.

For geometric output readers, use consistent bounded roundoff tolerances at
transformed boundaries. Test a nominally tangent feature and a real separated
negative control; do not widen an engineering acceptance limit to conceal a
reader error. The [B08 support review](../../../model/tpu_damping_box/README.md#four-printable-support-pairs--2026-10-20)
found strict capsule bounds rejecting a path after a roughly 1e-14 mm coordinate
roundoff; the shared reader's 1e-10 mm numerical tolerance remains distinct from
the object's printed-feature assumptions.

## Review from code and intent

Inspect the diff, current code, callers and original user intent. Passing tests or
compliant prose are supporting evidence, not substitutes for reading the code.
Check bypass entry points, fallback branches, writes during imports, omitted
acceptance fields and retained-evidence scope. Consider whether deleting a shortcut
or unnecessary abstraction would make future mistakes harder.

Report actionable findings with file/line, trigger, consequence and the smallest
correction. Distinguish demonstrated behavior from a prospective risk, operational
defaults from engineering assumptions, and in-scope defects from unrelated legacy
work. Review-only tasks report code fixes; implement them only when authorized.

## Improve this convention autonomously

When implementation or review exposes a concrete failure that this guidance missed,
correct the relevant rule or example autonomously within the task's authorization.
This includes skill maintenance during review unless the user explicitly forbids
edits. An explicitly read-only task reports the proposed update instead.

Base each update on an observed trigger and consequence, preserving user intent
and existing authority. Prefer a narrow correction over a growing list of rules;
remove obsolete or duplicated guidance. Do not weaken a rule to excuse a failing
implementation, turn an agent assumption into a user requirement, or use skill
maintenance to expand the product task. Link existing evidence when useful, validate
the skill and relevant behavior, and disclose the useful change in the handoff.
