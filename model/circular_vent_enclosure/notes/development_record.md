# V1 development record

The [object README](../README.md) owns current print/use instructions and readiness.
This record retains the decisions and discarded local geometry, not extra print variants.

## Method and finish line

Use exact CAD for nominal fit and forbidden material, geometric sections for an
initial airflow bottleneck screen, and Orca for the actual print layout and
support probe. Flow rate, downstream pressure, acoustic spectrum, actual rim
profile, fixture strength and printed properties are unavailable. CFD, acoustic
simulation and FEM would introduce decisive unknown boundary/material inputs;
they cannot qualify quietness or retention here. Finish a simple parametric V1,
paired print exports, useful views and a smoke slice, retaining those physical
questions explicitly. Single-piece architecture avoids an unqualified assembly joint.

## Interface update

Initial brief supplied Ø130 mm and 35 mm projection only. The user's follow-up
supplied approximately 20 mm rim height plus 15 mm gap to the disc. This replaced
an earlier speculative 25–35 mm emission band with the complete approximate
20–35 mm band. It does not identify a grippable Ø130 mm cylinder. The swept Ø130 mm
CAD envelope is deliberately a nominal collision reference, not measured valve CAD.
The 6 mm collar remains behind the air band. Fit clearance of 0.8 mm diametral
provides insertion room, not a holding-force source.

## Material reduction

The first 213 × 85 mm construction used 2.2 mm shell / 2.8 mm front, eight short
front ribs ending at radius 88 mm, and 46 × 37 mm windows with 45° roofs and R2 tips.
Its nominal projected exits were 93.62 cm². CAD solid-volume mass at an assumed
1.27 g/cm³ PETG density was 262.24 g, with 0.1562 N·m wall-axis gravity moment.

The user explicitly requested reducing material while retaining function. The
selected version uses the brief's lower shell/front thicknesses, 2.0 / 2.4 mm,
with eight 2 × 3 mm ribs extending into the R3 floor/wall blend and rounded rib
crests. Without the final window revision, this was 234.01 g; the delivered shape
is 233.27 g, 11.05% below the initial solid-CAD estimate. No measured plastic
density, strength or dynamic panel response is implied. Six top/bottom layers
make the front solid at the selected 0.2 mm layer height; other infill remains 7%.
The earlier default diagnostic profile estimated 203.32 g, but had fewer solid
face layers. Its mass must not be compared directly with the final 220.88 g slice
as an equal-stiffness material comparison. The 11% comparison is geometric under
the same assumed density, not a measured filament saving.

## Window/support refinement

The original slice completed without notices but the automatic-support probe
created tree support up to Z43.0, around radii 98–101 mm under the rounded window
tips. Reviewed the retained probe G-code using the shared
`physical_analysis.manufacturing.orca_linear_paths` reader; this was a local
support-location diagnostic, not a footprint or mesh audit. Supports could be
accessed through the openings, but removing the local need better fits V1 intent.

The final roofs rise 1.5 mm per tangential mm (56.3° from horizontal), use 0.65 mm
tip rounding, and extend the window height to 43 mm to preserve area (94.60 cm²).
General window corners remain R2 and exposed lips R0.65. The final selected-profile
auto-support probe generates no support. There is no broad horizontal bridge;
physical tip closure and PETG sag still require a print. This is local evidence
for this geometry/profile, not a universal printable tip radius or angle.

## Geometric flow screen

Measured actual post/window rays on the CAD. The uncut revolved interior is
axisymmetric; window cuts remove material and cannot reduce its circular core.
Two rays separated by half the window pitch cover a post and window under the
8-fold symmetry. Rear radial clearances are recorded at selected heights, and
four downstream sections at 2 mm intervals screen the entrance to the forward
chamber. A separate continuous annular keepout boolean checks 12 mm radial
clearance through the entire 20–35 mm band.

The local rear-band annular area of 58.34 cm² is not a complete-flow throat:
air enters throughout the 15 mm axial gap. The nominal source cylinder area
2π × 65 × 15 = 61.26 cm² describes only that idealized source geometry. Once past
the disc, the added annular section is at least 134.87 cm², the conservative front
turn area is 182.15 cm² (using the gap above ribs everywhere), and nominal projected
exit area is 94.60 cm². Projected area does not capture contraction, edge losses,
unequal outlet flow or the complete 3D minimum hydraulic section. Actual pressure
loss and noise remain unmeasured. None of these numbers is an airflow rating.

## Structural and use screen

With the density assumption, the delivered shape weighs about 2.29 N. Its geometric
centroid gives 0.1385 N·m gravity moment about a wall mounting plane with horizontal
axis; ceiling withdrawal differs. No friction coefficient, contact preload,
attachment capacity or load rating is available, so no analytical retention PASS
is claimed. The loose collar carries no demonstrated load.

The front has eight shallow radial supports joined into the shell blend instead
of an extra baffle. The 2.4 mm solid front satisfies the brief's thickness floor;
its stiffness/resonance is unqualified. Do not pursue a speculative modal solve
without relevant pressure/acoustic loading and a useful acceptance criterion.
Removal gives direct rear access for rinsing and inspection; drainage depends on
actual installation orientation and needs observation.

## Parametric and software review

Shape building writes no files; CAD publication stays in the shared evaluator.
The dataclass rejects nonfinite/nonpositive dimensions, invalid shapes/counts,
insufficient roof height, excessive taper and invalid height stacks. Unknown
variants are rejected by the shared product-verification CLI. User intent is
preserved in `brief.md` and its reviewed verification inventory. Physical and
subjective obligations stay UNKNOWN; nominal CAD PASS cannot satisfy them.

Construction spot checks: six windows at width54/height45.5 and eight teardrops at
width42/height55 both built valid CAD. They were not exported or sliced, and do
not inherit the delivered eight-pointed-window print evidence. Invalid shape,
roof slope, engagement and rib-count inputs were rejected. The standard entrypoint
conformance suite passes all 12 tests for this product.

Final review covers actual delivered STEP/STL geometry, placement, supplied profiles
and tool identities through the native evaluator's publication guards. The final
source review adjusted a fixed window-height restriction into a shoulder-relative
limit and made cutter depth follow hood/bore radii, so those parameters remain
usable. Rechecked final exports after these changes; no hand-edited mesh or STEP.

## Reflection

The consequential lesson is local: preserve the known emission band's clearance
before optimizing plastic, and compare mass on an equivalent geometric/process
basis. A smaller rounded window tip and steeper roof removed a concrete support
signal while preserving outlet area. Existing tools and guidance covered this
work; no shared API change or general manufacturing rule is justified by V1.
