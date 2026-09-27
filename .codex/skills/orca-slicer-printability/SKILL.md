---
name: orca-slicer-printability
description: Run an OrcaSlicer reference-profile smoke slice and review slicer-generated path summaries with the CLI. Results describe the selected profile only; inspection does not authorize redesign or printing.
---

# OrcaSlicer printability inspection

## Scope and when to use

Generic FDM review starts with [CAD/print planning](../cadquery-3d-design/references/print-planning.md).
Use geometry for support at bridge ends, projections, walls, gaps and
orientation. Use a slicer for its generated manufacturing paths; do not
recreate its planning algorithms. These are evidence choices, not software
modes:

- **Generic FDM:** the user's final profile is unknown; CAD/math and
  manufacturing assumptions provide the primary design review.
- **Reference OrcaSlicer:** a documented diagnostic profile provides a final
  exported-artifact smoke check or answers a specific path question.
- **Actual profile:** use the supplied actual OrcaSlicer settings when
  available for toolpath claims. These supersede generic reference settings.
  Do not silently translate another slicer's profile into OrcaSlicer or add
  more reference slicers.

A reference result means OrcaSlicer produced these paths under this profile.
It does not establish the user's temperatures, flow, supports, dimensional
accuracy, bridge quality, physical clearance, strength or tactile behavior.
Actual-profile paths are still toolpath intentions, not physical measurements.

## Smoke check and conditional investigation

1. Establish purpose: final mesh smoke slice, or a named unresolved path
   question. Reuse confirmed printer, material, orientation, assembly and
   support preferences; label unknown settings as diagnostic assumptions.
2. Choose supplied profiles or the maintained Qidi Q2C 0.4 mm / Generic PETG /
   0.20 mm Standard / 7% adaptive cubic reference set. See
   [CLI and profile setup](references/cli-and-paths.md). The default review
   envelope is 260 × 260 × 250 mm; use the user's safe limits when supplied.
   The Q2C system preset itself reports a 270 × 270 × 256 mm printable volume.
3. Use the [review helper](references/review-tool.md), or the CLI notebook when
   the helper is unsuitable. Use a fresh output directory. The helper records
   its placement choice, uses Orca's effective-settings export, checks
   `result.json`, requires fresh nonempty G-code, and parses deposited paths.
   This checks export-to-toolpath acceptance, not model function.
4. Read notices, effective profiles, actual deposited footprint/height and
   support count. Resolve relevant notices from structured slice results.
   For multiple plates, evaluate bounds separately. Resolve dimensions, gaps
   and clearances from CAD; this check reports Orca's generated paths, not
   physical fit. Roles and segment lengths alone do not establish anchors or
   unsupported spans.
5. Report the scoped result and remaining physical uncertainty; stop when the
   question is answered. Inspection-only requests do not authorize redesign,
   deployment, print tuning outside scope, or printing.

The helper's default `center` placement arranges the loaded layout onto the
plate without rotating objects. For a single STL this relocates that one mesh
as a whole and preserves its internal component positions. For a project with
several independent objects, use `--placement preserve` when its placement is
already valid, or `--placement assembly` when explicitly grouping the project
onto one plate is acceptable. Record the choice. Do not silently split, rotate,
scale, repair or union input geometry. See the [placement notes](references/review-tool.md#placement).

A known defect on a critical mating surface should inform an authorized
redesign, not merely recur in another trial with a disclaimer. For CAD decisions
or physical experiments, use [CAD design](../cadquery-3d-design/SKILL.md),
including the shared CadQuery command workflow.

## Read selectively

Use one slice for each changed set of relevant inputs, following AGENTS.md's
evidence reuse rules. The review wrapper orchestrates OrcaSlicer; the parser
produces structured summaries from its output. Neither is another slicer or
physical simulation. The wrapper has no automatic cache: compare recorded
inputs before reusing evidence, and use a fresh output directory when a new
slice is needed.

- [Review helper](references/review-tool.md): reproducible CLI slice, notices,
  effective settings, deposited bounds and per-layer path summaries.
- [CLI and path interpretation](references/cli-and-paths.md): Flatpak launch,
  profile inheritance, parser limits and manual commands.
- [Case lessons](references/case-lessons.md): retained observations from prior
  slicer investigations, with their original slicer/version and limits.
- [Notebook index](references/notebook.md): maintained findings.

## Automatically maintain this notebook

Update missing useful techniques during the investigation without waiting for
another request. Correct disproven advice; consolidate rather than append
session transcripts. Record the purpose, minimal reproduction, tested version,
profile/orientation assumptions, observation and limits. Keep raw evidence with
the object and link it here. Label untested ideas; do not generalize one
printer's clearance or bridge result into a universal rule. Ask whether a
recurring failure can be recognized earlier from CAD geometry, and capture that
geometric lesson in print planning or the relevant case lesson instead of
repeating screenshots.

Run new/changed helpers and validate changed skills before handoff. Mention
material additions. If maintenance is prohibited or unavailable, report that
limitation rather than claiming an update. This requirement does not expand
authorization to redesign or print.

## Evidence

Save the exact profile files or their repository paths, model path, CLI command,
effective settings, `result.json`, warnings, estimates and any useful layer
views inside the object's directory. Label purpose (smoke/investigation) and
profile scope (reference/actual) in the concise evidence record. Report smoke
acceptance separately from notices or unresolved manufacturing questions.
Keep raw G-code and slicer logs out of commits unless they add necessary
evidence. The helper ignores them by default. A generic diagnostic G-code file
is not a validated printer job. No automated free-air span, anchor, sag, stress
or pass/fail printability classifier is supplied.
