"""Isolate actual cap-window release, conditional on unloaded assembled closure.

No print geometry changes. Earlier elastic closing solves return the tab to
approximately zero deformation; this fixture does not independently prove
that closing succeeds. Both moving obstacles drive contact on the real head.
"""
import argparse
from dataclasses import replace
import json
from analyze import operation


def release(mesh=1.6, penalty=12000., increment=.006, timeout=3600):
    c=operation(mesh,penalty,increment,timeout)
    c.name='covered_lift_release_only'
    c.parts['lid_catch'].shape=c.parts['lid_catch'].shape.translate((0,0,-12))
    c.constraints[1]=replace(c.constraints[1],displacement_mm=(0,0,12),
        progress=((0,0),(.3,0),(.45,1/6),(.6,1/6),(.9,1),(1,1)))
    c.constraints[2]=replace(c.constraints[2],progress=((0,0),(.1,2/3.4),(.3,1),(.45,1),(.6,0),(1,0)))
    head=c.contacts[0].slave.region
    masters=tuple(contact.master for contact in c.contacts)
    c.contacts=[]
    c.contact('arm',head,masters,penalty_N_mm3=penalty,penetration_limit_mm=.02,
              discretization='surface_to_surface')
    return c


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory');p.add_argument('--backend',choices=('calculix','febio'),default='calculix')
    p.add_argument('--mesh',type=float,default=1.6);p.add_argument('--penalty',type=float,default=12000)
    p.add_argument('--increment',type=float,default=.006);p.add_argument('--timeout',type=float,default=3600)
    p.add_argument('--mesh-from');p.add_argument('--no-augmentation',action='store_true')
    p.add_argument('--two-pass',action='store_true')
    p.add_argument('--force-tolerance',type=float,default=1e-6,help='FEBio absolute free-DOF residual norm in N')
    a=p.parse_args();backend=None
    if a.backend=='febio':
        from physical_analysis.backends.febio import FebioBackend
        backend=FebioBackend(augmented_lagrange=not a.no_augmentation,two_pass=a.two_pass,
                            force_residual_tolerance_N=a.force_tolerance)
    r=release(a.mesh,a.penalty,a.increment,a.timeout).run(a.directory,backend=backend,mesh_from=a.mesh_from)
    print(json.dumps(dict(status=r.status,errors=r.errors,metrics=r.metrics),indent=2))
