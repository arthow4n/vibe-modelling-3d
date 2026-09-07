# Reduced production case: CAD and slicing review

The user approved E's closure after printing D/E and explicitly confirmed
158 × 78 × 63 mm internal dimensions. The case retains its previous rounded
shell, 3 mm walls/panels and broad edge chamfers. The E loop, insert receiver,
keeper and hinge profiles have zero symmetric volume difference from the test
definitions after translation. Hinge spacing and shell stiffness differ.

## Geometry and actual exports

CadQuery MCP evaluated `sunglasses_case.py`, the closed inspection entry point,
and `verify_production_case.py`. Three valid solids are exported: fixed body,
moving lid, and side-printed keeper. Checks cover the unobstructed rounded
cavity, closed fit, shell/hinge sweep at 5-degree intervals, opening obstruction
with a seated loop, clearance after outward release, and keeper capture against
upward/outward movement. Small tapered-key interference is intentional.

`geometry_checks.json` records E interface comparisons, final STEP/STL hashes,
individual component bounds and three watertight, nondegenerate mesh components
(50,656 triangles). All parts meet the bed at Z=0; STEP and STL bounds agree
within 0.035 mm per component. An alternate 168 × 88 × 68 mm cavity also passed
the geometry checks without changing the final exports. The source evaluator's
loose curved-surface bounds are conservative; exact STEP bounds and actual STL
vertices establish the bed position, as in the earlier keeper review.

## Slicing

PrusaSlicer 2.9.6, diagnostic PETG profile `../closure_review/review.ini`,
0.4 mm nozzle, 0.2 mm layers, supports disabled. From this directory:

```sh
prusa-slicer --load ../closure_review/review.ini --center 130,130 --export-gcode --output case.gcode ../../sunglasses_case.stl
python3 summarize.py
```

The fresh slice completed without warnings or support-material paths. It uses
225.90 g including the 5 mm brim; estimated time is 18h 23m 57s. There are 217
layers, with maximum commanded layer Z=43.4 mm for the 43.5 mm CAD height.
Deposited paths including half extrusion width and brim lie within
X 28.381–233.471 mm and Y 25.804–230.196 mm, inside the 260 × 260 × 250 mm safe volume.
`summary.json` retains hashes, actual bounds and estimates; `paths.json` retains
role statistics. Generic diagnostic G-code is not a validated printer job.

## Inspected local layer windows

- `hinge_layers.png`, Z=31.0/34.4/37.8: conical interfaces remain separated and
  grow from attached material. Clearance follows E, but the hinge now lies at
  Z=34.5 rather than Z=30, so its layer registration differs.
- `loop_layers.png`, Z=40.4/40.6/40.8: the 12 mm rail bridge has two existing
  leaf anchors. Its first spanning paths occur at 40.8 mm and are tagged
  Overhang perimeter (about 11.6 mm centreline span). E's first spanning layer
  was 36.2 mm. A 4.5 mm CAD translation does not preserve a 0.2 mm layer grid.
- `receiver_layers.png`, Z=29.4/30.4/31.4: the diamond keyway and sloping exit
  slit close progressively on preceding material, avoiding a hanging tooth.
- `keeper_layers.png`, Z=0.2/0.4/5.0: the tooth outline is present from the bed
  and follows existing perimeters. Local keeper paths have no overhang/bridge roles.

These checks support printing without added supports; they do not simulate sag,
friction, flexure, creep or impact resistance. D/E were physically successful by
user report. This smaller full-size case has not yet been physically printed.
