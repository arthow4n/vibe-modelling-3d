"""Actual-CAD interior sections: central storage void excludes hidden latch channels.

Volumes are midpoint integration of central cross-section area, not liquid
capacity, simultaneous packing or an ergonomic rating. No unprinted fit inferred.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import cadquery as cq
import m1_design as m1
import m4_design as m4
import m5_design as m5

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m5'
INPUTS=('m1_design.py','m2b_design.py','m3_design.py','m4_design.py','m5_design.py','m5_space_study.py')
THICKNESS=.02


def central_slice(parts,z):
    d=parts['dimensions']
    slab=m1.prism(d.width,d.depth,d.corner,z-THICKNESS/2,THICKNESS)
    void=slab.cut(parts['body']).cut(parts['cap'])
    central=[s for s in void.solids().vals() if s.isInside((0,0,z))]
    if len(central)!=1:raise ValueError('Expected one central storage section at '+str(z))
    return central[0]


def area(parts,z):return central_slice(parts,z).Volume()/THICKNESS


def section_stiffness(parts,z):
    result={}
    d=parts['dimensions']
    slab=m1.box(0,0,z,d.width+4,d.depth+4,THICKNESS)
    for name in ('fixed','cap'):
        cut=parts[name].intersect(slab).val()
        inertia=cq.Shape.matrixOfInertia(cut)
        result[name]=dict(area_mm2=cut.Volume()/THICKNESS,
            Ixx_mm4=inertia[0][0]/THICKNESS,Iyy_mm4=inertia[1][1]/THICKNESS)
    return result


def capacity(parts,step):
    d=parts['dimensions']
    # All candidates have the same floor/roof. Sample inside, not on a boundary.
    n=round((d.length-2*d.floor)/step)
    dz=(d.length-2*d.floor)/n
    return sum(area(parts,d.floor+(i+.5)*dz)*dz for i in range(n))/1000


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    records={}
    for name in ('M4','short_guard','thin_sleeve','flat75','flat77_light_cap','flat77_loose_corners','flat77'):
        parts=m5.build_candidate(name)
        d=parts['dimensions']
        tube=m1.box(0,0,178,55,40,350).val()
        record=dict(dimensions=asdict(d),sections_mm2={str(z):area(parts,z) for z in (100,165,180,200,220,245,258)},
            individual_tube_gap_mm=parts['body'].val().distance(tube),
            individual_tube_overlap_mm3=parts['body'].val().intersect(tube).Volume(),
            guide_cap_bending_sections=section_stiffness(parts,220),
            nominal_local_guide_plate_rigidity_ratio=(d.lap_wall/m4.D.lap_wall)**3)
        if name in ('M4','short_guard','flat77'):
            record['central_volume_ml_4mm']=capacity(parts,4)
        if name in ('M4','flat77'):
            record['central_volume_ml_2mm']=capacity(parts,2)
        records[name]=record
        print(name,json.dumps(record),flush=True)
    output=dict(scope=__doc__,slab_thickness_mm=THICKNESS,
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS},cases=records)
    (OUT/'space_study.json').write_text(json.dumps(output,indent=2)+'\n')


if __name__=='__main__':run()
