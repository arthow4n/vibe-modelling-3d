"""Check retained webs and transverse skin bridges in the thin batch."""
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import thin_design as t
import design as b

ROOT=Path(__file__).resolve().parent


def crossing_tracks(paths, start, end, z):
    """Distinct extrusion centreline crossings of a local transverse witness."""
    ax,ay=start; dx,dy=end[0]-ax,end[1]-ay
    hits=[]
    for x,y,nx,ny,pz,width,role in paths:
        if abs(pz-z)>1e-5:
            continue
        ex,ey=nx-x,ny-y
        det=dx*ey-dy*ex
        if abs(det)<1e-9:
            continue
        t=((x-ax)*ey-(y-ay)*ex)/det
        u=((x-ax)*dy-(y-ay)*dx)/det
        if 0<=t<=1 and 0<=u<=1:
            if not any(abs(t-h['position'])<.01 for h in hits):
                hits.append({'position':t,'width_mm':width,'role':role})
    return sorted(hits,key=lambda h:h['position'])


def require_multiple_tracks(paths,start,end,z,name,part):
    tracks=crossing_tracks(paths,start,end,z)
    substantial=[h for h in tracks if .38<=h['width_mm']<=.65]
    assert len(substantial)>=2, f'{name} {part}: needs two substantial paths, got {tracks}'
    return {'variant':name,'part':part,'z_mm':z,'tracks':tracks,'substantial_track_count':len(substantial)}


def main():
    report=json.loads((ROOT/'notes/thin_final.json').read_text())
    run=Path(report['slice']['kept_run_directory'])
    settings=json.loads((run/'effective-settings.json').read_text())
    assert all(settings[k]=='180' for k in ('bridge_angle','internal_bridge_angle'))
    assert settings['enable_support']=='0'
    paths=list(orca_linear_paths(run/'plate_1.gcode'))
    support=[p for p in orca_linear_paths(run/'support_probe/plate_1.gcode') if p[-1].startswith('Support')]
    assert not any(p[-1].startswith('Support') for p in paths)
    roofs=[]; witnesses=[]; probe_locations=[]; multi_tracks=[]
    fig,ax=plt.subplots(figsize=(10,7))
    ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in support],colors='#1598a5',linewidths=.4))
    # Centre the known 118 x 74.2 mm compound without rotating components.
    for i,name in enumerate(t.SELECTED_NAMES):
        v=t.variant_named(name)
        x=93+42*i; y=114.9
        for part,cy,base in (('cup',y,v.backing),('pad',y+41,v.backing+b.PAD_PRELOAD)):
            size=34 if part=='cup' else v.pad_size
            ax.add_patch(Rectangle((x-size/2,cy-size/2),size,size,fill=False,edgecolor='#334252'))
            ax.text(x,cy+size/2+1,f'{name} {part}',ha='center')
            local_support=[p for p in support if abs((p[0]+p[2])/2-x)<size/2 and abs((p[1]+p[3])/2-cy)<size/2]
            probe_locations.append({'variant':name,'part':part,'segments':len(local_support),
                'z_range_mm':[min(p[4] for p in local_support),max(p[4] for p in local_support)] if local_support else None})
            z=round(base+v.core+.2,3)
            local=[p for p in paths if abs(p[4]-z)<1e-5 and abs((p[0]+p[2])/2-x)<11 and abs((p[1]+p[3])/2-cy)<11]
            across=sum(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in local)
            along=sum(abs(p[3]-p[1])>3*abs(p[2]-p[0]) for p in local)
            assert across>0 and along==0, f'{name} {part}: bridge direction'
            roofs.append({'variant':name,'part':part,'first_skin_layer_z_mm':z,'transverse_segments':across,'longitudinal_segments':along,'roles':dict(Counter(p[-1] for p in local))})
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in local],colors='#ae59a7',linewidths=.35))
            for depth in (.1,round(v.core/2,1),round(v.core-.1,1)):
                # Sample centre of a 0.2 mm layer, matching the chevron locus.
                z=round(base+depth+.1,3)
                px=x-1.8+t.shift(v,depth)
                coverage=section_coverage(paths,x_mm=px,z_mm=z,span_mm=(cy-6,cy+6))
                assert coverage['uncovered_width_mm']<.01, f'{name} {part}: omitted web at {z}'
                witnesses.append({'variant':name,'part':part,'z_mm':z,'coverage':coverage})
                if name in ('I26','I22'):
                    multi_tracks.append(require_multiple_tracks(paths,(px-.85,cy+2.3),(px+.85,cy+2.3),z,name,part))
        # Opposing side-wall pairs have orthogonal toolpaths. Test all four.
        for depth in (.3,round(v.core/2,1),round(v.core-.3,1)):
            normal=-b.CUP_SIZE/2+v.backing+depth
            tangent=-1.8+t.shift(v,depth)
            for face,px,py in (('left',x+normal,y+tangent),('right',x-normal,y-tangent),
                               ('front',x-tangent,y+normal),('back',x+tangent,y-normal)):
                coverage=section_coverage(paths,x_mm=px,z_mm=18.,span_mm=(py-.08,py+.08))
                assert coverage['uncovered_width_mm']<.01, f'{name} {face}: omitted side web at {depth}'
                witnesses.append({'variant':name,'part':face,'depth_mm':depth,'coverage':coverage})
                if name in ('I26','I22'):
                    # Cross the local web in the tangent direction of each wall.
                    dx,dy=(0,.85) if face in ('left','right') else (.85,0)
                    multi_tracks.append(require_multiple_tracks(paths,(px-dx,py-dy),(px+dx,py+dy),18.,name,face))
    ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)')
    ax.set_title('Thin I: support-probe paths cyan; first contact-skin paths purple')
    fig.tight_layout();fig.savefig(ROOT/'renders/thin_path_review.png',dpi=150)
    # View the actual first-layer paths from below, where the recess is read.
    labels_fig,axes=plt.subplots(2,3,figsize=(10,7))
    for i,name in enumerate(t.SELECTED_NAMES):
        x=93+42*i
        for row,kind,cy in ((0,'cup',114.9),(1,'pad',155.9)):
            label_ax=axes[row,i]
            label_ax.set_xlim(18,-18);label_ax.set_ylim(-18,18)
            label_ax.set_aspect('equal');label_ax.set_title(f'{name} {kind}: underside')
            label_ax.set_xlabel('mm');label_ax.set_ylabel('mm')
    labels_fig.tight_layout();labels_fig.canvas.draw()
    for i,name in enumerate(t.SELECTED_NAMES):
        x=93+42*i
        for row,kind,cy in ((0,'cup',114.9),(1,'pad',155.9)):
            label_ax=axes[row,i]
            local=[p for p in paths if abs(p[4]-.2)<1e-5 and
                abs((p[0]+p[2])/2-x)<17.1 and abs((p[1]+p[3])/2-cy)<17.1]
            assert local, f'{name} {kind}: missing first-layer paths'
            points_per_mm=label_ax.get_window_extent().width/labels_fig.dpi*72/36
            label_ax.add_collection(LineCollection([[(p[0]-x,p[1]-cy),(p[2]-x,p[3]-cy)] for p in local],
                linewidths=[p[5]*points_per_mm for p in local],colors='#3d6679'))
    labels_fig.suptitle('Large labels: first-layer extrusion-width metadata, viewed from below',y=1.01)
    labels_fig.savefig(ROOT/'renders/thin_label_paths.png',dpi=160,bbox_inches='tight')
    result={'scope':'Orca 2.4.2 TPU profile, thin I batch; local paths only, not material/quietness qualification',
        'registration':'source compound translated (+73,+94.9) mm, unrotated',
        'primary_support_segments':0,'probe_support_segments':len(support),
        'probe_support_z_range_mm':[min(p[4] for p in support),max(p[4] for p in support)] if support else None,
        'probe_locations':probe_locations,'roofs':roofs,'web_witnesses':witnesses,
        'replacement_web_criterion':{'minimum_tracks':2,'substantial_width_range_mm':[.38,.65]},
        'replacement_web_tracks':multi_tracks}
    (ROOT/'notes/thin_path_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
