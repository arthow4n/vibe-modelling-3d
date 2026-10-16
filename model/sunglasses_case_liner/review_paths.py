"""Review only changed S16 manufacturing features in the final native slice."""
from collections import defaultdict, Counter
from pathlib import Path
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import design as d

ROOT = Path(__file__).resolve().parent


def multiple_tracks(paths, x, y, z, axis):
    # Axis-aligned section normal to the rib's deposited tracks.
    hits = []
    for ax,ay,bx,by,pz,width,role in paths:
        if abs(pz-z) > 1e-5:
            continue
        if axis == 'x':
            ax,ay,bx,by = ay,ax,by,bx
            fixed,centre = y,x
        else:
            fixed,centre = x,y
        if abs(bx-ax)<1e-9:
            continue
        t = (fixed-ax)/(bx-ax)
        cross = ay+t*(by-ay)
        if 0<=t<=1 and abs(cross-centre)<.7 and .38<=width<=.65:
            if not any(abs(cross-c)<.02 for c in hits):
                hits.append(cross)
    assert len(hits)>=2, f'Rib at {x,y,z}: fewer than two substantial tracks: {hits}'
    return len(hits)


def main():
    receipt = json.loads((ROOT/'notes/final_review.json').read_text())
    run = Path(receipt['slice']['kept_run_directory'])
    settings = json.loads((run/'effective-settings.json').read_text())
    assert all(settings[k]=='0' for k in ('enable_support','thick_bridges','thick_internal_bridges'))
    assert all(settings[k]=='0.1' for k in ('layer_height','initial_layer_print_height'))
    assert settings['wall_generator']=='arachne'
    assert all(settings[k]=='180' for k in ('bridge_angle','internal_bridge_angle'))
    paths = list(orca_linear_paths(run/'plate_1.gcode'))
    layers = defaultdict(list)
    for p in paths:
        layers[round(p[4],3)].append(p)
    assert not any(p[-1].startswith('Support') for p in paths)
    support = [p for p in orca_linear_paths(run/'support_probe/plate_1.gcode') if p[-1].startswith('Support')]
    # Source compound centred without rotation on the documented 270 mm bed.
    length,width,height,_ = d.dimensions()
    x = 135.
    ys = (135-(width+d.LAYOUT_GAP)/2,135+(width+d.LAYOUT_GAP)/2)
    gaps=[];tracks=[];roofs=[];channels=[]
    for cy in ys:
        for z in (.5,.8,1.2):
            lp = layers[z]
            for offset in (-6.6,2.2,6.6):
                air = section_coverage(lp,x_mm=x+offset,z_mm=z,span_mm=(cy-10,cy+10))
                assert air['filled_width_mm']<.01, 'Floor channel filled'
                channels.append(air)
            tracks.append(multiple_tracks(lp,x,cy+5.3,z,'x'))
        first = [p for p in layers[1.3] if abs((p[0]+p[2])/2-x)<12 and abs((p[1]+p[3])/2-cy)<12]
        assert first and all(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in first), 'Floor bridge does not cross ribs'
        roofs.append(dict(z_mm=1.3,roles=dict(Counter(p[-1] for p in first))))
        for z in (5.,15.,29.):
            for side in (-1,1):
                swapped = [(p[1],p[0],p[3],p[2],p[4],p[5],p[6]) for p in layers[z]]
                for offset in (2.2,6.6):
                    # Tangent X / normal Y for long walls; converse for ends.
                    for lp,tangent,span in (
                        (layers[z],x+offset,tuple(sorted((cy+side*width/2,cy+side*(width/2-d.THICKNESS))))),
                        (swapped,cy+offset,tuple(sorted((x+side*length/2,x+side*(length/2-d.THICKNESS)))))):
                        coverage=section_coverage(lp,x_mm=tangent,z_mm=z,span_mm=span)
                        assert len(coverage['intervals_mm'])==2, 'Missing or fused wall skins'
                        assert coverage['internal_gap_mm']>=.7, 'Wall core gap lost'
                        assert all(b-a>=.36 for a,b in coverage['intervals_mm']), 'Thin skin path'
                        gaps.append(coverage['internal_gap_mm'])
                tracks.append(multiple_tracks(layers[z],x,cy+side*(width/2-.8),z,'x'))
                tracks.append(multiple_tracks(layers[z],x+side*(length/2-.8),cy,z,'y'))
    bridge_heights=set();role='';extrusion_height=None
    for line in (run/'plate_1.gcode').open():
        if line.startswith(';TYPE:'):role=line[6:].strip()
        if line.startswith(';HEIGHT:'):extrusion_height=float(line[8:])
        if line.startswith('G1 ') and 'bridge' in role.lower() and re.search(r' E[0-9]',line):
            assert extrusion_height is not None
            bridge_heights.add(extrusion_height)
    assert bridge_heights and max(bridge_heights)<=.10001, 'Thick bridges intrude into core'
    fig,ax=plt.subplots(figsize=(9,8))
    for segments,color in ((support,'#168b88'),(layers[1.3],'#a75a9b')):
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in segments],colors=color,linewidths=.4))
    ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)')
    ax.set_title('S16 liner: first contact-skin layer purple; probe support teal')
    fig.tight_layout();(ROOT/'renders').mkdir(exist_ok=True)
    fig.savefig(ROOT/'renders/path_review.png',dpi=140)
    report=dict(scope='Slicer metadata only, not deposited-polymer measurements or physical approval',
        criteria=dict(core_gap_min_mm=.7,skin_width_min_mm=.36,rib_tracks_min=2,
                      track_width_range_mm=[.38,.65],bridge_height_max_mm=.1),
        floor_channel_samples=len(channels),wall_gap_samples=len(gaps),
        minimum_wall_gap_mm=min(gaps),rib_sections=len(tracks),minimum_rib_tracks=min(tracks),
        first_skin_layers=roofs,bridge_heights_mm=sorted(bridge_heights),
        support_probe=dict(segments=len(support),z_range_mm=[min(p[4] for p in support),max(p[4] for p in support)] if support else None))
    (ROOT/'notes/path_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
