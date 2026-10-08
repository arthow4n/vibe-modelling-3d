"""Finite audit of MyoArm's proximal middle/ring skin proxy overlap.

Not an anatomical impossibility proof. Isolated from product search; no geometry
is resized, and MuJoCo's imported masks/pairs remain visible in the report.
"""
import itertools
import json
from pathlib import Path
from execution.identity import digest
import numpy as np
import human_interaction as h


def audit():
    anatomy=h.anatomy_identity()
    model=h.Interaction(h.Setup(60.))
    names=('mcp3_flexion_r','mcp3_abduction_r','mcp4_flexion_r','mcp4_abduction_r')
    indices=[model.free.index(model.names.index(n)) for n in names]
    a,b=[model.model.geom(n).id for n in ('proxph3_coll_r','proxph4_coll_r')]
    q=model.model.qpos0[model.free].copy()
    best=-np.inf
    best_q=None
    distances=[]
    for values in itertools.product(*(np.linspace(model.bounds[0,i],model.bounds[1,i],7) for i in indices)):
        q[indices]=values;model.state(q,0.)
        distance=h.mujoco.mj_geomDistance(model.model,model.data,a,b,1.,None)*1000
        distances.append(distance)
        if distance>best:best=distance;best_q=list(values)
    old=h.Interaction(h.Setup(60.,(80.,500.,330.)))
    old.state(old.model.qpos0[old.free],0.)
    fixed=[g for g in old.human if old.model.body_weldid[old.model.geom_bodyid[g]]==0]
    old_setup=dict(shoulder_mm=[80.,500.,330.],
        fixed_proxy_desk_distances_mm={old.model.geom(g).name or f'geom#{g}':
            float(h.mujoco.mj_geomDistance(old.model,old.data,g,old.model.geom('desk').id,1.,None)*1000) for g in fixed},
        meaning='Historical shoulder height causes fixed imported torso/desk-plane overlap; not a physical seated-user conclusion')
    if h.anatomy_identity()!=anatomy:raise RuntimeError('Anatomy changed during audit')
    return dict(anatomy=anatomy,tools=h.tools(),audit_source_sha256=digest(Path(__file__)),old_setup=old_setup,
        joints=list(names),samples_per_joint=7,fixed_coordinates='Imported qpos0 for every other coordinate',states=len(distances),
        min_distance_mm=float(min(distances)),max_distance_mm=float(best),best_q_rad=best_q,
        meaning='Imported proxy overlap in every sampled MCP state; not proof over unsampled anatomy',
        action='Explicit supplemental self-collision exclusion; retain unchanged geoms and incomplete-coverage limitation')


if __name__=='__main__':
    report=audit()
    output=h.ROOT/'notes/myoarm_collision_audit.json'
    output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report))
