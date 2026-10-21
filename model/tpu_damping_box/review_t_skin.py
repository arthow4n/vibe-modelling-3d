"""Actual Classic wall and M1 label paths for the delivered T08/T16 full pairs."""
from collections import defaultdict
from math import sin, cos, pi
from pathlib import Path
import gzip
import json
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Patch
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import t_skin_design as d

ROOT=Path(__file__).resolve().parent
NOTES=ROOT/'notes/t_skin'
MARGIN=.06
COLORS={'Outer wall':'#2466b0','Inner wall':'#475569','Gap infill':'#c52d66',
        'Internal solid infill':'#cf711c','Bottom surface':'#cf711c','Top surface':'#cf711c',
        'Bridge':'#943c9d','Internal Bridge':'#943c9d','Overhang wall':'#73823e'}
SOURCES=('t_skin_design.py','design.py','support_design.py')
PROFILES=('profiles/tpu-support-classic-process.json','profiles/tpu95a.json',
          '../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json')


def local(paths,cx,cy,size):
    return [(x-cx,y-cy,nx-cx,ny-cy,z,w,r) for x,y,nx,ny,z,w,r in paths
            if abs((x+nx)/2-cx)<size/2+.05 and abs((y+ny)/2-cy)<size/2+.05]


def section(rows,z,tangent,span,angle):
    c,s=cos(angle*pi/180),sin(angle*pi/180)
    swapped=[(-s*x+c*y,c*x+s*y,-s*nx+c*ny,c*nx+s*ny,h,w,r) for x,y,nx,ny,h,w,r in rows]
    return section_coverage(swapped,x_mm=tangent,z_mm=z,span_mm=span)


def point_section(paths,x,y,z):
    return section_coverage(paths,x_mm=x,z_mm=z,span_mm=(y-.05,y+.05))


def draw(ax,paths,z,xlim,ylim,mirror=False):
    selected=[p for p in paths if abs(p[4]-z)<1e-5]
    for role in dict.fromkeys(p[-1] for p in selected):
        moves=[p for p in selected if p[-1]==role]
        ax.add_collection(LineCollection([[((-p[0] if mirror else p[0]),p[1]),
                                          ((-p[2] if mirror else p[2]),p[3])] for p in moves],
                                          colors=COLORS[role],linewidths=1.1))
    ax.set(xlim=xlim,ylim=ylim,aspect='equal',xlabel='mm',ylabel='mm')
    ax.grid(alpha=.15)


def save(fig,name):
    out=ROOT/'renders/print'/f'{name}.svg'
    fig.savefig(out)
    out.write_text('\n'.join(s.rstrip() for s in out.read_text().splitlines())+'\n')
    fig.savefig(out.with_suffix('.png'),dpi=150);plt.close(fig)


def main():
    plt.rcParams['svg.fonttype']='none'
    support_fig,saxes=plt.subplots(1,2,figsize=(12,6))
    results={};labels,laxes=plt.subplots(2,4,figsize=(16,7))
    walls,waxes=plt.subplots(2,2,figsize=(12,7))
    for row,name in enumerate(d.NAMES):
        v=d.variant_named(name)
        native=json.loads((NOTES/f'{name}_final.json').read_text())
        assert native['geometry']['valid'] and all(e['ok'] for e in native['exports'])
        smoke=native['slice'];assert smoke['ok']
        assert smoke['input_sha256']==digest(ROOT/f't_skin_{name}_m1.stl')
        run=Path(smoke['kept_run_directory'])
        settings=json.loads((run/'effective-settings.json').read_text())
        expected={'wall_generator':'classic','detect_thin_wall':'0','wall_loops':'2',
                  'outer_wall_line_width':'0.42','inner_wall_line_width':'0.45',
                  'initial_layer_print_height':'0.2','layer_height':'0.2',
                  'thick_bridges':'0','thick_internal_bridges':'0','enable_support':'0',
                  'elefant_foot_compensation':'0.15','elefant_foot_compensation_layers':'1'}
        assert all(settings[k]==val for k,val in expected.items())
        assert digest(run/'process.json')==digest(ROOT/'profiles/tpu-support-classic-process.json')
        raw=run/'plate_1.gcode';paths=list(orca_linear_paths(raw))
        assert not (set(p[-1] for p in paths)-COLORS.keys())
        cups=local(paths,60,60,34);pads=local(paths,102,60,v.pad_size)
        layers=defaultdict(list)
        for p in cups:layers[round(p[4],3)].append(p)
        zs=[round(1.8+i*.2,3) for i in range(152)]
        continuity=[]
        for angle in (0,90,180,270):
            widths=[];gaps=[]
            for z in zs:
                assert layers[z],(name,z,'missing upright layer')
                for t in (-11.,-6.6,-2.2,2.2,6.6,11.):
                    sec=section(layers[z],z,t,(-17,-17+v.wall),angle)
                    assert len(sec['intervals_mm'])==2,(name,z,angle,t,sec)
                    assert min(b-a for a,b in sec['intervals_mm'])>=v.skin-MARGIN,(name,z,sec)
                    assert sec['internal_gap_mm']>=.6-MARGIN,(name,z,sec)
                    widths.extend(b-a for a,b in sec['intervals_mm']);gaps.append(sec['internal_gap_mm'])
            for index in range(1,171):
                z=round(index*.2,3)
                # Profile deliberately shrinks only the first-layer outer boundary.
                inset=float(settings['elefant_foot_compensation']) if index==1 else 0.
                # Outside the upright air-core region, require the visible boundary
                # contour, not a fully filled calibrated polymer section.
                outer=section(layers[z],z,2.2,(-17+inset,-17+inset+.42),angle)
                assert outer['uncovered_width_mm']<MARGIN,(name,'outer skirt',angle,z,outer)
            for t in (-14.,14.):
                sec=section(layers[10.],10.,t,(-17,-17+v.wall),angle)
                assert sec['uncovered_width_mm']<MARGIN,(name,'corner land',sec)
            on=section(layers[3.],3.,0,(-17+v.skin,-17+v.skin+.6),angle)
            whole=section(layers[3.],3.,0,(-17,-17+v.wall),angle)
            off=section(layers[4.4],4.4,0,(-17,-17+v.wall),angle)
            assert on['uncovered_width_mm']<MARGIN,(name,'tie missing',on)
            assert len(off['intervals_mm'])==2 and off['internal_gap_mm']>=.6-MARGIN
            continuity.append({'face_deg':angle,'upright_layers':len(zs),'outside_contour_layers':170,'outside_contour_band_mm':.42,'tangent_samples':6,
                               'minimum_skin_mm':min(widths),'minimum_gap_mm':min(gaps),
                               'tie_core_layer':on,'tie_whole_wall_section':whole,'between_rows':off})
        panel_results=[];label_results=[]
        for col,(kind,part,size,base) in enumerate((('cup',cups,34,.4),('pad',pads,v.pad_size,.6))):
            air=point_section(part,2.2,2.2,base+.4)
            post=point_section(part,0,0,base+.4)
            roof=section_coverage(part,x_mm=2.2,z_mm=round(base+1.,3),span_mm=(-10,10))
            assert air['filled_width_mm']<.01 and post['uncovered_width_mm']<MARGIN
            assert roof['uncovered_width_mm']<MARGIN,(name,kind,'roof',roof)
            panel_results.append({'part':kind,'core_z':base+.4,'air':air,'post':post,'roof':roof})
            # Negative letter strokes remain void; character counters retain material.
            half=size/2
            cut=point_section(part,half-2.5,-half+3.75,.2)
            counter=point_section(part,half-(5.5 if name=='T08' else 8.5),
                                  -half+(3.75 if name=='T08' else 2.95),.2)
            between=point_section(part,half-4.,-half+5.35,.2)
            backed=point_section(part,half-2.5,-half+3.75,.4)
            assert cut['filled_width_mm']<.01,(name,kind,'label cut lost',cut)
            assert min(counter['filled_width_mm'],between['filled_width_mm'],backed['filled_width_mm'])>.06,(name,kind,'label counter/spacing/backing',counter,between,backed)
            label_results.append({'part':kind,'cut':cut,'counter':counter,'inter_glyph_material':between,'backing':backed})
            for step,z in enumerate((.2,.4)):
                ax=laxes[row,col*2+step]
                draw(ax,part,z,(-half+.8,-half+10.4),(-half+.5,-half+6.7),mirror=True)
                ax.set_title(f'{name} {kind} / Z {z:.1f} mm\n'+('Recesses: blank shapes; counters retained' if step==0 else 'Continuous solid backing over label'),fontsize=10)
        for col,z in enumerate((3.,4.4)):
            # Canonical left-wall section displayed as along-wall X / through-wall Y.
            display=[(y,x+17,ny,nx+17,h,w,r) for x,y,nx,ny,h,w,r in cups]
            draw(waxes[row,col],display,z,(-6,6),(-.15,v.wall+.15))
            waxes[row,col].set_title(f'{name}: {v.skin} mm per skin / {v.wall:.1f} mm total / Z {z}')
        bridge_heights=set();height=None;role=''
        for line in raw.read_text().splitlines():
            if line.startswith(';TYPE:'):role=line[6:].strip()
            if line.startswith(';HEIGHT:'):height=float(line[8:])
            e=re.search(r'\bE(-?(?:\d+(?:\.\d*)?|\.\d+))',line)
            if line.startswith('G1 ') and e and float(e[1])>0 and 'bridge' in role.lower():
                assert height is not None;bridge_heights.add(height)
        assert bridge_heights and max(bridge_heights)<=.20001,bridge_heights
        probe=list(orca_linear_paths(run/'support_probe/plate_1.gcode'))
        support=[p for p in probe if p[-1].startswith('Support')]
        support_z=sorted(set(p[4] for p in support))
        assert support and all(.99<=z<=1.21 for z in support_z),(name,'support beyond horizontal roof',support_z)
        ax=saxes[row]
        for cx,size in ((60,34),(102,v.pad_size)):
            ax.add_patch(plt.Rectangle((cx-size/2,60-size/2),size,size,fill=False,color='#475569'))
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in paths if abs(p[4]-1.)<1e-5],colors='#475569',linewidths=.7))
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in support],colors='#21a179',linewidths=.4))
        ax.set(xlim=(40,120),ylim=(40,80),aspect='equal',title=f'{name}: probe interfaces at Z {support_z}',xlabel='bed X / mm',ylabel='bed Y / mm')
        archive=NOTES/f'{name}_paths.gcode.gz';archive.write_bytes(gzip.compress(raw.read_bytes(),mtime=0))
        results[name]={'checks_passed':True,'artifact_identity':native['reuse']['artifact_identity'],
            'input_sha256':smoke['input_sha256'],'gcode_sha256':digest(raw),
            'source_sha256':{f:digest(ROOT/f) for f in (*SOURCES,f't_skin_{name}_m1.py')},
            'export_sha256':{f't_skin_{name}_m1.{ext}':digest(ROOT/f't_skin_{name}_m1.{ext}') for ext in ('step','stl')},
            'effective_settings':{k:settings[k] for k in expected},'profile_sha256':{p:digest(ROOT/p) for p in PROFILES},
            'wall_continuity':continuity,'horizontal_panels':panel_results,'labels':label_results,
            'bridge_extrusion_heights_mm':sorted(bridge_heights),'slicer_version':smoke['slicer_version'],
            'support_probe':smoke['support_probe'],'support_review':{'interface_z_mm':support_z,
                'decision':'Retain supports-off B horizontal post/roof strategy; auto probe adds inaccessible interface only inside floor/pad core. Actual roof coverage and thin bridge metadata checked; printed sag remains unqualified.'},'notices':smoke['log_notices']}
    support_fig.suptitle('Automatic-support probe: green interfaces are inside horizontal air cores\nGrey: actual supports-off Z 1.0 paths and panel outlines. No probe interfaces on upright ties or labels.',fontsize=12)
    support_fig.subplots_adjust(left=.06,right=.99,bottom=.12,top=.78,wspace=.2);save(support_fig,'t_skin_support_review')
    legend=[Patch(color=c,label=r) for r,c in COLORS.items()]
    labels.suptitle('Actual full-pair Classic M1 paths, viewed from underneath\nBlank glyphs = recessed letters, not colored TPU. Left: cup; right: lid pad. Z 0.4 shows solid backing.',fontsize=13)
    labels.legend(handles=legend,loc='lower center',ncol=5,fontsize=8)
    labels.subplots_adjust(left=.05,right=.99,bottom=.14,top=.78,hspace=.8,wspace=.3);save(labels,'t_skin_m1_label_paths')
    walls.suptitle('Delivered T08 / T16 actual Classic paths\nLeft: ties active. Right: between rows. Contents face is at the top; all TPU black.',fontsize=13)
    walls.legend(handles=legend,loc='lower center',ncol=5,fontsize=8)
    walls.subplots_adjust(left=.06,right=.99,bottom=.16,top=.80,hspace=.8,wspace=.2);save(walls,'t_skin_wall_paths')
    (NOTES/'paths.json').write_text(json.dumps({'category':'full-T-skin-M1-path-review','section_margin_mm':MARGIN,
        'variants':results,'reviewer_sha256':digest(Path(__file__))},indent=2)+'\n')
    print(json.dumps({n:{'checks_passed':r['checks_passed'],'wall_faces':len(r['wall_continuity']),
                         'bridge_heights':r['bridge_extrusion_heights_mm']} for n,r in results.items()}))

if __name__=='__main__':main()
