"""Close, pinch-release, lift and recover using physical contact drivers.

The release pad is a rigid engineering actuator, not a human finger model.
All progress curves use the shared intent API; no solver keywords live here.
"""
import argparse
import json
from components import *
from physical_analysis import (SnapFitQuestion, Material, Region, Support, Motion,
                               MatingPart, ManufacturingAssumption)

def snap_question(mesh=1.6,penalty=6000.,increment=.01,timeout=3600,discretization='surface_to_surface',contact_scope='whole_cap'):
    mat=Material('uncalibrated solid PETG',1200.,.38,
        'Isotropic elastic short-term assumption; vertical printed tab bonding is uncalibrated',.015)
    # Park clear of the cap, approach after closure, press, lift 2 mm,
    # withdraw through the window, then finish lifting the cap.
    # Its 9 mm width fits the real 11 mm cap window throughout the operation.
    pad=block(-4.5,BUTTON_FRONT+2,HEAD_Z-.2,9,1.2,1.2)
    head=Region(lower=(-CAM_WIDTH/2-.01,ARM_Y-ARM_T/2-.01,HEAD_Z-3.01),
                upper=(CAM_WIDTH/2+.01,BUTTON_FRONT+.01,HEAD_Z+3.01))
    # Diagnostic comparison: exclude outer cap faces beyond the pad's possible
    # outward reach; preserve inner catches and the complete lower lead.
    # This changes the fixture's contact selection, not the printed geometry.
    master=Region() if contact_scope=='whole_cap' else Region(upper=(float('inf'),BUTTON_FRONT+.15,float('inf')))
    # Normal actuation only; the finite pad's other faces are not a model
    # of skin edges, friction or vertical finger restraint.
    return SnapFitQuestion(name='covered_lift_close_release',part=snap_arm(),part_name='arm',material=mat,
        supports=(Support(Region.plane('z',ROOT_Z-2)),),contact_region=head,
        mating_parts=(MatingPart('lid_catch',analysis_cap().translate((0,0,12)),
            Motion((0,0,-12),name='lid',progress=((0,0),(.3,1),(.45,1),(.55,5/6),(.65,5/6),(.9,0),(1,0))),master),
            MatingPart('release_pad',pad,Motion((0,-3.4,0),name='pinch',
                progress=((0,0),(.3,0),(.32,2/3.4),(.45,1),(.55,1),(.65,0),(1,0))),Region.plane('y',BUTTON_FRONT+2))),
        observations={'head':head,'free_tab':Region(lower=(-20,0,ROOT_Z+.7),upper=(20,50,LID_TOP))},
        mesh_size_mm=mesh,penalty_N_mm3=penalty,max_increment=increment,timeout_seconds=timeout,
        discretization=discretization,contact_free_at=(.3,1),return_observation='free_tab',
        displacement_limits_mm={'free_tab':((-.2,.2),(-2.2,.01),(-.3,.9))},
        manufacturing=ManufacturingAssumption('Vertical solid tab under six-wall reviewed paths; layer bonding and printed recovery unknown.'))


def operation(*args, **kwargs):
    """Lower-level escape hatch for the retained isolated-release investigations."""
    return snap_question(*args, **kwargs).build_case()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');p.add_argument('--mesh',type=float,default=1.6)
    p.add_argument('--penalty',type=float,default=6000);p.add_argument('--increment',type=float,default=.01)
    p.add_argument('--timeout',type=float,default=3600)
    p.add_argument('--mesh-from',help='Reuse an existing unchanged-geometry mesh for a controlled parameter study')
    p.add_argument('--contact-scope',choices=('whole_cap','mating_side'),default='whole_cap')
    p.add_argument('--discretization',choices=('surface_to_surface','node_to_surface'),default='surface_to_surface')
    a=p.parse_args();r=snap_question(a.mesh,a.penalty,a.increment,a.timeout,a.discretization,a.contact_scope).run(a.directory,mesh_from=a.mesh_from)
    print(json.dumps(dict(status=r.status,errors=r.errors,metrics=r.metrics),indent=2))
