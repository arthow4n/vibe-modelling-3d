"""Target actual arm fill/relief for I's effective-solid local physics assumption."""
import json
import hashlib
from pathlib import Path
import cap_i_grip_keys as i
from physical_analysis.manufacturing import orca_linear_paths, section_coverage

directory=Path(__file__).parent
review=json.loads((directory/'notes/cap_i_review.json').read_text())
slice=review['slice']
assert slice['ok'] and slice['placement']=='preserve'
gcodes=list(Path(slice['kept_run_directory']).glob('*.gcode'))
assert len(gcodes)==1,'This local review expects the delivered single plate'
paths=list(orca_linear_paths(gcodes[0]))
sections=[]
for number,(ax,ay) in enumerate(i.PRINT_CENTRES,1):
    for xs in (-1,1):
        for ys in (-1,1):
            def local(x,y):
                px=(x-ax)*xs-i.h.KEY_WAIST_HALF_X
                py=(y-ay)*ys-i.KEY_SEAM_GAP/2
                return (px*i.TANGENT[0]+py*i.TANGENT[1],px*i.NORMAL[0]+py*i.NORMAL[1])
            registered=[]
            for x,y,nx,ny,z,width,role in paths:
                a,b=local(x,y),local(nx,ny)
                registered.append((*a,*b,z,width,role))
            for s in (.7,2.5):
                for z in (1.2,2.4):
                    arm=section_coverage(registered,x_mm=s,z_mm=z,
                        span_mm=(i.CORE_GROWTH-i.ARM_THICKNESS,i.CORE_GROWTH))
                    relief=section_coverage(registered,x_mm=s,z_mm=z,
                        span_mm=(i.RELIEF_N-i.RELIEF_WIDTH/2+.1,
                                 i.RELIEF_N+i.RELIEF_WIDTH/2-.1))
                    assert arm['uncovered_width_mm']<.05,'Assumed solid arm has a significant unfilled section'
                    assert relief['filled_width_mm']<.05,'Actual paths bridge/fill the middle of a flexure relief'
                    sections.append(dict(number=number,side=(xs,ys),station_mm=s,z_mm=z,
                        arm=arm,relief=relief))
record=dict(sections=sections,profile=slice['profiles'],slicer_version=slice['slicer_version'],
    gcode_sha256=hashlib.sha256(gcodes[0].read_bytes()).hexdigest(),
    stl_sha256=hashlib.sha256((directory/'cap_i_grip_keys.stl').read_bytes()).hexdigest(),
    scope='Registered local arm sections, recorded-width capsule approximation; '
          'not measured polymer, isotropy, bonding or strength. Gap middle excludes 0.1 mm edge margins.')
(directory/'notes/cap_i_paths.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,arm_sections=len(sections),
    max_unfilled_arm_mm=max(s['arm']['uncovered_width_mm'] for s in sections),
    max_filled_relief_middle_mm=max(s['relief']['filled_width_mm'] for s in sections))))
