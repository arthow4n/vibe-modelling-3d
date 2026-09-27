# Qidi Q2C 0.4 mm PETG reference profiles

These OrcaSlicer JSON settings select the bundled **Qidi Q2C 0.4 nozzle**
printer and **Generic PETG** filament profiles, with a 0.20 mm Standard process
customized to **7% adaptive cubic sparse infill**.

The three profiles are resolved snapshots of OrcaSlicer 2.4.2 Flathub presets:
`Qidi Q2C 0.4 nozzle`, `Generic PETG @Qidi Q2C 0.4 nozzle` and
`0.20mm Standard @Qidi Q2C`. Their parent values are included because the
2.4.2 headless CLI accepted child preset names but did not reliably apply
inherited filament/process settings from partial JSON files. The process
snapshot overrides the inherited Standard process's sparse infill density and
pattern. The effective settings export is the final authority for what a CLI
run actually used.

The Q2C preset and [manufacturer specifications](https://us.qidi3d.com/products/q2c)
report a 270 × 270 × 256 mm build volume. Orca review checks default to that
volume, including brim/support bounds. The repository's more conservative CAD
design envelope remains 260 × 260 × 250 mm; pass those smaller limits when a
review should enforce the design margin instead.

`Generic PETG` is a generic diagnostic material preset. It does not represent a
particular spool's temperature, flow, cooling or pressure-advance calibration,
and its G-code is not a validated printer job. Use actual user settings when
making claims about a specific spool or production setup.
