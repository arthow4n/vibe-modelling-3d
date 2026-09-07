# PrusaSlicer printability review — narrow-pick revision

Date: 2026-09-07

## Diagnostic setup

- Input: `usb_c_socket_cleaner.stl`, exported from `usb_c_socket_cleaner.py`;
  final diagnostic run: `run04/usb_c_socket_cleaner.gcode`.
- Orientation: source orientation, broad handle face on the bed at Z=0; no
  rotate, split, arrange, or scale operation.
- Bed placement: centered around X,Y = 130,130 on the confirmed 260 x 260 mm
  usable bed.
- Profile: `review.ini`; generic PLA assumptions, 0.4 mm nozzle, 0.2 mm
  layers, 3 perimeters, 3 mm brim, supports disabled.
- CLI: PrusaSlicer 2.9.6+flathub.org.

## Observed result

The fresh no-support slice completed with exit code 0 and a non-empty
687,138-byte ASCII G-code file. The log reported no support generation or
stability warning. The helper found 27 layers from Z=0.2 through 5.4 mm,
3.72 g estimated filament, and an estimated 20 min 36 s in normal mode.

The focused pick layer window shows a continuous narrow deposited stem from
the stop collar and the raised hook feature in the first layers. It is a
deliberately small one-line/two-line feature, not an absent or accidental
geometry gap. The broad handle and stop also slice normally in the full
layer-window preview.

The slice contains `Bridge infill` role paths, with a longest reported path of
13.97 mm at Z=4.6 mm. These occur in the broad handle/top-fill region; no
support paths were generated. The report and layer-window images are
diagnostic evidence only, not a guarantee of bridge surface quality.

## Remaining uncertainty

The slicer confirms toolpath generation and the intended flat orientation but
does not establish that a particular printer will resolve the 0.55 mm pick,
that the pick will fit every USB-C receptacle, or that the hook will remove
all debris without contact damage. Inspect the printed pick before use and
discard it if the edge is oversized, rough, or delaminated.
