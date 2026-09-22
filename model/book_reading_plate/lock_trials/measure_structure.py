"""Read-only solid-section audit through CadQuery MCP; no production exports."""
from pathlib import Path
import json,hashlib
import cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from lock_trials import parts,params,leaf,box
ROOT=Path(__file__).resolve().parent

def slab_properties(s,dx=.2):
    props=GProp_GProps(); BRepGProp.VolumeProperties_s(s.val().wrapped,props)
    mass=props.Mass(); c=props.CentreOfMass(); matrix=props.MatrixOfInertia()
    bb=s.val().BoundingBox()
    iy=(matrix.Value(2,2)-mass*dx**2/12)/dx
    iz=(matrix.Value(3,3)-mass*dx**2/12)/dx
    return {'area_mm2':mass/dx,'Iy_mm4':iy,'Iz_mm4':iz,
      'Sy_mm3':iy/max(bb.zmax-c.Z(),c.Z()-bb.zmin),
      'Sz_mm3':iz/max(bb.ymax-c.Y(),c.Y()-bb.ymin),
      'centroid_yz_mm':[c.Y(),c.Z()],'bounds_mm':[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]}
report={}; displays=[]
for i,k in enumerate('AB'):
    p=params(k);a,b=parts(k,labels=False)
    # Remove full latch band, including cover skins; the catch cannot carry rail bending.
    structural=a.cut(box(p.leaf_root-1,p.depth+1,p.leaf_y-6,p.leaf_y+6,-1,11))
    roots={}
    for x in [.5,1.5,2.75,p.depth-.5]:
        slab=structural.intersect(box(x-.1,x+.1,0,p.height,-1,11))
        roots[str(x)]=slab_properties(slab)
    clip=leaf(p).intersect(box(p.leaf_root+.9,p.leaf_root+1.1,0,p.height,-1,11))
    # Actual skin area / crop width / crop length, away from the catch and edge fillets.
    crop=box(3,p.depth-.3,10,12,0,3)
    skin=b.intersect(crop).val().Volume()/((p.depth-.3-3)*2)
    report[k]={'source_parameters':p.__dict__,'rail_sections':roots,
        'clip_root_section':slab_properties(clip),'receiver_rear_skin_mm':skin,
        'assembly_volume_mm3':a.val().Volume()+b.val().Volume(),
        'checks':{'valid':a.val().isValid() and b.val().isValid(),'solids':len(a.solids().vals())+len(b.solids().vals()),
                  'assembly_overlap_mm3':a.val().intersect(b.val()).Volume()}}
    # Front skin removed for inspection only, exposing channel and spring route.
    crop=box(-40,20,0,p.height,-1,5)
    displays.extend([a.intersect(crop).translate((0,i*70,0)).val(),b.intersect(crop).translate((12,i*70,0)).val()])
report['hashes']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['lock_trials.py','measure_structure.py']}
(ROOT/'notes/structural_review/cad_sections.json').write_text(json.dumps(report,indent=2)+'\n')
result=cq.Compound.makeCompound(displays)
