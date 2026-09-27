---
name: orca-slicer-printability
description: Run an OrcaSlicer reference-profile smoke slice and review slicer-generated path summaries with the CLI. Results describe the selected profile only; inspection does not authorize redesign or printing.
---

# OrcaSlicer printability inspection

## Scope

Start with [CAD/print planning](../cadquery-3d-design/references/print-planning.md).
Use CAD geometry to check support at bridge ends, projections, walls, gaps and
orientation. Use Orca for the paths it generated; do not recreate its planning
algorithms. A reference slice says Orca produced paths under the selected
profiles. It does not establish temperatures, flow, dimensional accuracy,
bridge quality, physical clearance, strength or tactile behavior.

This skill covers final-mesh smoke reviews and aggregate path summaries. It does
not request layer-window checks or generate layer images. Resolve geometry
questions in CAD; do not treat the path summary as a detailed local investigation
across selected layers.

Choose nozzle, layer height, material, walls and infill during the design
agreement, before CAD detail; see [AGENTS.md](../../../AGENTS.md). The user's
preferred starting point is the Qidi Q2C with a 0.4 mm nozzle and 0.2 mm
layers. A 0.8 mm nozzle and several PLA, PETG and TPU filaments are available.
Two walls with 7% adaptive cubic infill are the user's general experience for
ordinary prints, not a strength requirement. Explain and discuss consequential
changes to this starting approach before relying on them in the design.

The maintained Qidi Q2C 0.4 mm, Generic PETG, 0.20 mm Standard, two-wall,
7% adaptive cubic profiles are a diagnostic fallback, not the user's fixed
production setup. Prefer compatible supplied Orca profiles for the agreed
nozzle, material and process. If the fallback differs from the intended print,
state the mismatch and limit conclusions to diagnostic path acceptance; do not
claim that its settings predict the agreed print. A 0.8 mm or TPU design needs
an appropriate printer/process/filament profile for setup-specific path claims;
if none is available, record that evidence gap. Do not substitute the 0.4 mm
PETG profile silently. Do not translate another slicer's profile into Orca or
add more reference slicers. STEP is the user's primary print-ready interchange
file. The installed headless Orca CLI rejects STEP input, so for a final smoke
review slice the matching exported STL. This result does not verify Orca's GUI
STEP import; do not describe it as a STEP slice. Use 3MF when it is the agreed
print file. Reuse a result only while its
model, profiles, placement and slicer version still match; follow the evidence
reuse rules in AGENTS.md.

## Run the review

For a normal final model, run this from the repository root:

```sh
./evaluate_model.py model/object_name/object_name.py --views none --slice
```

It exports the STEP/STL pair and runs this helper on the STL. Optional
`--slice-printer`, `--slice-process`
and `--slice-filament` accept compatible Orca JSON profiles; otherwise the
diagnostic defaults below apply. The evaluator returns the slice result in its
single JSON report. Use the standalone helper below when reviewing an already
exported file without rebuilding the model.

The evaluator also passes through `--slice-placement`,
`--slice-expect-no-supports` and `--slice-keep-run` when needed. A completed
slice that needs review exits 2 and reports `slice.review_required=true`;
failure exits 1. Read stage status even if a view render failed.

For an agreed setup with different profiles, pass them in the same command:

```sh
./evaluate_model.py model/object_name/object_name.py --views none --slice \
  --slice-printer model/object_name/notes/printer.json \
  --slice-process model/object_name/notes/process.json \
  --slice-filament model/object_name/notes/filament.json
```

For an existing export, run the unified helper from the repository root. It infers OrcaSlicer, loads
profiles, slices the model, reads effective settings, summarizes deposited
paths and prints one JSON report to stdout. It never sends a printer job.

```sh
uv run --locked python .codex/skills/orca-slicer-printability/scripts/review_print.py \
  --model model/object_name/object_name.stl
```

The CLI help and this table are the interface contract; keep argument names
and defaults synchronized:

| Argument | Default | Meaning |
| --- | --- | --- |
| `--model MODEL` | Required | STL or 3MF to slice. |
| `--printer PRINTER` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json` | Diagnostic 0.4 mm printer and machine dimensions. |
| `--process PROCESS` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json` | Diagnostic 0.20 mm, two-wall, 7% adaptive cubic process. |
| `--filament FILAMENT` | `.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json` | Diagnostic Generic PETG. |
| `--placement {preserve,center,assembly}` | `center` | Center the layout without rotation or auto-orientation. |
| `--expect-no-supports` | Off (`false`) | Request review if Orca generates support paths. |
| `--keep-run` | Off (`false`) | Retain temporary G-code and diagnostics. |

To use the agreed setup with other Orca profiles, pass all three compatible
profile files:

```sh
uv run --locked python .codex/skills/orca-slicer-printability/scripts/review_print.py \
  --model model/object_name/object_name.stl \
  --printer model/object_name/notes/printer.json \
  --process model/object_name/notes/process.json \
  --filament model/object_name/notes/filament.json \
  --placement preserve
```

The printer profile also supplies the checked machine bounds. There is no
separate bed-size argument: bounds come from Orca's effective
`printable_area` and `printable_height`. The Qidi Q2C profile defines the
manufacturer's **270 × 270 × 256 mm** build volume
([Q2C specifications](https://us.qidi3d.com/products/q2c)). Use a printer
profile with smaller dimensions when those are the appropriate usable limits.
Only axis-aligned rectangular printable areas are supported; the helper errors
on other shapes rather than guessing. Orca is inferred in this order:
`ORCASLICER_COMMAND`, host `orca-slicer`, then Flatpak OrcaSlicer. Its CLI
timeout is fixed at 600 seconds.

### Placement

`center` is the default. It uses `--arrange 1 --orient 0
--allow-rotations=0`. One STL moves as a whole and retains internal component
positions. For a multi-object project, use `preserve` when its existing
placement is intentional, or `assembly` when grouping the objects on one plate
is acceptable. Do not silently rotate, scale, repair, split or union the input.

## Read the result

The helper verifies Orca's exit status, a successful `result.json` with one or
more sliced plates, fresh nonempty G-code matched to every reported plate ID,
effective settings and parseable deposition. The JSON report includes selected
profiles and effective settings, slicer version, printer volume, placement,
whether supports were expected, notices, and per-plate:

- deposited XY bounds including half line width, brim and generated support;
- layer range and count, support-segment count and path-role totals;
- longest bridge-role centerlines and filament/time metadata.

Bounds exclude travel, start/end machine motion and physical flow spread. A
missing G-code width uses the parser's 0.45 mm fallback, which is only a
diagnostic estimate. Path roles and segment lengths do not establish anchors,
free-air spans, clearance or physical print quality. The helper does not assess
whether Orca repaired a mesh or retained every intended component.

The notice list combines structured plate warnings with keyword-filtered log
lines. An empty list does not prove the full slicer log is message-free. Use
`--keep-run` when the complete log or raw G-code is needed; on success the JSON
includes the retained directory, and on error the message gives its location.
Otherwise G-code, logs, `result.json`, effective settings and intermediate files
are deleted automatically.

Exit 0 means no automated review condition was found. Exit 2 means Orca reported
a notice, paths extend beyond the selected printer volume, or the optional
no-support expectation was violated. Exit 1 means the review could not
complete. These statuses are not universal printability verdicts.

Keep one concise object record with model and profile paths, Orca version,
placement, effective settings, smoke result, notices, per-plate bounds and
support presence, plus physical limitations. Keep temporary files only when
they answer a concrete question. No automatic layer-window views, free-air
span, anchor, sag, stress, support-removal accessibility, mesh-repair assessment
or physical printability classifier is provided.

## Related references

- [CLI and path interpretation](references/cli-and-paths.md): Flatpak launch,
  profile inheritance and parser limits.
- [Case lessons](references/case-lessons.md): retained observations and limits.

Correct disproven advice and consolidate useful techniques instead of appending
session transcripts. Record tested slicer version, profile assumptions,
observation and limits. Do not generalize one printer's clearance or bridge
result into a universal rule. Capture reusable geometric lessons in print
planning or the relevant case lesson. Inspection does not authorize redesign,
deployment, print tuning outside scope or printing.
