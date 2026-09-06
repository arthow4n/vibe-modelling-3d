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

The initial working parser was object-specific:
[case analysis script](../../../../model/sunglasses_case/notes/slicer_review/analyze.py).
It expects two named diagnostic files. The reusable helper below now accepts
one file and can render selected layer windows. Neither calculates true
unsupported spans.

## Inspect one G-code file and render layer windows

Verified on 2026-09-05 with PrusaSlicer 2.9.6 and the revised flat-print case:
[inspect_gcode.py](../scripts/inspect_gcode.py) uses the Python standard library
to produce feature counts, layer counts, longest bridge segments and optional
SVG close-ups. It rejects absolute E, relative XYZ, inch units, arcs and
nonplanar deposition. It ignores stationary retractions/unretractions and travel.
Its expected input is commented, linear, ASCII PrusaSlicer G-code in millimetres.

```sh
python3 .codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py \
  "$run_dir/case.gcode" --json "$review_dir/case_paths.json" \
  --svg "$review_dir/hinge_layers.svg" --layers 33.6 37.0 40.6 \
  --window 82 117 108 140
```

The example window is Xmin, Ymin, Xmax, Ymax in **sliced bed coordinates** for
the revised sunglasses case, centered at 130,130. Choose heights and coordinates
from the actual current paths, not raw CAD coordinates. Requested layers must
exist; the script refuses to substitute a materially different layer silently.

Gray lines show the preceding deposited layer at its reported extrusion width;
thin colored/black lines show current centerlines. This helps inspect where
material grows, whether gaps persist and what lies beneath a bridge-labeled
path. It is not a continuous material-coverage calculation or sag simulation.
Numerical line clipping is used: the local ImageMagick renderer produced
incorrect results with SVG clip paths during development. The corrected SVG
and PNG were visually inspected. Where ImageMagick is available, conversion is:

```sh
convert -background white "$review_dir/hinge_layers.svg" "$review_dir/hinge_layers.png"
```

The helper was exercised on both full-case and hinge-coupon output, with
additional checks for deposition versus travel/retraction, rejected coordinate
modes, arcs, nonplanar extrusion and numerical window clipping. Continue to
extend its format coverage only with tests; it is not a general G-code interpreter.

## Long bridge-role paths can lie over internal infill

In the revised flat case, a diagnostic profile with 6 top and 6 bottom layers
at 0.2 mm left a sparse infill band inside the 3 mm floor. At Z=2.0 mm,
PrusaSlicer emitted bridge-role paths up to about 184 mm long over that infill,
without the earlier long-bridge warning. Their full length was not an empty
span. Inspect preceding material before classifying such paths as failures.

Using 8 top and 8 bottom layers made those 3 mm panels solid throughout; the
final case and coupon had no Bridge infill or support roles and no stability
warnings. That setting is specific to these panel thicknesses and layer height,
not a general instruction to eliminate all infill or bridge roles. Evidence:
[flat-print review](../../../../model/sunglasses_case/notes/support_free_review/report.md).

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

## Clean slicing does not prove clean mesh topology

The rounded sunglasses hinge exported a few degenerate triangles at exact cone
apices even though its CAD solids were valid and PrusaSlicer emitted no warning.
Small flat tips eliminated the degenerate facets; final exported meshes were
checked independently for paired triangle edges, component count and bed contact.
When moving-part reliability matters, retain these mesh checks alongside slicer
warnings and path inspection. A clean slice alone did not reveal this defect.

## What has not been established yet

Selected layer-window SVGs are now supported by the helper above. Automatic
free-air span measurement, support-removal accessibility checking and a reliable
pass/fail printability score remain unimplemented here. No universal safe bridge length or overhang-angle limit
has been established; behavior depends on geometry, anchors, process and material.
Slicer evidence does not physically measure sag, surface finish or hinge freedom.

## Check the actual brim and deposited-path footprint

Verified 2026-09-06 with PrusaSlicer 2.9.6 on the dental travel case, using the
existing `read_paths` helper and a centered 260 × 260 mm bed with 3 mm brim:
[object summary script](../../../../model/dental_travel_case/notes/slicer_review/summarize.py).
For each deposited straight segment, extend both endpoints in X/Y by half its
reported extrusion width, then take global min/max. Include `Skirt/Brim` paths.
Check maximum layer Z independently against the **250 mm** safe height.

The final case had X 3.122–256.876 and Y 11.202–248.220 mm, with Z up to 61.8 mm.
This checks generated paths rather than relying only on model bounds plus nominal
brim width. It is conservative for straight segments of the reported width, but
not a prediction of ooze/flow spread or a check of travel/start/end machine moves.
The parser's existing limits (absolute XYZ, relative E, linear ASCII moves) apply.

In the same investigation, a circular-bottom clip produced a `Loose extrusions`
warning on the accessories plate but not on a mixed coupon plate. Inspecting the
lower-arc layers identified abrupt lateral growth; adding a supporting pedestal
removed the accessory warning. Replacing small grip bumps alone did not. Do not
assume a clean mixed-plate warning result validates the same part in every layout;
inspect the production plate's paths. See the object's review report and layer
images for geometry and profile scope, rather than treating the fix as universal.
