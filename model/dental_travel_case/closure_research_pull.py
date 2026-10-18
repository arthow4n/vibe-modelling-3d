"""Conditional straight-pull spring/ramp estimate; never a hanging-load rating.

The cap's actual lip is loaded radially, with the roof clamped. Combine this
compliance with the retained body study, and exact CAD bump/lip clearance paths.
No coupled contact, peel, friction, creep or long-body grip is simulated.
"""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
import numpy as np
from physical_analysis import StructuralQuestion, Region, Support, SurfaceForce, QuestionStudy
from physical_analysis.evidence import retain_run
import closure_research_design as design
from closure_research_flex import MATERIAL

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'notes/closure_research'
KINDS = ('shell_broad', 'shell_end')


def cap_question(kind):
    if kind not in KINDS:
        raise ValueError(kind)
    axis = 1 if kind == 'shell_broad' else 0
    r = (design.D.depth if axis == 1 else design.D.width) / 2 - 2
    # Complete narrow lip, including its CAD-bounded lower edge. A smaller box
    # inside this face selected no complete coarse-mesh triangles.
    pad = Region((-5.3, r, 245.8), (5.3, r, 248.0)) if axis == 1 else Region((r, -5.3, 245.8), (r, 5.3, 248.0))
    force = (0, 1, 0) if axis == 1 else (1, 0, 0)
    return StructuralQuestion(name='pull_cap_' + kind, part=design.build(kind)['cap'],
        material=MATERIAL, supports=(Support(Region.plane('z', 264)),),
        forces=(SurfaceForce(pad, force),), observations={'pad': pad},
        mesh_size_mm=2.5, nonlinear=False, max_increment=1.)


def run(kind, directory, compact):
    if compact.exists():
        raise ValueError('Choose new evidence destination')
    study = QuestionStudy(cap_question(kind), decision='Cap flexibility can lower the straight-pull force; resolve compliance to about 10%, not printed force calibration',
        metrics=('max_displacement_mm',), relative_tolerance=.1, mesh_levels=1)
    result = study.run(directory)
    print(kind, result.status, flush=True)
    for level in ('baseline', 'mesh_sensitivity_1'):
        if (directory / level / 'result.json').exists():
            retain_run(directory / level, compact / level)
    (compact / 'study_result.json').write_text((directory / 'study_result.json').read_text())


def required_retraction(cap, bump, lift, axis, extra_gap):
    """Positive-side actual tooth versus receiver, radially shifted rigid shapes.

    extra_gap moves the receiver outward, representing a local radial fit
    deviation, not a re-built global cap. Intersection tolerance is 1e-7 mm3.
    """
    shift = [0., 0., float(lift)]
    shift[axis] = extra_gap
    receiver = cap.translate(tuple(shift))
    def blocked(delta):
        motion = [0., 0., 0.]
        motion[axis] = -delta
        return bump.translate(tuple(motion)).intersect(receiver).Volume() > 1e-7
    if not blocked(0.):
        return 0.
    low, high = 0., 1.1
    if blocked(high):
        raise ValueError('Retraction bracket insufficient')
    for _ in range(15):
        mid = (low + high) / 2
        if blocked(mid):
            low = mid
        else:
            high = mid
    return high


def spring_path(travel, retraction, compliance, catches):
    """F = dU/ds for frictionless quasistatic elastic radial spring(s)."""
    energy = catches * np.asarray(retraction)**2 / (2 * compliance)
    force = np.gradient(energy, travel)
    # A released hanging body can accelerate through the initial axial play.
    # In the ideal zero-damping model, W*s supplies all stored elastic energy
    # when W >= max(U/s). This differs from a slowly supported pull's peak dU/ds.
    work_ratio = (energy[1:]-energy[0]) / (np.asarray(travel)[1:]-travel[0])
    return dict(energy_Nmm=energy.tolist(), force_N=force.tolist(),
        peak_force_N=float(max(force)), barrier_Nmm=float(max(energy)),
        undamped_seated_release_force_N=float(max(work_ratio)))


def section_segments(shape, axis, radius):
    """Actual central CAD section; only straight edges near the retained lip."""
    plane = 'YZ' if axis == 1 else 'XZ'
    sliced = cq.Workplane(plane).add(shape).section().val()
    segments = []
    for edge in sliced.Edges():
        a, b = edge.startPoint().toTuple(), edge.endPoint().toTuple()
        if min(a[axis], b[axis]) > radius-1 and min(a[2], b[2]) < 251 and max(a[2], b[2]) > 240:
            if edge.geomType() != 'LINE':
                raise ValueError('Curved lip needs a different profile representation')
            segments.append(((a[axis], a[2]), (b[axis], b[2])))
    if not segments:
        raise ValueError('Missing central profile')
    return segments


def radius_at(segments, z, *, outer):
    values = []
    for (r0,z0), (r1,z1) in segments:
        if min(z0,z1)-1e-8 <= z <= max(z0,z1)+1e-8:
            if abs(z1-z0) < 1e-9:
                values.extend((r0,r1))
            else:
                values.append(r0+(r1-r0)*(z-z0)/(z1-z0))
    if not values:
        raise ValueError(f'Profile does not cover height {z}')
    return max(values) if outer else min(values)


def profile_retraction(tooth, receiver, travel, extra_gap):
    lower = min(p[1] for edge in tooth for p in edge)
    upper = max(p[1] for edge in tooth for p in edge)
    # Piecewise linear difference has extrema at either profile's breakpoints.
    knots = {p[1] for edge in tooth for p in edge}
    knots.update(p[1]+travel for edge in receiver for p in edge if lower <= p[1]+travel <= upper)
    return max(0., max(radius_at(tooth,z,outer=True)-radius_at(receiver,z-travel,outer=False)-extra_gap for z in knots))


def report():
    body = json.loads((OUT / 'flex_summary.json').read_text())
    # Existing source guard, not a claim of newly solved body/contact mechanics.
    for name, digest in body['source_sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Body evidence stale: ' + name)
    rows = {}
    for kind in KINDS:
        axis = 1 if kind == 'shell_broad' else 0
        folder = OUT / 'pull' / kind
        records = []
        for level, mesh in (('baseline', 2.5), ('mesh_sensitivity_1', 1.75)):
            answer = replace(cap_question(kind), mesh_size_mm=mesh).read_evidence(folder / level)
            if not answer.completed:
                raise ValueError('Incomplete cap study')
            records.append(json.loads((folder / level / 'result.json').read_text()))
        cap_c = abs(records[1]['metrics']['observations']['pad']['mean_mm'][axis])
        coarse_c = abs(records[0]['metrics']['observations']['pad']['mean_mm'][axis])
        body_c = body['cases'][kind]['pad_mean_displacement_at_1N_mm']
        body_result = json.loads((OUT/'flex'/kind/'mesh_sensitivity_1/result.json').read_text())
        body_pad = body_result['metrics']['observations']['pad']
        cap_pad = records[1]['metrics']['observations']['pad']
        parts = design.build(kind)
        radius = (design.D.sleeve_depth if axis == 1 else design.D.sleeve_width) / 2
        bump = design.local_bump(radius, design.D.latch_z, design.D.bump_width, design.D.detent).val()
        if axis == 0:
            # local_bump is on +Y; rotate onto +X (the assembled pair is symmetric).
            bump = bump.rotate((0,0,0), (0,0,1), -90)
        tooth = section_segments(bump, axis, radius)
        receiver = section_segments(parts['cap'].val(), axis, radius)
        paths = {}
        for gap in (-.15, 0., .15):
            travel = np.linspace(0, 6, 481)
            delta = [profile_retraction(tooth, receiver, s, gap) for s in travel]
            witnesses = []
            for s in (0., 1., 2., 3., 6.):
                direct = required_retraction(parts['cap'].val(), bump, s, axis, gap)
                planar = profile_retraction(tooth, receiver, s, gap)
                if abs(direct-planar) > .001:
                    raise ValueError('Central section fails to represent actual 3D bump/lip path')
                witnesses.append(dict(travel_mm=s, CAD_retraction_mm=direct, profile_retraction_mm=planar))
            nominal = spring_path(travel, delta, body_c + cap_c, 2)
            coarse = spring_path(travel[::2], delta[::2], body_c + cap_c, 2)
            paths[str(gap)] = dict(travel_mm=travel.tolist(), radial_retraction_mm=delta,
                CAD_witnesses=witnesses, **nominal,
                peak_force_step_change=abs(nominal['peak_force_N'] - coarse['peak_force_N']) / nominal['peak_force_N'],
                release_energy_step_change=abs(nominal['undamped_seated_release_force_N']-coarse['undamped_seated_release_force_N'])/nominal['undamped_seated_release_force_N'])
        scenarios = []
        for modulus in (900, 1200, 1800):
            for gap, path in paths.items():
                for count in (1, 2):
                    peak = path['peak_force_N'] * modulus/1200 * count/2
                    scenarios.append(dict(E_MPa=modulus, extra_radial_gap_mm=float(gap), active_catches=count,
                        peak_force_N=peak, equivalent_static_mass_g=peak/9.80665*1000,
                        undamped_seated_release_mass_g=path['undamped_seated_release_force_N']*modulus/1200*count/2/9.80665*1000))
        rows[kind] = dict(body_compliance_mm_N=body_c, cap_compliance_mm_N=cap_c,
            cap_compliance_mesh_change=abs(cap_c-coarse_c)/cap_c,
            cap_native_input_sha256=records[1]['provenance']['input_sha256'],
            cap_load=records[1]['provenance']['loads'], cap_mesh=records[1]['provenance']['mesh'],
            cap_balance=records[1]['metrics']['max_force_balance_relative'],
            cap_peak_strain_at_1N=records[1]['metrics']['question']['peak_strain'],
            radial_pad_displacement_extrema_mm_N=dict(
                body=sorted(abs(body_pad[k][axis]) for k in ('min_mm','max_mm')),
                cap=sorted(abs(cap_pad[k][axis]) for k in ('min_mm','max_mm'))),
            nominal_max_radial_force_per_catch_N=max(paths['0.0']['radial_retraction_mm'])/(body_c+cap_c),
            nominal_scaled_peak_strain=dict(
                body=body['cases'][kind]['max_principal_strain_at_1N']*max(paths['0.0']['radial_retraction_mm'])/(body_c+cap_c),
                cap=records[1]['metrics']['question']['peak_strain']*max(paths['0.0']['radial_retraction_mm'])/(body_c+cap_c)),
            # Unsupported body only: cap is held. Density is an explicit
            # illustrative hypothesis, not measured material or sliced mass.
            full_body_solid_volume_mm3=parts['body'].val().Volume(),
            tooth_section_segments_mm=tooth, receiver_section_segments_mm=receiver,
            paths=paths, scenarios=scenarios)
        print(kind, 'body/cap mm/N', body_c, cap_c, 'nominal force N', paths['0.0']['peak_force_N'], flush=True)
    output = dict(scope='Frictionless straight-pull reduced spring/ramp estimate. Independent catches, clamped crop base and cap roof; not full assembly contact, peel or safe hanging mass.',
        source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in
            ('closure_research_pull.py','closure_research_design.py','m1_design.py','notes/closure_research/flex_summary.json')},
        cases=rows)
    (OUT/'pull_estimate.json').write_text(json.dumps(output, indent=2)+'\n')
    draw(output)


def draw(data):
    from closure_research_drawings import canvas, label, section, save, BLUE, ORANGE, RED
    import m1_design as base
    items = canvas('How much can these wall snaps hold? A conditional straight-pull estimate', 940)
    label(items, 25, 78, 'Both plastic walls bend. A small bump is a spring-loaded ramp, not a positive lock.', 19)
    p = design.build('shell_broad')
    path = data['cases']['shell_broad']['paths']['0.0']
    peak_index = int(np.argmax(path['force_N']))
    lift = path['travel_mm'][peak_index]
    clip = base.box(0,24,248,4,9,12).val()
    xf = lambda v: (65+32*(v.y-20), 130+32*(253-v.z))
    section(items, p['body'].val().intersect(clip), 'YZ', (0,0,0), xf, BLUE)
    cap = p['cap'].val().translate((0,0,lift))
    section(items, cap.intersect(clip), 'YZ', (0,0,0), xf, ORANGE)
    section(items, p['body'].val().intersect(cap).intersect(clip), 'YZ', (0,0,0), xf, RED)
    label(items, 25, 568, f'Actual CAD at {lift:.2f} mm lift; red must be relieved by bending.', 17)
    label(items, 25, 600, 'Body moves inward ←   → Cap spreads outward', 18)
    label(items, 25, 632, 'The model shares this gap using both computed FEM compliances.', 16)
    label(items, 640, 130, 'Straight pull, two independent catches, E = 1200 MPa', 17)
    max_force = max(v['paths']['0.0']['peak_force_N'] for v in data['cases'].values()) * 1.2
    for tick in range(int(max_force)+1):
        y = 520 - tick/max_force*320
        items.append(f'<path d="M660,{y} H1160" stroke="#ddd"/>')
        label(items, 618, y+5, f'{tick} N', 14)
    items.append('<path d="M660,190 V520 H1160" fill="none" stroke="#243444"/>')
    for kind, color, title in (('shell_broad',BLUE,'R1 broad walls'), ('shell_end',ORANGE,'R2 end walls')):
        row = data['cases'][kind]; path = row['paths']['0.0']
        points = ' '.join(f'{660+s/6*500:.2f},{520-max(0,f)/max_force*320:.2f}' for s,f in zip(path['travel_mm'],path['force_N']))
        items.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        peak = path['peak_force_N']
        yy = 586 if kind=='shell_broad' else 620
        label(items, 640, yy, f'{title}: {peak:.1f} N ≈ {peak/9.80665*1000:.0f} g equivalent', 18)
    label(items, 790, 552, 'Cap withdrawal: 0 → 6 mm', 16)
    label(items, 25, 702, 'Equivalent grams means a slow, steady downward load: 100 g ≈ 0.98 N. It is NOT a safe payload rating.', 19)
    label(items, 25, 746, 'Initial slack allows a suddenly released body to gain speed: the zero-damping energy limit is lower (see notes).', 18)
    label(items, 25, 790, 'R3: ring deformation/peeling is not resolved. R4: lifting loads the rails; its sliding snap is a different load.', 18)
    label(items, 25, 834, 'Shown curves omit friction, joint rocking and coupled contact; negative recovery force is omitted from this plot.', 17)
    label(items, 25, 884, 'Native cap/body stiffness, CAD ramp path, mesh/travel checks and fit/material scenarios are retained in the notes.', 17)
    save('pull_estimate', items, extra_sources=('closure_research_pull.py',), data_files=('notes/closure_research/pull_estimate.json',))


if __name__ == '__main__':
    if sys.argv[1:] == ['report']:
        report()
    elif len(sys.argv) == 5 and sys.argv[1] == 'run':
        run(sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]))
    else:
        raise SystemExit('Usage: closure_research_pull.py run KIND NEW_NATIVE_DIRECTORY NEW_COMPACT_DIRECTORY | report')
