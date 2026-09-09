---
name: prusa-slicer-printability
description: Investigate FDM printability with PrusaSlicer CLI, layer paths and controlled comparisons. Use for orientation, overhang, bridge, support or moving-part slicing concerns. Automatically maintained notebook; inspection does not authorize redesign or printing.
---

# PrusaSlicer printability inspection

Connect evidence to a specific manufacturing/toolpath question. A valid solid, successful
slice or absence of warnings does not prove that a physical print will succeed.

## Investigation workflow

1. Establish the question and reuse confirmed printer, material, orientation,
   assembly and support preferences. Label diagnostic defaults.
2. Choose a supplied or documented profile. Preserve print-in-place positions;
   do not silently split, arrange, rotate, scale, repair or union the input.
3. Use the [review helper](references/review-tool.md) for a reproducible slice,
   or the [CLI notebook](references/cli-and-paths.md) for an investigation it
   does not cover. Confirm fresh nonempty output, not only a zero exit code.
4. Inspect the summary first; inspect relevant current/preceding layers when a
   specific uncertainty, warning or fit-critical feature requires it. Target bridge anchors,
   fit-critical surfaces, moving gaps and actual deposited footprint including
   brims. Roles and segment lengths alone do not establish unsupported spans.
5. Report facts, geometric interpretation and remaining physical uncertainty
   separately. Stop when the question is answered. Inspection-only requests do
   not authorize redesign, deployment, print tuning outside scope, or printing.

A known defect on a critical mating surface should inform an authorized redesign,
not merely recur in another trial with a disclaimer. For CAD decisions or
physical experiments, use [CAD design](../cadquery-3d-design/SKILL.md), including
the required CadQuery MCP workflow.

## Read selectively

Use one slice for each changed set of relevant inputs, following AGENTS.md's
evidence reuse rules. Detailed layer diagrams are conditional, not routine
deliverables. Select the layer window from the unresolved feature/question; do
not inspect arbitrary layers for reassurance after that question is answered.
For another window on the same slice, use `inspect_gcode.py` on
saved G-code rather than rerunning PrusaSlicer. The review wrapper orchestrates
the slicer; the parser inspects its output. Neither is another slicer or physical
simulation. The wrapper has no automatic cache: compare recorded inputs before
reusing evidence, and use a fresh output directory when a new slice is needed.

- [Review helper](references/review-tool.md): standard slice reports and windows.
- [CLI and path interpretation](references/cli-and-paths.md): configuration,
  parser limits, manual commands and interpreting layer-window SVGs.
- [Case lessons](references/case-lessons.md): warnings, internal infill, anchors,
  droop despite clean slices, mesh defects, brim bounds and layer registration.
- [Notebook index](references/notebook.md): entry point for maintained findings.

## Automatically maintain this notebook

Update missing useful techniques during the investigation without waiting for
another request. Correct disproven advice; consolidate rather than append session
transcripts. Record the purpose, minimal reproduction, tested version,
profile/orientation assumptions, observation and limits. Keep raw evidence with
the object and link it here. Label untested ideas; do not generalize one printer's
clearance or bridge result into a universal rule.

Run new/changed helpers and validate changed skills before handoff. Mention
material additions. If maintenance is prohibited or unavailable, report that
limitation rather than claiming an update. This requirement does not expand
authorization to redesign or print.

## Evidence

Save the profile or exact profile reference, input hashes, command/version,
warnings, estimates and useful layer views inside the object's directory.
Keep raw G-code/logs out of commits unless they add necessary evidence. A generic
diagnostic G-code file is not a validated printer job. No automated free-air span,
anchor, sag, stress or pass/fail printability classifier is supplied.
