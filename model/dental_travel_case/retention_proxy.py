"""Practical beam/contact-direction proxy, mm/N/MPa; not a 3D retention rating.

Exact planar elastica of a uniform leaf with a rigid eccentric tooth. The
frictionless retaining reaction follows the rotating flat shoulder, unlike the
old fixed-world traction experiment. Receiver radial compliance, fit loss and
one-catch load concentration are explicit. Does not simulate corner passage,
fracture, distributed contact, torsion, shell buckling, or impact.
"""
from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_bvp
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Leaf:
    length: float
    width: float
    thickness: float
    eccentricity: float
    modulus: float

    @property
    def rigidity(self):
        return self.modulus*self.width*self.thickness**3/12


def from_dimensions(d, modulus):
    # Center of actual common flat land: .25 guide edge to outer .25 fillet.
    contact_r = d.beam_outer + (d.lap_clearance+d.hook_projection-.25)/2
    neutral_r = d.beam_outer-d.beam_thickness/2
    return Leaf(d.hook_bottom-d.beam_root-1, d.beam_width,
                d.beam_thickness, contact_r-neutral_r, modulus)


def rod(leaf, load, *, follower, points=65, tolerance=1e-7):
    """End force (H,P), angle phi inward, tip offset e to the outside.

    EI*phi'' = P*sin(phi)-H*cos(phi); tip moment e*(P*cos(phi)+H*sin(phi)).
    H=P*tan(phi_tip) for a rotating flat retaining face, or H=0 for the
    independently retained fixed-global-Z traction fixture. Receiver translates
    without face rotation in this reduction. Numerics never bypass failure.
    """
    if load < 0 or leaf.rigidity <= 0 or points < 9:
        raise ValueError('Nonnegative tensile load, positive rigidity and >=9 nodes required')
    EI, L, e = leaf.rigidity, leaf.length, leaf.eccentricity
    x = np.linspace(0, L, points)
    k = np.sqrt(load/EI)
    guess = np.zeros((4, points))
    guess[0] = e*load/EI*x
    guess[1] = e*load/EI
    guess[2] = e*load/(2*EI)*x*x
    guess[3] = x
    def equations(s, y, parameter):
        H = parameter[0]
        return np.vstack((y[1], (load*np.sin(y[0])-H*np.cos(y[0]))/EI,
                          np.sin(y[0]), np.cos(y[0])))
    def boundary(a, b, parameter):
        H, angle = parameter[0], b[0]
        return np.array([a[0], a[2], a[3],
            EI*b[1]-e*(load*np.cos(angle)+H*np.sin(angle)),
            H-load*np.tan(angle) if follower else H])
    solution = solve_bvp(equations, boundary, x, guess,
                         p=[load*e*k*np.sinh(k*L) if follower else 0.],
                         tol=tolerance, max_nodes=4096)
    if not solution.success:
        raise RuntimeError('Elastica did not converge: '+solution.message)
    y = solution.sol(x)
    angle = float(y[0,-1])
    if abs(angle) > .65 or abs(float(solution.p[0])) > max(1., load):
        raise ValueError('Outside declared modest-rotation contact branch')
    inward = float(y[2,-1]+e*(1-np.cos(angle)))
    return dict(inward_mm=inward, tip_angle_rad=angle,
        radial_contact_force_N=float(solution.p[0]),
        tooth_axial_motion_mm=float(y[3,-1]+e*np.sin(angle)-L),
        maximum_outer_fiber_strain=float(np.max(np.abs(y[1]))*leaf.thickness/2),
        max_ode_residual=float(max(solution.rms_residuals)),nodes=len(solution.x))


def receiver_stiffness(d, modulus, *, end_fixity):
    """Blind-pocket skin as a transverse strip, supported by pocket sidewalls.

    Uniform strip width is the 1.2mm axial tooth bearing height. Pocket clear
    span includes two 3mm gabled flanks. Simply-supported and fixed-end limits
    differ by four. Thin-strip bending omits membrane stiffening; no fit to M1.
    """
    span = d.hook_width+6
    thickness = (d.pocket_outer_skin+d.skin_reinforcement
                 if hasattr(d,'skin_reinforcement') else .8)
    return end_fixity*4*modulus*1.2*thickness**3/span**3


def capture_margin(leaf, load, *, engagement, fit_loss, receiver_k, follower):
    answer = rod(leaf, load, follower=follower)
    retreat = answer['radial_contact_force_N']/receiver_k
    # Project the outer edge of the finite land, not only its centroid.
    projection_loss=engagement/2*(1-np.cos(answer['tip_angle_rad']))
    return dict(**answer,receiver_retreat_mm=retreat,land_projection_loss_mm=float(projection_loss),
                remaining_flat_capture_mm=engagement-fit_loss-answer['inward_mm']-retreat-projection_loss)


def first_capture_loss(leaf, *, engagement, fit_loss, receiver_k, follower):
    if engagement <= fit_loss:
        return 0.
    def margin(load):
        return capture_margin(leaf,load,engagement=engagement,fit_loss=fit_loss,
                              receiver_k=receiver_k,follower=follower)['remaining_flat_capture_mm']
    # Stop at first crossing; never extend through the rounded-edge escape stage.
    lo=0.
    for hi in np.arange(.25,30.01,.25):
        if margin(float(hi)) <= 0:
            return float(brentq(margin,lo,float(hi),xtol=1e-6))
        lo=float(hi)
    return None


def guide_response(d, modulus, moment, *, end_fixity, load_spread_fraction):
    """Bearing couple M/lap, two springs in series at each end of guide.

    Cap strip spans the straight depth between rounded corners. Body guide pads
    lie between the integral liner-side webs and corners, two pads in parallel.
    Effective axial width is lap*load_spread_fraction, an uncalibrated sensitivity (1/4..1/2).
    A point force at each bearing plane is deliberately more local than pressure
    on a complete tube. Guide slots and ring/corner coupling are not resolved.
    """
    cap_span=d.depth-2*d.corner
    body_span=d.depth/2-d.corner-(d.beam_width/2+2.8)
    width=d.lap*load_spread_fraction
    def stiffness(t,span):
        return end_fixity*4*modulus*width*t**3/span**3
    body_k=2*stiffness(d.lap_wall,body_span)
    cap_k=stiffness(d.receiver_wall,cap_span)
    spring=1/(1/body_k+1/cap_k)
    reaction=abs(moment)/d.lap
    local_deflection=reaction/spring
    theta=(2*d.lap_clearance+2*local_deflection)/d.lap
    # This is a conditional linear-strip estimate; do not interpret gross bending.
    valid=local_deflection <= min(d.lap_wall,d.receiver_wall)/2
    return dict(moment_Nmm=moment,guide_reaction_N=reaction,
        spring_N_per_mm=spring,body_span_mm=body_span,cap_span_mm=cap_span,
        local_relative_deflection_mm=local_deflection,
        joint_rotation_bound_deg=float(np.degrees(theta)),within_small_bending_scope=valid)


def run():
    import m1_design, m2b_design, m3_design
    modules={'M1':m1_design,'M2B':m2b_design,'M3':m3_design}
    result=dict(scope='Conditional flat-capture-loss proxy, not pull-off or escape force. '
        'No friction; no property fitting. Loads are quasi-static. Liner excluded.',
        assumptions=dict(modulus_MPa=[800,1200,2200],fit_loss_mm=[0,.25,.5],
                         receiver_end_fixity=[1,4],single_catch_load_N=[0,2,4,6,8,10,12],
                         bearing_spread_fraction=[.25,.5],moment_Nmm=[100,250,500]),
        first_capture_search_limit_per_catch_N=30,
        null_threshold_meaning='No flat-capture crossing found up to 30N/catch; not infinite strength.',
        variants={},source_sha256={})
    for name,module in modules.items():
        d=module.D
        leaves=[]
        for E in result['assumptions']['modulus_MPa']:
            leaf=from_dimensions(d,E)
            for fit in result['assumptions']['fit_loss_mm']:
                for fixity in (1,4):
                    stiffness=receiver_stiffness(d,E,end_fixity=fixity)
                    loss=first_capture_loss(leaf,engagement=1.5,fit_loss=fit,
                                            receiver_k=stiffness,follower=True)
                    leaves.append(dict(modulus_MPa=E,fit_loss_mm=fit,
                        receiver_end_fixity=fixity,receiver_k_N_per_mm=stiffness,
                        first_flat_capture_loss_per_catch_N=loss,
                        symmetric_axial_total_at_same_state_N=None if loss is None else 2*loss,
                        one_catch_total_at_same_state_N=loss))
        leaf=from_dimensions(d,1200)
        curve=[]
        for P in np.arange(0,12.001,.5):
            response=capture_margin(leaf,float(P),engagement=1.5,fit_loss=.25,
                receiver_k=receiver_stiffness(d,1200,end_fixity=1),follower=True)
            curve.append(dict(per_catch_axial_N=float(P),**response))
            if response['remaining_flat_capture_mm']<=0:break
        operation=[]
        L=d.beam_tip-d.beam_root-1
        a=d.press_z-d.beam_root-1
        for E in (800,1200,2200):
            I=d.beam_width*d.beam_thickness**3/12
            P=d.release*6*E*I/(a*a*(3*L-a))
            operation.append(dict(modulus_MPa=E,pad_force_N=P,
                pad_travel_mm=P*a**3/(3*E*I),nominal_root_strain=P*a*d.beam_thickness/(2*E*I)))
        guidance=[dict(modulus_MPa=E,end_fixity=f,load_spread_fraction=b,
                      **guide_response(d,E,M,end_fixity=f,load_spread_fraction=b))
                  for E in (800,1200,2200) for f in (1,4) for b in (.25,.5) for M in (100,250,500)]
        edge_controls=[]
        for edge in (-.75,.75):
            for follow in (False,True):
                edge_leaf=replace(from_dimensions(d,800),eccentricity=from_dimensions(d,800).eccentricity+edge)
                edge_controls.append(dict(eccentricity_mm=edge_leaf.eccentricity,
                    follower=follow,first_flat_capture_loss_per_catch_N=first_capture_loss(edge_leaf,
                        engagement=1.5,fit_loss=.5,receiver_k=receiver_stiffness(d,800,end_fixity=1),follower=follow)))
        handling=[]
        for E in (800,1200,2200):
            for total in (5,10,20):
                for moment in (0,100,250):
                    r=d.width/2-d.receiver_wall
                    for route in ('catch_couple','guide_couple','one_catch'):
                        P=(total/2+moment/(2*r) if route=='catch_couple' else
                           total if route=='one_catch' else total/2)
                        guide_moment=(0 if route=='catch_couple' else
                                      moment+total*r if route=='one_catch' else moment)
                        guide=guide_response(d,E,guide_moment,end_fixity=1,load_spread_fraction=.25)
                        first=next(x['first_flat_capture_loss_per_catch_N'] for x in leaves
                                   if x['modulus_MPa']==E and x['fit_loss_mm']==.5 and x['receiver_end_fixity']==1)
                        if guide['local_relative_deflection_mm'] >= 1.:
                            remaining=None
                            state='guide movement consumes the assumed capture budget'
                        elif first is not None and P>=first:
                            remaining=None
                            state='load exceeds first flat-capture loss; no post-loss solution attempted'
                        else:
                            response=capture_margin(from_dimensions(d,E),P,engagement=1.5,
                                fit_loss=.5+guide['local_relative_deflection_mm'],
                                receiver_k=receiver_stiffness(d,E,end_fixity=1),follower=True)
                            remaining=response['remaining_flat_capture_mm']
                            state='capture remains' if remaining>0 else 'flat capture lost'
                        handling.append(dict(modulus_MPa=E,total_axial_N=total,
                            applied_moment_Nmm=moment,load_path=route,
                            one_catch_axial_N=P,guide_moment_Nmm=guide_moment,
                            guide_small_bending_scope=guide['within_small_bending_scope'],
                            remaining_capture_mm=remaining,state=state,
                            scope='Declared conservative load-path scenario; not a solved shell equilibrium or rigorous bound.'))
        result['variants'][name]=dict(leaf=asdict(leaf),capture_sensitivity=leaves,contact_edge_controls=edge_controls,
            handling_scenarios=handling,
            central_response=curve,guide_sensitivity=guidance,release_beam_estimate=operation,
            fixed_world_12N=rod(leaf,12,follower=False))
        result['source_sha256'][module.__name__+'.py']=hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
    result['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    target=ROOT/'notes/m3/proxy.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+'\n')
    for name,v in result['variants'].items():
        values=[x['first_flat_capture_loss_per_catch_N'] for x in v['capture_sensitivity'] if x['first_flat_capture_loss_per_catch_N'] is not None]
        print(name,'flat-capture-loss range N/catch:',min(values),max(values),
              'fixed-world 12N:',v['fixed_world_12N']['inward_mm'], 'uncrossed:',sum(x['first_flat_capture_loss_per_catch_N'] is None for x in v['capture_sensitivity']))


if __name__=='__main__':
    run()
