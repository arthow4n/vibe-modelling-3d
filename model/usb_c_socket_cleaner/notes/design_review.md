# Design assumptions and use notes

## Interface assumptions

The USB-IF Type-C Cable and Connector Specification Release 2.0, Figure 3-1,
gives a nominal receptacle opening of 8.34 mm wide, a nominal receptacle
inside thickness of 2.56 mm, a 6.69 mm tongue width, a 0.70 mm tongue
thickness, and a 6.20 mm reference shell length. The source keeps these values
near the top so the cleaner can be adjusted if a particular receptacle is
unusually tight or has a damaged/misaligned shell.

The cleaner intentionally does not model a USB-C plug. It uses two 0.45 mm
wide tines, each offset into a nominal side gutter, leaving 0.15 mm from the
tine's inner edge to the nominal tongue edge and about 0.225 mm to the nominal
outer shell edge. The 0.55 mm tine thickness is below the nominal vertical
clearance on either face of the tongue. These are conservative nominal
clearances, not a guarantee for every connector or print profile.

## Printing and operation

- Print the complete one-piece tool flat on its broad Z=0 face.
- Use PLA or PETG with a 0.4 mm nozzle; a 0.16-0.20 mm layer height and at
  least three perimeters are reasonable starting settings.
- No supports are intended. The tines are deliberately narrow and may be a
  single extrusion line; inspect the first layer and discard a tine with voids
  or a rough oversized edge.
- Power the device down and disconnect it before cleaning. Insert the rounded
  tine noses gently until the stop collar meets the receptacle, sweep in and
  out a few times, and withdraw straight. Turn the tool over for the opposite
  face of the tongue. Do not twist, pry against the center tongue, or use a
  metal tool.
- The stop is set for about 5.75 mm tine insertion against the 6.20 mm reference
  shell depth. Actual port recesses and internal EMC features vary; do not
  force the tool if the stop meets an enclosure before the connector shell.

## Limitations

The model has not been physically trial-printed or tested in a specific port.
The CAD review can check nominal envelope clearance but cannot establish
contact spring deflection, debris removal effectiveness, or the strength of a
single-line FDM tine. Compressed air and a professional non-metallic cleaning
tool remain safer choices for valuable or energized equipment.

Reference: https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf
