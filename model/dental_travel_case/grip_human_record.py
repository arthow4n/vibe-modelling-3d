"""Independent replay of completed discovery and three placement translations.

Translation preserves the native finger posture, rather than claiming a fresh
optimization at every placement. Failed searches remain inconclusive.
"""
from dataclasses import asdict
import json
import numpy as np
from scipy.spatial.transform import Rotation
import mujoco
import scipy
from execution.identity import digest
from grip_human_study import (OUT, ROOT, GripScene, Setup, CANDIDATES, STARTS,
    SEED, MAX_NFEV, CONTACT_MM, NORMAL_DEG, CLEARANCE_MM, PENETRATION_MM,
    TRAVEL_STEP_MM, sources, anatomy_identity, build_three_line)
from grip_human_views import draw_pose


class ReceiptError(ValueError):
    """A retained attempted search is incomplete or malformed."""


def tools():
    return dict(mujoco=mujoco.__version__,numpy=np.__version__,scipy=scipy.__version__)


def screens():
    return dict(contact_mm=CONTACT_MM,normal_deg=NORMAL_DEG,
        forbidden_clearance_mm=CLEARANCE_MM,own_half_penetration_mm=PENETRATION_MM,
        opposition_angle_deg=60.,contact_separation_mm=20.,travel_step_mm=TRAVEL_STEP_MM)


def record_sources():
    return {**sources(),**{p:digest(ROOT/p) for p in ('grip_human_record.py','grip_human_views.py')}}


def translated(q,base,scene,*,lift_mm=0.):
    q=np.asarray(q,dtype=float).copy()
    for i in range(2):
        offset=len(base.free)+i*6
        q[offset+2]+=scene.centers[i]-base.centers[i]+(lift_mm if i==0 else 0.)
        R=Rotation.from_rotvec(q[offset+3:offset+6]).as_matrix()
        q[offset+3:offset+6]=Rotation.from_matrix(scene.rotation@base.rotation.T@R).as_rotvec()
    return q


def replay_candidates(record):
    """Recompute acceptance; stored status and diagnostics never supply a pass."""
    dimensions=build_three_line()['dimensions']
    base=GripScene(Setup(**record['setup']),dimensions,local_hands=True)
    attempts=record['attempts']
    if not attempts or [a['start'] for a in attempts]!=list(range(len(attempts))):
        raise ReceiptError('Incomplete discovery start ordering')
    if len(attempts)>STARTS:raise ReceiptError('Unexpected extra starts')
    replayed=[base.diagnostics(a['result']['diagnostics']['q_rad'],lift_mm=0.) for a in attempts]
    # A failed pose is selected only to expose the failure, never for promotion.
    best=min(range(len(attempts)),key=lambda i:(not replayed[i]['accepted'],attempts[i]['result']['cost']))
    q=np.array(replayed[best]['q_rad']);runs=[]
    for candidate in CANDIDATES:
        for tilt in (0.,-25.):
            scene=GripScene(Setup(candidate,tilt,350.,1150.),dimensions,local_hands=True)
            pose=translated(q,base,scene)
            endpoint=scene.diagnostics(pose,lift_mm=0.)
            path=[]
            if endpoint['accepted']:
                for lift in np.arange(0.,6.+TRAVEL_STEP_MM/2,TRAVEL_STEP_MM):
                    held=translated(q,base,scene,lift_mm=float(lift))
                    path.append(dict(lift_mm=float(lift),diagnostics=scene.diagnostics(held,lift_mm=float(lift))))
            runs.append(dict(setup=asdict(scene.setup),diagnostics=endpoint,path=path,
                status='PASS' if endpoint['accepted'] else 'INCONCLUSIVE'))
    return base,best,replayed,runs


def main():
    raw=json.loads((OUT/'discovery.json').read_text())
    if raw['sources']!=sources() or raw['anatomy']!=anatomy_identity():
        raise ValueError('Discovery identity changed; do not relabel stale states')
    identity=record_sources()
    base,best,replayed,runs=replay_candidates(raw)
    count=len(raw['attempts'])
    report=dict(schema_version=1,sources=identity,anatomy=raw['anatomy'],tools=tools(),
        screens=screens(),search=dict(starts=STARTS,seed=SEED,max_nfev=MAX_NFEV),
        completion=dict(completed_starts=count,planned_starts=STARTS,
            stop_reason='Finite search completed or an endpoint accepted' if count==STARTS or any(d['accepted'] for d in replayed) else 'Incomplete search: further IK tuning stopped by agent; interrupted states supply no evidence'),
        parameters=dict(saved_key='q_rad',finger_coordinates='first 40: native joint radians in audit/free-joint order',
            placements='then right and left: object-local wrist XYZ millimetres, world rotation-vector XYZ radians'),
        setup=raw['setup'],audit=raw['audit'],attempts=raw['attempts'],selected_start=best,
        replayed_discovery=replayed,runs=runs,
        method=f'{count} completed starts of planned {STARTS}-start balanced diagonal search; same native posture rigidly translated to other bands and rotated upright. No arm-reach, dynamics, force or comfort qualification.')
    for run in runs:
        if run['setup']['tilt_deg']!=-25.:continue
        scene=GripScene(Setup(**run['setup']),build_three_line()['dimensions'],local_hands=True)
        d=run['diagnostics'];name=run['setup']['candidate']
        label='Accepted finite endpoint only' if d['accepted'] else 'UNSUCCESSFUL SEARCH: contact/collision screens not satisfied. No usable grasp established.'
        draw_pose(scene,d['q_rad'],OUT/('pose_'+name),title=name.capitalize()+' band placement — native MyoSim hand skins',status=label)
    if identity!=record_sources():raise RuntimeError('Replay inputs changed during recording')
    (OUT/'study.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(accepted_discovery=sum(d['accepted'] for d in replayed),runs=[dict(setup=r['setup'],status=r['status']) for r in runs])))


if __name__=='__main__':main()
