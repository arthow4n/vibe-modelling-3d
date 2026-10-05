# Q1 diagnostic Orca profiles

These JSON snapshots derive from OrcaSlicer 2.4.2's bundled Qidi profiles.
Upstream: [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer),
[AGPL-3.0 licence](https://github.com/OrcaSlicer/OrcaSlicer/blob/main/LICENSE.txt),
preserved verbatim in [LICENSE.txt](LICENSE.txt). This licence scope covers the
two profile JSONs, not the independently authored CadQuery geometry.

`generic_tpu_95a_q2c.json` resolves, in inheritance order:
`resources/profiles/Qidi/filament/Q2/fdm_filament_q_common.json`,
`Generic TPU 95A @Q2C.json`, and
`Generic TPU 95A @Qidi Q2C 0.4 nozzle.json`. Only inheritance flattening,
the diagnostic name, settings ID and user-instantiation metadata changed.

`tpu_020_2walls_7percent.json` starts from the repository's already resolved
Q2C .20 mm/two-wall/7% adaptive cubic process snapshot. Q1 caps wall/infill
speeds at 30 mm/s and first-layer speeds at 20 mm/s, and changes the settings
name/ID. The object's README and native slice report own the effective settings,
results and physical limitations; these snapshots are not spool calibration.
