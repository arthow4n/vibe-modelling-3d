# OrcaSlicer CLI setup smoke slice

On 2026-09-27, the Flatpak `com.orcaslicer.OrcaSlicer` 2.4.2 CLI sliced the
existing `vaseline_container.stl` using the repository's Qidi Q2C 0.4 mm / Generic
PETG / 0.20 mm / 7% adaptive cubic profiles. The unified review helper read the
build volume from Orca's effective printer settings: 270 × 270 × 256 mm, with
printable XY coordinates 0–270 mm on both axes. This verifies the headless
installation, profile loading and generated toolpaths; it did not send a job to
a printer or change model geometry.

## Effective settings and result

- Printer: Qidi Q2C, 0.4 mm nozzle, 270 × 270 × 256 mm build volume
  ([manufacturer specifications](https://us.qidi3d.com/products/q2c)).
- Filament: Generic PETG, 250°C nozzle (245°C first layer), 80°C hot plate.
- Process: 0.20 mm layers, 7% adaptive cubic sparse infill.
- Placement: centered by Orca with auto-orientation and arrangement rotation
  disabled. The single STL mesh and its internal part positions stayed together.
- OrcaSlicer returned success, reported one sliced plate with no warning, and
  produced nonempty G-code. Parsed output has 114 layers and `Sparse infill`
  paths. The deposited XY bounds including half line width and brim are X
  67.775–202.171 mm, Y 96.775–173.225 mm; Z is 0.2–22.8 mm. It fits the Q2C
  volume. No support paths were generated under these profiles.

The equivalent current smoke-slice command is below. The historical run used
the retired `--expect-no-supports` flag; its saved evidence remains historical.

```sh
uv run --locked python .codex/skills/orca-slicer-printability/scripts/review_print.py \
  --model model/vaseline_container/vaseline_container.stl
```

The profile files are [printer](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json),
[Generic PETG](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json), and
[process](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json).
The [shared OrcaSlicer skill](../../../../.codex/skills/orca-slicer-printability/SKILL.md)
describes the helper and its temporary output lifecycle.

The JSON report is printed to stdout. G-code, logs, effective settings and
intermediate records are temporary and removed at exit; rerun with `--keep-run`
only if those diagnostics are needed. This is profile-specific smoke evidence,
not a calibrated print job or physical test. The object's earlier
user-reported physical print status remains as recorded in its main README.
