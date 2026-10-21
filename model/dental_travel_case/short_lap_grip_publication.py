"""Inspect native three-line paths, then associate current paired exports."""
import json
import re
from pathlib import Path
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from closure_research_checks import hashes
from closure_research_verification import require_sources
from short_lap_grip_checks import ROOT,OUT,STEM,INPUTS
from short_lap_grip import RAMP
from grip_placement import dimensions,LAYOUTS
from short_lap_thin import WALL

PUBLICATION_INPUTS=INPUTS+('short_lap_grip_publication.py','../../physical_analysis/manufacturing.py')


def main():
    checks=json.loads((OUT/'finished_checks.json').read_text());require_sources(checks['source_sha256'])
    inputs=hashes(PUBLICATION_INPUTS)
    receipt=json.loads((OUT/'finished_slice.json').read_text())
    assert receipt['ok'] and receipt['geometry']['valid'] and receipt['slice']['ok']
    sl=receipt['slice'];assert sl['input_sha256']==hashes((STEM+'.stl',))[STEM+'.stl']
    assert sl['support_probe']['ok'] and not sl['support_probe']['generated']
    assert sl['placement']=='center' and sl['effective_settings']['wall_loops']=='3'
    assert sl['effective_settings']['layer_height']=='0.2'
    gcode=Path(sl['kept_run_directory'])/'plate_1.gcode'
    paths=list(orca_linear_paths(gcode));d=dimensions();band=LAYOUTS['selected'];rows=[]
    # Same accepted export placement as the old pair: cap +112 mm X, centred
    # as one STL by Orca. Its unchanged exterior backing determines X offset.
    cx=78.675;cy=135.
    for name,print_center,xcenter in (('body',d.seam+band.body_center_mm,cx),
                                    ('cap',d.length-d.seam-band.cap_center_mm,cx+112)):
        for dz in (-7.,0.,7.):
            z=print_center+dz
            # Orca slices halfway through each 0.2 mm layer, reports its top Z.
            axial=abs(z-.1-print_center)
            u=min(1.,max(0.,(band.band_width_mm/2-axial)/RAMP))
            inset=band.depth_mm*u**3*(10-15*u+6*u*u)
            hi=xcenter+d.width/2-inset;lo=hi-WALL;hits=set()
            for x,y,nx,ny,zz,w,role in paths:
                if abs(zz-z)>1e-5 or abs(ny-y)<1e-9 or role.startswith(('Support','Brim')):continue
                if min(y,ny)<=cy<=max(y,ny):
                    at=x+(nx-x)*(cy-y)/(ny-y)
                    if lo-.05<=at<=hi+.05:hits.add((round(at-lo,4),w,role))
            swapped=((y,x,ny,nx,zz,w,r) for x,y,nx,ny,zz,w,r in paths)
            coverage=section_coverage(swapped,x_mm=cy,z_mm=z,span_mm=(lo,hi))
            assert len(hits)==3,(name,z,hits)
            assert coverage['uncovered_width_mm']<.05 and coverage['internal_gap_mm']<.01,(name,z,coverage)
            rows.append(dict(part=name,print_z_mm=z,span_mm=[lo,hi],strokes=[dict(offset_mm=a,width_mm=w,role=r) for a,w,r in sorted(hits)],coverage=coverage))
    text=gcode.read_text();mass=float(re.search(r'^; total filament used \[g\] = ([\d.]+)',text,re.M)[1])
    assert inputs==hashes(PUBLICATION_INPUTS),'Inputs changed during publication review'
    record=dict(source_sha256=inputs,artifacts=hashes((STEM+'.step',STEM+'.stl','notes/grip_human/finished_slice.json','notes/grip_human/finished_checks.json')),
        sections=rows,estimated_mass_g=mass,slice_input_sha256=sl['input_sha256'],
        scope='Selected Q2C PETG profile; three strokes at band landing and ramps. No printed strength/feel inference')
    (OUT/'finished_publication.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(sections=[dict(part=r['part'],z=r['print_z_mm'],strokes=len(r['strokes'])) for r in rows],estimated_mass_g=mass)))


if __name__=='__main__':main()
