# R2 selection: higher pull force and cleaner separation

The [current object record](../README.md) owns the next print. The
[first implementation record](r1_baseline.md) and original source/exports remain
the printed control. The user says R1 works reasonably well, but release leaves
rough surfaces and recoil is too weak. Very high wall count made the actual
print practically solid. Exact printer/profile, material batch, printed hash,
extension, force, dwell and recovery time remain unknown.

## Architecture comparison before detailed construction

The user explicitly delegates exploration and selection. The
[schematic screen](../renders/concepts/r2_architecture_screen.svg) compares:

| Route | Effect on recoil | Printing / surface consequence | Decision |
| --- | --- | --- | --- |
| Thicker upright circular helix | Increases section stiffness | Larger pitch can reduce fusion, but stacked undersides and peeling remain | Retain as fallback, not selected |
| Circular helix laid horizontally | Can retain the same spring geometry | Each turn can have a foot, but circular upper bore closes through broad overhangs; support can spoil the inner surface | Not selected for this first horizontal trial |
| Horizontal rounded-house coil | Thicker cord, smaller transverse circuit, fewer turns | Each circuit has a flat foot; sideways turn gaps stay clear of roofs; angled roof closes with a small rounded apex | Selected as one new printable sample |
| Preloaded assembly or higher-rebound material | Could change initial tension or material recovery | Extra assembly/unknown stock or changed material; would confound this TPU geometry experiment | Consider only after feedback if recovery remains limiting |

A is amber and C green in the schematic; both represent the same TPU material.
These are design directions, not physically tested alternatives. The drawing
is schematic, not a dimensional CAD or print proof. R2 remains a real three-
dimensional winding: each circuit advances along X continuously, rather than
being a set of separate loops or a planar zigzag. End frames close the winding
at both ends, preserving hook attachment without an extra part.

## Why this should pull harder

[Mid-West Spring's engineering note](https://www.mwspring.com/rate-formula/)
gives the standard close-coiled round-wire relationship
`k = G d^4 / (8 N D^3)`: increasing wire size and reducing coil diameter/active
turn count raise spring rate. This is a direction screen for our design, not a
numerical force formula for thick, noncircular, printed TPU coils.

R2 uses a 5.2 mm round cord instead of R1's 4.0 × 3.2 mm chamfered hexagon, and
four total circuits rather than six. Its transverse path is smaller than the
original 16 mm mean-diameter circle. Section rigidity and turn count are the
chosen levers; increasing fill cannot explain an improvement over the user's
already practically solid baseline. The section screen retains applied dimensions
and its limited analytical conclusion separately from the physical test.

There is no deliberate assembly preload or initial tension. Force approaches
zero near the original shape in an ordinary unstressed elastic spring. We have
not created a constant-force retractor. R2 trades some stored cord length and
available extension for force. No extension ratio or force gain is rated.

[Qi & Boyce's TPU experiments](https://doi.org/10.1016/j.mechmat.2004.08.001)
report hysteresis, rate dependence and cyclic softening in their tested TPUs.
That supports treating restoring stiffness and energetic snap-back as separate
questions; it does not calibrate this user's filament. An isotropic static FEM
with guessed TPU properties would not establish recovery speed or printed
hysteresis, so no such model is used. The finish line is a meaningful geometry
change with clean manufacturable gaps, a selected-profile slice and a physical
comparison against the existing R1 sample.

## Manufacturing and experiment

Keep TPU, 0.4 mm nozzle, 0.2 mm layers, Classic paths and solid material. Use three
walls plus 100% fill, or the user's high-wall-count approach for a closer process
comparison. The shared solid TPU profile is retained; it is a diagnostic setup,
not a recovered record of the user's settings. No supports, brim or ironing are
planned. Every circuit's round bottom is flattened 0.6 mm at the bed plane.
The four-circuit centerline advances 24 mm; the 5.5 mm outboard frame offset and 5.2 mm frame thickness give
40.2 mm total length. The width is 19.2 mm, and planned peak height is 17.4 mm. Native corner rounds reduce the
sharp theoretical roof height. Hook frames have rounded edges and preserve the
open house-shaped bore.

Nominal sideways turn spacing is 0.8 mm. This is larger than R1's 0.4 mm but
still small; it is an experimental clearance, not a statement that the user's
printer lacks precision. Most importantly, it is lateral rather than a small
vertically stacked gap. Sweep inclination reduces the shortest normal gap
slightly; evaluate the actual adjacent-circuit geometry before claiming clearance.
Broad 6.0 × 4.2 mm foot tabs join the outboard eye frames to the terminal feet.
They avoid relying on coincident frame/sweep surfaces and put a substantial load
path below the hook opening. This costs extra end length; the active four-turn
coil itself advances only 24 mm. Middle turns must not
be welded. A roof apex still needs a short closure and round cord undersides
still overhang locally, so inspect actual paths/support probe and test printed
surface quality. Supports in turn gaps would defeat the selected clean-release
architecture.

Cool the print, remove it and check whether the middle turns are already separate
without peeling broad faces apart. Compare R1/R2 at the same extra end-to-end
extension and similar pull/release speed, first gently, then over several short
cycles. Do not equate "twice relaxed length" across different sample lengths.
Record force feel separately from recovery speed and residual length immediately
and after a short rest. If gaps fuse or the roof sags, revise printing geometry
first; if force rises but recovery stays slow, material damping is still a
possible limit, not evidence that more infill is needed. No heavy load or long
hold is required for this first geometry comparison.


## Construction evidence and abandoned implementations

A single interpolated spline for all four circuits was unsuitable for native
sweeping: default transport failed even for a small profile; fixed-binormal
transport built a small-radius tube, but the full evaluation exited with an
EOFError before publishing any exports (native report elapsed about 584 s).
The execution metadata records failed run `e049a86f1f6e42a48916f86968571a54`
with EOFError. No completed geometry or slice was recovered or promoted.
The specific native termination cause was not established.

The replacement uses exact straight edges and helical corner arcs, with X
advance proportional to transverse path length. Each arc endpoint is checked
against its adjacent line to 0.00001 mm. This is the same selected physical
architecture with a simpler exact construction, not a new scheduler or solver.
The native CadQuery sweep then produced valid cord geometry. Directly intersecting
the original end frames with the coiled tube produced an invalid combined shape;
a small frame inset and a 0.00001 mm fuzzy union did not resolve it. Those attempts
are not deliverables. Instead, outboard frames and broad foot tabs make the
intended terminal connection explicit. End-frame extrusion rims have 0.6 mm
rounds; tab vertical edges and top edges are rounded 0.8 and 0.6 mm respectively.


The first valid horizontal slice, with 0.25 mm foot flattening, completed without
notices. The auto-support probe generated Support roles only at Z0.2/0.4/0.6 mm
around the lower round-foot flanks; no Support interface roles or roof-height
supports occurred. The first-layer image showed all four circuit feet and both
end frames on the bed. This prompted the final 0.6 mm foot flattening, increasing
bed contact and reducing the initial overhang. The isolated section screen is
for the untrimmed round cord, not a claim that this flattened foot has exactly
the same rigidity. Primary bridge paths at Z12.8 in this superseded shallow-foot
slice were at end-frame roof closures, not between adjacent coil turns. The
final native receipt and path review supersede those stage-specific observations.


## Final review and limits

The final 0.6 mm flattening model and R2 automatic-bridge process are associated
with their paired exports by `r2_cad_slice_review.json`. Native geometry is valid,
the centered Q2C/TPU 0.4 mm / 0.2 mm slice completes, and no filtered notices
occur. The support-probe review flag remains true: low supports still occur only
at Z0.2/0.4/0.6, around lower foot flanks. Increasing foot flattening did not
eliminate that signal; do not claim otherwise. Supports remain disabled for this
experimental print. The broad feet are on the bed, lower overhangs grow over
existing material through a few layers, and any remaining roughness is on
accessible undersides rather than bonded faces between successive turns.
No supports are proposed at the roof or inside the raised winding. This is a
reviewed manufacturing risk for a small trial, not physical qualification.

The inherited fixed 180-degree bridge directions were reconsidered after viewing
actual frame-roof paths. A separate R2 profile uses automatic external/internal
bridge directions and no model-direction alignment. The final paths were opened:
Z0.2 retains each foot; Z12.4 closes both end-frame roofs, with bridge paths now
running across the opening between existing roof sides. The image overlays
Z12.2 paths in gray to show the surrounding supporting material. Orange is
Bridge-labelled TPU, blue other current-layer TPU; these are the same material.
The longest bridge-labelled deposition segment is about 4.06 mm, including
anchored portions; it is not a measured unsupported span. The frame profile has
sloping sides and a small rounded inner apex. All remaining sag/adhesion claims
require the print. No extra material/profile changes or slicers are introduced.

All 20 sampled centerline/gap witnesses passed, including gap-side witnesses
±0.2 mm around the center of the nominal opening. Three matching local native
material crops measured 0.74418, 0.74418 and 0.74384 mm shortest separation,
above the preselected 0.6 mm geometric trial screen. Both eye-center witnesses
are open, with occupied foot controls. This is targeted geometry, not a generic
bounds/mesh audit, and the geometric threshold is not a printed-clearance rating.

The ideal untrimmed R2 circle has 21.24 mm² area versus R1's 8.32 mm² hexagon
(2.55×). Its Saint-Venant torsion constant is 71.78 mm⁴; R1's exact polar area
moment is 11.23 mm⁴, an upper bound on R1's Saint-Venant torsion constant.
Thus the isolated ideal section has a strong rigidity increase under the same
isotropic elastic material assumption. The section ratio 6.39 is not a force
multiplier for either complete spring. Foot trimming, end restraint, noncircular
path bending, thick curved-rod effects and printed anisotropy/hysteresis are
outside that section screen. No guessed material modulus or return-time model
is needed to choose this next physical trial.

Handoff reflection: the useful local lesson is to keep the printed control and
separate increased restoring stiffness from TPU's energy recovery. A clean
slice does not explain rough physical separation. Horizontal spacing addresses
that observed manufacturing interaction directly. Exact segmented paths and
outboard eye tabs removed the CAD construction failure; no shared API or generic
performance framework change is justified. The next useful evidence is the
user's print, not more numerical variants.
