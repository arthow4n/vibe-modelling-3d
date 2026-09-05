---
name: prusa-slicer-printability
description: Investigate FDM printability with the PrusaSlicer CLI, using slicer warnings, layer toolpaths and controlled comparisons to assess overhangs, bridges, supports and moving-part clearances. Use when inspecting a model's intended print orientation or diagnosing slicing concerns. Maintained automatically as a living notebook of verified investigation techniques; does not authorize redesign or printing.
---

# PrusaSlicer printability notebook

This skill is a **living investigation notebook**, not a finished manual or a
printability certification tool. Use it to connect slicer evidence to a specific
geometric concern. A valid CAD solid, successful slice, or absence of warnings
does not prove that a physical print will succeed.

Read [the investigation notebook](references/notebook.md) for tested commands,
observed CLI behavior, toolpath interpretation and known limitations. Consult
the installed CLI's help for version-specific options instead of assuming that
every historical command or profile still applies.

## Automatically maintain this skill

The agent is expected to maintain this skill **without waiting for a separate
user request**. Whenever an investigation reveals a useful way of using
PrusaSlicer to inspect printability that is missing here, update this skill or
its notebook during the same task, before handoff. Also correct existing advice
when new evidence disproves it. This maintenance is part of applying the skill,
not merely a suggestion to offer the user later.

- Add reusable, verified findings: commands, settings, warning behavior,
  extraction methods, useful comparisons, and failures that affect interpretation.
- For a new technique, record its purpose, minimal reproduction, tested version
  and relevant profile/orientation assumptions, observed result, and limitations.
  Link to supporting object artifacts when useful; keep raw object data there.
- Label untested ideas as hypotheses. Do not present a proposed parser, metric,
  visualization or CLI capability as implemented or verified until exercised.
- Edit or consolidate the relevant entry instead of appending repeated session
  transcripts. Keep this entry point short; extend the linked notebook or add
  a focused reference when a technique needs substantial detail.
- Do not generalize one printer, material, bridge length or user's preference
  into a universal rule. Preserve explicit scope limits and existing preferences.
- Validate changed instructions and run any new or modified helper scripts.
  Follow repository commit/push rules for relevant skill changes and briefly
  identify the learned technique in the handoff. If maintenance is explicitly
  prohibited or the skill is unavailable for writing, report that limitation
  instead of claiming it was updated.

## Investigate within the requested scope

1. Establish the question: for example, whether an overhead wall requires
   bridging, whether supports invade a captive joint, or whether a thin wall
   produces useful extrusion paths. Use the user's existing printer, material,
   orientation, assembly and support requirements. Ask only for missing inputs
   that materially affect the conclusion; label diagnostic defaults.
2. Locate PrusaSlicer and check its version/help. Use the supplied printable
   model as the baseline. Record the exact input, orientation and profile;
   preserve relative positions of print-in-place components. Do not silently
   split, arrange, rotate, scale, repair or union the model.
3. Slice with settings appropriate to that question. Capture stdout and stderr
   and confirm that a fresh, nonempty output was actually generated. Match the
   baseline to the user's support requirement. A supported comparison is only
   an investigation aid when useful within scope, never a substitute for meeting
   a no-support requirement.
4. Read warnings and inspect the relevant layer features, not just the process
   return code or final time estimate. Locate problematic paths by print height
   and relate them back to the model. Distinguish reported slicer facts, measured
   toolpath quantities, inferred printing risks and unverified physical behavior.
5. Stop once the requested question is answered with sufficient evidence.
   Inspection-only requests do not authorize geometry changes, print tuning
   beyond the investigation, deployment to a printer or physical printing.

Slicing supplements CAD evaluation. In this repository, actual CadQuery changes
still follow AGENTS.md and the CadQuery design skill, including evaluate_file.

## Evidence and handoff

Keep an object's diagnostic profile, commands, concise findings and useful
measurements or images inside `model/<object_name>/`, normally in a notes
subdirectory. Preserve reproducibility without committing huge G-code dumps,
redundant intermediate renders or raw logs that add no evidence. Account for
ignore rules when retaining a warning log; alternatively quote it in the report.

Report what was tested, the specific warning or geometric finding, its effect
on the user's requirement, and remaining uncertainty. Diagnostic G-code made
with generic motion/temperature settings is not a validated printer job. Include
physical testing only when it has actually happened. Before finishing, check
whether the investigation taught a missing technique and maintain this notebook.
