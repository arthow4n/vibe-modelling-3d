"""Local thin-sandwich toolpath evidence from the retained native slice."""
from pathlib import Path
from collections import defaultdict
import json
import math
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import design as d
from checks import inside

ROOT=Path(__file__).resolve().parent


def local_paths(paths,q,tangent):
    tx,ty=tangent.x,tangent.y
    nx,ny=-ty,tx
    return [((a-q.x)*tx+(b-q.y)*ty,(a-q.x)*nx+(b-q.y)*ny,
             (c-q.x)*tx+(e-q.y)*ty,(c-q.x)*nx+(e-q.y)*ny,z,w,r)
            for a,b,c,e,z,w,r in paths]


def crossing_tracks(paths):
    hits=[]
    for x,y,nx,ny,z,width,role in paths:
        if (y<=0<ny or ny<=0<y) and .35<=width<=.65:
            u=-y/(ny-y)
            hit=x+u*(nx-x)
            if abs(hit)<.65 and not any(abs(hit-h)<.03 for h in hits):
                hits.append(hit)
    return len(hits)


def main():
    receipt=json.loads((ROOT/'notes/final_review.json').read_text())
    run=Path(receipt['slice']['kept_run_directory'])
    settings=json.loads((run/'effective-settings.json').read_text())
    assert settings['enable_support']=='0'
    assert settings['layer_height']==settings['initial_layer_print_height']=='0.2'
    assert settings['thick_bridges']==settings['thick_internal_bridges']=='0'
    assert settings['bridge_angle']==settings['internal_bridge_angle']=='180'
    paths=list(orca_linear_paths(run/'plate_1.gcode'))
    layers=defaultdict(list)
    for p in paths:
        layers[round(p[4],3)].append(p)
    assert not any(p[-1].startswith('Support') for p in paths)
    # Compound is centered as a whole, unrotated. Both ordinary outer profiles
    # reach +/-34.9 mm, with the cap's centre placed at X=82 mm.
    shift_x,shift_y=135-41,135
    gaps=[];ribs=[];regions={}
    fig,axes=plt.subplots(2,3,figsize=(13,8))
    for ax,(part,z) in zip(axes.flat,(('body',10.),('body',150.),('body',180.),
                                     ('cap',190.),('cap',220.))):
        printed_z=round(z-d.D.floor-d.END_GAP if part=='body' else d.D.length-d.D.floor-d.END_GAP-z,3)
        lp=layers[printed_z]
        assert lp,('Missing layer',part,z,printed_z)
        # Convert actual printed coordinates back to assembled CAD XY.
        local=[(a-shift_x-(82 if part=='cap' else 0),
                (b-shift_y)*(-1 if part=='cap' else 1),
                c-shift_x-(82 if part=='cap' else 0),
                (e-shift_y)*(-1 if part=='cap' else 1),pz,w,r)
               for a,b,c,e,pz,w,r in lp]
        wire=d.section_wire(d.envelope(part,.8),z)
        n=math.ceil(wire.Length()/d.PITCH)
        p=d.cup(part).val()
        region=[]
        for edge in wire.Edges():
            # Include all distinct straight and curved regions. Search a few
            # positions to avoid intentionally solid ribs at a witness.
            found=None
            for f in (.15,.3,.45,.6,.75,.9):
                q=edge.positionAt(f)
                if inside(p,(q.x,q.y,z)):
                    continue
                coverage=section_coverage(local_paths(local,q,edge.tangentAt(f)),
                    x_mm=0,z_mm=printed_z,span_mm=(-.8,.8))
                if len(coverage['intervals_mm'])==2 and coverage['internal_gap_mm']>=.5:
                    found=coverage
                    break
            if edge.Length()>2 or edge.geomType()=='CIRCLE':
                assert found,('No retained core/skin witness',part,z,edge.geomType(),edge.Center().toTuple())
                assert all(b-a>=.3 for a,b in found['intervals_mm']),'Missing substantial skin path'
                gaps.append(found['internal_gap_mm']);region.append(found)
        for i in range(n):
            q=wire.positionAt(i/n)
            t=wire.tangentAt(i/n)
            # A straight section is enough to establish the retained .9 mm rib
            # tracks; corner/concave core coverage is checked separately above.
            if abs(t.x)<1e-6 or abs(t.y)<1e-6:
                tracks=crossing_tracks(local_paths(local,q,t))
                if tracks>=2:
                    ribs.append(tracks)
                    break
        else:
            raise AssertionError(('No two-track rib',part,z))
        regions[f'{part}:{z}']=len(region)
        ax.add_collection(LineCollection([[(v[0],v[1]),(v[2],v[3])] for v in local],linewidths=.6))
        ax.autoscale();ax.set_aspect('equal');ax.set_title(f'{part}, assembly Z={z:g}')
    support=list(orca_linear_paths(run/'support_probe/plate_1.gcode'))
    support=[p for p in support if p[-1].startswith('Support')]
    ax=axes.flat[-1]
    ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in support],linewidths=.3,color='teal'))
    ax.autoscale();ax.set_aspect('equal');ax.set_title('Automatic support probe, all heights')
    floors=[]
    for cx in (shift_x,shift_x+82):
        for z in (.6,.8,1.0):
            coverage=section_coverage(layers[z],x_mm=cx+2.2,z_mm=z,span_mm=(shift_y-10,shift_y+10))
            assert coverage['filled_width_mm']<.01,'Floor air channel filled'
            floors.append(coverage)
        roof=[p for p in layers[1.4] if abs((p[0]+p[2])/2-cx)<12 and abs((p[1]+p[3])/2-shift_y)<10]
        assert roof and all(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in roof),'First skin bridge does not cross ribs'
    height=None;role='';bridge_heights=set()
    for line in (run/'plate_1.gcode').open():
        if line.startswith(';HEIGHT:'):height=float(line[8:])
        if line.startswith(';TYPE:'):role=line[6:].strip()
        if (line.startswith('G1 ') and ('X' in line or 'Y' in line)
                and 'bridge' in role.lower() and re.search(r' E(?:[0-9]|\.)',line)):
            assert height is not None
            bridge_heights.add(height)
    assert bridge_heights, 'No bridge extrusion-height metadata captured'
    assert max(bridge_heights)<=.20001,'Bridge intrudes into shallow core'
    (ROOT/'renders').mkdir(exist_ok=True)
    fig.tight_layout();fig.savefig(ROOT/'renders/path_review.png',dpi=150)
    report={'scope':'Slicer metadata, not measured deposited TPU or acoustic approval',
            'core_gap_minimum_criterion_mm':.5,'minimum_sampled_gap_mm':min(gaps),
            'skin_core_regions':regions,'rib_track_minimum':min(ribs),
            'floor_air_samples':len(floors),'bridge_heights_mm':sorted(bridge_heights),
            'support_probe_segments':len(support),
            'support_probe_z_range_mm':([min(p[4] for p in support),max(p[4] for p in support)] if support else None)}
    (ROOT/'notes/path_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
