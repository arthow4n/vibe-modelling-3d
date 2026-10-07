---
name: engineering-reflection
description: Reflect on modelling and engineering work, print feedback, or repeated effort in this repository; carry evidence-backed lessons, preferences and useful automation into the owning records, skills or shared tools. Use at a phase handoff, on a print report, or when the user asks for reflection or workflow improvement.
---

# Engineering reflection

Turn recent evidence into a smaller, more reliable next workflow. This skill
owns the reflection checkpoint; existing design skills and repository rules
own the engineering requirements. Apply it within the current task and user
authorization, including any pause or prohibition on file edits or commands.
Reflection does not authorize another product variant or print experiment.

## Choose the scope

- At a modelling-phase handoff, briefly review new decisions, surprises and
  repeated work before committing. A rough-study or sample handoff counts; do
  not wait for a final product. Review only the completed phase.
- On a print report, first update the object's print-status record and root
  index using the [physical-feedback rules](../cadquery-3d-design/references/physical-experiments.md#learning-from-trial-prints).
  If rejected, correct readiness/conclusions through the
  [failure guidance](../cadquery-3d-design/references/physical-experiments.md#when-product-use-fails).
  Then reflect on what the new observation changes. A preference or failure
  reported before printing remains that kind of evidence.
- On an explicit reflection request, review the requested session, object or
  workflow more broadly, including simplification and shared-code opportunities.

Reuse the conversation, current object record, changed source and existing
evidence. Inspect relevant shared instructions and consumers before proposing
changes; avoid a repository-wide audit for a local handoff. Do not repeat a
reflection on unchanged evidence or rerun CAD, slices or solvers just to reflect.
Use [workflow performance analysis](../workflow-performance-analysis/SKILL.md)
when repeated agent effort, tool usage or time/token consumption needs measurement.
For modelling-effort investigations, reflection establishes the milestone and
necessary engineering evidence; activity counts alone cannot decide that work
was wasteful. The performance skill owns per-object attribution and publication
requirements. Ordinary handoffs need no performance report.
Use [engineering execution](../engineering-execution/SKILL.md) for computational
profiling, benchmarks or recovery; reflection still owns lesson placement.

## Identify what should change

Look across function and handling, reference fidelity, manufacturing, physical
feedback, user preferences, evidence quality, agent effort and tool reuse.
For a candidate improvement, establish:

1. **Evidence and consequence:** what happened, under which known inputs, and
   what decision, misleading claim, wasted print or repeated work it exposed.
   Separate observation from interpretation; leave unknown causes/settings
   unknown. Include successful reusable interfaces as well as failures.
2. **Prevention or reuse:** the earliest useful decision/check that could have
   changed the outcome, or the concrete operation worth sharing. A check needs
   an expected result and an action that changes with it. It must represent the
   intended source item and use, rather than reproduce the design's assumptions.
3. **Existing coverage:** was guidance missing, ambiguous, hard to discover,
   already adequate but not applied, or was a tool contract insufficient?
   Strengthen routing or the concrete check when guidance already exists;
   do not append another copy of the same warning.
4. **Transfer and cost:** which other contexts benefit, what stays local, and
   whether the improvement reduces total work without losing required evidence.
   One demonstrated consumer can justify shared functionality; hypothetical
   future usefulness alone cannot. Removing redundant work is a valid result.

Challenge the mechanism itself before tuning its defaults. If measurements show
cost without a demonstrated benefit for the consumer, compare removing it with
keeping it; existing code and hypothetical usefulness are not reasons to retain
it. State which requirement still needs protection and use the smallest existing
control that satisfies it. When evidence or user feedback overturns a conclusion,
revise the recommendation and implement the authorized simplification instead of
repeating the earlier defense. Keep the limits of the evidence explicit; this
does not require proving a mechanism is useless in every conceivable workload.
Do not replace a removed control with a renamed or more complex equivalent
without a demonstrated consumer requirement and benefit.

An unexplained physical result can still justify a corrected status or bounded
lesson. It does not justify an invented root cause, material calibration or
universal tolerance. A working coupon qualifies its tested interface, not the
complete product. Avoid converting a one-off idea into a standing preference.

## Put the result in its owning source

| Result | Owner and action |
| --- | --- |
| Dimensions, matching variants, uncertain causes, exact checks or print observations | Update the object's existing decision/evidence record and affected root-index summary. Keep fixtures and acceptance criteria with the object. |
| Explicit or repeated user preference | Update [user preferences](../cadquery-3d-design/references/user-preferences.md#updating-this-record) with scope and linked evidence; retain project-specific requirements locally. |
| Transferable design success/failure | Add or revise a concise [reusable-evidence entry](../cadquery-3d-design/references/reusable-model-lessons.md), linking the detailed object record and naming transfer limits. |
| Missing design decision or workflow instruction | Edit the responsible skill/reference, or [AGENTS.md](../../../AGENTS.md) for repository workflow. Link the owner rather than repeat its procedure in several places. |
| Coding/interface failure or review gap | Improve [coding conventions](../coding-conventions/SKILL.md#improve-this-convention-autonomously) using the observed trigger and consequence; keep product facts and tool contracts with their owners. |
| Repeated code or a concrete API gap | Improve the existing shared script/API under the extension rules below. Share the general operation; retain object-specific geometry, material assumptions and pass/fail thresholds locally. |

Before extracting code, identify its actual caller and current shared API.
Try the existing API first when it covers the question; failure to use it is
not a reason to build another abstraction. Repeated builders/checks for variants
of one object normally belong in an object-owned helper. Shared parsing,
execution or numerical operations can belong in the existing repository API.
Prefer deleting duplication or extending a current abstraction over a new
framework. Do not add a reflection script to manufacture lessons or automate
engineering judgment.

For a consequential API gap, record the missing operation, motivating consumer,
decision and smallest reusable extension in the existing decision record. Use the
current API first when adequate; an object-specific workaround can establish the
fixture, then revisit whether reusable behavior belongs in the shared question or
study API before handoff. Implement justified in-scope improvements now. If that
cannot be completed, name the specific blocker, scope boundary or insufficient
benefit and the remaining unsupported capability; do not silently defer it.
One demonstrated consumer is enough; no second consumer or routine API audit is
required. Seek a decision if the change materially alters the agreed scope.

Qualify an extension on its motivating consumer, with appropriate regression or
numerical benchmarks, and document its contract and limits beside implementation.
Record what it changed: a decision, misleading result caught or repeated work
avoided. Keep experimental routes optional until benefit is demonstrated; useful
failed experiments can remain evidence without a permanent public feature.

Make worthwhile, authorized changes now. Keep unqualified future explorations
as brief ideas in the existing object record when useful; do not implement them
as part of reflection. If editing is prohibited, retain notes in the conversation
and distinguish them from saved changes. No worthwhile delta means no file edit,
extra report, placeholder TODO or new requirement.

## Validate and hand off

Validate only the change made: document links and consistency for instructions;
the skill-creator validator for a new or substantially changed skill; meaningful
consumer/regression checks for shared code. Numerical extensions need appropriate
benchmarks. Exercise extracted code on the motivating consumer and record what
decision changed or repeated work disappeared; do not claim benefit merely
because code moved. Revisit affected CAD/exports/slices only if their inputs changed.

Use the repository's normal review, commit and push workflow. In the ordinary
handoff, briefly state the useful lesson, what changed and where, verification,
and any retained uncertainty or deliberately local work. When no shared change
is justified, say so if the user asked. Keep one current record instead of a
separate reflection log, scoring system or duplicate completed checklist.
