# OrcaSlicer CLI setup smoke slice

On 2026-09-27, the Flatpak `com.orcaslicer.OrcaSlicer` 2.4.2 CLI sliced the
existing `vaseline_container.stl` with the repository's reference Qidi Q2C
0.4 mm / Generic PETG profiles. This verifies the headless installation,
profile loading and generated toolpath path; it did not send a job to a printer
or change the model geometry.

## Effective settings

- Printer: Qidi Q2C, 0.4 mm nozzle, with a 270 × 270 × 256 mm build volume
  ([manufacturer specifications](https://us.qidi3d.com/products/q2c)). This
  check used the helper's default full machine volume, without a `--bed`
  override; the CAD design envelope remains the repository's more conservative
  260 × 260 × 250 mm.
- Filament: Generic PETG, 250°C nozzle (245°C first layer), 80°C hot plate.
- Process: 0.20 mm layers, 7% adaptive cubic sparse infill.
- Placement: centered by Orca with auto-orientation and arrangement rotation
  disabled. The single STL mesh and its internal part positions stayed together.
- Scope: reference settings only. Generic PETG values are not calibrated to a
  particular spool or physical printer result.

## Result

OrcaSlicer returned success, reported one sliced plate with no warning, and
created a fresh nonempty G-code file. The exported effective settings identify
Qidi Q2C, 0.4 mm, PETG, 7% sparse infill and `adaptivecubic`. Parsed output has
114 layers and `Sparse infill` paths. The deposited XY bounds including half
line width and brim are X 67.775–202.171 mm, Y 96.775–173.225 mm; Z is
0.2–22.8 mm. It fits the Q2C build volume. No support paths were
generated under this profile.

- [Review summary](orca_review_q2c_default_01/summary.json) and [CLI result](orca_review_q2c_default_01/result.json)
- [Exact command](orca_review_q2c_default_01/command.json), [effective settings](orca_review_q2c_default_01/effective-settings.json), and [path summary](orca_review_q2c_default_01/paths.json)
- [Shared OrcaSlicer skill](../../../../.codex/skills/orca-slicer-printability/SKILL.md)
- Profiles: [printer](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json), [Generic PETG](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json), and [process](../../../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json).

G-code and raw logs are ignored in the run directory. This is reference-profile
evidence, not a validated print job or physical test. The object's earlier
user-reported physical print status remains as recorded in its main README.
