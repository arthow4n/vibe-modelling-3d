# Qidi Q2C 0.4 mm PETG reference profiles

These OrcaSlicer JSON presets select the bundled **Qidi Q2C 0.4 nozzle** printer
and **Generic PETG** filament profiles, with a 0.20 mm Standard process customized
to **7% adaptive cubic sparse infill**.

The printer and filament JSON files are copied from the OrcaSlicer 2.4.2
Flathub bundle. The process JSON inherits OrcaSlicer's bundled
`0.20mm Standard @Qidi Q2C` profile and overrides only its name, infill density
and infill pattern. These profiles therefore require an OrcaSlicer installation
that supplies their inherited system presets; the reviewed setup used Flathub
`com.orcaslicer.OrcaSlicer` 2.4.2.

The Q2C preset reports a 270 × 270 mm printable area and 256 mm height. For
repository reference reviews, continue to use the more conservative practical
envelope of 260 × 260 × 250 mm, including brim/support bounds.

`Generic PETG` is a generic diagnostic material preset. It does not represent a
particular spool's temperature, flow, cooling or pressure-advance calibration,
and its G-code is not a validated printer job. Use actual user settings when
making claims about a specific spool or production setup.
