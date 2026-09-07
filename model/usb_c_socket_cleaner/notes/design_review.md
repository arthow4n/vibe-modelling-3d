# Revised design assumptions and use notes

## What changed

The first revision used two narrow side-gutter rails. That was not a useful
scraper: it could guide along the port but did not present a broad edge to the
lint pocket. This revision replaces it with one centered flat paddle with an
intentional chisel edge. The blade is the functional cleaning surface.

## Interface assumptions

The USB-IF Type-C Cable and Connector Specification Release 2.0, Figure 3-1,
gives a nominal receptacle opening of 8.34 mm wide, a nominal receptacle
inside thickness of 2.56 mm, a 6.69 mm tongue width, a 0.70 mm tongue
thickness, and a 6.20 mm reference shell length.

The blade is 5.90 mm wide at the root and 5.55 mm wide at its chisel end, so
it can sit under the nominal 6.69 mm center tongue with 0.395 mm per-side
width margin at the root. It is 0.45 mm thick versus the nominal 0.93 mm
vertical gap on either face of the tongue, leaving about 0.48 mm nominal
height clearance. The blade reaches 5.85 mm before the 10.5 mm-wide stop
collar meets the receptacle mouth.

These are nominal connector-envelope assumptions, not a guarantee for every
socket. A port with a bent tongue, unusually shallow shell, obstructing EMC
feature, or heavy first-layer bulge may not accept the blade.

## Actual use

1. Power the device down and disconnect all cables. Hold the rounded handle.
2. Look into the port and place the broad blade flat on the lower cavity floor,
   under the center tongue. The 0.18 mm nose and sloped top lead-in go first.
3. Slide it straight in gently until the stop collar meets the port mouth.
   Keep light downward pressure so the blade stays against the floor.
4. Pull the blade back out slowly. The crisp front edge is the scraper: it
   drags compacted lint toward the opening. Repeat short in/out strokes rather
   than prying or levering.
5. Turn the whole tool over and repeat against the opposite cavity face if
   needed, then use a blower to remove loosened debris.

The edge is intentionally crisp for scraping; the handle, stop, and exposed
grip edges are rounded or chamfered. Do not twist the blade, pry against the
center tongue, scrape the visible contact springs, or use a metal tool.

## Printing and limitations

- Print the complete tool flat on its broad Z=0 face.
- PLA or PETG with a 0.4 mm nozzle is assumed; 0.16–0.20 mm layer height and
  at least three perimeters are reasonable starting settings.
- No supports are intended. The 0.45 mm blade thickness is three 0.2 mm
  layers only approximately; inspect the edge and discard a rough,
  oversized, or delaminated print.
- CAD and slicing checks cannot establish a particular port's actual fit,
  cleaning effectiveness, or safe force limit. Physical testing remains
  outstanding.

Reference: https://www.usb.org/sites/default/files/USB%20Type-C%20Spec%20R2.0%20-%20August%202019.pdf
