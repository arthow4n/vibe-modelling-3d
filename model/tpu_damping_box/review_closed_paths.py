"""Closed-skin path review: check open gaps, not just material presence."""
import json,re
from collections import defaultdict,Counter
from pathlib import Path
from math import cos,sin,pi,sqrt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from review_thin_paths import require_multiple_tracks
import skin_design as s

ROOT=Path(__file__).resolve().parent


def bridge_heights(path):
    role='';height=None;heights=defaultdict(set)
    for line in path.open():
        if line.startswith(';TYPE:'):role=line[6:].strip()
        if line.startswith(';HEIGHT:'):height=float(line[8:])
        if line.startswith('G1 ') and ('X' in line or 'Y' in line) and 'bridge' in role.lower():
            m=re.search(r' E([0-9.]+)',line)
            if m and float(m[1])>0:
                assert height is not None,'Missing bridge-height metadata'
                heights[role].add(height)
    assert heights,'No bridge metadata found'
    assert all(h<=.10001 for values in heights.values() for h in values),'Thick bridge would intrude into shallow core'
    return {k:sorted(v) for k,v in heights.items()}


def wall_paths(paths,x,y,angle):
    c,t=cos(angle*pi/180),sin(angle*pi/180)
    result=[]
    for ax,ay,bx,by,z,width,role in paths:
        u,v=c*(ax-x)+t*(ay-y),-t*(ax-x)+c*(ay-y)
        nu,nv=c*(bx-x)+t*(by-y),-t*(bx-x)+c*(by-y)
        # Swap canonical tangent/normal to use the shared vertical section API.
        result.append((v,u,nv,nu,z,width,role))
    return result


def main():
    receipt=json.loads((ROOT/'notes/closed_final.json').read_text())
    run=Path(receipt['slice']['kept_run_directory'])
    settings=json.loads((run/'effective-settings.json').read_text())
    for key in ('thick_bridges','thick_internal_bridges','enable_support'):
        assert settings[key]=='0',key
    assert settings['layer_height']=='0.1' and settings['initial_layer_print_height']=='0.1'
    assert settings['wall_generator']=='arachne'
    assert all(settings[k]=='180' for k in ('bridge_angle','internal_bridge_angle'))
    paths=list(orca_linear_paths(run/'plate_1.gcode'))
    assert not any(p[-1].startswith('Support') for p in paths)
    layers=defaultdict(list)
    for p in paths:layers[round(p[4],3)].append(p)
    support=[p for p in orca_linear_paths(run/'support_probe/plate_1.gcode') if p[-1].startswith('Support')]
    heights=bridge_heights(run/'plate_1.gcode')
    fig,ax=plt.subplots(figsize=(8,8))
    ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in support],colors='#199fa8',linewidths=.35))
    gapfig,gapaxes=plt.subplots(2,1,figsize=(9,4))
    roofs=[];channels=[];webs=[];gaps=[];proposals=[]
    for i,name in enumerate(s.SELECTED_NAMES):
        v=s.variant_named(name);x=114+42*i;y=114.8
        for part,cy,base,size in (('cup',y,v.backing,34),('pad',y+41,v.backing+v.preload,v.pad_size)):
            ax.add_patch(Rectangle((x-size/2,cy-size/2),size,size,fill=False,color='#334252'))
            ax.text(x,cy+size/2+1,f'{name} {part}',ha='center')
            z=round(base+v.core+.1,3)
            local=[p for p in layers[z] if abs((p[0]+p[2])/2-x)<11 and abs((p[1]+p[3])/2-cy)<11]
            across=sum(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in local)
            along=sum(abs(p[3]-p[1])>3*abs(p[2]-p[0]) for p in local)
            assert across>0 and along==0,f'{name} {part}: wrong bridge direction'
            roofs.append({'variant':name,'part':part,'first_skin_z_mm':z,'roles':dict(Counter(p[-1] for p in local))})
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in local],colors='#a65bb0',linewidths=.35))
            local_support=[p for p in support if abs((p[0]+p[2])/2-x)<size/2 and abs((p[1]+p[3])/2-cy)<size/2]
            proposals.append({'variant':name,'part':part,'segments':len(local_support),'z_range_mm':
                [min(p[4] for p in local_support),max(p[4] for p in local_support)] if local_support else None})
            for layer in range(1,round(v.core/.1)+1):
                z=round(base+.1*layer,3);lp=layers[z]
                for offset in (-2.2,2.2,6.6):
                    empty=section_coverage(lp,x_mm=x+offset,z_mm=z,span_mm=(cy-6,cy+6))
                    assert empty['filled_width_mm']<.01,f'{name} {part}: channel filled at {z}'
                    channels.append({'variant':name,'part':part,'z_mm':z,'x_offset_mm':offset,'filled_width_mm':empty['filled_width_mm']})
                material=section_coverage(lp,x_mm=x,z_mm=z,span_mm=(cy-6,cy+6))
                assert material['uncovered_width_mm']<.01,f'{name} {part}: support omitted'
                webs.append(require_multiple_tracks(lp,(x-.7,cy+2.3),(x+.7,cy+2.3),z,name,part))
                swapped=[(p[1],p[0],p[3],p[2],p[4],p[5],p[6]) for p in lp]
                clear=section_coverage(swapped,x_mm=cy+2.3,z_mm=z,span_mm=(x+.55,x+3.85))
                assert clear['filled_width_mm']<.01,f'{name}: transverse 3.3 mm channel obstructed'
        for z in (5.,18.,30.):
            for face,angle in (('left',0),('front',90),('right',180),('back',270)):
                local=wall_paths(layers[z],x,y,angle)
                for tangent in (-6.6,-2.2,2.2,6.6):
                    coverage=section_coverage(local,x_mm=tangent,z_mm=z,span_mm=(-17,-17+v.thickness))
                    assert len(coverage['intervals_mm'])==2,f'{name} {face}: skins missing or fused'
                    gap=coverage['internal_gap_mm']
                    assert gap>=v.core-.10001,f'{name} {face}: inadequate skin gap'
                    assert all(b-a>=.36 for a,b in coverage['intervals_mm']),f'{name}: thin skin path'
                    gaps.append({'variant':name,'face':face,'z_mm':z,'tangent_mm':tangent,'gap_mm':gap,'coverage':coverage})
                    if z==18 and face=='left' and tangent==2.2:
                        ga=gapaxes[i]
                        for a,b in coverage['intervals_mm']:
                            ga.add_patch(Rectangle((a+17,.2),b-a,.6,color='#467387'))
                        ga.set_xlim(-.1,1.7);ga.set_ylim(0,1);ga.set_yticks([])
                        ga.set_title(f'{name}: normal wall section between ribs; path-metadata gap {gap:.3f} mm')
                        ga.set_xlabel('Distance from exterior (mm)')
    ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)')
    ax.set_title('Closed batch: probe support cyan; first skin paths purple')
    fig.tight_layout();fig.savefig(ROOT/'renders/closed_path_review.png',dpi=150)
    gapfig.tight_layout();gapfig.savefig(ROOT/'renders/closed_gap_review.png',dpi=150)
    # Same-scale first-layer preview: ID recesses are one 0.1 mm layer deep.
    lf,axes=plt.subplots(2,2,figsize=(8,8))
    for i,name in enumerate(s.SELECTED_NAMES):
        x=114+42*i
        for row,kind,cy in ((0,'cup',114.8),(1,'pad',155.8)):
            a=axes[row,i];a.set_xlim(18,-18);a.set_ylim(-18,18);a.set_aspect('equal');a.set_title(f'{name} {kind}: underside')
    lf.tight_layout();lf.canvas.draw()
    for i,name in enumerate(s.SELECTED_NAMES):
        x=114+42*i
        for row,kind,cy in ((0,'cup',114.8),(1,'pad',155.8)):
            a=axes[row,i]
            local=[p for p in layers[.1] if abs((p[0]+p[2])/2-x)<17.1 and abs((p[1]+p[3])/2-cy)<17.1]
            scale=a.get_window_extent().width/lf.dpi*72/36
            a.add_collection(LineCollection([[(p[0]-x,p[1]-cy),(p[2]-x,p[3]-cy)] for p in local],
                linewidths=[p[5]*scale for p in local],colors='#467387'))
    lf.savefig(ROOT/'renders/closed_labels.png',dpi=150)
    result={'scope':'Orca path metadata, not measured polymer or physical validation',
        'registration':'2-column source translated (+94,+94.8) mm without rotation',
        'criteria':{'layer_mm':.1,'bridge_height_max_mm':.1,'minimum_skin_path_mm':.36,
            'minimum_skin_gap_mm':'nominal core minus 0.1','channel_air_witness_width_mm':3.3,
            'support_minimum_tracks':2,'support_track_width_range_mm':[.38,.65]},
        'bridge_heights_mm':heights,'roofs':roofs,'core_channels':channels,'support_tracks':webs,
        'wall_gaps':gaps,'support_proposals':proposals,
        'old_I22_CAD_screen':{'core_mm':1.,'chevron_normal_web_mm':.9,
            'same_layer_horizontal_channel_mm':3.6-.9*sqrt(1+(1/1.3)**2),
            'interpretation':'Neighbouring ribs do not nominally join. Thick returning legs/printed spreading are different questions; exact reported feature unresolved.'}}
    (ROOT/'notes/closed_path_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'roofs':len(roofs),'open_core_channels':len(channels),'support_sections':len(webs),
        'wall_gap_sections':len(gaps),'min_wall_gap_mm':{n:min(g['gap_mm'] for g in gaps if g['variant']==n) for n in s.SELECTED_NAMES},'bridge_heights':heights},indent=2))


if __name__=='__main__':
    main()
