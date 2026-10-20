# Short-lap slim box — end-wall snaps, separate cap

## Authorized direction — 2026-10-19

The user discards the hinged box and reopens the small-bite wall-snap direction.
The earlier noisy/firm short-sample observations remain physical evidence, but
noise is now potentially acceptable. The user hypothesizes that less overlap
will reduce the nuisance and asks for a grounded shorter range with very good
retention, including resistance to sideways handling. This supersedes the stop
on this closure family; it does not reverse the hinge trial's physical failure.

The printed M1 remains the usable baseline with inadequate retention. Historical
R1–R4 specimens and their force calculations remain untouched. This revision
uses R2's opposed end-wall bumps: the complete walls bend, without independent
cantilever arms. A ramped snap can pull open; it is not a separately released lock.

## Sideways-hit clarification — 2026-10-20

The user explicitly means that **a sideways hit must not open the box**. This
is an unintended-release requirement. The current prototype has **UNKNOWN**
coverage: neither the 2 N static stiffness comparison nor the 11.22 N centered
slow-pull estimate establishes that the cap stays attached during a lateral hit.
The intended use is knocks and bumps inside a travel bag; no numerical impact
severity has been specified or measured.
The coupled-release investigation is **INCONCLUSIVE**. Keep the current 30 mm
prototype; the available results do not justify a further overlap reduction or
a side-impact force rating. No geometry fix is claimed from these snapshots.

Review of the current geometry and study fixtures identifies the missing path:
a hit can rock the cap, spreading a receiving wall and loading one ramped bite
before the other. Sequential peel release is a possible failure mode, not an
observed failure of this unprinted candidate. The guide study omits the bites;
the side-bearing study observes bearing-band motion, without solving snap
engagement; the pull model prescribes axial withdrawal and independent catches.
Together these do not determine whether that lateral escape path is blocked.

Further retention work must track both bites through lateral rocking and wall
deformation, including one-bite release followed by the other. A defined lateral
impact on a loaded full box must ultimately establish closure retention under
its stated hit location, support, direction and severity. The short joint sample
can assess local fit and effort but omits the full box's inertia and leverage.
The 30 mm candidate remains a prototype; no sideways-hit rating is assigned.

The user subsequently specifies **knocks and bumps inside a travel bag**, and
authorizes verification and correction. The computational question is
whether the complete cap, with axial movement free, peels off the deformable
30 mm joint during transverse roof displacement. The body perimeter is clamped
16 mm below the seam; a small roof patch moves sideways, with its axial DOF free
and an explicit .05 N seating bias. This is a quasi-static weakness search, not
an impact-time simulation or measured bag load. A provisional 10 N lateral
roof-force comparison is agent-selected, not user acceptance or a safe rating.
Inspect contact/engagement and stop this route if failed numerical quality or
resource limits prevent interpretation; do not infer retention from failure.
If a weak escape path is found, revise it before refining force precision.
Otherwise resolve relevant mesh/increment/contact sensitivity to about 10% and
retain the need for a loaded physical knock test.

The [rigid contact-sequence search](short_lap/rocking.json) includes both bites,
both principal rocking axes and initial shifts of −.10 / 0 / +.10 mm. With no
initial shift, widthwise rocking picks up the far bite at **.0877–.0881°**,
before the guide at **.1941–.1945°**. At the adverse +.10 mm shift these become
**.1568–.1572°** and **.3904–.3907°**. Broad-face rocking at +.10 mm shift also
picks up both bites before its guide. Thus the guide-only angle cannot be used
as free assembled motion or a retention limit. A rigid ±.10 mm widthwise shift
alone gives a tiny **.00112 mm³** flank overlap at the near bite; a printed joint
would have to deform there. That overlap is not a measured preload or failure.

The initial [full](short_lap/flex/lateral_x/baseline/result.json) and
[mirror-half](short_lap/flex/lateral_half_x/baseline/result.json) contact attempts
were deliberately interrupted during initial contact settling, with **no accepted
loading frames**. The initial simultaneous side displacement and tiny seating
load did not establish the unloaded cap state cleanly; these attempts do not
show opening or establish any force threshold. Both meshes have positive
Jacobians. The revised fixture holds lateral displacement at zero over the first
10% of its load parameter to establish seating, then drives sideways with the
axial DOF still free. The half-domain has zero normal displacement on the actual
mirror plane and half the seating load; full lateral reaction is twice its
reaction. This restriction covers centered principal-plane loading, not diagonal
or asymmetric impacts. The fresh solve reuses only the identity-checked mesh,
never the interrupted displacement/contact solution. Source:
[lateral study](../short_lap_lateral.py).

The later seated runs were interrupted before completing their loading paths;
accepted snapshots survive, but **neither run is a completed retention study**.
The additional initially shifted-cap attempt never accepted a frame. These
interruptions are not measured opening events. The native process owners no
longer existed when work continued, so incomplete jobs were not called complete
or silently resumed. The shorter targeted restart uses fresh solutions, the
previous finalized X-half mesh only, and a fresh Y mesh. Its first mesh-reuse
attempt correctly rejected the orphaned runs' missing final receipts; the retry
preserves this guard rather than fabricating a receipt.

| Diagnostic accepted state | Equivalent full lateral roof force | Additional inward tooth retraction needed on sampled axial withdrawal |
| --- | ---: | --- |
| Widthwise X, .889 mm roof drive | 12.64 N | Negative-X tooth: **.028 mm**; positive-X tooth: **.347 mm** |
| Broad-side Y, .356 mm roof drive | .00298 N | Both mirrored end teeth: **.506 mm** |

These are **conditional static snapshots, not safe-force or impact ratings**.
The X state consumes nearly all capture at one bite while the other remains
engaged; it does not demonstrate complete cap release. Its roof has lifted
.406 mm on average despite the small seating bias. The Y state lifts .104 mm,
primarily taking up geometric play before bearing.
Snapshot force-balance errors are below 3e−7 relative; reported contact
penetrations are .00798 / .000111 mm, below the provisional .03 mm screen. No
mesh, increment or contact sensitivity has qualified these coupled results.
The largest absolute principal strain is .713% / .00105%; uncalibrated isotropic
PETG supplies no printed strength or impact allowable.

The last accepted-step records at X=.22 / Y=.16 were initially inspected as
17.81 N / 1.084 N states. Their complete nodal fields yielded the preliminary
one-bite loss / remaining-capture observations. Contact-location diagnostics then
rejected them: CDIS/CSTR row counts were **3501/3481** and **348/298**.
The interrupted jobs left the final pressure blocks short by 20 / 50 rows.
Consequently those states cannot supply complete contact-quality evidence;
the table uses the preceding complete output frames instead. The inspection
reader now rejects mismatched rows, and the shared native summary applies the
same check before accepting numerical evidence. Reproduction of the retained
frames checks their full fields and original frozen input/case identities.
The existing backend's physical-intent comparison also matches the retained
X/Y shapes, material, supports, loading and numerical settings to the current
builders, and rejects a deliberately changed fixture. The capture reader uses
this association before selecting teeth with current production dimensions.
The complete X=.20 contact-location diagnostic places peak pressure on the
negative-X retaining lip; the other loaded locations are the sleeve guidance
and seam seat. Its 159.7 MPa local penalty-pressure peak is mesh/contact-sensitive
and is not a printed-material strength measurement or allowable.

The [snapshot reader](../short_lap_lateral_capture.py) keeps native IDs and
checks complete finite nodal/integration-point fields with the existing native
summary and matching contact displacement/pressure rows before inspecting
deformed surface triangles. Virtual axial withdrawal
samples 0–6 mm with radial bisection brackets ≤.01 mm. A fixed 1.2 mm inward
shift clears every sampled path as a negative control. The unloaded X control
recovers the nominal .5 mm obstruction within .01 mm. The .05 mm additional
retraction screen is agent-selected geometry discrimination, not retention-force
acceptance. Constant initial penetration alone does not count as capture.

Reports: [X loaded](short_lap/lateral_capture_seated_x_0.2.json),
[Y loaded](short_lap/lateral_capture_seated_y_0.14.json),
[unloaded control](short_lap/lateral_capture_seated_x_0.02.json).
[Actual deformed X section](short_lap/lateral_seated_x_0.2.svg).
Their [snapshot archives](short_lap/snapshots/) retain the frozen deck, case,
regions, native accepted-step log and the original selected DAT frame, gzip
compressed. Expand each file into its `scope.json` source directory to inspect
again; do not use these one-frame archives as complete-run evidence. Raw local
native jobs are ignored. The original capture reports record the source identity
used at their creation, including the native summary implementation.

The decisive physical check is the existing **full 30 mm prototype**, loaded
with the actual travel contents and printed in the delivered PETG placement and
settings below. Mark the seated seam, then try realistic knocks in the intended
bag against both broad faces, both widthwise ends and corners; inspect for a
partially lifted or unlatched end as well as complete opening. Record the bag,
surrounding contents, approximate action and direction so the result has a
defined scope. Any partial unlatching or opening requires revision before further
overlap reduction. Staying seated supports that tested use only, not a universal
impact/force rating. The joint crop is useful for fit and deliberate opening
effort, but omits body span, contents and inertia; it cannot settle this question.
The existing full prototype is more informative than another smaller coupon or
an uncalibrated impact simulation. No current prototype print is reported.

## Selected prototype and why

The delivered candidate uses **30 mm overlap**, about **62% shorter than 78 mm**.
Keep **24–30 mm** as the practical prototype range; 18 mm is not the first choice
for the complete 90 mm cap. This is a comparison-based choice, not a qualified
minimum or a measured backpack rating. The exterior stays **264 × 74.2 × 51.2 mm**.
Only the reinforced **30 mm** candidate is delivered for printing. A reinforced
24 mm lower-end trial has not been mechanically qualified; do not shorten/scale
the exports or inherit the 30 mm numbers for it.

[Actual CAD sections and comparison](short_lap/sections.svg) ·
[Full print layout](../renders/print/short_lap/short_lap_case_isometric.png) ·
[Joint-test layout](../renders/tests/short_lap/short_lap_joint_test_isometric.png)

The first comparison retained the old .65 mm bump and .15 mm guide clearance.
Its conditional nominal centered-pull peaks were **6.84 / 6.39 / 6.08 N** for
18 / 24 / 30 mm laps. The corresponding ideal undamped energy thresholds were
**2.39 / 2.23 / 2.13 N**, including no damping/friction. These are force scales
from a reduced model, not safe hanging loads. They show why shortening alone is
not a reliable retention improvement: body stiffening and cap spreading compete.
The largest guide-only roof motions in the checked principal/diagonal rigid
poses were **1.46 / 1.03 / .78 mm**, respectively, before loaded wall deformation.

A first 24 mm refinement tightened the per-side guide gap to .10 mm, used a
.8 mm bump and lengthened the closing ramp. Its nominal elastic proxy rose to
**9.95 N** slow-pull peak and **4.23 N** ideal energy threshold, but the side-load
fixture exposed substantial wall flexibility. It is retained for comparison,
not published as another print option.

The selected revision therefore uses a **2 mm sleeve and 2.7 mm cap receiving
band**, with the cap returning smoothly to 2 mm wall beyond that band. The body
and remaining cap stay at 2 mm; there are no long internal spring guards. Its
**.6 mm bump** is smaller than either the first refinement or M1's 2 mm independent
hook. The closing ramp stays longer, and the .10 mm guide gap and .10 mm axial
pocket allowance are separate choices. Printed fit remains uncalibrated.

The new central mouth is **64.6 × 41.6 mm**. Actual CAD gives .8 mm minimum
individual brush/tube passage clearance. This preserves the exterior and removes
cantilever channels, but it does **not** inherit the old full box's combined
packing acceptance. No thinner toothpaste proxy or invented taper was used.

The selected [force/energy screen](short_lap/reinforced.json) predicts a nominal
**11.22 N centered slow-pull peak** and **4.61 N ideal undamped seated-release
threshold**, at E1200 MPa, nominal fit and two independently engaged catches.
The latter compares elastic energy with driving work; it is not a drop result
or a payload rating. Across the declared E900–1800 MPa / ±.15 mm local radial-fit
scenarios, two-catch peaks span **5.80–22.06 N**, and ideal energy thresholds
**1.69–11.61 N**. These are model scenarios, not confidence intervals or guaranteed
print bounds. One engaged catch halves this independent-spring model's numbers;
actual peeling can be worse. No friction is credited for retention.

The selected guide-only worst roof motion is **.52 mm** in the checked rigid
principal/diagonal poses. That is separate from loaded wall flexibility. Nominal
linearly scaled peak-strain indicators are about **.41% body / .16% cap**; peaks
are not mesh-qualified material allowables, printed recovery or fatigue evidence.

## Comparison and fixtures

Compare **18, 24 and 30 mm** overlap, versus the historical 78 mm research lap.
Restore the printed M1's **74.2 × 51.2 × 264 mm** exterior; keep its 174 mm seam,
R4 handled ends, plain interior and two printed parts. Retain .15 mm side guide
clearance, .65 mm bump projection and the short recovery track after the snap.
Grips are recessed on the broad walls, away from the two end catches.

The question is whether a substantially shorter guide can retain a useful snap
barrier without excessive stiffness or sideways rocking. Choose the shortest
credible compromise, not an alleged universal minimum. A provisional **8–18 N
slow centered pull** is an agent-selected comparison target, not a user threshold
or achieved print measurement. Check reduced force/energy across E900–1800 MPa,
±.15 mm local radial fit and one/two engaged catches. Independently compare rigid
guide rocking and a 2 N sideways cap-end load screen (180 Nmm at the seam).
That load is a gentle-handling comparison assumption, not an impact rating.

Use exact CAD for paths, capture, fit and guide contact. New actual-CAD radial
compliance solves use the established CalculiX structural questions and a mesh
comparison to 10% displacement precision. Body: full perimeter cropped 16 mm
below the seam, lower ring clamped, 1 N inward on one crest. Cap: complete cap,
roof clamped, 1 N outward on its lip. Both use the same uncalibrated E1200 MPa,
nu .38 isotropic hypothesis as the earlier study. Combine the two compliances
with the actual snap profile using the existing elastic-energy derivative.
These fixtures compare geometry, not a hand or full deformable joint contact.

If the shorter candidates become too stiff, lose engagement under guide play,
or rock excessively, lengthen within the tested range or revise the local bite;
do not infer that shorter is automatically quieter or easier. Stop numerical
refinement once the choice is resolved to this precision. Friction, printed
anisotropy, creep, peel/impact, actual noise and recovery remain physical unknowns.

The later [side-bearing screen](short_lap/reinforced_side.json) applies matching
equal/opposite forces to two 4 mm-high bands on the actual cap/body, with the
body's lower crop clamped and cap roof clamped. The 30 mm candidate's band
centers are 24 mm apart: 7.25 N at the upper contact and −5.25 N at the lower
give the body 2 N net lateral load and 180 Nmm seam moment. Cap loads are opposite.
Both X and Y paths are tested. Their relative band displacement is extrapolated
to the roof with a rigid-band assumption; it is not a coupled contact solve or
an unrestricted full-shell rotation prediction. Local traction is distributed
over selected planar surface triangles; it is not calibrated contact pressure.

In those same conditional fixtures, estimated extra roof motion falls from
**5.25 to 1.23 mm in X**, and **10.01 to 2.66 mm in Y**: about **77% / 73% less**
than the first thin-wall 24 mm candidate. Final mesh changes of the derived
quantity are **.86% / 1.82%**, within the declared 10% screen. This supports the
30 mm reinforced prototype choice while leaving printed stiffness, off-center
release and impact strength unresolved. The guide-only .52 mm result and these
loaded extrapolations answer different questions; they are not a validated
combined movement bound. The side screen uses E1200 MPa and the stated grips/
traction bands, not a calibration against the user's print.

Numerical stopping uses **10% change in the derived roof-motion quantity** that
can change the reinforcement decision, plus the native quality and force-balance
checks. Individual patch-mean changes remain visible. An initial patch-only
reader stopped at **10.56%** on the first candidate's small lower X-pad response
(about .008 mm difference); this was not a native solve failure. Rather than
relax the 10% tolerance, the report compares the actual decision quantity from
both meshes and retains that local sensitivity. Neither mesh stability nor
reinforcement qualifies printed strength or an impact rating.

## Files and print/use setup

The authoritative production source is [short_lap_reinforced.py](../short_lap_reinforced.py).
Earlier comparison builders are [short_lap_design.py](../short_lap_design.py) and
[the first refinement](../short_lap_refinement.py); their native records remain scoped.
The final selected overlap is `SELECTED_OVERLAP`; `build(overlap)` requires an
explicit declared choice. Historical M1, M2–M5, R1–R4 and hinged files are retained;
do not mix their bodies/caps or assume the old TPU liner fits this new mouth.

| Layout | Python | Primary STEP | Matching STL |
| --- | --- | --- | --- |
| Full prototype | [Source](../short_lap_case.py) | [Full pair](../short_lap_case.step) | [Full pair](../short_lap_case.stl) |
| Production joint test | [Source](../short_lap_joint_test.py) | [Test pair](../short_lap_joint_test.step) | [Test pair](../short_lap_joint_test.stl) |

Use PETG, the established 0.4 mm nozzle / 0.2 mm layers, **three walls and 7%**
adaptive cubic as starting settings, with the actual spool's appropriate
temperatures/cooling. Supplied poses are body upright and cap inverted onto its
closed end. Import each pair at 100%, millimetres, without rotating its parts.
There are no printed labels, separate springs, hinges, hardware or assembly tools.
The STEP is primary; the STL uses the same selected geometry and placement.
Three walls are a deliberate change from the usual two-wall starting point:
the bearing walls are load paths, and their sections should contain several
extrusion paths. The effective isotropic FE modulus is still an uncalibrated
hypothesis; wall count does not supply printed material properties.
The sleeve disengages after about 30 mm withdrawal, but a loaded box's cap must
still clear the projecting brush head: expect roughly 85–90 mm total axial lift
for complete removal, as in the original split. Shorter overlap reduces guided
surface travel, not the attached brush's length or all opening motion.

The production test preserves the entire perimeter, **16 mm below the seam**,
the full selected sleeve and both catches. It uses the **complete 90 mm production
cap**, which can be reused with a later full body. Shortening the cap just to
save material would move its roof restraint closer to the snap and could make
the test misleadingly stiff. The open-bottom crop omits the full lower body and
floor; it changes restraint and cannot qualify whole-case leverage or retention.

Start with the joint pair if another trial is worthwhile. Grip the rigid lower
band, away from the end snaps. Push the cap straight on, then pull via the two
broad-face recesses. Compare centered pull with a gentle one-sided pull and
sideways rocking; stop for whitening, cracking or permanent spread. A useful
result has both snaps returning, intentional separation manageable, no obvious
seam instability and no continued tooth drag after the initial few millimetres.
Excessive force calls for changing the local bump/ramp or compliance, rather than
automatically shortening the lap again. Weak holding or easy peeling calls for
more capture/support, not an assumption that friction will compensate. Check
10 cycles and a closed overnight dwell if initial operation is unchanged; those
are observation checkpoints, not a life rating.

This test is cheaper than another complete body and can reject fit/effort/return
failures. It cannot establish quietness, whole-box backpack security or full
packing on its own. A full prototype must still be tried with the actual brush,
tube and any desired packing, including off-center handling, before treating the
closure as accepted. The actual tube taper, combined easy packing, material
properties, print-force range and acceptable loaded impact remain unmeasured.

## FDM review

The full body is 204 mm tall in its supplied upright pose; cap height is 90 mm.
The test body is 46 mm tall, on its flat complete cut ring. The two layouts use
the same 112 mm X separation, broad flat feet and upright/inverted layer
directions. The 270 × 270 × 256 mm Q2C profile supplies final placement limits;
the selected diagnostic process includes an automatic 5 mm brim.

The main cup walls are 2 mm, sleeve 2 mm, receiving band 2.7 mm and local pocket
skin about 2.05 mm at the crest. The .6 mm bump has a .8 mm radial-profile rise
over 1 mm axial rise including its embedded root; the closing ramp is longer.
The cap's internal thickness transition spreads .7 mm over 4 mm. These features
grow from existing material in the chosen poses. The relief track opens toward
the cap rim and removes rubbing after the snap. No separate flexible beam, slot
or trapped support cavity is introduced. The .10 mm guide gap is an assembly
clearance between separately printed parts, not a print-in-place gap.

Both handled ends retain actual R4 blends above the established tangent feet,
with small softened foot edges. Cap rim corners retain seating surfaces; the
two 3 mm-high grip recesses have .8 mm rounded cut corners. Retaining surfaces
are deliberately not rounded away. PETG layer bonding, recovery, surface drag
and fatigue remain unmeasured. The three-wall slice/section review is distinct
from the effective homogeneous/isotropic numerical material assumption.

Both final STL layouts passed **OrcaSlicer 2.4.2**, centered without rotation,
with the shared Q2C 0.4 mm / Generic PETG printer-filament pair and the local
[three-wall process](short_lap/profiles/process.json). Effective settings were
.2 mm layers, three walls, 7% adaptive cubic, 5 mm automatic brim and support off;
the separate automatic-support probes generated no support. Neither report had
filtered log notices. Native receipts: [full](short_lap/short_lap_case_slice.json),
[test](short_lap/short_lap_joint_test_slice.json). These are diagnostic process
checks, not actual-spool qualification or Orca's separate GUI STEP import.

The [targeted path review](short_lap/paths.json) inspects the 2 mm sleeve and
2.05 mm pocket skin in the actual test slice. Each has **five crossing paths**,
including gap fill; recorded widths are .42–.48 mm. Their width-coverage
approximations leave about .006 / .0035 mm uncovered at the section boundaries,
below the .15 mm local review tolerance, and no internal gap. This is not a
deposited-polymer or whole-part-solidness measurement. The two useful print views
were visually inspected; paired STEP/STL exports came from the same final poses.

## Reproduction and evidence boundaries

The new [study](../short_lap_study.py) uses `QuestionStudy` and its existing
identity-checked evidence readers. Retained compact native records live under
[flex](short_lap/flex/); raw native output is local/ignored. Never overwrite a
completed run or relabel interrupted work as complete. To repeat the numerical
studies, choose a new output destination in the study source, then run through
`./execute.py`. The [report](../short_lap_report.py) reads existing evidence and
does not silently launch replacement solves. The [comparison](short_lap/comparison.json)
includes actual-CAD witnesses and E/fit/one-catch sensitivities, not just nominal
numbers. The [CAD record](short_lap/cad.json) has separate fit and motion scope.
Native `cq.Assembly` holds the named print parts. The established object-local
pair/path checks suffice for these two coaxial cups; no additional constraint
solver or assembly-geometry adapter is needed for the stated finite poses.

```sh
./execute.py --threads 1 model/dental_travel_case/short_lap_checks.py
./execute.py --threads 1 model/dental_travel_case/short_lap_report.py
./execute.py --threads 1 model/dental_travel_case/short_lap_reinforced_study.py
./execute.py --threads 1 model/dental_travel_case/short_lap_side_study.py report-final
./execute.py --threads 1 model/dental_travel_case/short_lap_drawings.py
task_slice_setup=(
  --slice-printer .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json
  --slice-process model/dental_travel_case/notes/short_lap/profiles/process.json
  --slice-filament .codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json
)
./evaluate_model.py model/dental_travel_case/short_lap_case.py --slice "${task_slice_setup[@]}" --report model/dental_travel_case/notes/short_lap/short_lap_case_slice.json --summary
./evaluate_model.py model/dental_travel_case/short_lap_joint_test.py --slice "${task_slice_setup[@]}" --slice-keep-run --report model/dental_travel_case/notes/short_lap/short_lap_joint_test_slice.json --summary
./execute.py model/dental_travel_case/short_lap_toolpaths.py
./execute.py model/dental_travel_case/short_lap_delivery.py
./execute.py model/dental_travel_case/verification.py --variant slim-short-lap
```

The source/export/slice association binds both current print layouts to their
builders. A matching old mesh and old slice alone cannot qualify revised source.
The shared verification plan retains inherited requirement IDs and physical
UNKNOWNs. This user's new small-bite direction explicitly supersedes M1's earlier
deeper independent-teeth implementation request under its stable requirement ID;
the original instruction and observations remain in [M1](m1.md). Scope authority
and noise tolerance changed; the earlier printed samples' high effort/noise did
not become successful tests of this new full geometry.

## Print status

The shared [verification report](short_lap/verification.json) records separate
CAD, reduced-mechanics, side-screen and slice evidence; actual printed acceptance
remains UNKNOWN. The previous intent/CLI phase passed **26 tests**. This
investigation passed **19 focused regression tests**, including incomplete
contact output rejection; all three retained native snapshots reproduce their
complete field summaries. The real-solver node/surface-contact and open-gap
benchmarks also accept complete fields under the strengthened guard. Reflection:
shorter guidance and stronger retention are separate design choices; explicitly
checking wall compliance changed the recommendation from a thin 24 mm joint to
the reinforced 30 mm prototype. Existing shared guidance already covers that
distinction; no new solver infrastructure or standing noise preference is needed.

| Item | Print status | Artifact(s) | User result or remaining physical checks |
| --- | --- | --- | --- |
| Test piece(s) | No — newly modelled | `short_lap_joint_test.step` / `.stl` | Actual fit, effort, return, noise and dwell untested |
| Final printable object(s) | No — new prototype | `short_lap_case.step` / `.stl` | Actual packing, integrated retention, sideways stability, impact and life untested |

## Attribution

Primary language model: GPT-6 (exact runtime variant not exposed). Reasoning
effort: not exposed. Harness: Codex shared-workspace API agent. Provider: OpenAI.
No sub-agents used. Reuses this repository's M1 rounded shells and R2 wall-snap
builders; prior contributors remain in [historical provenance](provenance.md).
No third-party geometry imported; repository licensing remains applicable.
