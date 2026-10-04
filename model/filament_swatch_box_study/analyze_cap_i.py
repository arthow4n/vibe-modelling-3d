"""Local actual-key arm flexure screen; not complete frictional key insertion.

The full-key contact geometry is checked separately. Here a crop preserves one
real slot, root, arm and pad; a clamped core and flat mating flank compress and
unload it through contact. Effective solid material is an explicit assumption.
"""
import json
import math
import argparse
import sys
from pathlib import Path
import cap_i_grip_keys as i
from physical_analysis import SnapFitQuestion, MatingPart, Support, Motion, Region, PETG_SCREEN, ManufacturingAssumption


def arm_fixture(number=2):
    key=i.grip_key(number,label=False)
    local=(key.translate((-i.h.KEY_WAIST_HALF_X,-i.KEY_SEAM_GAP/2,0))
           .rotate((0,0,0),(0,0,1),-math.degrees(math.atan2(i.TANGENT[1],i.TANGENT[0]))))
    # Start at -1.2 to omit a disconnected sliver from the opposite arm.
    fixture=local.intersect(i.block(-1.2,i.LENGTH+.5,-.6,2.1,0,i.KEY_HEIGHT))
    if len(fixture.val().Solids())!=1:
        raise ValueError('Actual-arm crop must contain one attached arm and its core support')
    return fixture


def question(number=2,mesh=.3,penalty=5000,timeout=None):
    travel=i.PROJECTIONS[number-1]-i.h.KEY_FIT_GAP
    # y=-n in the local fixture. Pressing the outward pad inwards is positive y.
    root=Region((-1.2,-.6,-.01),(-.55,2.1,i.KEY_HEIGHT+.01))
    crest=Region((i.PAD_STATION-.12,-i.PROJECTIONS[number-1]-.01,i.ENTRY_HEIGHT+.2),
                 (i.PAD_STATION+.12,-i.PROJECTIONS[number-1]+.06,i.KEY_HEIGHT+.01))
    projection=i.PROJECTIONS[number-1]
    wall=i.block(3.1,5.35,-projection-.65,-projection-.05,-.1,i.KEY_HEIGHT+.1)
    return SnapFitQuestion(name=f'I_arm_{number}',part=arm_fixture(number),material=PETG_SCREEN,
        supports=(Support(root),),
        contact_region=Region((3.1,-.6,-.01),(5.35,.16,i.KEY_HEIGHT+.01)),
        mating_parts=(MatingPart('pocket_wall',wall,Motion.round_trip((0,travel+.05,0))),),
        penalty_N_mm3=penalty,penetration_limit_mm=.02,
        contact_free_at=(1,),return_observation='pad',return_tolerance_mm=1e-4,
        displacement_limits_mm={'pad':((-.2,.2),(-.02,travel+.04),(-.08,.08))},
        observations={'pad':crest},mesh_size_mm=mesh,nonlinear=True,max_increment=.1,
        timeout_seconds=timeout,
        manufacturing=ManufacturingAssumption(
            'Effective homogeneous solid PETG screening assumption: E=1200 MPa, nu=.38, '
            'provisional strain screen 1.5%; no printed calibration. Key flat, .4 mm nozzle, '
            '.2 mm layers. Local sliced fill must be reviewed before print recommendation. '
            'Clamped cropped core; one rounded pad contacted by a rigid flat pocket flank. '
            'Normal compression only; complete key insertion, friction and other arms omitted.'))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,required=True,help='Fresh run directory, relative to cwd')
    parser.add_argument('--numbers',type=int,nargs='+',choices=(1,2,3),default=(1,2,3))
    parser.add_argument('--mesh',type=float,default=.3)
    parser.add_argument('--penalty',type=float,default=5000)
    parser.add_argument('--timeout',type=float,help='Explicit per-solve deadline; none by default')
    parser.add_argument('--serial',action='store_true',help='Run variants sequentially for comparison or limited capacity')
    args=parser.parse_args(argv)
    if len(set(args.numbers))!=len(args.numbers):
        parser.error('Each key number must be unique; variants own separate output directories')
    if len(args.numbers)>1 and not args.serial:
        from execution.batch import ScriptTask, run
        directory=args.directory.resolve()
        common=('--directory',str(directory),'--mesh',str(args.mesh),'--penalty',str(args.penalty),'--serial')
        if args.timeout is not None:
            common+=('--timeout',str(args.timeout))
        answers=run([
            ScriptTask(f'key_{number}',Path(__file__),common+('--numbers',str(number)),
                       outputs=(directory/f'key_{number}',),threads=1)
            for number in args.numbers
        ])
        for name,answer in answers.items():
            if answer.get('error'):
                print(f'{name}: {answer["error"]}',file=sys.stderr)
        return int(any(answer['exit_code']!=0 for answer in answers.values()))
    failed=False
    for number in args.numbers:
        answer=question(number,args.mesh,args.penalty,args.timeout).run(args.directory/f'key_{number}')
        q=answer.metrics.get('question',{})
        failed=failed or not q.get('numerical_evidence_adequate') or q.get('design_screen_passes') is False
        print(json.dumps(dict(number=number,status=answer.status,completed=answer.completed,
            force_N=answer.metrics.get('peak_motion_force_N',{}).get('drive'),strain=q.get('peak_strain'),
            adequate=q.get('numerical_evidence_adequate'),screen=q.get('design_screen_passes'))),flush=True)
    return int(failed)


if __name__=='__main__':
    raise SystemExit(main())
