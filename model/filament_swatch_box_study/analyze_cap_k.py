"""Actual off-center K panel normal passage/unloading screen, not a creep solve.

A rigid flat face compresses the rounded crown through the thick-card passage
travel, then withdraws. This tests actual plate/root torsion rather than treating
the complete width as a uniformly loaded beam. Complete card lowering, dome
entry/exit friction and the card's strength are outside this local fixture.
"""
import argparse
from pathlib import Path
import json
import dome_latch_study as k
from physical_analysis import SnapFitQuestion,MatingPart,Motion,Support,Region,PETG_SCREEN,ManufacturingAssumption


def question(mesh=.65,timeout=600):
    target=k.travel_screen(2.2)['pass_flat_face_travel_y_mm']
    deepest=k.free_nose_y()
    low=k.DOME_Z-k.NOSE_RADIUS
    high=k.DOME_Z+k.SHOULDER_OUTER_RADIUS+.1
    root=Region((-k.PANEL_WIDTH/2-.01,k.j.ROOT_Y-.01,k.j.slots.FLOOR-.11),
                (k.PANEL_WIDTH/2+.01,k.j.ROOT_Y+k.PANEL_THICKNESS+.01,k.j.slots.FLOOR+k.j.ROOT_BLEND))
    crest=Region((k.DOME_X-k.SHOULDER_OUTER_RADIUS-.1,deepest-.01,low-.1),
                 (k.DOME_X+k.SHOULDER_OUTER_RADIUS+.1,k.j.ROOT_Y+.1,high))
    wall=k.j.g.block(k.DOME_X-k.SHOULDER_OUTER_RADIUS-.1,k.DOME_X+k.SHOULDER_OUTER_RADIUS+.1,
        deepest-.65,deepest-.05,low-.1,high)
    return SnapFitQuestion(name='K_actual_plate_passage',part=k.card_panel(),material=PETG_SCREEN,
        supports=(Support(root),),contact_region=crest,observations={'crown':crest},
        mating_parts=(MatingPart('flat_card_face',wall,Motion.round_trip((0,target+.05,0))),),
        penalty_N_mm3=10000,penetration_limit_mm=.02,
        contact_free_at=(1,),return_observation='crown',return_tolerance_mm=1e-4,
        displacement_limits_mm={'crown':((-.3,.3),(-.04,k.RELIEF_BACK_Y-k.j.ROOT_Y-k.PANEL_THICKNESS-.05),(-.7,.3))},
        mesh_size_mm=mesh,nonlinear=True,max_increment=.1,timeout_seconds=timeout,
        manufacturing=ManufacturingAssumption('Effective homogeneous isotropic solid PETG assumption: '
            'E=1200 MPa, nu=.38, provisional short-term strain screen 1.5%; not calibrated. '
            'Floor-down .4 mm nozzle/.2 mm layers, 0.8 mm panel. Actual off-centre crown/plate; '
            'clamped floor/root region and rigid normal flat-face passage/return. '
            'No complete card lowering, friction, dome resting contact, card damage or creep prediction.'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--mesh',type=float,default=.65)
    args=p.parse_args()
    answer=question(args.mesh).run(args.directory)
    q=answer.metrics.get('question',{})
    print(json.dumps(dict(status=answer.status,completed=answer.completed,
        adequate=q.get('numerical_evidence_adequate'),screen=q.get('design_screen_passes'),
        strain=q.get('peak_strain'),force_N=answer.metrics.get('peak_motion_force_N',{}).get('drive'))))
    raise SystemExit(0 if q.get('numerical_evidence_adequate') and q.get('design_screen_passes') else 1)
