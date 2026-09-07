# Closure experiments after the very-tight sample failed to retain

Print one complete sample per file. Every sample includes both hinges and the
latch; there is no combined plate. STEP and STL share the open print orientation.
The original full case's geometry and exports have not been redesigned.

## What the physical feedback established

On 2026-09-07 the user reported that the very-tight hinge/deep-latch sample
still tilted and the latch barely retained the halves. That sample is preserved
in Git at `1c6b8c3`; its STL SHA256 was
`1d47c05826aca5a4c3159d5f331c5c01e45630bc641939c541cece1c5002cef8`.
It had 0.20 mm radial cone clearance and 0.20 mm axial ear clearance. The full
case had also been printed: shape and hinge operation were acceptable, but
play and weak retention were not. These observations supersede earlier notes
saying physical testing was outstanding.

## Diagnosis and test hypotheses

The old baseline tooth tip lay 0.4 mm from the wall and its catch reached
1.4 mm: their peak projections overlapped by 1.0 mm. The supposed deep variant
moved the tooth to 1.2 mm and extended the catch to 2.2 mm, leaving the same
1.0 mm projected overlap. Its slopes changed, but its nominal bite did not
increase. Both retaining faces were ramps, allowing a pull to push them apart.
Earlier descriptions calling that a deeper engagement were misleading.

The new loop's rail sits beneath a flat retaining shoulder with 0.4 mm vertical
clearance. A top entry ramp assists closure. Pull the loop outward to clear the
shoulder before opening. Greater spring stiffness alone would not correct a
missing undercut; this changes the load-bearing contact geometry.

The previous small coupon had only one short joint. All new samples use two
conical joints 36 mm apart, with the same physically printable 0.20/0.20 mm
clearances. A rigid CAD tilt test about Y first detected collision at 1.6 degrees
for a single joint and 0.5 degrees for the pair (0.1-degree sampling). This
supports testing bearing separation before making the gap smaller again. It
does not measure printed friction, flex, axial play or wear. The production
case already has two joints; this comparison is against the previous coupon.

| File stem / embossed label | Hypothesis | Nominal outward travel to clear catch |
| --- | --- | ---: |
| `A_twin_hinge_loop_1p8` / A | Spaced bearings plus positive loop retention | 1.8 mm |
| `B_twin_hinge_loop_2p6` / B | More engagement travel tolerates greater relative movement | 2.6 mm |
| `C_located_loop_2p6` / C | B plus internal locating tabs reduces closed sideways movement | 2.6 mm |

Begin with A. Compare B if A's release is comfortable but you want more engagement
margin. Compare C with B to isolate the locating tabs. Their nominal side-wall
gap is 0.20 mm, engagement height 2.5 mm, with chamfered entry. Labels are embossed
inside the samples. The rail is 1.8 mm thick in the release direction: B's 2.6 mm
is travel needed to clear the overhanging catch, not 2.6 mm of contact area.

## Print and test

Use PETG, 0.4 mm nozzle, 0.2 mm layers and your calibrated printer profile.
The diagnostic slices used 5 perimeters, 8 top/bottom layers and 5 mm brim,
with supports off. Each sample is about 60 × 104 × 39 mm open and uses about
63 g including the diagnostic brim (roughly 5 h 40 min at generic speeds).
Keep both halves together in their supplied positions and orientation.

These samples deliberately include a 12 mm bridge across the loop between two
anchored leaves. The catch's flat retaining lip also has a **one-sided overhang**
of about 1.9 mm for A or 2.7 mm for B/C beyond its buttress. It is not a bridge
anchored at both ends. This is the main print risk: sag or roughness can consume
the 0.4 mm vertical latch clearance. Inspect that underside and the loop bridge
before judging fit. No added supports are generated, but print success is not
established. A is the less demanding starting trial.

1. After cooling and removing the brim, gently free both hinge joints. Compare
   side tilt while open, before involving the latch. Do not force a fused joint.
2. Pull the loop outward while closing the first time; let it return beneath the
   catch. Confirm it has seated, rather than resting against the catch tip.
3. Try opening without operating the loop. It should stop against the flat
   shoulder. Then pull the loop outward and open deliberately.
4. Compare ordinary snap closing, release comfort, sideways play when closed,
   and retention during a gentle shake. Record whether any failure is bridge
   sag, hinge binding/play, failure to seat, or escape after seating.

Report the embossed letter, print settings, and those observations. No glasses
are needed for these trials. They do not validate impact resistance, fatigue,
the full case's stiffness, or a load rating. These are candidate fixes for
physical comparison, not a claim that the final case now stays shut.

## Verification and references

`closure_trials.py` is the source and builds/exports all three candidates.
`VIEW` selects print, closed or a central latch section; `SELECT` chooses the
rendered candidate. Each export contains two valid, separate solids. Checks
cover closed fit, shell/hinge sweep, bed contact, positive interference on
opening with the latch seated, and clearance after outward release. Rigid
release displacement checks do not simulate the bending leaves or their stress.
`verify_closure_exports.py` reimports STEP and checks its solids and bounds
against the watertight STL meshes through CadQuery MCP.

See `closure_review/` for the profile, layer images, exported mesh checks and
slicer summary. All three slices completed without stability warnings or added
supports. Layer inspection identified the supported loop bridge and the separate
catch overhang; the absence of a warning does not certify either.

Design reference: [Formlabs snap-fit guide](https://formlabs.com/uk/blog/designing-3d-printed-snap-fit-enclosures/)
describes a cantilever returning after insertion and an undercut providing
retention, with geometry and material controlling release. Its general
principles informed the loop latch; its process/material advice is not a PETG
clearance or fatigue specification. Dimensions above are this project's trials.

The superseded hinge coupon and five tolerance-sample STL files were removed
to make the current choices clear. They remain recoverable at `1c6b8c3`, along
with their source and slicing evidence. The production source no longer
regenerates those obsolete sample exports.
