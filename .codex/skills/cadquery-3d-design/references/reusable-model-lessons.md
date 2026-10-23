# Reusable model evidence

During planning, check for a similar interface or manufacturing problem here,
then read the linked object's current source and evidence. Reuse a successful
builder when practical. Preserve its mating geometry and print orientation;
reassess movement, loads, stiffness or printing where the new assembly changes
the relevant conditions. A fit or print result applies to the tested
configuration, not every material or printer.

## Find a relevant problem

- [TPU skins, damping and shell stability](#tpu-skins-damping-and-shell-stability)
- [Joining, retention and full assembly paths](#joining-retention-and-full-assembly-paths)
- [Contents support, access and useful form](#contents-support-access-and-useful-form)
- [Structural questions and numerical evidence](#structural-questions-and-numerical-evidence)

Each entry gives the resulting recommendation, its evidence and transfer limits.
It is a discovery index, not another methodology or a set of universal acceptance
rules. Follow the linked object for current status and reproducible detail.

## TPU skins, damping and shell stability

**Actual layer-height correction, 2026-10-16:** the user confirms all liner
prints so far used **0.2 mm**, including the research and ironing trials that
requested 0.1 mm. All physical results in the liner entries below have that
reported layer height; remaining settings retain their stated unknowns.
Historical 0.1 mm path evidence is diagnostic only. See the
[owning correction](../../../../model/tpu_damping_box/README.md#actual-liner-layer-height-correction--2026-10-16)
and the [future liner default](user-preferences.md#printer-manufacturing-and-available-hardware).

### Backing skin and printed integrity versus retained paths

Preserve both skins for this follow-up; path presence alone did not establish printed integrity.

**Evidence:** [I22/I30/I10 physical report](../../../../model/tpu_damping_box/README.md#i22--i30--i10-print-feedback--latest-report): I22 quietness is accepted, similar to I30; open-backed I10 has broken shell-side regions despite earlier CAD/path checks and no proposed support.

**Scope and limits:** Actual print/use feedback at user-confirmed 0.2 mm layers; other settings and precise cause unknown. Both skins are now required for this follow-up; later S16/S12 both work; S16 is preferred (entry below). [Print planning](print-planning.md#functional-process-co-design) owns skin/channel/bridge-height review. No universal rule that all exposed TPU ribs fail follows.

### Closed-skin TPU: upright wall integrity does not follow from flat coupons

Keep vertical skin continuity separate from horizontal finish and retained paths.

**Evidence:** [Slim dental liner print report, 2026-10-19](../../../../model/dental_travel_case_liner/README.md#wall-print-feedback--2026-10-19): both inner and outer wall skins are locally broken, whereas the sunglasses liner did not show that problem. Both use the nominal S16 sandwich and similar straight-channel widths; wall heights and transitions differ.

**Scope and limits:** Cause and actual speeds remain unknown; recalled 80 mm/s and 9 mm³/s are not directly comparable settings. [Deferred TPU side-wall work](../../../../model/tpu_damping_box/README.md#deferred-side-wall-printing-investigation--2026-10-19) must preserve relevant orientation/height/restraint. Neither flat F0–F7 coupons nor a successful small cup qualifies tall walls; no universal pocket-size, Arachne or speed verdict follows.

### Classic generator choice versus ordinary-profile compatibility

Checking `wall_generator=classic` alone does not establish ordinary slicing
compatibility when the diagnostic also narrows widths or enables thin-wall recovery.

**Evidence:** [R1 rejection and R2 correction](../../../../model/tpu_damping_box/README.md#ordinary-classic-repair--r2): the user declines all four unprinted R1 sets for missing walls. Ordinary 0.42/0.45 mm Classic widths with recovery off reproduce missing A16 skins and empty-layer errors in the other sets. R2 retains the requested total thicknesses by reallocating skin/core/support material.

**Scope and limits:** Slicer failure and user preprint rejection, not printed breakage or a calibrated material limit. The user's original complete settings remain unknown. [Print planning](print-planning.md#functional-process-co-design) owns the workflow correction; the object's selected widths and 0.5 mm skins are setup-specific experiments, not a universal minimum.

### Overall thinness versus printable local features

Separate overall lining thickness from substantial local feature width and path count.

**Evidence:** [TPU liner rejection and regression](../../../../model/tpu_damping_box/README.md#thin-feature-rejection-and-prevention): I24/I20 were rejected before printing despite retained single paths; I26/I22 keep much thinner overall sandwiches with 0.9 mm webs and two/three substantial paths at checked sections.

**Scope and limits:** User preprint rejection and diagnostic path evidence, not a failed print or universal nozzle limit. [Print planning](print-planning.md#printability) owns the corrected workflow. Quietness and physical robustness of replacements remain unknown.

### S16 adaptation: ironing a bridged TPU contact skin

Start a comparable ironing trial at 50% flow; check finish and skin/channel integrity.

**Evidence:** [S16 liner sample print report](../../../../model/sunglasses_case_liner/README.md#ironing-flow-print-feedback--2026-10-16): user tried 10%, 30%, 50% and 100% ironing flow; 10/30 leave surface line gaps, 50 is described as perfect, 100 raises/bumps the top.

**Scope and limits:** The sample was printed at user-confirmed 0.2 mm layers. For future comparable S16 adaptations, start an ironing trial at 50% and check finish plus skin/channel integrity. This is the preferred tested value for the reported setup, not a universal TPU preset. The user suspects TPU combined with a bridged skin; causation is unisolated. Exact spool/other process settings, ironing speed/spacing and printed file remain unknown. No ironing-off control, channel-integrity, damping or full-panel finish result follows; distinguish ironing flow from normal extrusion flow.

### Damping-core coverage around rounded bends

Check damping-core coverage around bends as well as along straight walls.

**Evidence:** [Sunglasses liner corner review](../../../../model/sunglasses_case_liner/README.md#corner-coverage-investigation--2026-10-16): user holds off before printing; straight walls are hollow but all four rounded bends are solid. The revised model uses curved cores/radial ribs with both skins; CAD and sliced corner-gap/skin/rib/cap checks pass.

**Scope and limits:** Preprint concern, not a physical damping failure. Straight-wall path checks did not cover corner contacts; future transfers require explicit CAD and sliced witnesses around bends. [Print planning](print-planning.md#functional-process-co-design) owns spatial coverage review. The revision has no physical use report; S16 sample approval remains scoped to its original fixture.

### Preferred closed-skin straight-rib TPU damping profile

T08 M1 is now the preferred printed damping-box baseline; retain S16 and B08/B16
as historical approved references and qualify each new application.

**Evidence:** [Printed S16/S12 comparison](../../../../model/tpu_damping_box/README.md#s16--s12-print-feedback--2026-10-16): both work; user prefers S16 over S12/I22, good compared with I30/original 4 mm I. S16: 0.4 mm backing + 0.8 mm air core + 0.4 mm contact skin; 0.9 mm straight ribs at 4.4 mm pitch.

**Scope and limits:** Approved starting profile for rigid-shell/TPU impact liners, including the requested sunglasses-case adaptation. Preserve both skins and local rib dimensions; review new coverage, corners, installation, contents and printing. Consult the linked S16 adaptation ironing lesson when choosing the contact-skin finish. Subjective single-setup evidence at user-confirmed 0.2 mm layers; other exact settings, cause, dB, wear and application performance unknown. No universal optimum or material calibration.

**Later comparison:** [2026-10-21 A/B/C report](../../../../model/tpu_damping_box/notes/b_surface_concepts.md): user approves B08/B16 with damping similar to S16 and improved object-facing finish, tentatively favoring B08 print quality; rejects A16/A20 frames and C12/C16 solids for damping. Phone ranges are approximate observations, not calibrated attenuation. Existing B tie layers contain more disconnected deposition chains than layers between ties, while their visible contact contour stays closed. Printed strings/seam artifacts and tall-liner survival remain unresolved; proposed SVG patterns have no CAD/slice/physical qualification. This advances the experiment without replacing successful application-specific S16 evidence. The user subsequently finds D tie changes inadequate as the main surface solution and requests [architectural separation](../../../../model/tpu_damping_box/notes/surface_decoupling.md), explicitly unconstrained in thickness, with solid corner lands. The reported issue is visible surface patterns/occasional bumps in black TPU. The user later finds E1 interesting but its color/space explanation unclear, drops E2/E4 and doubts E3. The later [print-first review](../../../../model/tpu_damping_box/notes/print_first_concepts.md) retires E5/E6 loose cores for complete-liner assembly burden, reworks E1 as an integral carrier and compares a connected flat folding blank. It exposes orientation, layer support, floor/lid and all part counts; the user confirms two cup pieces plus the usual lid pad are acceptable. The user subsequently sets aside the nested-cup proposal because separate printing still depends on thin upright TPU walls, which previously failed in the tall dental liner. The user also rejects the flat folding architecture for poor printability when adapted to other model shapes; both proposals are retired, with no CAD, slice or physical qualification. Removing core-to-skin print junctions does not address independent wall stability/deposition risks. The subsequent [N1–N3 SVG discussion](../../../../model/tpu_damping_box/notes/preformed_surface_concepts.md) compares ordinary sparse infill, tangent curved webs and two preformed trough halves with their largest faces horizontal. Setup dependencies and seam costs are explicit. The user then authorizes [concrete infill studies with actual paths](../../../../model/tpu_damping_box/notes/infill_study/README.md): a 6 mm wall proxy produces sparse cores and three surface contours under ordinary Classic for Gyroid 20/30% and Cross Hatch 20%. No full-box or physical qualification is inferred. The later [B-derived adaptive slice study](../../../../model/tpu_damping_box/notes/tie_surface_study/README.md) finds closely overlapping nominal passes in the 0.5 mm skins, distinguishes gap fill from normal perimeters, and favors straight-tie 1.2/1.6 mm skins for further comparison. Rounded/swept roots and an N2 R0.25 blend add local loops/work despite smoother CAD. Six new slices are successful; the defect cause, finish/damping gains and tall-liner transfer remain physical unknowns.

**Latest full-pair physical result:** [T08/T16 comparison](../../../../model/tpu_damping_box/notes/t_skin/README.md#physical-feedback--2026-10-21): user calls T08 the new golden standard, with damping effectively equivalent to approved predecessors and substantially better appearance than B/S. Its upright wall is 0.8 / 0.6 air / 0.8 mm (2.2 mm total), with discrete 0.8 mm ties, solid corners and local M1 IDs; floor/pad retain B's 0.4 / 0.8 air / 0.4 mm construction. T16's extra normal perimeter paths did not make it better: it feels too firm and noisier, so it is rejected. This is subjective physical evidence with exact runtime settings unknown, not calibrated acoustics or a minimum printable thickness. The [thinner-gap follow-up](../../../../model/tpu_damping_box/notes/thin_gap/README.md) is an experiment, not an approved replacement. Preserve application-specific S16 successes within their original scope.

### Flat-faced folded-web TPU impact liner

Preserve the accepted folded-web baseline before thinning it.

**Evidence:** [Damping-box physical comparison](../../../../model/tpu_damping_box/README.md#user-print-feedback--2026-10-16): user approved 4 mm I, clearly quieter than E/H; solid A remained noisy in the PLA shell.

**Scope and limits:** Subjective single reported setup at user-confirmed 0.2 mm layers; exact printed files and other settings unknown. I uses 0.6 mm chevron webs and contact skin, 2.6 mm core, 0.8 mm backing. Preserve the baseline before thinning; this does not calibrate TPU, prove a cause or qualify PETG shells or thinner derivatives.

### Flat contact skin over CAD air channels

Inspect actual bridge direction across the intended supports.

**Evidence:** [TPU damping-box path review](../../../../model/tpu_damping_box/README.md#printing-and-manufacturing-review): Orca 2.4.2 automatically bridged E/F pads along their hidden channels; explicit 180° external/internal bridge direction made all ten structured roof layers cross the webs.

**Scope and limits:** Sliced paths with the documented Q2C/TPU profiles and unrotated layout; printed sag and channel integrity remain unknown; subsequent subjective quietness is recorded separately. Short CAD spans alone do not establish that automatic bridge direction uses them.

**Later physical limit:** [L20 floor clarification](../../../../model/dental_travel_case_liner/notes/floor_surface_review.md) reports broken/cracking interior-floor surface during a canceled dental print, despite okay early wall regions and retained small-cup damping preference. L20 doubled the older wall skins to 0.8 mm but retained a 0.4 mm, two-layer interior floor over discrete posts. A 3.6 mm inter-post gap along a row is not a maximum bridge span for tracks missing the rows. Stopped layer and actual ironing are unknown; roof thickness/support and finishing remain separate hypotheses, not a diagnosed cause.

### Soft-on-soft contact versus quiet sliding; connected geometry versus continuous coverage

Evaluate sliding sound separately from impact cushioning; the swatch direction remains discontinued.

**Evidence:** [Q1F and all-TPU G hood reports](../../../../model/filament_swatch_box_study/README.md#tpu-damping-discontinued-2026-10-06): Q1F joins but its contrasting skin/upper attachment disappoint. Changing the hood to TPU still leaves audible TPU-on-TPU rubbing, somewhat quieter but unacceptable. User discontinued the damping project; follow-up SVGs remain untested history.

**Scope and limits:** Physical subjective results, settings/hashes unknown. Layer-line/roughness cause is a user hypothesis, not isolated evidence. Impact cushioning and sliding sound need separate acceptance; TPU substitution alone failed here, not in every TPU application. Single-solid connectivity does not establish continuous appearance or attachment feel. Preserve working joining evidence; do not automatically resume this project.

### Retained mesh versus printed whole-shell shape after material/construction changes

Reassess complete-shell shape and feel after material or wall-construction changes.

**Evidence:** [Unchanged G hood in TPU](../../../../model/filament_swatch_box_study/README.md#tpu-damping-discontinued-2026-10-06) remained usable but had locally expanded/shrunken-looking, movable upper regions. Earlier [PETG vase hood](../../../../model/filament_swatch_box_study/README.md#v1-single-wall-vase-hood--additional-transparency-trial) held the base but bulged/popped under handling.

**Scope and limits:** Separate trials; exact process settings, shape-change timing and common cause unknown. Successful fit and nominal CAD do not qualify shell shape stability/feel in another material or wall construction. Review the whole shell's material, section and handling; no universal thickness, calibrated stiffness or printing-defect diagnosis follows.

### Separate soft insert inside an accepted modular outline

Budget contents, rigid walls and soft layers together; check connectivity and installation separately.

**Evidence:** [Q1F quiet swatch box](../../../../model/filament_swatch_box_study/README.md#quiet-tpu-revision--q1f-with-the-accepted-exterior-2026-10-05) fits a separately printed 0.8 mm TPU sleeve and recessed seat inside the old exterior by reducing rigid walls; the actual old G hood, card pocket and I3 joining routes remain in the CAD checks. Two port cuts initially severed the sleeve; inward connecting bands and matching installation channels restore one insert.

**Scope and limits:** Packaging, connectivity, sampled motion and reference slicing only; no measured quietness, force, elastic installation or strength. Budget fixed contents, outer datums, local wall thickness and contact layers together. Port access, part connectivity and insert installation are separate questions; local clearance and valid solids alone do not establish the intended assembly. Dimensions/material thickness are object-specific.

### Spiral-vase shell mating to existing catches

Review deposited inner mating paths and complete-shell handling separately.

**Evidence:** [V1 swatch hood](../../../../model/filament_swatch_box_study/README.md#v1-single-wall-vase-hood--additional-transparency-trial) uses a filled slicer envelope, retaining waist and rim taper. Its [path study](../../../../model/filament_swatch_box_study/notes/v1_path_checks.json) checks the generated wall at four catches and the rim. The shared [path reader](../../../../physical_analysis/README.md#sliced-manufacturing-paths) retains rising-path endpoint heights. Subsequent PETG vase print holds the base but is rejected for easy deformation, opposite-side bulging and popping/crackling sounds.

**Scope and limits:** CAD envelope dimensions alone do not locate the deposited inner mating surface; width, path position and spiral rise matter at these contacts. Local overlap/path acceptance does not establish complete-shell shape stability or comfortable handling. Exact printed artifact/settings/base and root cause are unknown; do not generalize this failure to all PETG or vase prints. The automatic-support probe is inapplicable where Orca forbids supports. Accepted G hood is retained; no further hood exploration requested.

## Joining, retention and full assembly paths

### A fastener witness must traverse every mating part

Extend the obstruction witness through every mating part.

**Evidence:** [Damping-box closure review](../../../../model/tpu_damping_box/README.md#verification-and-physical-status): a shaft ending at the body/lid plane missed a wrong screw diagonal; the full 12 mm shaft rejects that lid pose.

**Scope and limits:** Targeted rigid CAD obstruction only; detailed nut fit, tightening and shake retention remain unreported. A clear witness cannot cover a mating solid it never enters.

### Local catch bite versus full-shell retention and overlap

Review shell spreading, peel/rock and bearing span before transferring local catch success.

**Evidence:** [Full slim M1 print](../../../../model/dental_travel_case/notes/m1.md#full-box-print-feedback--2026-10-15): usable storage and actual brush/tube/floss fit, but the full box pulls apart without pressing the releases despite better-feeling small samples. The 12 mm overlap feels too short/unstable; user stopped further revisions.

**Scope and limits:** Physical bypass and subjective instability, not a measured force or impact break. Rigid hook obstruction and a local leaf screen omit elastic shell escape and complete-object leverage. Review receiver spreading, peel/rock and bearing span before relying on catch depth or coupon success. Exact print/settings and escape mode unknown; suggested 2–3× overlap is untested, not a universal rule.

### Clearance capture versus a firm connection

Identify a real holding-force source; clearance capture alone did not provide grip.

**Evidence:** [H swatch connector print](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status): user reports PETG key falls out and no useful grip/join. H's rigid key had 0.2 mm normal clearance and no preload. The [shared friction screen](../../../../physical_analysis/README.md#friction-only-retention-screen) rejects that zero-force route before printing.

**Scope and limits:** Rigid obstruction and clean slicing did not establish retention. Separate entry allowance from seated play and identify an actual holding-force source. Printed dimensions/settings are unknown; this is not a printer defect or a universal numerical tolerance. On 2026-10-03 the user reported all three I spring-preloaded replacement keys work, with 3 feeling better. Preserve the successful interface and advance to complete-box use; exact print settings, the reason for preference, holding force and durability remain unknown.

### Inherited ports versus two-ended key capture

Check stopping and capture at each non-equivalent complete-base port.

**Evidence:** [J4/K4 print report](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#j4k4-print-report--2026-10-04): J4's key works after explicit rechecking. K4's key works on one end only; the user reports no stopping wall at the other. Earlier grip checks proved parent geometry unchanged.

**Scope and limits:** Interface preservation does not qualify an inherited interface's job. Before claiming a module joins on either end, verify required stops/capture at each non-equivalent complete-base port, not just equality to the parent or one local socket. Exact failed end, printed hashes/settings and CAD cause are unconfirmed; the user's visual K2 concern is not another physical print result. Repairs are deferred.

### Taller walls enclosing an inherited open relief

Review new ceilings and support-removal access when walls enclose an existing relief.

**Evidence:** [Archive R1 support review](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#support-review-and-reflection): extending the display base above its catch reliefs created ceilings; Orca generated support inside the narrow clearances. The existing shared path reader located the support contacts. Sloped ceilings and floor chamfers removed the final probe's generated supports while nominal card, G hood and both key-end checks passed.

**Scope and limits:** CAD and reference-slice evidence only; no R1 physical print report. Preserved mating dimensions do not preserve manufacturing conditions when surrounding walls enclose a formerly open feature. Review the new roof, removal access and remaining wall before accepting support or changing a proven catch. No force, material or universal overhang qualification follows.

### Cover retention versus suspended contents weight

Screen suspended contents weight separately from comfortable opening effort.

**Evidence:** [Archive A full-load lift](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#archive-r2-a-print-report--2026-10-04): the user loaded all 15 cards, fitted G hood and lifted by the hood; the base stayed attached.

**Scope and limits:** Physical success for this printed assembly and lift; actual mass, force margin, duration, acceleration and print settings are unmeasured. Screen the weight suspended across the closure independently of opening effort; preserve the successful interface, but reassess heavier contents or joined modules. No shock, fatigue or universal material rating follows.

### Captive hinge and side-printed keeper

Preserve the accepted local hinge/keeper interface; reassess changed integration.

**Evidence:** [Sunglasses case E closure](../../../../model/sunglasses_case/notes/printing_and_design.md#e-mechanism-integration): D/E samples were printed and accepted; the integrated full case was reported working. Its source preserves the accepted interface dimensions.

**Scope and limits:** Greater bearing separation, different shell stiffness, layer registration and untested fatigue can change the behavior. Translate the local interface rather than scaling it.

### Printed screw-top closure

Reuse thread geometry as a starting reference and check the new opening path.

**Evidence:** [Vaseline container](../../../../model/vaseline_container/README.md#decisions-and-evidence): the full base/lid pair with a 3 mm pitch thread and 0.30 mm nominal radial allowance was printed and reported good.

**Scope and limits:** The actual material and print profile are unknown. Use the geometry as a starting reference, then check the new thread and opening motion.

### Large plate joined with printed screws

Preserve successful thread fit while reviewing screw-drive orientation and changed load paths.

**Evidence:** [Book reading plate](../../../../model/book_reading_plate/README.md#what-changed-after-the-successful-l-sample): the sample's thread fit worked; the downward-facing drive socket printed poorly. The revised head-up screw and final plate were reported to print nicely.

**Scope and limits:** The print report does not establish load capacity or long-term creep. Recalculate the load path when loads, geometry or supports differ; review the drive socket orientation and thread interface where changed.

### Solid printed fastener cores versus valid hollow threads

Co-design a coarse screw and matching nut for FDM; verify core material after the complete sweep/boolean construction, separately from solid-infill paths.

**Evidence:** [Travel-case printed fastener correction](../../../../model/dental_travel_case/notes/rotary_refinement.md#the-old-thread-really-was-hollow): the user correctly identified a hollow thread in the model. The old intended root cylinder disappeared during the sweep union/trim, while validity, connectivity and slicing passed. A targeted axial material witness catches the old source and STEP as a negative control and passes on the new custom pair. Replacement threads use the larger book-plate success as a starting reference; the existing shell/wheel interface is retained.

**Scope and limits:** The hole is a confirmed CAD defect, not an inferred material or infill failure. The exact kernel cause is unisolated. The coarse pair was subsequently included in a successful complete PLA rotary trial; strength and durability remain unmeasured. The later [conical-head revision](../../../../model/dental_travel_case/notes/rotary_case.md#conical-wheel-and-screw-revision) preserves that thread but remains physically untested. A solid core and 100% infill do not establish strength. Do not require ISO compatibility solely because stock nuts exist.

### STEP warnings despite a valid source solid

A reported STEP import problem can justify inspecting the actual affected export, including components that failed to remain solids.

**Evidence:** [Travel-case cap/screw repair](../../../../model/dental_travel_case/notes/matte_rotary.md#verification-and-remaining-limits): the old valid source cap reimported as an open shell, while the screw had mismatched tessellation boundaries. Enumerating only `Solids()` silently omitted the failed cap. Direct circular scallops and a non-tangent thread-tip cut yielded two solid STEP components with closed tessellation.

**Scope and limits:** This is a targeted response to demonstrated export trouble, not a routine round-trip audit. Source validity, STL slice acceptance and a specific GUI STEP importer answer different questions. The exact GUI warning was not reproduced; matte-PLA bonding and physical fit remain untested.

### Cropped connector samples versus complete entry

Check full assembly entry, not only cropped mating geometry.

**Evidence:** [G swatch join proof](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#rejected-underside-route): shared end-pocket crops passed local fit, but the [full-base vertical entry check](../../../../model/filament_swatch_box_study/check_cap_g.py) caught the longer drop-in head under the tall end wall. Shorter embedded ends clear it.

**Scope and limits:** Measured rigid CAD interference, not a print result. A crop can preserve mating geometry yet omit a blocker along the assembly path. Check that path against the complete neighbouring components before treating a local fit sample as representative; the sample still cannot establish complete handling or strength.

### Occasional separation versus a permanent handle

Match projecting controls to operation frequency and physical access needs.

**Evidence:** [G/H swatch connector feedback](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#h--wider-connector-without-a-handle): the user found G's projecting arm unnecessary for modules usually left joined. H omits it; [CAD checks](../../../../model/filament_swatch_box_study/check_h.py) cover a relative-base lift and withdrawal with hoods removed.

**Scope and limits:** Form/use feedback before a reported print, plus rigid motion evidence. Consider operation frequency before adding a protruding control; do not assume H's removal effort, nail comfort or joint strength are physically qualified, or omit handles when frequent operation needs them.

## Contents support, access and useful form

### Mechanism packaging versus desktop footprint

Challenge mechanism packaging and show the occupied footprint before detailed stability work.

**Evidence:** [Phone stand v2 rejection](../../../../model/analysis_phone_stand/README.md#rejection-before-printing-and-footprint-explanation): user rejects the unprinted 224 × 246 mm raised easel because rear structure and forward feet consume too much horizontal space. Long transverse keeper flexures enlarged the rear width; the tap calculation screened an already chosen footprint.

**Scope and limits:** Product-design rejection, not a print or material failure. A passing stability screen does not establish minimum necessary dimensions. Show the occupied footprint at a stated scale and challenge mechanism packaging before detailing; preserve useful local analysis independently of the rejected product.

### Opening grip versus pickup recess

Check the force direction needed to restrain the base during hood withdrawal.

**Evidence:** [Swatch underside-grip review](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#underside-grip-direction-review): user confirms the two underside recesses after printing a base, questions their direction and purpose. Source shows downward-facing 45-degree ramps claimed as opposing opening grips.

**Scope and limits:** A normal push against these ramps has an upward component on the base, whereas hood withdrawal needs the base held down. Opening could still use friction or other surfaces; neither usefulness nor inability to open was physically established by this report. Exact printed variant/settings are unknown. Check each hand's part, access and force direction before calling a cutout a release aid; printability alone is insufficient.

### Exposed contents versus redundant finger cutouts

Compare actual grasp with and without a cutout, including all final rim junctions.

**Evidence:** [R1 entrance rejection](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#r1-entrance-rejection-and-alternatives): user rejects the unprinted archive tray's deep scoops as unnecessary with 35 mm of card already exposed, and identifies sharp-looking inward scoop/top-rim junctions despite the rounded cut profile.

**Scope and limits:** Visual product rejection, not physical comfort or print failure. Compare actual grasp with/without a cutout before adding it; inspect final inner and outer junctions in plan and section, not just a named fillet or circular cutting tool. CAD fit and slice completion do not establish access value. Exact wall height/radii do not transfer to other contents.

### Sparse contents and effective retaining height

Count effective retaining height at feasible intermediate contents positions.

**Evidence:** [Archive wall-height study](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#continuous-rim-wall-height-study): a gravity-restoring screen and source-card contact fixtures find an intermediate single-card position controls the continuous-wall proposal. Reserving height for the entrance changes the counted straight support.

**Scope and limits:** Analytical/CAD evidence, unprinted. Screen feasible content positions, including intermediate lean, and the CG moment about real retaining contact; any wall contact or end-position sample alone is insufficient. Count a flare/round as retaining support only with evidence for its actual contact. The sufficient height screen is not an absolute escape threshold, shock rating or universal wall-height ratio.

### Corner guides and truthful floor-contact fixtures

Use the real contents outline and verify floor support in each evaluated pose.

**Evidence:** [Archive R2 comparison](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#archive-r2--four-retaining-forms): all four full-wall/corner/side-guide forms block selected actual-card yaw/lean challenges. A rectangular bottom approximation wrongly excluded diagonal candidates and lifted sideways-lean cards off the floor; the chamfered outline and explicit floor-contact assertions correct those fixtures.

**Scope and limits:** CAD/analytical evidence for all four; the later [A print report](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#archive-r2-a-print-report--2026-10-04) accepts the continuous-wall form for single-card/sparse browsing and integration with J4, the existing key and G hood. B/C/D remain unprinted. Use real lower content geometry for feasible pose generation and verify support in the evaluated pose. A low continuous wall constrains sparse contents as well as joining the raised guides. Selected blocked poses do not prove global containment, and slim guides did not fail these samples; guide stiffness/handling for B/C/D and durability remain open. Preserve the successful A mating interfaces when reusing the archive pattern; exact return sizes and heights do not transfer.

### Minimal gravity postcard support

Use the reported Wave geometry as a starting point, not validation of other holders.

**Evidence:** [Wave postcard display](../../../../model/postcard_display/README.md#print-status): the user reports the full Wave holder was printed and works well. Its [builder](../../../../model/postcard_display/style_variants.py) combines low front stops with curved rear arms.

**Scope and limits:** Actual material, printer settings and card dimensions were not reported. Reuse the seating/retention geometry as a starting point; changed backing, footprint or card stiffness needs its own review. The report does not validate the other variants or every card size/orientation.

### Entry clearance versus seated steadiness

Check seated steadiness separately from successful insertion and relaxed interference.

**Evidence:** [Swatch base physical history](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status): the first PETG base rocked and varied laterally; the printed [spring revision](../../../../model/filament_swatch_box_study/card_base_petg_5.py) grips nicely front/back, but its tiny end spring gives no useful sideways pressure.

**Scope and limits:** Actual dimensions, forces and nozzle/profile remain unknown. Entry paths, relaxed interference and independent spring/filled-path screens do not establish useful centering in the coupled contact sequence. The later D base is reported probably fine, without detailed centering/grip observations; do not infer a tolerance, friction or material calibration.

### Source handedness and opposing spring support

Use source-handed geometry and opposing supports, retaining physical alignment limits.

**Evidence:** [J/K revision diagnosis](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#jk-print-feedback-and-revisions): original J tilts cards; original K fails dome engagement because its reference represented a reflected swatch. Later [J4/K4 print feedback](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#j4k4-print-report--2026-10-04) prefers J4's firmer grip but reports full-seat tilt and bottom movement despite opposing-rail CAD checks; K4 retention is reasonable but looser/flappier.

**Scope and limits:** Use source-frame references and proper whole-item rotations. Opposing support and local tilt witnesses remain narrower than actual seated alignment; strong grip does not establish upright storage. Excess bottom clearance is the user's hypothesis, not a diagnosed cause or tolerance calibration. Exact print hashes/settings and long-term response remain unknown; further fixes are deferred.

### Tall covers around standing contents

Check the full contents/base/cover sweep and moving-weight stability.

**Evidence:** [Swatch cap comparison](../../../../model/filament_swatch_box_study/notes/cap_comparison.md#comparison-at-handoff) and [sampled hinged sweep](../../../../model/filament_swatch_box_study/check_cap_c.py) found rear cavity fillets catching the base and square bearing crowns blocking the roof tail; an open-box gravity screen motivated a rear foot.

**Scope and limits:** Check the complete contents/base/cover sweep; mating pin clearance alone missed these contacts. This geometry used a high hinge and fixed rear wall, not a universal hinge architecture. Apply the [handling stability screen](design-decisions.md#whole-object-form-and-handling) when moving weight can cause tipping. Mass assumptions remain uncalibrated; no physical report qualifies stability, hinge strength or retention.

### Snap packaging versus cover bulk and comfort

Review complete cover bulk and exposed-edge comfort beyond local snap clearance.

**Evidence:** The printed [D swatch box](../../../../model/filament_swatch_box_study/README.md#physical-history-and-print-status) fits okay, but the user rejects hood bulk and insufficient exposed-edge rounding; the base is probably fine. The [source](../../../../model/filament_swatch_box_study/cap_d_snap_5.py) extends a 6 mm snap/relief envelope up the shell.

**Scope and limits:** Local clearance, beam and slice passes did not qualify whole-cover handling. Consider local reinforcement instead of extending mechanism packaging everywhere; source fillets alone do not prove comfortable edges. Exact printed files/settings are unknown; no thinning strategy, material calibration or retention rating is physically qualified.

### Representative staged physical development

Use representative stages when local uncertainty warrants them; qualify integration separately.

**Evidence:** [Sunglasses-case development](#staged-development-and-form-exploration): accepted D/E samples preceded integration into the reported working full case.

**Scope and limits:** Preserve the tested conditions and recheck changed integration; sample acceptance does not establish full-product handling or durability.

### Form choices before detailed variants

Explore unresolved form choices cheaply before detailed variants.

**Evidence:** [Postcard and tray exploration](#staged-development-and-form-exploration) produced visual comparisons and printable alternatives. Retrospective workflow judgment: rough studies would often have informed those choices earlier.

**Scope and limits:** This is a sequencing lesson, not an observed print failure or a requirement for variants when a clear reference already settles form.

### Premature mechanism commitment

Challenge whole-product value before refining a doubtful mechanism.

**Evidence:** [Four rejected swatch-storage designs](#four-rejected-swatch-storage-designs) repeated excessive engineering around weak product concepts despite earlier architecture guidance.

**Scope and limits:** Challenge mechanism necessity and total product cost on rough complete geometry; resolve whole-product value before local mechanics. A coupon or numerical pass cannot justify the product.

## Structural questions and numerical evidence

### Named configurations and required contact in assembly review

Share actual named components/poses and distinguish required contact from forbidden overlap.

**Evidence:** [Quiet Q1/Q1F API trial](../../../../model/filament_swatch_box_study/README.md#named-assembly-engineering-2026-10-06) shares actual parts/poses across checks and inspection, distinguishes forbidden overlap from required support/retention, and rejects wrong hood placement, absent beads and a floating card. Full-scene and coincident-card subtraction produced invalid Booleans; exact component sets, per-part comparisons and rigid card-placement datums answer the intended placement question. Floor witnesses now crop the actual base instead of using an independent full block.

**Scope and limits:** Digital organization and geometric acceptance only; no automatic completeness, elastic installation, force or printed validity. Keep contact masks/envelopes local and explicit. A failed Boolean is not zero difference; choose evidence for the actual comparison question. Datum checks qualify rigid placement, not arbitrary geometry equality. Numerical limits stay object-specific.

### Seated load versus keeper release

Separate seated load support from release, and restrain the real mounting region.

**Evidence:** [Raised phone stand v2](../../../../model/analysis_phone_stand/HISTORY_V2.md#evidence-and-physical-analysis-scope) is rejected before printing for excessive footprint; its local fixtures use V seats for compression, stock pins for rotation, an independently guided keeper and a native force-loaded `ContactQuestion`. The exact guided spring was revised after a strain-screen rejection; actual sliced sections establish local fill.

**Scope and limits:** Unprinted, conditional isotropic PETG. Guide cages and root-pad restraints are explicit idealizations; no preload, friction, fatigue or freely rotating assembly solve is established. Clamp the actual mounting pad, not a narrowed transition. Use combined master surfaces for several obstacles sharing a slave region, and keep native completion separate from acceptance/refinement.

### Printed housing shares contact load

Model mating-body compliance when it can change the design decision.

**Evidence:** [Compact phone stand v3](../../../../model/analysis_phone_stand/README.md#analysis-and-verification) extended `ContactQuestion` with supported deformable mates. Actual nose/housing fixtures directed reinforcement to the nose; an independent equal-cantilever benchmark checks load sharing and retained identity.

**Scope and limits:** Unprinted, conditional solid PETG and explicit local restraints. Use deformable mates when their compliance changes a design decision; this does not establish a free hinge, friction, preload or whole-product acceptance.

### Analysis-driven flexible catch

Reuse the analysis pattern without treating the rejected product as a positive precedent.

**Evidence:** [Phone stand API experiment](../../../../model/analysis_phone_stand/HISTORY.md#what-using-the-api-changed): prescribed release and local holding-contact solves informed a wider root and positive travel stop; force was stable across the recorded refinement studies. The user rejected the product before printing on 2026-10-04; everyday use and functionality had not been adequately discussed.

**Scope and limits:** Unprinted, solid PETG assumptions. Local peak strain was mesh sensitive; sharp-tooth pass-over failed. Reuse the analysis pattern, not the product architecture, numerical load rating or material limit. An analysis-exercise objective still requires a worthwhile product and agreed use; local mechanics do not establish that value.

### Known snap, flexure and structural questions

Use scoped questions/studies; synthetic numerical fixtures do not qualify a product.

**Evidence:** [Shared engineering questions](../../../../physical_analysis/README.md#use) bind explicit intent to evidence and bounded studies. Phone release reproduces retained results; the book plain-back cross-check agrees within 6%; a [local rounded-contact fixture](../../../../physical_analysis/experiments/ipc/fixtures/rounded_snap/README.md) exercises passage/return and evidence guards.

**Scope and limits:** The fixture is synthetic geometry derived from a failed product, not a product precedent. Its force remains increment-sensitive. Numerical, material, manufacturing and physical evidence remain separate.

### Numerical mesh conversion at tiny contact gaps

Preserve double-precision meshes and inspect independent crossing witnesses.

**Evidence:** [IPC investigation](../../../../physical_analysis/experiments/ipc/README.md) independently compared supplied and native rest meshes and caught MEDIT version-1 float32 conversion despite high-precision ASCII. Version 2 preserves doubles; accepted-frame triangle checks catch crossing without relying on selected contact nodes.

**Scope and limits:** IPC has not qualified complete rounded-fixture passage. Mesh witnesses are independent numerical evidence, not global exact-CAD or continuous-path proof; rounded obstacle facets need separate sensitivity.

## Maintaining this index

Add or revise an entry autonomously when a printed result, measured model check,
or repeatable failure can save work on another object. Link to the current
object record and source, state what was actually observed and under which known
setup, and name the boundary of transfer. Keep detailed measurements and trial
history in the object directory. For removed products, link Git history and retain
only a concise negative lesson here. Remove or correct an entry when later evidence
supersedes it; do not append session narratives or untested clearance rules.

## Staged development and form exploration

**Observed physical evidence:** the [sunglasses-case record](../../../../model/sunglasses_case/notes/printing_and_design.md#e-mechanism-integration)
reports D and E samples printed and accepted, a slight preference for E, then a
working integrated full case. Representative smaller experiments established the
consequential interface before committing to the complete print. Transfer that
sequence when local behavior is the uncertainty; preserve geometry and process,
and keep final integrated use and untested fatigue distinct from sample success.

**Retrospective design judgment:** [postcard silhouettes](../../../../model/postcard_display/README.md#three-further-sculptural-alternatives)
and [tray patterns](../../../../model/faceted_storage_tray/README.md#options-and-files)
show form choices that could have been compared in rough studies before detailed
variants and exports. Their records include positive print reports for Wave and
H respectively; those do not establish that earlier exploration would have changed
the selected style. The transferable improvement is to recognize unresolved form
choices without waiting for a variants request, then compare only meaningful
differences cheaply. Printed texture may still warrant representative samples;
silhouette alone normally warrants rough visual evidence first.

## Four rejected swatch-storage designs

The sliding box, lift-off box, upright file and hinged case were removed. The
original sliding version was physically printed and found unusable; the other
three were rejected before printing. The hinged case was rejected for visible
design, architecture and proposed use, not demonstrated print or material failure.
The earlier [three-design cleanup](https://github.com/arthow4n/vibe-modelling-3d/commit/818ee96fa37615c1ab376fad9f7c1a636de38ab6)
and [hinged-case commit](https://github.com/arthow4n/vibe-modelling-3d/commit/1c30dd337298285f9d6ae0deb97343048c95c64e)
preserve the rejected work in Git history; none is a positive product or latch pattern.

**Retrospective design judgment:** the hinged case's three screw/nut connections,
separate flexible catch, release button, surrounding reliefs and substantial
analysis were disproportionate to the improvement in browsing: the proposed use
still removed horizontal packets and fanned them in hand. The proposed retention
coupon represented local latch mechanics, omitting full enclosure, actual hinge
motion, contents and browsing. It was not physical validation, and even a successful
print could not settle whether the product was desirable.

Earlier architecture guidance alone did not prevent premature commitment. Use
[adaptive development and feedback](design-decisions.md#feedback-and-autonomous-continuation):
make the uncertain complete form and operation reviewable cheaply, and stop for
consequential concept judgment before dependent mechanisms, simulation, slicing
or coupon recommendations. Do not diagnose unobserved tolerance/material causes
for a concept rejection. Abandon weak concepts regardless of sunk work; numerical
experiments can remain independent evidence without preserving the product.
