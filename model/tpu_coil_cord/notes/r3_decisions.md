# R3: round, tight, horizontal, approximately 70 mm × 15 mm

The user printed R2 and prefers R1 in practical feel. The thicker cord, outboard
end frames and non-round outline are unwanted. R2 print success is not evidence
that its recoil or cleanup improved; those outcomes and actual settings were
not reported. The user requests a round helix similar to R1, kept horizontal,
with merged terminal loops, substantially tighter gaps, and about 70 mm overall
compressed length. A follow-up specifies about 15 mm outside diameter, including
the terminal loops. That latest size supersedes the initial finger-scale diameter.

## Selected geometry and finish line

- 15.0 mm nominal outside diameter; 8.6 mm bore.
- 3.2 mm round cord, 20 turns, 3.35 mm pitch, 0.15 mm nominal axial gap.
- 67.0 mm helical centerline rise + 3.2 mm end-section envelope = 70.2 mm overall.
- Horizontal axis X. The full circular envelope is preserved: no shaved feet,
  asymmetric peak, added end frame or outboard connecting tab.
- Closed terminal turns use the same major radius and section as the winding,
  overlapping the terminal regions within the original envelope, as on R1.
  Those terminal joins are intentional and must stay intact during freeing.

The round section has 8.04 mm² nominal area, versus R1's 8.32 mm² hexagon and
R2's 21.24 mm² round section. This restores R1-like material quantity rather than
pursuing the rejected stiffness increase. Twenty turns make a longer spring;
R1 force/feel is not inherited, and no force or usable extension is rated.
The circular outer envelope is uniform around its axis. The winding's helical
phase and closed ends do not make the entire object mathematically axisymmetric.

The 0.15 mm gap follows the explicit request to tighten substantially beyond
R2's 0.8 mm and R1's 0.4 mm. Do not carry the R2 check's 0.6 mm criterion into
this revision. The R3 local geometric screen is 0.10 mm minimum at sampled
adjacent-turn witnesses; this is a geometric guard against unintended closure,
not a calibrated minimum printed gap. Physical adhesion/stringing may still
require hand release. Printed-material spread and recovery are unmeasured.

The round lower surfaces start as narrow contacts on the bed and widen through
the first layers. The round upper bore closes through overhangs/short bridges.
Review actual first-layer and upper paths and the support probe; do not assume
that horizontal orientation alone solves all printing issues. Keep the existing
TPU 0.4 mm / 0.2 mm solid Classic setup with automatic bridge directions. A
selected-profile slice and local CAD/path checks are enough to choose this
physical trial; no guessed elastic modulus or dynamic recoil simulation is used.

## Construction attempts retained as history

An initial approximately 20 mm-diameter R1-like faceted section built and
exported, but the horizontal slice failed (Orca result return_code -100; only a
generic slicing-failure message was retained). Do not assert a diagnosed slicer
cause. Independently, the sharp radial tip of that section makes very narrow
horizontal bed contacts. The 3.2 mm circular section was selected for similar
material area, a rounder cord and broader contacts near the lowest points.

The first long periodic helical surface produced an approximately 102 MB STL
at the required 0.003 mm absolute meshing settings. Construction now uses native
one-turn helical edges, joined into the same winding before sweeping. This bounds
each surface's parameter span while preserving the intended geometry; tolerances
are not loosened to force export.

Sequential torus/helix fusions for round terminal turns gave unreliable results:
one rejected build retained only a terminal torus, despite a positive kernel
validity flag. The failed STL export and tiny STEP output supplied a concrete
reason to inspect native faces/solids/material content during diagnosis. Those
are targeted failure diagnostics, not a routine export-audit requirement.
At the final 15 mm outside diameter, fusing all three bodies simultaneously
retained the helical centerline and produced valid geometry before surface
unification. A subsequent clean/unify operation invalidated that result, so it
is omitted. Source guards now require material at three retained centerline
stations to reject loss of the winding before publication. The final delivered
native report, not these abandoned attempts, owns current export/slice evidence.

## Physical trial

Print one R3 horizontally as supplied, using the same TPU if available. Preserve
solid material and automatic bridge directions; the existing profile's R2 name
is historical metadata and does not select geometry. Cool before freeing middle
turns gently. Stop if freeing tears the cord. Keep closed terminal-turn joins.
Report whether the tighter gaps remain separate, whether circular roofs sag,
which surfaces need cleanup, and whether R3 feels preferable. For comparisons,
use the same extra end-to-end extension and similar pull/release speed, not the
same fraction of relaxed length. No heavy load or prolonged hold is required.

Keep R1 as the preferred printed control and R2 as superseded evidence. The
finish line is one round, compact, approximately 70 × 15 mm horizontal test
spring with integral ends, source/STEP/STL and scoped geometry/slice evidence.
If printed release or roof quality fails, that failure changes the next printing
choice; a numerical force prediction would not settle it.


## Final evidence and handoff reflection

The final native report covers the 15 mm outside-diameter source, matched STEP
and STL in the same horizontal placement, and a completed centered TPU slice
with no filtered notices. The separate view report has the same artifact identity;
its opened isometric image shows the round envelope, tight winding and integrated
terminal turns, without outboard eyes or flats. The chosen Q2C / TPU 0.4 mm
setup retains 0.2 mm layers, three walls and solid material; reference nozzle/bed
values are 230/35 °C, not a recovered record of either physical print.

Twenty-four paired material/void witnesses passed across three middle turns and
eight angles, including ±0.025 mm about each gap midpoint. Two isolated native
crops across adjacent turns measured 0.149391 mm shortest clearance, above the
0.10 mm geometric screen. Both terminal bores are empty, and material anchors in
both terminal turns and the middle belong to the same connected native solid.
This addresses the demonstrated terminal-fusion failure without routine generic
solid-count, bounds or mesh audits. There is no continuous printed-clearance claim.

The first-layer path image retains separate contact patches along the complete
winding. The opened primary Z12.2 roof image overlays Z12.0 paths in gray, current
ordinary paths in blue and bridge-labelled TPU in orange. The 2.14 mm longest
bridge-labelled deposition segment includes anchors; it is not an unsupported-
span measurement. The automatic probe generates Support and Support interface
roles from Z0.2 through Z11.8 around the feet and inside the bore under circular
upper surfaces. This is a materially larger support signal than R2's low-foot
signal, and it is not dismissed as an absence of supports. The selected print
is deliberately unsupported: supports in the long 8.6 mm bore and 0.15 mm turn
gaps would introduce difficult TPU removal, while asymmetric roofs or feet
would undo the user's explicit form preference. Circular roof sag, small contact
adhesion and tight-gap fusion remain open physical outcomes of this prototype.

R2 and R3 now share the identical linear relative-extrusion reader in the local
`gcode_paths.py`, replacing a duplicated reader in the active diagnostic. It
rejects relative XYZ, absolute E and arcs after the first layer marker. Its
extrusion roles reproduced both retained R2 primary/probe role sets; the R3
actual-path review ran successfully through the same reader. No old CAD, exports
or slice receipt was rewritten as a consequence of this small extraction.

Reflection: a higher section rigidity was not a substitute for the user's preferred
feel and uniform form. The user's rejection changes the selected architecture
and readiness even though R2 had printed. R3 follows the requested round,
compressed geometry rather than preserving R2's local print advantages. These
preferences and uncertain print outcomes stay object-owned; no universal gap
minimum, TPU modulus or spring-return rule is inferred. The next useful evidence
is this physical print, not another geometry or force-optimization study.
