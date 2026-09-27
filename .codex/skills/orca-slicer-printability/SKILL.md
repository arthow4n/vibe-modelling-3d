---
name: orca-slicer-printability
description: Run an OrcaSlicer reference-profile smoke slice and review slicer-generated path summaries with the CLI. Results describe the selected profile only; inspection does not authorize redesign or printing.
---

# OrcaSlicer printability inspection

## Scope

Generic FDM review starts with [CAD/print planning](../cadquery-3d-design/references/print-planning.md).
Use CAD geometry for support at bridge ends, projections, walls, gaps and
orientation. Use a slicer for paths Orca actually generated; do not recreate its
planning algorithms. A successful slice says Orca produced paths under the
selected profiles. It does not establish temperatures, flow, supports,
dimensional accuracy, bridge quality, physical clearance, strength or tactile
behavior. Toolpath intentions are not physical measurements.

This skill does not request layer-window checks or generate layer images.
Resolve geometry questions in CAD; use the path summary only for a remaining
question about Orca's generated paths. It supports smoke review and aggregate
path summaries, not a detailed local path investigation across selected layers.

Use the maintained Qidi Q2C 0.4 mm / Generic PETG / 0.20 mm Standard / 7%
adaptive cubic profile set by default. Use supplied Orca profiles when a review
needs the user's actual settings; do not silently translate another slicer's
profile into OrcaSlicer or add more reference slicers. See
[CLI and profile setup](references/cli-and-paths.md).

For the final smoke review, slice the final exported STL or 3MF. Reuse an
existing result only when its model, profiles, placement and slicer version
still match; follow the evidence reuse rules in [AGENTS.md](../../../AGENTS.md).

## Unified review command

From the repository root, run
`.codex/skills/orca-slicer-printability/scripts/review_print.py`. It infers the
Orca command, loads profiles, slices the model, reads effective settings,
summarizes deposited paths and prints one JSON report to stdout. G-code, logs
and intermediate files live in a temporary directory and are removed when the
command exits. Use `--keep-run` only when raw diagnostics are needed; its JSON
report includes the retained directory. The parser is an internal module, not a
separate command.

The CLI help and this table are the interface contract. Keep option names and
defaults synchronized:

| Argument | Default | Meaning |
| --- | --- | --- |
| `--model PATH` | Required | STL or 3MF to slice. |
| `--printer PATH` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json` | Printer and machine dimensions. |
| `--process PATH` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json` | 0.20 mm Standard, 7% adaptive cubic sparse infill. |
| `--filament PATH` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json` | Generic PETG. |
| `--placement {preserve,center,assembly}` | `center` | Centering mode; rotation and auto-orientation stay disabled. |
| `--expect-no-supports` | Off (`false`) | Request review if Orca generates support paths. |
| `--keep-run` | Off (`false`) | Preserve temporary G-code and diagnostics. |

There is no separate `--bed`: bounds come from Orca's effective printer
`printable_area` and `printable_height`. Qidi Q2C defaults to the manufacturer's
**270 × 270 × 256 mm** build volume
([Q2C specifications](https://us.qidi3d.com/products/q2c)). Supply a printer
profile with smaller limits when those are the appropriate usable dimensions.
The helper supports axis-aligned rectangular printable areas and stops with an
error for another shape rather than guessing. Slicer selection is inferred in
this order: `ORCASLICER_COMMAND`, host `orca-slicer`, Flatpak OrcaSlicer.

The default `center` placement uses `--arrange 1 --orient 0
--allow-rotations=0`. A single STL moves as one mesh and retains internal
component positions. For a project with independent objects, use `preserve` if
the existing placement is intentional, or `assembly` when grouping the objects
is acceptable. Record the selected placement in the object note. Do not
silently split, rotate, scale, repair or union input geometry.

## Review and evidence

Read effective profiles, Orca notices, per-plate bounds and support paths.
Bounds include half the reported line width, brim and generated support paths;
they exclude travel, start/end machine motion and physical flow spread. Support
counts are reported on every run. `--expect-no-supports` makes any generated
support path a review condition; it does not change support settings. For
multiple plates, evaluate bounds separately. Resolve dimensions, gaps and
clearance from CAD. Roles and segment lengths alone do not establish anchors or
unsupported spans.

The notice list combines structured per-plate warnings with keyword-filtered
log lines, so an empty list does not establish that the full slicer log is
message-free. Use `--keep-run` if the complete log needs review. The helper does
not assess whether Orca repaired a mesh or whether every intended component was
retained.

Exit 0 means no automated review condition was found. Exit 2 means Orca
reported a notice, paths extend beyond the selected printer volume, or the
optional no-support expectation was violated. Exit 1 means the review could not
complete. None of these statuses is a universal printability verdict.

Keep one concise object record with profile file paths, Orca version, model,
placement, effective settings, smoke-slice result, notices, per-plate footprint
and height, support presence, and physical limitations. Do not save temporary
report files by default. Keep raw evidence only when it answers a concrete
question. No automated free-air-span, anchor, sag, stress, support-removal
accessibility, mesh-repair assessment or physical printability classifier is
supplied.

## Related references

- [Review helper](references/review-tool.md): command, arguments and output.
- [CLI and path interpretation](references/cli-and-paths.md): Flatpak launch,
  profile inheritance and parser limits.
- [Case lessons](references/case-lessons.md): retained observations and limits.
- [Notebook index](references/notebook.md): maintained findings.

## Notebook maintenance

Correct disproven advice and consolidate useful techniques instead of appending
session transcripts. Record the tested slicer version, profile assumptions,
observation and limits. Label untested ideas. Do not generalize one
printer's clearance or bridge result into a universal rule. Capture reusable
geometric lessons in print planning or the relevant case lesson. Inspection
does not authorize redesign, deployment, print tuning outside scope or printing.
