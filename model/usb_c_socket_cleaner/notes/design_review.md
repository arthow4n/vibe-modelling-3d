# Revised design assumptions and use notes

## What changed

The earlier fork and broad paddle were poor interpretations for this job.
This revision is a narrow plastic port pick: one thin stem sits in one side
channel beside the USB-C center tongue, and a small raised rear shoulder hooks
compacted lint during the pull-out stroke. The narrow pick can be moved a
little within the side channel instead of trying to occupy the whole opening.

## Interface assumptions

The USB-IF Type-C Cable and Connector Specification Release 2.0, Figure 3-1,
gives a nominal receptacle opening of 8.34 mm wide, a nominal receptacle
inside thickness of 2.56 mm, a 6.69 mm tongue width, a 0.70 mm tongue
thickness, and a 6.20 mm reference shell length.

The pick is 0.55 mm wide and is located in a nominal 0.825 mm side channel,
with 0.12 mm clearance to the tongue and about 0.155 mm to the outer shell.
Its flat stem is 0.35 mm thick. The hook rises to 0.55 mm and stays below the
nominal 0.93 mm vertical space on either face of the tongue. It reaches
5.85 mm before the 10.5 mm-wide stop collar meets the receptacle mouth.

These are nominal connector-envelope assumptions, not a guarantee for every
socket. A port with a bent tongue, unusually shallow shell, obstructing EMC
feature, or heavy first-layer bulge may not accept the pick.

## Actual use

1. Power the device down and disconnect all cables. Hold the rounded handle.
2. Look into the port and put the thin pick into one side of the center
   tongue, lying lightly against the lower inside wall. Do not aim at the
   visible contact springs.
3. Slide the low nose straight toward the back of the port. Use only light
   pressure; the wide stop collar prevents excessive insertion.
4. Pull the pick back slowly. The raised rear shoulder and sharp side edges
   are the scraping/catching features: they should loosen and drag lint out.
   Use short strokes and a small side-to-side sweep within the side channel;
   do not lever against the center tongue.
5. Rotate the tool 180 degrees in plan to reach the other side, and flip it
   over to work on the opposite face. Finish with a blower to remove loosened
   debris.

The pick is deliberately plastic rather than metal. Its edge is intentionally
crisp for lint removal, while the grip and stop edges are rounded/chamfered.
Do not twist hard, scrape the contact springs, or use the pick in an energized
port.

## Printing and limitations

- Print the complete tool flat on its broad Z=0 face.
- PLA or PETG with a 0.4 mm nozzle is assumed; 0.12–0.16 mm layer height and
  at least three perimeters are a reasonable starting point for the pick.
- No supports are intended. The 0.55 mm hook height and 0.35 mm stem
  thickness are small FDM features; inspect the pick before use and discard a
  rough, oversized, or delaminated print.
- CAD and slicing checks cannot establish a particular port's actual fit,
  cleaning effectiveness, or safe force limit. Physical testing remains
  outstanding.

References:

- https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf
- https://www.ifixit.com/Guide/How%2Bto%2BClean%2Bthe%2BPorts%2Bon%2Byour%2BElectronic%2BDevice/164721
