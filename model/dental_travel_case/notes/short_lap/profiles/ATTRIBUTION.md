# Short-lap diagnostic process

`process.json` derives from the repository's maintained
`.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json`
resolved Orca/Qidi process snapshot. Its retained inherited preset is
`0.20mm Standard @Qidi X3`. Upstream attribution: OrcaSlicer contributors and
Qidi profile contributors; repository snapshot edits retain their provenance.

This revision changes the process name and `wall_loops` from 2 to 3, keeping
0.2 mm layers, 7% adaptive cubic and the automatic 5 mm brim. It is a diagnostic
process, not filament calibration. Use the shared Q2C 0.4 mm printer and Generic
PETG filament JSONs as the complete triplet. All profile JSON content in this
directory is distributed under [AGPL-3.0](LICENSE.txt); CAD and notes retain the
repository's default licence.
