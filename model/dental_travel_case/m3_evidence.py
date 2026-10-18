"""Associate finished M3 exports and native receipts with the frozen CAD sources.

Run after completed publication/native runs. This does not turn partial evidence
into physical acceptance. Native archives remain the owning detailed records.
"""
from dataclasses import replace
import gzip
import hashlib
import json
from pathlib import Path
import tempfile

import cadquery as cq
import m3_design as design

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m3'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def native_shape(directory):
    with tempfile.NamedTemporaryFile(suffix='.brep') as f:
        f.write(gzip.decompress((directory/'part_0.brep.gz').read_bytes()))
        f.flush()
        return cq.Shape.importBrep(f.name)


def run():
    base=ROOT/'notes/retention'
    coarse=base/'dental_m3_land_12'
    fine=base/'dental_m3_land_12_curved'
    # The preliminary narrow CAD failed the contents margin; its isolated catch
    # is the same final catch translated by -.4mm. Check the actual saved BREP.
    translated=native_shape(coarse).translate((-.4,0,0))
    current=native_shape(fine)
    delta=translated.cut(current).Volume()+current.cut(translated).Volume()
    if delta>1e-6:raise ValueError('Native geometry was not equivalent after translation')
    a=json.loads((coarse/'result.json').read_text())
    b=json.loads((fine/'result.json').read_text())
    press=json.loads((base/'dental_m3_press_7/result.json').read_text())
    for x in (a,b,press):
        if not x['completed']:raise ValueError('Expected completed local native evidence')
    summary=dict(scope='Local fixed-world traction and pressure only; no whole-product contact or strength qualification.',
        preliminary_narrow_width_mm=74.2,final_main_width_mm=75.,
        native_geometry_translation_mm=[-.4,0,0],native_symmetric_difference_mm3=delta,
        coarse_shoulder_mm=a['metrics']['observations']['shoulder']['mean_mm'][0],
        current_curvature_mesh_shoulder_mm=b['metrics']['observations']['shoulder']['mean_mm'][0],
        relative_shoulder_change=abs(b['metrics']['observations']['shoulder']['mean_mm'][0]/a['metrics']['observations']['shoulder']['mean_mm'][0]-1),
        peak_strain_coarse=a['metrics']['max_abs_principal_strain'],peak_strain_curved=b['metrics']['max_abs_principal_strain'],
        native_force_balance_relative=b['metrics']['max_force_balance_relative'],
        press_minimum_tooth_inward_mm=press['metrics']['observations']['tooth']['min_mm'][0],
        press_peak_strain=press['metrics']['max_abs_principal_strain'],
        failed_uniform_refinement='dental_m3_land_12_final: Gmsh high-order ScaledJac optimization failed; no mechanics result. Adapted once to curvature sizing; succeeded.',
        mesh_provenance={name:json.loads((directory/'result.json').read_text())['provenance']['mesh'] for name,directory in (('coarse_narrow',coarse),('current_curved',fine))})
    (OUT/'native_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    inputs=['m1_design.py','m2b_design.py','m3_design.py','m3_case.py']
    outputs=['m3_case.step','m3_case.stl','notes/m3/export_slice.json','notes/m3/toolpaths.json',
             'notes/m3/native_summary.json','notes/retention/dental_m3_press_7/result.json',
             'notes/retention/dental_m3_land_12_curved/result.json']
    record=dict(scope='Post-completion source/artifact association after guarded CAD publication; not a physical validation.',
        inputs={p:sha(ROOT/p) for p in inputs},outputs={p:sha(ROOT/p) for p in outputs})
    (OUT/'evidence_association.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':run()
