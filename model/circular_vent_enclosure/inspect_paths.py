"""Read the final Orca paths for thin hood walls and local support removal review."""
import json
from pathlib import Path
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
from execution.identity import digest
from vent_parameters import Parameters

ROOT=Path(__file__).resolve().parent


def inspect():
    p=Parameters(); reports={}; paths={}; findings={}; visuals=ROOT/'renders/print'
    for part,filename in (('hood','final_review.json'),('clamp','clamp_review.json')):
        receipt=json.loads((ROOT/'notes'/filename).read_text())
        assert receipt['slice']['ok']
        raw=Path(receipt['slice']['kept_run_directory'])
        primary_support=str(receipt['slice']['effective_settings']['enable_support'])=='1'
        path=raw/'plate_1.gcode' if primary_support else raw/'support_probe/plate_1.gcode'
        paths[part]=list(orca_linear_paths(path))
        support=[v for v in paths[part] if v[-1].startswith('Support')]
        top=max(v[4] for v in support) if support else min({v[4] for v in paths[part]},key=lambda z:abs(z-(p.hood_standoff-8)))
        at_top=[v for v in paths[part] if abs(v[4]-top)<1e-6]
        lines=['<svg xmlns="http://www.w3.org/2000/svg" width="810" height="850" viewBox="0 0 270 283">',
               '<rect width="270" height="283" fill="white"/>',
               f'<text x="5" y="8" font-family="sans-serif" font-size="4">{part}: actual Orca paths at support top Z{top:.2f} mm</text>',
               '<text x="5" y="14" font-family="sans-serif" font-size="3.5">Blue: part; orange: support. Line width is slicer metadata.</text>']
        for x,y,nx,ny,z,width,role in at_top:
            if role.startswith('Brim'): continue
            color='#e58e2c' if role.startswith('Support') else '#376d9f'
            lines.append(f'<path d="M{x:.4f} {283-y:.4f}L{nx:.4f} {283-ny:.4f}" fill="none" stroke="{color}" stroke-width="{width:.4f}" stroke-linecap="round"/>')
        lines.append('</svg>');(visuals/(part+'_support_paths.svg')).write_text('\n'.join(lines))
        findings[part]=dict(input_sha256=receipt['slice']['input_sha256'],gcode_sha256=digest(path),
            supports_in_primary=primary_support,support_z_min_mm=min((v[4] for v in support),default=None),
            support_z_max_mm=top if support else None,support_segments=len(support),
            support_roles=sorted({v[-1] for v in support}))
        reports[part]=receipt
    sections=[]
    for z in (16.,42.):
        outer=p.radius if z < p.taper_start else p.radius-p.slope*(z-p.taper_start)
        inner=p.inner_radius(z)
        span=(135+inner,135+outer)
        coverage=section_coverage(paths['hood'],x_mm=135,z_mm=z,span_mm=span)
        crossings=[]
        for x,y,nx,ny,height,width,role in paths['hood']:
            if abs(height-z)>1e-5 or role.startswith(('Support','Brim')) or abs(nx-x)<1e-10: continue
            if not min(x,nx)<=135<=max(x,nx):continue
            at=y+(ny-y)*(135-x)/(nx-x)
            if span[0] <= at <= span[1]:crossings.append((round(at,5),width,role))
        count=len({v[0] for v in crossings})
        assert count >= 3, f'Fewer than three actual extrusion paths at Z{z}: {crossings}'
        assert coverage['uncovered_width_mm'] < .15, (z,coverage)
        sections.append(dict(z_mm=z,span_mm=span,distinct_crossings=count,
            crossings=crossings,coverage=coverage))
    masses={};seconds={}
    for part,r in reports.items():
        g=Path(r['slice']['kept_run_directory'])/'plate_1.gcode'
        for line in g.open():
            if line.startswith('; filament used [g] ='):
                masses[part]=float(line.split('=')[1])
    return dict(variant='v2-clamp',sections=sections,supports=findings,
        primary_filament_estimates_g=masses,combined_primary_filament_g=sum(masses.values()),
        reduction_vs_v1_slice_percent=100*(1-sum(masses.values())/220.88),
        source_sha256={name:digest(ROOT/name) for name in ('circular_vent_enclosure.py','mounting_clamp.py','vent_parameters.py','inspect_paths.py')},
        scope='Selected-profile local path coverage and accessible support locations only. '
              'Not deposited dimensions, print strength, sag or successful physical support removal.')


if __name__=='__main__':
    result=inspect()
    (ROOT/'notes/manufacturing_paths.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
