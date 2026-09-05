# Verified investigation techniques

This notebook grows through actual use. Add new verified methods and correct
old ones automatically according to SKILL.md. Entries describe observations,
not guaranteed physical outcomes.

## Discover the installed CLI

Verified 2026-09-05 with **PrusaSlicer 2.9.6+flathub.org** on Linux:

```sh
command -v prusa-slicer
prusa-slicer --help
prusa-slicer --help-fff | rg -A 5 -- '--(support-material|overhangs|bridge-speed|gcode-comments|use-relative-e-distances)'
```

In the tested workspace, `prusa-slicer` is a wrapper around the Flatpak
application. It accepts normal CLI slicing arguments. Do not hardcode that
installation path or assume every machine has the same wrapper. Check file
access if a sandboxed installation cannot read the model or write the output.

## Reproducible diagnostic slices

The verified command form is:

```sh
prusa-slicer --load "$review_profile" --center "$bed_center" \
  --export-gcode --output "$run_dir/without_supports.gcode" "$model_path" \
  > "$run_dir/without_supports.log" 2>&1
```

Set these variables from the current object and printer. `review_profile` is a
saved INI profile with `support_material = 0` for the no-support baseline;
`bed_center` is the bed center in `X,Y` millimetres. `run_dir` must be a fresh
directory inside the object's directory, so an old G-code file cannot masquerade
as a successful new result. Quoting matters for paths containing spaces.

Record the confirmed settings separately from assumptions. The first verified
case used a 260 mm square bed (`--center 130,130`), PETG, an assumed 0.4 mm nozzle,
0.2 mm layers, 5 perimeters, 6 top/bottom layers and 25% infill. These values are
an example, not defaults suitable for all models or printers. A real user profile
is preferable when making printer-specific judgments.

For a controlled support comparison, the tested override is
`--support-material`, with a different output file and the same model, position
and remaining settings. Record support style, threshold and contact gaps; they
affect the result. Do not conduct unrelated comparisons after the question is
answered, or treat generated supports as an acceptable fix when supports are
disallowed.

Preserve the entire print-in-place assembly as one positioned input. The CLI
offers `--split`, arrangement and rotation transforms, but those change the
experiment. Any orientation comparison must be deliberate and documented.

## A zero exit code may not mean that slicing happened

Observed in 2.9.6: a profile with `use_relative_e_distances = 1` and no extruder
reset in layer G-code returned **exit code 0**, printed a configuration error,
and produced no G-code. The message requested `G92 E0` in `layer_gcode`.

The diagnostic profile succeeded after adding:

```ini
use_relative_e_distances = 1
layer_gcode = G92 E0
gcode_comments = 1
binary_gcode = 0
```

Do not overwrite a user's existing layer script indiscriminately; preserve its
commands when applying a needed reset. Check both the log and a fresh nonempty
output file. Distinguish configuration failure, completed slicing with warnings,
and completed slicing without warnings. None is physical print validation.

## Locate long bridges in actual toolpaths

The tested ASCII output includes `;Z:` layer-height markers and `;TYPE:` feature
markers such as `Bridge infill`, `Overhang perimeter`, `Support material` and
`Support material interface`. Confirm the roles present in the current output
instead of relying on a fixed complete list.

For a simple linear-move parser:

- Track absolute XYZ positions across moves, including travel. Track coordinate
  mode, extrusion mode and resets; the original diagnostic parser explicitly
  requires absolute XYZ and relative E and rejects incompatible mode changes.
- Count positive-E XY moves as deposited paths, excluding stationary unretractions.
  Strip comments before extracting numeric coordinates.
- Associate each deposited segment with its layer, feature role, endpoints and
  source line. For straight XY moves, length is `hypot(dx, dy)`.
- Handle or reject arcs and other unsupported motion explicitly when extending
  a parser. Do not silently apply a G0/G1-only method to arbitrary G-code.
- A segment length includes any anchoring and is **not automatically the free-air
  bridge span**. A long path can also be split across several moves. Feature
  totals and longest segments are useful leads, not a complete support analysis.
- Supported first layers may still be tagged `Bridge infill`. That role alone
  does not prove there is air underneath; compare preceding model/support layers.

The initial working parser is object-specific, not a general skill CLI:
[case analysis script](../../../../model/sunglasses_case/notes/slicer_review/analyze.py).
It expects the two named diagnostic files and uses only the Python standard
library. Inspect its actual coverage before reuse. It does not generate plots
or calculate true unsupported spans. Generalize it into a tested helper only
when that is useful to a subsequent investigation.

## Recorded case: standing sunglasses case

Evidence: [report](../../../../model/sunglasses_case/notes/slicer_review/report.md)
and [measurements](../../../../model/sunglasses_case/notes/slicer_review/measurements.json).
The tested geometry and analysis are retained in Git at `9b8af79`; future model
revisions may no longer reproduce these numbers.

With supports disabled, PrusaSlicer explicitly reported:

> Detected print stability issues:
> Long bridging extrusions
> Consider enabling supports.

At Z=171.2 mm, the upper cavity wall closed with `Bridge infill` segments up to
87.186 mm long, including anchors. Mapping that layer back to the standing case
identified the overhead wall. The completed G-code therefore supplied evidence
against accepting that orientation for the user's no-support requirement.

The support comparison added support/interface paths below the wall. It still
used bridge-role paths at Z=171.2 mm, illustrating why role labels need spatial
context. It was a diagnostic comparison, not an approved support-based solution.

## What has not been established yet

No general headless layer-image generator, automatic free-air span measurement,
support-removal accessibility checker or reliable pass/fail printability score
has been implemented or verified in this notebook. A future investigation may
add them after testing. No universal safe bridge length or overhang-angle limit
has been established; behavior depends on geometry, anchors, process and material.
Slicer evidence does not physically measure sag, surface finish or hinge freedom.
