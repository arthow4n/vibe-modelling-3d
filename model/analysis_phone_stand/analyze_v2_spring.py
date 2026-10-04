"""Exact production spring, prescribed guided end: cheaper local release screen."""
import argparse
import json
from pathlib import Path
import v2_components as d
from analyze_v2 import material
from physical_analysis import FlexureQuestion,Motion,Support,Region,QuestionStudy,ManufacturingAssumption

def question(mesh=1.2):
    return FlexureQuestion(name='v2_guided_spring',part=d.leaf(1),part_name='spring',
        material=material(),supports=(Support(Region((d.ROOT_X-3,d.ROOT_Y-5,d.LEAF_Z),
            (d.ROOT_X+7,d.ROOT_Y+5,d.LEAF_Z)),name='full_width_mount_pad'),),
        mesh_size_mm=mesh,max_increment=.1,timeout_seconds=180,
        motion=Motion((0,-d.RELEASE_TRAVEL,0),Region.plane('x',8),name='guided_end'),
        acceptance={'peak_motion_force_N.guided_end':4},
        manufacturing=ManufacturingAssumption('Exact production leaf flat on XY, solid PETG; moving pad idealized guided translation. Force is per leaf; two leaves act in parallel.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path)
    a=p.parse_args()
    q=question()
    r=QuestionStudy(q,'Provisional 1.5% spring strain and <8 N total release; 20% numerical sensitivity cannot change acceptance',
        ('max_strain_by_part.spring','peak_motion_force_N.guided_end'),relative_tolerance=.2,mesh_levels=1,motion_levels=1).run(a.directory)
    print(json.dumps({'status':r.status,'errors':r.errors,'question':r.metrics['question']}))
