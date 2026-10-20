"""Inspect actual Classic slices of the four delivered support pairs.

Checks path metadata, not deposited polymer or strength. Local thresholds allow
0.06 mm path-width/endpoint rounding against the declared CAD feature budget.
"""
import json
import subprocess
import hashlib
from math import cos,sin,pi
import re
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
import support_design as d

ROOT=Path(__file__).resolve().parent
MARGIN=.06


def normal_section(paths, z, tangent, thickness):
    # Left wall: normal X, tangent Y. Shared parser sections run along Y.
    swapped=[(y,x,ny,nx,h,w,r) for x,y,nx,ny,h,w,r in paths]
    return section_coverage(swapped,x_mm=tangent,z_mm=z,span_mm=(-17,-17+thickness))


def local_paths(paths,cx,cy,size):
    return [(x-cx,y-cy,nx-cx,ny-cy,z,w,r) for x,y,nx,ny,z,w,r in paths
            if abs((x+nx)/2-cx)<size/2+.05 and abs((y+ny)/2-cy)<size/2+.05]


def bridge_heights(path):
    role=''; height=None; result=set()
    for line in path.open():
        if line.startswith(';TYPE:'): role=line[6:].strip()
        if line.startswith(';HEIGHT:'): height=float(line[8:])
        e=re.search(r'\bE(-?(?:\d+(?:\.\d*)?|\.\d+))',line)
        if line.startswith('G1 ') and e and float(e[1])>0 and 'bridge' in role.lower():
            assert height is not None, 'Bridge extrusion lacks height metadata'
            result.add(height)
    assert result and max(result)<=.20001, result
    return sorted(result)


def main():
    fig,axes=plt.subplots(4,4,figsize=(15,14))
    probe_fig,probe_axes=plt.subplots(2,4,figsize=(15,7))
    results={}
    before_after,comparison_axes=plt.subplots(2,4,figsize=(15,7))
    controls={}
    for row,name in enumerate(d.NAMES):
        v=d.variant_named(name)
        receipt=json.loads((ROOT/f'notes/support_{name}_final.json').read_text())
        assert receipt['geometry']['valid'] and all(x['ok'] for x in receipt['exports'])
        assert receipt['slice']['ok']
        assert receipt['slice']['input_sha256']==digest(ROOT/f'support_{name}.stl')
        run=Path(receipt['slice']['kept_run_directory'])
        settings=json.loads((run/'effective-settings.json').read_text())
        for key,value in {'wall_generator':'classic','layer_height':'0.2',
                          'initial_layer_print_height':'0.2','enable_support':'0',
                          'thick_bridges':'0','thick_internal_bridges':'0',
                          'seam_gap':'0%','detect_thin_wall':'0'}.items():
            assert settings[key]==value,(name,key,settings[key])
        profile=json.loads((ROOT/'profiles/tpu-support-classic-process.json').read_text())
        for key in ('wall_generator','detect_thin_wall','wall_loops','line_width','outer_wall_line_width','inner_wall_line_width','filter_out_gap_fill',
                    'bridge_angle','internal_bridge_angle'):
            assert settings[key]==profile[key], (name,'stale process',key)
        paths=list(orca_linear_paths(run/'plate_1.gcode'))
        support=[p for p in orca_linear_paths(run/'support_probe/plate_1.gcode')
                 if p[-1].startswith('Support')]
        assert not any(p[-1].startswith('Support') for p in paths)
        heights=bridge_heights(run/'plate_1.gcode')
        # Derive Orca's whole-compound translation from the authored layout.
        minx=20-17; maxx=62+v.pad_size/2
        shift=(135-(minx+maxx)/2,115.)
        cups=local_paths(paths,20+shift[0],135,34)
        pads=local_paths(paths,62+shift[0],135,v.pad_size)
        layers=defaultdict(list)
        for p in cups: layers[round(p[4],3)].append(p)
        # The reported failure was loss of entire walls at ordinary widths.
        # Cover every upright source layer, all four sides and six locations
        # between supports; an empty layer or retained tie alone cannot pass.
        first=round(v.thickness+.2,3)
        last=round(v.wall_height-d.RIM_CAP,3)
        zs=[round(first+.2*i,3) for i in range(round((last-first)/.2)+1)]
        continuity=[]
        for angle in (0,90,180,270):
            c,s=cos(angle*pi/180),sin(angle*pi/180)
            widths=[];gaps=[]
            for z in zs:
                assert z in layers,(name,'missing upright layer',z)
                swapped=[(-s*x+c*y,c*x+s*y,-s*nx+c*ny,c*nx+s*ny,h,w,r)
                         for x,y,nx,ny,h,w,r in layers[z]]
                for tangent in (-11.,-6.6,-2.2,2.2,6.6,11.):
                    sec=section_coverage(swapped,x_mm=tangent,z_mm=z,
                                         span_mm=(-17,-17+v.thickness))
                    assert len(sec['intervals_mm'])==2,(name,z,angle,tangent,'walls missing',sec)
                    sizes=[b-a for a,b in sec['intervals_mm']]
                    assert min(sizes)>=v.wall_skin-MARGIN,(name,z,angle,tangent,'skin too thin',sec)
                    assert sec['internal_gap_mm']>=v.wall_core-MARGIN,(name,z,angle,tangent,'gap lost',sec)
                    widths.extend(sizes);gaps.append(sec['internal_gap_mm'])
            continuity.append({'face_deg':angle,'layers':len(zs),'z_range_mm':[first,last],
                'tangent_samples_per_layer':6,'minimum_skin_path_mm':min(widths),
                'minimum_gap_mm':min(gaps)})
        # The outside skirt also continues below the contact floor and above
        # the inner-wall core into the pad pocket. Check it through full height.
        outer=[]
        for angle in (0,90,180,270):
            c,s=cos(angle*pi/180),sin(angle*pi/180)
            widths=[]
            for index in range(1,round(34/.2)+1):
                z=round(index*.2,3)
                assert z in layers,(name,'outside wall layer missing',z)
                swapped=[(-s*x+c*y,c*x+s*y,-s*nx+c*ny,c*nx+s*ny,h,w,r)
                         for x,y,nx,ny,h,w,r in layers[z]]
                for tangent in (-11.,-6.6,-2.2,2.2,6.6,11.):
                    # The supplied process deliberately insets the first
                    # layer by 0.15 mm; judge the compensated base, not an
                    # unprinted nominal strip outside its intended edge.
                    inset=float(settings['elefant_foot_compensation']) if index==1 else 0.
                    sec=section_coverage(swapped,x_mm=tangent,z_mm=z,
                                         span_mm=(-17+inset,-17+v.wall_skin))
                    # Require an ordinary outer-wall bead, not occupation of
                    # every hundredth of the .5 mm CAD allowance. On solid
                    # floor layers the .42 mm perimeter need not fill that
                    # entire allowance at every infill crossing.
                    required=min(float(settings['outer_wall_line_width'])-.02,
                                 v.wall_skin-inset-.01)
                    assert sec['filled_width_mm']>=required,(name,z,angle,'outside wall interrupted',sec)
                    widths.append(sec['filled_width_mm'])
            outer.append({'face_deg':angle,'layers':170,'tangent_samples_per_layer':6,
                          'minimum_filled_skin_mm':min(widths),'minimum_ordinary_bead_mm':float(settings['outer_wall_line_width'])-.02,'first_layer_inset_mm':float(settings['elefant_foot_compensation'])})
        wall_sections=[]
        for z in (3.2,5.4,10.,18.,29.6):
            for angle in (0,90,180,270):
                # Rotate path into canonical left-wall coordinates.
                c,s=cos(angle*pi/180),sin(angle*pi/180)
                lp=[(c*x+s*y,-s*x+c*y,c*nx+s*ny,-s*nx+c*ny,h,w,r)
                    for x,y,nx,ny,h,w,r in layers[z]]
                sec=normal_section(lp,z,2.2,v.thickness)
                assert len(sec['intervals_mm'])==2,(name,z,angle,sec)
                assert sec['internal_gap_mm'] >= v.wall_core-MARGIN,(name,z,sec)
                assert all(b-a>=v.wall_skin-MARGIN for a,b in sec['intervals_mm'])
                if v.topology=='frame' and z==10.:
                    cross=normal_section(lp,z,(v.frame_opening+d.FRAME_CROSS_WEB)/2,v.thickness)
                    assert cross['uncovered_width_mm']<MARGIN,(name,angle,'cross-web',cross)
                if v.topology=='ties' and z==3.2:
                    tie=normal_section(lp,z,0,v.thickness)
                    assert tie['uncovered_width_mm']<MARGIN,(name,angle,'tie',tie)
                wall_sections.append({'z_mm':z,'face_deg':angle,'section':sec})
        if v.topology=='frame':
            sec=normal_section(layers[10.],10.,0,v.thickness)
            assert len(sec['intervals_mm'])==2,(name,sec)
            assert sec['internal_gap_mm']>=v.frame_opening-MARGIN,(name,sec)
            assert all(b-a>=v.wall_skin+v.tie_size-MARGIN for a,b in sec['intervals_mm']),(name,sec)
            cross=normal_section(layers[10.],10.,(v.frame_opening+d.FRAME_CROSS_WEB)/2,v.thickness)
            assert cross['uncovered_width_mm']<MARGIN,(name,'frame cross-web missing',cross)
            topology={'frame_center':sec,'cross_web':cross}
        else:
            on=normal_section(layers[3.2],3.2,0,v.thickness)
            off=normal_section(layers[5.4],5.4,0,v.thickness)
            assert on['uncovered_width_mm']<MARGIN,(name,on)
            assert len(off['intervals_mm'])==2 and off['internal_gap_mm']>=v.wall_core-MARGIN,(name,off)
            firstz=round(d.tie_heights(v)[0]-v.tie_size/2+.2,3)
            first_tie_section=normal_section(layers[firstz],firstz,0,v.thickness)
            assert first_tie_section['uncovered_width_mm']<MARGIN,(name,'first tie layer',first_tie_section)
            topology={'tie_present':on,'tie_absent_between_rows':off,
                      'first_tie_layer_mm':firstz,'first_tie_section':first_tie_section}
        panels=[]
        for kind,part,base in (('cup',cups,d.FLOOR_SKIN),('pad',pads,d.FLOOR_SKIN+d.PRELOAD)):
            z=round(base+v.core/2,3)
            # Core is void at x=2.2,y=2.2, regardless of architecture.
            sec=section_coverage(part,x_mm=2.2,z_mm=z,span_mm=(2.,2.4))
            assert sec['filled_width_mm']<.01,(name,kind,z,sec)
            if v.topology=='frame':
                opening=section_coverage(part,x_mm=0,z_mm=z,span_mm=(-3,3))
                assert opening['filled_width_mm']<.01,(name,kind,opening)
            else:
                post=section_coverage(part,x_mm=0,z_mm=z,span_mm=(-v.tie_size/2,v.tie_size/2))
                assert post['uncovered_width_mm']<MARGIN,(name,kind,post)
            # First upper skin must cover the full local test field.
            roofz=round(base+v.core+.2,3)
            roof=section_coverage(part,x_mm=2.2,z_mm=roofz,span_mm=(-10,10))
            assert roof['uncovered_width_mm']<MARGIN,(name,kind,roof)
            panels.append({'part':kind,'core_z_mm':z,'air':sec,'roof_z_mm':roofz,'roof':roof})
        # Corner cores stay air. Both orthogonal skins are visible in this band.
        corner=section_coverage(cups,x_mm=-17+v.wall_skin+.2,z_mm=10.,
                                span_mm=(-17+v.wall_skin+.15,-17+v.wall_skin+.25))
        assert corner['filled_width_mm']<.01,(name,corner)
        # Record probe location and review whether proposals are inside trapped
        # cores. Supports stay OFF: these are explicit bridge experiments.
        proposals=[]
        for kind,cx,size in (('cup',20+shift[0],34),('pad',62+shift[0],v.pad_size)):
            sp=local_paths(support,cx,135,size)
            proposals.append({'part':kind,'segments':len(sp),'z_range_mm':
                [min(p[4] for p in sp),max(p[4] for p in sp)] if sp else None})
        for kind,cx,size,ax in (
                ('cup',20+shift[0],34,probe_axes[0,row]),
                ('pad',62+shift[0],v.pad_size,probe_axes[1,row])):
            sp=local_paths(support,cx,135,size)
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in sp],
                linewidths=.25,colors='#d48320',alpha=.4))
            ax.set_xlim(-18,18);ax.set_ylim(-18,18);ax.set_aspect('equal')
            ax.set_title(f'{name} {kind} / probe XY',fontsize=10)
            ax.set_xticks([]);ax.set_yticks([])
        # Four same-scale diagnostic views per candidate.
        views=((cups,.2,'Cup ID: underside'),(pads,.2,'Pad ID: underside'),
               (cups,3.2,'Wall ties / loops at Z 3.2'),(cups,5.4,'Between rows at Z 5.4'))
        for col,(part,z,title) in enumerate(views):
            ax=axes[row,col]
            selected=[p for p in part if abs(p[4]-z)<1e-5]
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in selected],
                linewidths=[p[5]*2.5 for p in selected],colors='#2367b1'))
            ax.set_xlim(18,-18) if col<2 else ax.set_xlim(-18,18)
            ax.set_ylim(-18,18);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
            ax.set_title(f'{name} / {title}',fontsize=10)
        control=json.loads((ROOT/f'notes/rejected_r1/support_{name}_ordinary.json').read_text())
        original=subprocess.check_output(['git','show',f'8f1e611:model/tpu_damping_box/support_{name}.stl'],cwd=ROOT)
        input_sha=hashlib.sha256(original).hexdigest()
        ax=comparison_axes[0,row]
        if control['slice']['ok']:
            assert control['slice']['input_sha256']==input_sha
            old_run=Path(control['slice']['kept_run_directory'])
            # R1 used .3 mm A skins; its pad was 33.0 mm, hence a different
            # whole-compound centering offset than the corrected .5 mm skins.
            old_pad=33.0 if name.startswith('A') else 32.8
            old_cx=20+135-(3+62+old_pad/2)/2
            old=local_paths(orca_linear_paths(old_run/'plate_1.gcode'),old_cx,135,34)
            old=[p for p in old if abs(p[4]-10)<1e-5]
            missing=normal_section(old,10.,2.2,v.thickness)
            assert missing['filled_width_mm']<.01,(name,'negative control unexpectedly retained walls',missing)
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in old],colors='#b54b42',linewidths=.7))
            controls[name]={'input_revision':'8f1e611','input_sha256':input_sha,
                'ordinary_failure':'wall skins absent between frames','section':missing}
        else:
            raw=json.loads((ROOT/f'notes/rejected_r1/support_{name}_orca_result.json').read_text())
            warning=' '.join(p['warning_message'] for p in raw['sliced_plates'])
            assert 'empty layer' in warning.lower(),(name,raw)
            ax.text(0,0,'Orca refused slice:\nempty layers after\nthin walls disappeared',ha='center',va='center',fontsize=10,color='#b54b42')
            controls[name]={'input_revision':'8f1e611','input_sha256':input_sha,
                'ordinary_failure':warning}
        ax.set_title(f'{name} rejected R1 / ordinary Classic',fontsize=10)
        ax=comparison_axes[1,row]
        now=layers[10.]
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in now],colors='#2367b1',linewidths=.7))
        ax.set_title(f'{name} corrected R2 / same Classic process',fontsize=10)
        for a in comparison_axes[:,row]:
            a.set_xlim(-18,18);a.set_ylim(-18,18);a.set_aspect('equal');a.set_xticks([]);a.set_yticks([])
        # The user subsequently identified the repo defaults. Test the exact
        # diagnostic default triplet too, without presenting PETG temperatures
        # or 7% fill as the intended TPU recipe.
        default_receipt=json.loads((ROOT/f'notes/support_{name}_repo_default.json').read_text())
        assert default_receipt['slice']['ok'],(name,'repository default slice failed')
        assert default_receipt['slice']['input_sha256']==digest(ROOT/f'support_{name}.stl')
        default_run=Path(default_receipt['slice']['kept_run_directory'])
        ds=json.loads((default_run/'effective-settings.json').read_text())
        assert ds['wall_generator']=='classic' and ds['detect_thin_wall']=='0'
        dp=local_paths(orca_linear_paths(default_run/'plate_1.gcode'),20+shift[0],135,34)
        dl=defaultdict(list)
        for p in dp:
            if p[-1] in ('Outer wall','Inner wall'):dl[round(p[4],3)].append(p)
        default_faces=[]
        for angle in (0,90,180,270):
            c,s=cos(angle*pi/180),sin(angle*pi/180)
            widths=[]
            for z in zs:
                assert z in dl,(name,'default process lost upright layer',z)
                swapped=[(-s*x+c*y,c*x+s*y,-s*nx+c*ny,c*nx+s*ny,h,w,r)
                         for x,y,nx,ny,h,w,r in dl[z]]
                for tangent in (-11.,-6.6,-2.2,2.2,6.6,11.):
                    sec=section_coverage(swapped,x_mm=tangent,z_mm=z,
                                         span_mm=(-17,-17+v.thickness))
                    assert len(sec['intervals_mm'])==2,(name,'default walls missing',z,angle,sec)
                    sizes=[b-a for a,b in sec['intervals_mm']]
                    assert min(sizes)>=v.wall_skin-MARGIN,(name,'default skin too thin',z,angle,sec)
                    widths.extend(sizes)
            default_faces.append({'face_deg':angle,'layers':len(zs),
                'z_range_mm':[first,last],'minimum_skin_path_mm':min(widths),
                'tangent_samples_per_layer':6})
        default_info={'checks_passed':True,'wall_generator':ds['wall_generator'],
            'detect_thin_wall':ds['detect_thin_wall'],'outer_width_mm':ds['outer_wall_line_width'],
            'inner_width_mm':ds['inner_wall_line_width'],'filament':ds['filament_type'],
            'sparse_infill_density':ds['sparse_infill_density'],'faces':default_faces,
            'gcode_sha256':digest(default_run/'plate_1.gcode'),
            'scope':'Exact repository-default diagnostic path compatibility; not a TPU print recipe.'}
        source_files=('design.py','support_design.py',f'support_{name}.py',
                      'profiles/tpu-support-classic-process.json','profiles/tpu95a.json',
                      'review_support_paths.py','../../physical_analysis/manufacturing.py',
                      '../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.4-nozzle.json')
        source_files += (f'notes/rejected_r1/support_{name}_ordinary.json',
                         f'notes/support_{name}_repo_default.json',
                         '../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/qidi-q2c-0.20-standard-adaptive-cubic-7.json',
                         '../../.codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg/generic-petg-qidi-q2c-0.4.json')
        if not control['slice']['ok']:
            source_files += (f'notes/rejected_r1/support_{name}_orca_result.json',)
        results[name]={'revision':'R2','checks_passed':True,'artifact_identity':receipt['reuse']['artifact_identity'],
            'source_sha256':{n:digest(ROOT/n) for n in source_files},
            'export_sha256':{f'support_{name}.{ext}':digest(ROOT/f'support_{name}.{ext}') for ext in ('step','stl')},
            'gcode_sha256':digest(run/'plate_1.gcode'),'center_translation_mm':shift,
            'repo_default':default_info,'effective_process':{k:settings[k] for k in ('wall_generator','wall_loops',
                'line_width','outer_wall_line_width','inner_wall_line_width','detect_thin_wall','layer_height','enable_support','bridge_angle','internal_bridge_angle',
                'filter_out_gap_fill')},
            'bridge_heights_mm':heights,'wall_sections':wall_sections,'wall_continuity':continuity,'outside_full_height':outer,'topology':topology,
            'panels':panels,'corner_air':corner,'support_proposals':proposals}
    probe_fig.suptitle('Automatic-support proposals only • supports OFF in supplied print process')
    probe_fig.tight_layout();probe_fig.savefig(ROOT/'renders/support_probe_review.png',dpi=150)
    fig.suptitle('Actual Classic toolpaths • blue strokes use recorded widths • IDs read from below')
    fig.tight_layout();fig.savefig(ROOT/'renders/support_path_review.png',dpi=150)
    before_after.suptitle('Ordinary Classic: 0.42/0.45 mm wall widths, thin-wall detection OFF')
    before_after.tight_layout();before_after.savefig(ROOT/'renders/support_classic_before_after.png',dpi=150)
    report={'category':'slicer-path-metadata','limits':'No physical strength, deposited gap or damping claim.',
            'criteria':{'feature_rounding_allowance_mm':MARGIN,'max_bridge_height_mm':.2},'variants':results,'rejected_batch_controls':controls}
    (ROOT/'notes/support_path_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:{'checks_passed':r['checks_passed'],'support_proposals':r['support_proposals']}
                      for n,r in results.items()},indent=2))


if __name__=='__main__':
    main()
