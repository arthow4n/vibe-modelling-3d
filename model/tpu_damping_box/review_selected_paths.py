"""Selected-layout thin-web preservation and first-roof bridge inspection."""
import json
from collections import Counter
from pathlib import Path
from math import sin, pi
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import design as d
from selection import SELECTED_NAMES

ROOT=Path(__file__).resolve().parent


def shift(v,depth):
    h=d.ZONE-d.BACKING-v.skin
    if v.core=='chevron':
        return -0.5+2*min(depth/h,1-depth/h)
    if v.core=='bowed':
        return d.BOW_AMPLITUDE*sin(pi*depth/h)
    raise ValueError(v.core)


def main():
    report=json.loads((ROOT/'notes/selected_final.json').read_text())
    run=Path(report['slice']['kept_run_directory'])
    settings=json.loads((run/'effective-settings.json').read_text())
    assert all(settings[k]=='180' for k in ('bridge_angle','internal_bridge_angle'))
    assert settings['enable_support']=='0'
    primary=list(orca_linear_paths(run/'plate_1.gcode'))
    support=[p for p in orca_linear_paths(run/'support_probe/plate_1.gcode') if p[-1].startswith('Support')]
    assert not any(p[-1].startswith('Support') for p in primary)
    fig,ax=plt.subplots(figsize=(8,9))
    ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in support],colors='#16a0b6',linewidths=.4))
    rows=[]; preserved=[]
    for i,name in enumerate(SELECTED_NAMES):
        # Source layout 2 columns, translated as one compound to bed centre.
        x=114+(i%2)*42; y=73+(i//2)*84
        v=d.variant_named(name)
        for part,cy,size,z in [('cup',y,34,4-v.skin+.2),('pad',y+41,32,4+d.PAD_PRELOAD-v.skin+.2)]:
            ax.add_patch(Rectangle((x-size/2,cy-size/2),size,size,fill=False,edgecolor='#334252'))
            ax.text(x,cy+size/2+1,f'{name} {part}',ha='center')
            if name=='A':continue
            local=[p for p in primary if abs(p[4]-z)<1e-5 and abs((p[0]+p[2])/2-x)<12 and abs((p[1]+p[3])/2-cy)<12]
            across=sum(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in local)
            along=sum(abs(p[3]-p[1])>3*abs(p[2]-p[0]) for p in local)
            assert across>0 and along==0, f'{name} {part}: wrong bridge direction'
            rows.append({'variant':name,'part':part,'first_roof_z_mm':z,'roles':dict(Counter(p[-1] for p in local)),
                         'transverse_segments':across,'longitudinal_segments':along})
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in local],colors='#a65cb8',linewidths=.35))
        if name in ('H','I'):
            h=d.ZONE-d.BACKING-v.skin
            # Both horizontal cores: three layers through each web depth.
            for kind,base,cy in (('cup-floor-core',d.BACKING,y),('pad-core',d.BACKING+d.PAD_PRELOAD,y+41)):
                for depth in (.3,.9,1.7):
                    layer=round(base+depth+.1,1)
                    px=x-1.8+shift(v,depth)
                    coverage=section_coverage(primary,x_mm=px,z_mm=layer,span_mm=(cy-6,cy+6))
                    assert coverage['uncovered_width_mm']<.01, f'{name}: {kind} omitted at z={layer}'
                    preserved.append({'variant':name,'part':kind,'z_mm':layer,'coverage':coverage})
            # Wall web: inspect the same depth locations in its XY section.
            for depth in (.4,h/2,h-.4):
                px=x-16.2+depth
                py=y-1.8+shift(v,depth)
                coverage=section_coverage(primary,x_mm=px,z_mm=18.0,span_mm=(py-.1,py+.1))
                assert coverage['uncovered_width_mm']<.01, f'{name}: wall web omitted at depth={depth}'
                preserved.append({'variant':name,'part':'cup-side-core','depth_mm':depth,'coverage':coverage})
    ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)')
    ax.set_title('Selected batch: support probe cyan; first roof paths purple')
    fig.tight_layout();fig.savefig(ROOT/'renders/selected_path_review.png',dpi=150)
    result={'scope':'Selected A/E/H/I; Orca toolpath metadata only, not printed material or acoustic evidence',
      'registration':'2-column source layout translated (+94,+53) mm; no component rotation',
      'primary_support_segments':0,'probe_support_z_range_mm':([min(p[4] for p in support),max(p[4] for p in support)] if support else None),
      'roof_layers':rows,'thin_core_witnesses':preserved}
    (ROOT/'notes/selected_path_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
