# Integrated 96 W MacBook charger cable holder

One-piece PETG replacement with a slide-in MagSafe 3 cradle beside the band.
The primary Python file is standalone and does not import downloaded geometry.
STEP and STL use the same print orientation: ring flat on XY at Z=0.
Envelope: 85 × 42.84 × 24.98 mm. One valid solid, about 6.43 cm³.

## Files and use

- `../macbook_charger_holder.py`: authoritative full model, evaluate directly.
- `../macbook_charger_holder.step` and `.stl`: full printable replacement.
- `../cradle_test.py`, `.step`, `.stl`: optional representative connector coupon.
- `../export_and_check.py`: regenerate exports and geometry verification report.
- `../renders/`: inspected full views and coupon view.

Slide the band onto the charger as with the original. Orient the cradle on a
broad face, facing away from the mains plug so that the first cable run leads
toward the plug end. With both ends disconnected, slide the MagSafe housing
cable-first down the rails until its shoulders meet the stop. Its contact face
points toward the open, raised rail ends; nothing enters or grips the contacts.
Route the cable through the central open slot into the first groove (X=12).
Skip the covered neighbouring groove at X=17.4 and continue across the exposed
grooves starting at X=22.8. Tuck the disconnected USB-C housing beneath the final
wraps within the charger's outline. Do not force the cable over a sharp bend.
Unwind before sliding the MagSafe head back out; grip its housing at the scallop.

The cradle's rails retain the head laterally and outward. The wound cable holds
it toward the stop; this is not a snap-lock and can slide out before winding.
USB-C retention uses the wraps, not a precisely positioned USB-C socket. Its
finishing position and whether the full cable tucks comfortably must be tested
with the user's cable. No physical fit or winding test has occurred.

## Dimensions and adjustments

Recovered from the supplied original STEP: opening 79.6 × 28 mm, corner R6,
wall 2.7 mm, axial band width 6 mm, repeated groove pitch 5.4 mm. The analytic
reference reconstruction differs by 0.001864 mm³ in symmetric difference.
The integrated cradle locally fills part of the tooth row; the original opening
is unchanged, but added stiffness means original physical grip does not prove
the replacement has exactly the same installation force.

Published measurements for an earlier genuine MagSafe 3 housing are
18.81 × 13.18 × 4.48 mm. Source: Chongdiantou's original measured comparison,
https://www.chongdiantou.com/archives/112019.html . These are not verified
measurements of the user's black M4 Pro cable. The cavity adds 0.35 mm per side
and 0.45 mm total depth clearance. Rail lips overlap each housing side by 1.2 mm.
The cable exit is 5 mm wide, relieved down into the existing round groove.

Adjust `side_clearance` for sideways binding/play and `depth_clearance` for
front-to-back fit. `head_width`, `head_length`, and `head_thickness` describe the
nominal housing. `cradle_center` selects the starting position, and `head_stop_z`
sets its offset from the band. A 0.55 mm side-clearance variant was also built
successfully. The reference scallop termination is fixed: changing tooth count
or pitch also requires updating the termination construction. Do not interpret
those reference constants as independently supported customization options.

Print the coupon in the exported orientation, using the same PETG/profile as
the full object. It reproduces the complete cradle and local band root. Check
insertion, housing shoulder support, cable exit, and housing removal without
pulling on the cable. It does not test whole-band flexibility or winding.

## Printing and checks

Use PETG, 0.4 mm nozzle, ring face down. Diagnostic slice used 0.2 mm layers,
4 perimeters, 5 top/bottom layers and 20% infill, supports disabled. Retaining
lips grow from the bed, and the open cable slot requires no roof bridge.
Use the user's normal PETG temperatures and printer profile for an actual job.
The 260 × 260 × 250 mm safe volume leaves ample room for a brim if needed;
the small coupon has less adhesion area than the full ring.

PrusaSlicer 2.9.6 produced 125 layers without stability warnings. Parsed paths
contained no bridge, overhang-perimeter or support roles. Layer close-ups at
Z=6.2, 10.2 and 24.8 mm were inspected: rail/lip paths sit over prior material,
and the pocket opens above the housing stops. See `slicing/paths.json` and
`slicing/cradle_layers.png`. This is geometric/slicer validation, not a test print.
The diagnostic G-code is ignored and is not a validated machine job.

Reproduction from repository root:

```sh
prusa-slicer --load model/macbook_charger_holder/notes/slicing/diagnostic.ini --center 130,130 --export-gcode --output model/macbook_charger_holder/notes/slicing/holder.gcode model/macbook_charger_holder/macbook_charger_holder.stl
python3 .codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py model/macbook_charger_holder/notes/slicing/holder.gcode --json model/macbook_charger_holder/notes/slicing/paths.json --svg model/macbook_charger_holder/notes/slicing/cradle_layers.svg --layers 6.2 10.2 24.8 --window 88 107 114 118
```

STEP reimport checks confirmed valid single solids. STEP/STL bounds agree within
0.03 mm for both exports. Triangulation can inflate reported CAD bounds by a few
microns; source placement is Z=0. Reports are in `verification.json`.

## Reference attribution

Based on **96W MacBook Charger Cable Management**, original model and creator
page: https://www.printables.com/model/765229-96w-macbook-charger-cable-management .
The user supplied the original STL and STEP archive and subsequently confirmed
the listing's licence as **CC BY-NC-SA 4.0**, correcting the earlier “CC BY”
description. This object is not MIT-licensed. See [LICENSE](../LICENSE) and
[ATTRIBUTION.md](../ATTRIBUTION.md) for scope, licence links and credits.
The creator's display name remains pending because the archive contains no
author metadata and the listing was blocked by HTTP 403 during this work.
Changes: standalone analytic reconstruction, integrated MagSafe parking rails,
cable-exit shoulders, finger scallop, softened rails, and optional fit coupon.
Preserve this attribution with redistributed derivatives; this object's original
reference-derived geometry should not be treated as covered solely by the
repository's root licence.

Downloaded originals and temporary reference inspection files are held only in
`../references/`, excluded by the object's `.gitignore`. They are not committed.
