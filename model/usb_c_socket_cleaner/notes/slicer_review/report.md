# PrusaSlicer printability review

Date: 2026-09-07

## Diagnostic setup

- Input: `usb_c_socket_cleaner.stl`, exported from `usb_c_socket_cleaner.py`;
  final diagnostic run: `run02/usb_c_socket_cleaner.gcode`.
- Orientation: source orientation, broad handle face on the bed at Z=0; no
  rotate, split, arrange, or scale operation.
- Bed placement: centered around X,Y = 130,130 on the confirmed 260 x 260 mm
  usable bed.
- Profile: `review.ini`; generic PLA assumptions, 0.4 mm nozzle, 0.2 mm
  layers, 3 perimeters, 3 mm brim, supports disabled.
- CLI: PrusaSlicer 2.9.6+flathub.org.

## Observed result

The fresh no-support slice completed with exit code 0 and a non-empty
691,292-byte ASCII G-code file. The log reported no support generation or
stability warning. The helper found 27 layers from Z=0.2 through 5.4 mm,
3.73 g estimated filament, and an estimated 20 min 42 s in normal mode.

The selected first-layer paths show both narrow fork tines as continuous
deposited perimeter lines from the rounded noses into the stop collar. The
0.55 mm tine thickness is represented in the next two layers and then ends as
intended; this confirms that the tip is a small, intentionally thin feature,
not an accidentally missing solid.

The slice contains `Bridge infill` role paths, with a longest reported path of
13.97 mm at Z=4.6 mm. These occur in the broad handle/top-fill region; no
support paths were generated. The report and layer-window images are
diagnostic evidence only, not a guarantee of bridge surface quality.

## Remaining uncertainty

The slicer confirms toolpath generation and the intended flat orientation but
does not establish that a particular printer will resolve a 0.45 mm tine, that
the printed tine will fit every USB-C receptacle, or that the tool will remove
all debris without contact damage. Inspect the printed tip before use and
discard it if the tine is oversized, rough, or delaminated.
