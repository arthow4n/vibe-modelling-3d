"""Linear Timoshenko frame screen of isolated webs, not a noise prediction."""
import json
import sys
from pathlib import Path
from math import pi, hypot, sin, cos, sqrt
import numpy as np
import design as d
from execution.identity import digest

ROOT=Path(__file__).resolve().parent


def centreline(name, subdivisions):
    v=d.variant_named(name)
    h=d.ZONE-d.BACKING-v.skin
    z=np.linspace(0,h,subdivisions+1)
    if v.core=='straight':
        x=np.zeros_like(z)
    elif v.core=='inclined':
        x=-0.6+1.2*z/h
    elif v.core=='chevron':
        x=-0.5+2*np.minimum(z/h,1-z/h)
    elif v.core=='bowed':
        x=d.BOW_AMPLITUDE*np.sin(pi*z/h)
    else:
        raise ValueError(name)
    return np.column_stack((x,z))


def stiffness(name, subdivisions, nu, *, tangential_fixed):
    """E=1, width=1 mm; end rotations fixed, selected lateral restraint.

    Exact two-node linear Timoshenko element; no native continuum solver.
    The displacement is a normalization for linear stiffness, not an operating
    deformation. No energy loss, strain acceptance, prestress or inertia model.
    """
    points=centreline(name,subdivisions)
    t=d.variant_named(name).rib_wall
    area=t
    inertia=t**3/12
    shear=1/(2*(1+nu))
    matrix=np.zeros((3*len(points),3*len(points)))
    for i,(p,q) in enumerate(zip(points,points[1:])):
        dx,dz=q-p
        length=hypot(dx,dz)
        c,s=dx/length,dz/length
        phi=12*inertia/((5/6)*shear*area*length**2)
        a=area/length
        b=12*inertia/((1+phi)*length**3)
        k=6*inertia/((1+phi)*length**2)
        f=(4+phi)*inertia/((1+phi)*length)
        g=(2-phi)*inertia/((1+phi)*length)
        local=np.array([[a,0,0,-a,0,0],[0,b,k,0,-b,k],[0,k,f,0,-k,g],
                        [-a,0,0,a,0,0],[0,-b,-k,0,b,-k],[0,k,g,0,-k,f]])
        rot=np.array([[c,s,0],[-s,c,0],[0,0,1]])
        transform=np.zeros((6,6));transform[:3,:3]=rot;transform[3:,3:]=rot
        indices=np.arange(3*i,3*i+6)
        matrix[np.ix_(indices,indices)]+=transform.T@local@transform
    prescribed=np.array([0,1,2,len(matrix)-2,len(matrix)-1]+([len(matrix)-3] if tangential_fixed else []))
    free=np.setdiff1d(np.arange(len(matrix)),prescribed)
    u=np.zeros(len(matrix));u[-2]=1
    u[free]=np.linalg.solve(matrix[np.ix_(free,free)],-matrix[np.ix_(free,prescribed)]@u[prescribed])
    return float((matrix@u)[-2])


def bow_chord_check():
    """Sample source boundary chord error before accepting its 32 segments."""
    v=d.variant_named('H');h=d.ZONE-d.BACKING-v.skin
    profile=d.bowed_profile(v)
    n=d.BOW_SEGMENTS+1
    boundaries=(profile[:n],list(reversed(profile[n:])))
    errors={}
    for step in (2,1):
        maximum=0.
        for side,boundary in zip((-1,1),boundaries):
            points=boundary[::step]
            for (xa,za),(xb,zb) in zip(points,points[1:]):
                for fraction in (.25,.5,.75):
                    z=za+(zb-za)*fraction
                    slope=d.BOW_AMPLITUDE*pi/h*cos(pi*z/h)
                    exact=d.BOW_AMPLITUDE*sin(pi*z/h)+side*v.rib_wall*sqrt(1+slope*slope)/2
                    maximum=max(maximum,abs(exact-(xa+(xb-xa)*fraction)))
        errors[str(d.BOW_SEGMENTS//step)]=maximum
    limit=.003  # object-owned chord budget, matching export deflection scale
    assert errors[str(d.BOW_SEGMENTS)]<limit
    assert errors[str(d.BOW_SEGMENTS)]<errors[str(d.BOW_SEGMENTS//2)]
    return {'sampled_max_x_error_mm':errors,'limit_mm':limit,'scope':'quarter/midpoint samples of source boundary chords; not exact normal-thickness qualification'}


def main():
    # Qualify the frame assembly on the exact axial straight-member solution.
    axial=d.variant_named('C').rib_wall/(d.ZONE-d.BACKING-d.variant_named('C').skin)
    assert abs(stiffness('C',16,.49,tangential_fixed=True)-axial)<1e-8, 'Straight bar regression failed'
    results={}
    for name in ('C','D','E','G','H','I'):
        fine=stiffness(name,64,.49,tangential_fixed=True)
        finer=stiffness(name,128,.49,tangential_fixed=True)
        relative=abs(finer-fine)/finer
        assert relative<.005, 'Frame discretization changes the selection materially'
        results[name]={'k_over_E_per_1mm_width':finer,'relative_64_128_change':relative,
          'tangential_free_stiffness':stiffness(name,128,.49,tangential_fixed=False),
          'nu_0.3_stiffness':stiffness(name,128,.3,tangential_fixed=True),'centreline_length_mm':float(np.linalg.norm(np.diff(centreline(name,128),axis=0),axis=1).sum())}
    reference=results['D']['k_over_E_per_1mm_width']
    for name,row in results.items():
        row['relative_to_D']=row['k_over_E_per_1mm_width']/reference
        row['relative_to_E']=row['k_over_E_per_1mm_width']/results['E']['k_over_E_per_1mm_width']
        row['tangential_free_relative_to_E']=row['tangential_free_stiffness']/results['E']['tangential_free_stiffness']
    # The selection is useful only if the proposed webs are more compliant
    # under the stated restricted model. This is an engineering screen.
    assert results['H']['relative_to_E']<1 and results['I']['relative_to_E']<1
    result={'category':'analytical-initial-compliance-screen',
      'versions':{'numpy':np.__version__,'python':sys.version.split()[0]},
      'source_sha256':{name:digest(ROOT/name) for name in ('design.py','compliance_screen.py')},
      'relative_refinement_limit':.005,'bow_chord_check':bow_chord_check(),
      'assumptions':{'E':'normalized 1 N/mm²; no calibrated TPU modulus','width_mm':1,
       'nu':.49,'shear_factor':5/6,'boundary':'base fixed; top rotation fixed and normal displacement prescribed; tangential fixed/free sensitivity',
       'omissions':'skins, corners, edge frames, nonlinear deformation, viscoelasticity, air, inertia, acoustics, printed anisotropy'},
      'results':results,'skin_bending_ratio_0.6_to_0.8':(.6/.8)**3,
      'conclusion':'I isolated webs have lower initial stiffness than E; H is approximately E. Lateral-end sensitivity does not predict acoustics; actual quietness UNKNOWN.'}
    (ROOT/'notes/compliance_screen.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
