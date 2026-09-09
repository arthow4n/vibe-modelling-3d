---
name: prusa-slicer-printability
description: Run a final exported-mesh smoke slice or investigate slicer-sensitive FDM toolpaths with PrusaSlicer CLI and targeted layer paths. Results are reference-profile evidence unless actual user settings are supplied. Inspection does not authorize redesign or printing.
---

# PrusaSlicer printability inspection

## Scope and when to use

Generic FDM review starts with [CAD/print planning](../cadquery-3d-design/references/print-planning.md).
Use geometry for support at bridge ends, projections, walls, gaps and orientation.
Use a slicer for its generated manufacturing paths; do not recreate its planning
algorithms. These are evidence choices, not software modes:

- **Generic FDM:** user's final profile unknown; CAD/math and manufacturing
  assumptions provide the primary design review.
- **Reference slicer:** repository PrusaSlicer plus a documented diagnostic profile
  provides a final exported-artifact smoke check or answers a specific path question.
- **Actual profile:** use the supplied actual slicer/settings when available for
  toolpath claims; these supersede generic reference settings. Do not silently
  translate another slicer's profile into PrusaSlicer or add more reference slicers.

A reference result means this slicer produced these paths under this profile.
It does not establish the user's supports/extrusions, dimensional accuracy,
bridge quality, physical clearance, strength or tactile behavior. Actual-profile
paths are still intentions, not physical measurements.

## Smoke check and conditional investigation

1. Establish purpose: final mesh smoke check, or a named unresolved path question.
   Reuse confirmed printer, material, orientation, assembly and support preferences;
   label unknown settings as diagnostic assumptions.
2. Choose a supplied or documented profile. Preserve relative component positions
   and intended orientation; do not silently split, arrange, rotate, scale, repair
   or union the input. Record the helper's whole-layout bed centering.
3. Use the [review helper](references/review-tool.md) without `--windows` for the
   final smoke slice, or the [CLI notebook](references/cli-and-paths.md) where the
   helper is unsuitable. Check successful slicing and fresh nonempty deposited
   toolpaths. Read the compact summary for notices, footprint/height, supports and
   surprising treatment; resolve relevant notices without automatically escalating
   to images. This establishes export-to-toolpath acceptance only.
4. Go beyond smoke only when a material uncertainty depends on generated paths:
   near-width-limit features, disappearing walls, variable-width perimeters,
   bridge classification, support contact, close moving gaps, layer discretization
   or first-layer/brim interactions. Inspect structured facts first. Request a
   targeted current/preceding-layer window only if those facts cannot answer the
   question and spatial path topology is easier to understand visually. Roles and
   segment lengths alone do not establish anchors or unsupported spans.
5. Report the scoped result and remaining physical uncertainty; stop when answered.
   Inspection-only requests do not authorize redesign, deployment, print tuning
   outside scope, or printing.

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
clearance or bridge result into a universal rule. Ask whether a recurring failure
can be recognized earlier from CAD geometry, and capture that geometric lesson
in print planning or the relevant case lesson instead of repeating screenshots.

Run new/changed helpers and validate changed skills before handoff. Mention
material additions. If maintenance is prohibited or unavailable, report that
limitation rather than claiming an update. This requirement does not expand
authorization to redesign or print.

## Evidence

Save the profile or exact profile reference, input hashes, command/version,
warnings, estimates and any necessary layer views inside the object's directory.
Label the purpose (smoke/investigation) and profile scope (reference/actual) in
the concise evidence record; report smoke acceptance separately from notices or
unresolved manufacturing questions. See the helper reference for available fields.
Keep raw G-code/logs out of commits unless they add necessary evidence. A generic
diagnostic G-code file is not a validated printer job. No automated free-air span,
anchor, sag, stress or pass/fail printability classifier is supplied.
