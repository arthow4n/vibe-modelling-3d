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

The [design setup agreement](../cadquery-3d-design/references/user-preferences.md#printer-manufacturing-and-available-hardware)
owns nozzle, layers, material, walls/infill and printer defaults. Reuse the agreed
setup; inspection does not independently revise it.

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
add more reference slicers. For export pairing, absolute STL meshing and GUI
STEP-import limits, use the
[evaluator contract](../../../execution/README.md#cad-evaluation-and-exports).
The headless review uses STL (or agreed 3MF), not STEP.
Reuse a result only while its model, profiles, placement
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
when needed. Read stage statuses even when a render fails; the
[result interpretation](#read-the-result) owns review conditions and exit meanings.

To review an existing export without rebuilding, use:

```sh
./evaluate_model.py --slice-existing model/object_name/object_name.stl
```

Use `--slice-printer`, `--slice-process` and `--slice-filament` with all three
compatible Orca JSON profiles for a different agreed setup, for either command.
The maintained defaults live in this skill's `profiles/qidi-q2c-petg/` directory;
CLI `--help` lists exact paths and options. `--slice-keep-run` retains raw diagnostics.
This review never sends a printer job.

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
