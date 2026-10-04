---
name: orca-slicer-printability
description: Run an OrcaSlicer smoke slice with an automatic-support probe and review its status, warnings and effective settings. Results describe the selected profile only; inspection does not authorize redesign or printing.
---

# OrcaSlicer printability inspection

## Scope

Start with [CAD/print planning](../cadquery-3d-design/references/print-planning.md).
Use CAD geometry to check support at bridge ends, projections, walls, gaps and
orientation. A reference slice says Orca completed a plate under the selected
profiles. It does not establish temperatures, flow, dimensional accuracy,
bridge quality, physical clearance, strength or tactile behavior.

This skill covers final-mesh smoke reviews and a narrow automatic-support probe
through the repository's shared evaluator.
Resolve geometry questions in CAD; inspect Orca's GUI preview when generated
support or a specific path could change the design.

Choose nozzle, layer height, material, walls and infill during the design
agreement, before CAD detail; see [AGENTS.md](../../../AGENTS.md). The user's
preferred starting point is the Qidi Q2C with a 0.4 mm nozzle and 0.2 mm
layers. A 0.8 mm nozzle and several PLA, PETG and TPU filaments are available.
Two walls with 7% adaptive cubic infill are the user's general experience for
ordinary prints, not a strength requirement. Explain and discuss consequential
changes to this starting approach before relying on them in the design.

The maintained Qidi Q2C 0.4 mm, Generic PETG, 0.20 mm Standard, two-wall,
7% adaptive cubic profiles are a diagnostic fallback, not the user's fixed
production setup. They are resolved OrcaSlicer 2.4.2 snapshots because the
headless CLI did not reliably apply inherited values from partial presets;
check effective settings rather than trusting preset names. Prefer compatible
supplied Orca profiles for the agreed nozzle, material and process. If the
fallback differs from the intended print, state the mismatch and limit
conclusions to diagnostic path acceptance; do not claim that its settings
predict the agreed print. A 0.8 mm or TPU design needs
an appropriate printer/process/filament profile for setup-specific path claims;
if none is available, record that evidence gap. Do not substitute the 0.4 mm
PETG profile silently. Do not translate another slicer's profile into Orca or
add more reference slicers. STEP is the user's primary print-ready interchange
file. The installed headless Orca CLI rejects STEP input, so for a final smoke
review slice the matching exported STL. This result does not verify Orca's GUI
STEP import; do not describe it as a STEP slice. The shared evaluator's STL
export uses Orca GUI's default STEP-import meshing settings (0.003 mm absolute
linear deflection, 0.5 rad angular deflection), but reimport and Open Cascade
version differences can still change the triangles. Use 3MF when it is the
agreed print file. Reuse a result only while its model, profiles, placement
and slicer identity still match. The evaluator verifies these identities and reuses
completed reviews automatically, marking `slice.reused`. Use `--fresh` for newly
executed slice evidence or `--slice-keep-run` for raw diagnostics. Version discovery
is cached by tool identity; the primary result can supply its own automatic-support
probe when its effective settings qualify. Shared resource budgets can overlap
independent slices without changing their evidence requirements. See
[shared execution](../../../execution/README.md).

## Run the review

For a normal final model, run this from the repository root:

```sh
./evaluate_model.py model/object_name/object_name.py --views none --slice
```

It exports the STEP/STL pair, reviews the STL with OrcaSlicer, and probes
automatic supports in the same call. Optional
`--slice-printer`, `--slice-process`
and `--slice-filament` accept compatible Orca JSON profiles; otherwise the
diagnostic defaults below apply. The evaluator returns the slice result in its
single JSON report. Use `--slice-existing` below only when reviewing an already
exported file without rebuilding the model.

The evaluator also accepts `--slice-placement` and `--slice-keep-run`
when needed. A completed slice that needs review exits 2 and reports
`slice.review_required=true`;
failure exits 1. Read stage status even if a view render failed.

For an agreed setup with different profiles, pass them in the same command:

```sh
./evaluate_model.py model/object_name/object_name.py --views none --slice \
  --slice-printer model/object_name/notes/printer.json \
  --slice-process model/object_name/notes/process.json \
  --slice-filament model/object_name/notes/filament.json
```

For an existing export, use the same command from the repository root. It
infers OrcaSlicer, loads profiles, slices the file, reads effective settings
and prints one JSON report to stdout. It never sends a printer job.

```sh
./evaluate_model.py --slice-existing model/object_name/object_name.stl
```

The CLI help and this table are the interface contract for slice options:

| Argument | Default | Meaning |
| --- | --- | --- |
| `--slice` | Off | Export the CAD result as STEP/STL and review its STL. |
| `--slice-existing STL_OR_3MF` | Off | Review an existing STL or 3MF without rebuilding CAD. |
| `--slice-printer PRINTER` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json` | Diagnostic 0.4 mm printer and machine dimensions. |
| `--slice-process PROCESS` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json` | Diagnostic 0.20 mm, two-wall, 7% adaptive cubic process. |
| `--slice-filament FILAMENT` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json` | Diagnostic Generic PETG. |
| `--slice-placement {preserve,center,assembly}` | `center` | Center the layout without rotation or auto-orientation. |
| `--slice-keep-run` | Off | Retain temporary G-code and diagnostics. |

To use the agreed setup with other Orca profiles, pass all three compatible
profile files:

```sh
./evaluate_model.py --slice-existing model/object_name/object_name.stl \
  --slice-printer model/object_name/notes/printer.json \
  --slice-process model/object_name/notes/process.json \
  --slice-filament model/object_name/notes/filament.json \
  --slice-placement preserve
```

The printer profile supplies Orca's machine bounds. There is no
separate bed-size argument; the effective settings report includes
`printable_area` and `printable_height`. The Qidi Q2C profile defines the
manufacturer's **270 × 270 × 256 mm** build volume
([Q2C specifications](https://us.qidi3d.com/products/q2c)). Use a printer
profile with smaller dimensions when those are the appropriate usable limits.
Orca is inferred in this order:
`ORCASLICER_COMMAND`, host `orca-slicer`, then Flatpak OrcaSlicer. Slicing and
the support probe run without an automatic runtime deadline, following the
[repository deadline rule](../../../AGENTS.md#shared-engineering-execution).

### Placement

`center` is the default. It uses `--arrange 1 --orient 0
--allow-rotations=0`. One STL moves as a whole and retains internal component
positions. For a multi-object project, use `preserve` when its existing
placement is intentional, or `assembly` when grouping the objects on one plate
is acceptable. Record any different placement or compound splitting intended
when importing STEP in Orca's GUI. Do not silently rotate, scale, repair, split
or union the input.

## Read the result

The evaluator checks Orca's exit status and `result.json` for a completed plate,
then reports the selected profiles, key effective settings, slicer version,
placement, sliced plate IDs and notices. It also probes the same model and
placement with automatic supports enabled and `bridge_no_support=0`, while
keeping the profile's overhang threshold and maximum bridge length. If the
primary slice already uses those auto-support settings, its output serves as
the probe; otherwise Orca runs a second diagnostic slice. The evaluator reads
only Orca's `;TYPE:` line labels from that slice and reports whether support
or support-interface roles occurred, by plate. It does not reconstruct motion
or measure unsupported spans, deposited bounds, mesh repair, clearance or
physical print quality.

`support_probe.generated=true` requests review, not redesign. Orca may propose
unnecessary support, or omit support that the physical print needs. Inspect the
support's location and removal path in Orca's GUI when generated; inspect a
specific suspect bridge there even when the probe finds none. A probe failure
is reported as `support_probe.ok=false` and also requests review. Open the
sliced layout in Orca's GUI when acceptance is ambiguous or print-aid location
affects removal or use. A completed slice covers routine bed-fit acceptance
under the selected profile.

The notice list combines structured plate warnings with keyword-filtered log
lines. An empty list does not prove the full slicer log is message-free. Use
`--slice-keep-run` when the complete log or raw G-code is needed; on success the JSON
includes the retained directory (with any second slice under `support_probe/`),
and on error the message gives its location.
Otherwise G-code, logs, `result.json`, effective settings and intermediate files
are deleted automatically.

Exit 0 means no automated review condition was found. Exit 2 means Orca reported
a notice or the support probe needs review. Exit 1 means the primary review
could not complete. These statuses are not
universal printability verdicts.

Keep one concise object record with model and profile paths, Orca version,
placement, effective settings, smoke result, support-probe result, notices and
physical limitations.
Keep temporary files only when they answer a concrete question.

Correct disproven advice and consolidate useful techniques instead of appending
session transcripts. Record tested slicer version, profile assumptions,
observation and limits. Do not generalize one printer's clearance or bridge
result into a universal rule. Capture reusable geometric lessons in print
planning or the [reusable model evidence index](../cadquery-3d-design/references/reusable-model-lessons.md)
when transferable. Inspection does not authorize redesign, deployment, print
tuning outside scope or printing.
