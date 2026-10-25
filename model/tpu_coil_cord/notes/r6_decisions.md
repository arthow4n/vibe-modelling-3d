# R6 rejected: circular winding with shaved contact flats

**Rejected by the user before printing. Do not print R6.** Its round swept cord
plus isolated exterior trims misinterpreted the requested continuous flat-sided
swept profile. CAD/slicer success below remains historical manufacturing evidence,
not product acceptance. See [R7 decisions](r7_decisions.md) for the correction.

## Intent and retained baseline

The user returns to the cord after accepting R5 as okay. They request a circular
variant that retains flat contact, aiming to eliminate the octagonal edges and
see whether the flats provide enough printing support. This authorizes one new
short TPU printable experiment. The ~70 mm version remains deferred. The
connector's SVG concepts are a separate object and are unchanged.

R5 remains an accepted control, not a failed or superseded physical result.
Its source, exports, CAD/slice checks and physical report are retained. The
[historical R5 summary](r5_baseline.md) preserves its setup, shape reasoning,
measurements and limitations. Earlier R3/R4 had much smaller gaps and were long;
returning to a round shape does not justify repeating their failed spacing.

## Geometry and rationale

Use a native circular helix and circular 3.2 mm radial/axial profile, with five
circuits at 4.4 mm pitch. This retains 1.2 mm nominal axial gaps and 25.2 mm
relaxed length. The 15 mm untrimmed diameter is close to R5's 15.15 mm corner
envelope. Mean radius is 5.9 mm; nominal bore diameter is 8.6 mm. The circular
section, changed mean radius and changed bore mean this is a form/printability
trial, not an isolated or predicted stiffness comparison with R5.

Two opposed exterior trims remove 0.5 mm at top and bottom, leaving 14 mm
height and full 15 mm width. The circular centerline and bore are untouched.
Only these two shallow contact planes interrupt the round outer form. There are
no polygon vertices, side flats, added feet, thin tabs, brims or sacrificial
connectors. Two opposed flats retain perpendicular mirror axes in the nominal
transverse envelope and allow either flat down. This does not claim that a
chiral, advancing helix is itself mirror symmetric. A literal perfect circular
exterior and finite planar contact cannot coexist; flat boundaries remain by
intent. No extra fillets shrink the contact lands for this print trial.

The winding uses the established R3/R4 native helical sweep representation with
bounded one-turn edges. Integral circular terminal turns are fused in the same
envelope, rather than added outboard rings. The complete torus/helix union is
performed at once because historical sequential periodic unions lost middle
material despite validity. A retained-material guard spans both ends and the
middle after trimming. The R6 source is independent so historical parameter
values and accepted artifacts are not changed by imports or global overrides.

## Manufacturing decision and expected observation

Reuse the existing horizontal Q2C/TPU process: 0.4 mm nozzle, 0.2 mm layers,
Classic, three walls and 100% rectilinear fill (or the user's high-wall solid
approach). Keep supports, brim and ironing off. A brim can link adjacent feet;
TPU supports in the bore/gaps would complicate freeing the spring. The flats
address contact area; they cannot establish bed adhesion or eliminate the
round bore's unsupported roof. The experiment intentionally tests the return
to curved overhangs. Its result must be judged against the accepted R5 print,
not inferred from a support-free reference toolpath.

The 5 mm² per-middle-foot geometric screen and 1.0 mm local gap screen are
retained from R5 before measurement. They can reject an inadequate flat or
lost clearance; neither is a calibrated adhesion threshold or TPU tolerance.
The local review also checks winding material, empty neighboring gaps, a
4 mm-radius open bore at 36 angular locations and open terminal centers.
Source and G-code hashes bind its local evidence to reviewed inputs.

The selected supports-off slice and the automatic-support probe have different
roles. The actual path plot shows separate first-layer feet, middle side-wall
paths, proposed support locations and the first roof bridge layer. The roof
midpoint check is a bounded continuation of the prior gap-crossing screen,
using 0.005 mm for STL deflection/G-code rounding, not gap allowance. It does
not qualify bead widths, all toolpaths, adhesion, sag or spring recovery.

After cooling, inspect flat adhesion, separation between the middle coils and
any bore-roof strings/sag before stretching gently. Keep the intentional terminal
joins. If roofs fail while feet hold, the contact experiment succeeded in one
respect but round overhang printing remains unresolved; do not automatically
make the long version. No force gain, safe load, fatigue life or maximum
extension is claimed. Exact spool and user Cura settings remain unknown.

## Delivered evidence and handoff reflection

Final native geometry is valid in CadQuery 2.8.0. The paired horizontal exports
and opened isometric/end views show round winding/cord, a circular bore, two
shallow opposed flats and integrated terminal loops. OrcaSlicer 2.4.2 accepted
the centered layout with the same complete printer/process/filament triplet as
R5. Effective settings retain 0.4/0.2 mm, three walls, 100% rectilinear fill,
no brim/supports and reference 230/35 °C temperatures. The automatic probe
still generates support/interface, reaching Z12.2 inside the roof; it remains
a deliberate experimental uncertainty rather than a clean support-free verdict.

Thirty-six material/gap/bore witness sets pass. Open terminal bores pass. Four
sampled middle feet each have about 10.01016 mm² contact, exceeding the retained
5 mm² local screen. Total planar contact is 60.76717 mm²; local adjacent-turn
clearance is 1.19163 mm, exceeding the 1.0 mm screen. All 101 bridge midpoints
at Z11.8/12.0 are inside sampled current-layer material at 0.005 mm numerical
tolerance. The first-layer, side-wall, support-probe and roof path image was
opened: feet and middle sections remain separate in the selected slice.
These outcomes satisfy local geometric intent, not printed adhesion or roofs.

The reflection is product-local: R5 acceptance allows a return to round geometry
without undoing its larger spacing and short test length. Preserve the accepted
control and change contact/form explicitly. No new universal TPU gap, support,
material or adhesion rule is inferred; existing native export and path tools
were adequate and need no shared-framework change.
