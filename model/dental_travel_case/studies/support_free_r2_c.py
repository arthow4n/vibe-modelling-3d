"""Section-only feasibility screen; does not build/export the production case.

Y is across the closed case; Z is up from the table. Two independent hinge
angles describe a manually guided two-pivot opening, not a constrained linkage.
Polygonal shell sections omit axial end shaping, mounts, covers and latches.
"""
import json
import math
from collections import deque
from pathlib import Path
import sys
import numpy as np

HEIGHT = 60.0
WIDTH = 132.0
HALF = HEIGHT / 2
HORIZONTAL_WALL = 3.2  # >=2.49 mm normal at the maximum shoulder slope
FLOOR = 2.4
BASE_HALF = 50.0
SHOULDER_POWER = 1.5
GROWTH = (WIDTH/2-BASE_HALF)*SHOULDER_POWER/HALF  # geometry, not a print limit
LAYER = 0.2
AXIS_Y = 49.5
AXIS_Z = 8.0
LINK = HEIGHT - 2 * AXIS_Z  # 44 mm; vertical when shut
RIM_GAP = 0.6  # total vertical clearance; covering overlap is NOT modelled
PIVOT_CLOSED = np.array([AXIS_Y, HEIGHT-AXIS_Z])
STEP_DEG = 3
CONTACT_TOL = 1e-6  # mm projected separation; touching rim contacts allowed


def half_width(z):
    if not 0 <= z <= HALF:
        raise ValueError('Height outside the half-shell section')
    return WIDTH/2-(WIDTH/2-BASE_HALF)*(1-z/HALF)**SHOULDER_POWER


def rectangle(y0,z0,y1,z1):
    return np.array([[y0,z0],[y1,z0],[y1,z1],[y0,z1]], dtype=float)


def brush_outline():
    # Circumscribed 64-sided polygon encloses the reported 30 mm cylinder.
    radius=15/math.cos(math.pi/64)
    return np.array([[-36+radius*math.cos(u),33+radius*math.sin(u)]
                     for u in np.linspace(0,2*math.pi,64,endpoint=False)])


def brush_cells():
    vertices=brush_outline()
    return np.array([[[-36,33],vertices[i],vertices[(i+1)%64],vertices[(i+2)%64]]
                     for i in range(0,64,2)])


def shell_cells(rim_gap):
    # Piecewise section represents complete floor plus two outward-growing walls.
    cells=[np.array([[-half_width(0),0],[half_width(0),0],
                     [half_width(FLOOR),FLOOR],[-half_width(FLOOR),FLOOR]])]
    levels=np.linspace(FLOOR, HALF-rim_gap/2, 57)
    for z0,z1 in zip(levels[:-1],levels[1:]):
        for sign in (-1,1):
            cells.append(np.array([[sign*half_width(z0),z0], [sign*half_width(z1),z1],
                                   [sign*(half_width(z1)-HORIZONTAL_WALL),z1],
                                   [sign*(half_width(z0)-HORIZONTAL_WALL),z0]]))
    return np.array(cells)


def collide(a,b):
    """Convex quadrilateral SAT with bounding-box rejection; section contact only."""
    amin,amax=a.min(axis=1),a.max(axis=1)
    bmin,bmax=b.min(axis=1),b.max(axis=1)
    mask=np.all(np.minimum(amax[:,None,:],bmax[None,:,:])-
                np.maximum(amin[:,None,:],bmin[None,:,:]) > CONTACT_TOL,axis=2)
    ia,ib=np.nonzero(mask)
    if not len(ia): return False
    aa,bb=a[ia],b[ib]
    edges=np.concatenate((np.roll(aa,-1,axis=1)-aa,
                          np.roll(bb,-1,axis=1)-bb),axis=1)
    axes=np.stack((-edges[:,:,1],edges[:,:,0]),axis=2)
    axes/=np.linalg.norm(axes,axis=2)[:,:,None]
    pa=np.einsum('pvi,pai->pav',aa,axes)
    pb=np.einsum('pvi,pai->pav',bb,axes)
    overlap=np.minimum(pa.max(axis=2),pb.max(axis=2))-np.maximum(pa.min(axis=2),pb.min(axis=2))
    return bool(np.any(np.all(overlap > CONTACT_TOL,axis=1)))


def placed_lid(cells,phi_deg,theta_deg,axis_y,axis_z,link):
    phi,theta=map(math.radians,(phi_deg,theta_deg))
    r=np.array([[math.cos(phi),math.sin(phi)],[-math.sin(phi),math.cos(phi)]])
    pivot=np.array([axis_y+link*math.cos(theta),axis_z+link*math.sin(theta)])
    closed_pivot=np.array([axis_y,HEIGHT-axis_z])
    closed=cells.copy()
    closed[:,:,1]=HEIGHT-closed[:,:,1]
    return (closed-closed_pivot) @ r.T + pivot


def run():
    # Guard the actual geometric interpretation before using it for the study.
    unit=np.array([rectangle(0,0,1,1)])
    assert collide(unit,np.array([rectangle(.5,.5,1.5,1.5)]))
    assert not collide(unit,np.array([rectangle(1,0,2,1)]))
    assert not collide(unit,np.array([rectangle(2,2,3,3)]))
    body=shell_cells(RIM_GAP)
    no_gap_body=shell_cells(0.0)
    no_gap_witnesses=[]
    for phi,theta in ((0,87),(3,90),(3,87)):
        blocked=collide(placed_lid(no_gap_body,phi,theta,AXIS_Y,AXIS_Z,LINK),no_gap_body)
        assert blocked, 'No-gap initial motion witness changed'
        no_gap_witnesses.append({'lid_degrees':phi,'link_degrees':theta,'shell_collision':blocked})
    # Fixed full-height separator and conservative item sections; altered
    # placement is an engineering choice, not a change to existing fit samples.
    separator=np.array([rectangle(-15.4,FLOOR,-13,HEIGHT-FLOOR-.6)])
    head=rectangle(-43.5,21.5,-28.5,46.5)  # 15 x 25 mm, 1 mm above handle axis
    contents=np.concatenate((brush_cells(),np.array([head,rectangle(-12,4.4,48,48.4)])))
    assert not collide(body,contents), 'Stationary contents do not fit section'
    assert not collide(separator,contents), 'Separator cuts through contents'
    guard=np.concatenate((body,separator,contents))
    short_link=placed_lid(body,180,0,AXIS_Y,23.0,14.0)
    short_link_collides=collide(short_link,body)
    assert short_link_collides, 'Short-link negative witness no longer detects shell collision'
    phis=list(range(0,181,STEP_DEG))
    thetas=list(range(0,91,STEP_DEG))
    legal=np.zeros((len(phis),len(thetas)),dtype=bool)
    for i,phi in enumerate(phis):
        for j,theta in enumerate(thetas):
            lid=placed_lid(body,phi,theta,AXIS_Y,AXIS_Z,LINK)
            legal[i,j]=(lid[:,:,1].min() >= -CONTACT_TOL and not collide(lid,guard))
    start=(0,len(thetas)-1)
    finish=(len(phis)-1,0)
    queue=deque([start]) if legal[start] else deque()
    previous={start:None} if legal[start] else {}
    edges_checked=0
    rejected_edges=0
    first_rejected_pose=None
    def edge_failure(first,second):
        for fraction in np.linspace(0,1,16)[1:-1]:
            phi=phis[first[0]]+(phis[second[0]]-phis[first[0]])*fraction
            theta=thetas[first[1]]+(thetas[second[1]]-thetas[first[1]])*fraction
            lid=placed_lid(body,phi,theta,AXIS_Y,AXIS_Z,LINK)
            if lid[:,:,1].min() < -CONTACT_TOL or collide(lid,guard):
                return {'lid_degrees':float(phi),'link_degrees':float(theta)}
        return None
    while queue:
        cell=queue.popleft()
        if cell==finish: break
        i,j=cell
        # A connected sampled route: lid angle only increases; link may be
        # repositioned independently. No promise of intuitive/one-hand operation.
        for nxt in ((i+1,j),(i,j+1),(i,j-1),(i+1,j+1),(i+1,j-1)):
            u,v=nxt
            if 0<=u<len(phis) and 0<=v<len(thetas) and legal[nxt] and nxt not in previous:
                edges_checked+=1
                failure=edge_failure(cell,nxt)
                if failure is not None:
                    rejected_edges+=1
                    if first_rejected_pose is None:
                        first_rejected_pose=failure
                    continue
                previous[nxt]=cell
                queue.append(nxt)
    route=[]
    if finish in previous:
        cell=finish
        while cell is not None:
            i,j=cell
            route.append({'lid_degrees':phis[i],'link_degrees':thetas[j]})
            cell=previous[cell]
        route.reverse()
    sketch_width=120.0
    exact_lens_base_half=sketch_width/2*math.sqrt(1-.965**2)
    lens_first_growth=(sketch_width/2/HALF)*.965/math.sqrt(1-.965**2)
    return {
        'scope':'2D sampled shell/contents/table section; no production CAD or print qualification',
        'geometry_mm':{'width':WIDTH,'height':HEIGHT,'horizontal_wall':HORIZONTAL_WALL,'floor':FLOOR,
                       'flat_base_width':2*BASE_HALF,'shoulder_power':SHOULDER_POWER,
                       'total_rim_gap':RIM_GAP,
                       'body_pivot':[AXIS_Y,AXIS_Z],
                       'lid_closed_pivot':PIVOT_CLOSED.tolist(),'link_axis_spacing':LINK,
                       'open_rear_rim_gap':2*AXIS_Y+LINK-WIDTH},
        'underside_screen':{'layer_mm':LAYER,'maximum_side_growth_mm_per_mm':GROWTH,
                            'maximum_side_growth_per_layer_mm':GROWTH*LAYER,
                            'proposed_axial_growth_mm_per_mm':.5,
                            'combined_corner_growth_bound_mm_per_mm':math.hypot(GROWTH,.5),
                            'sketched_lens_flat_width_mm':2*exact_lens_base_half,
                            'sketched_lens_initial_growth_mm_per_mm':lens_first_growth,
                            'sketched_lens_initial_growth_per_layer_mm':lens_first_growth*LAYER,
                            'interpretation':'Geometric overhang screen only; actual deposited paths/material behavior unknown'},
        'motion_screen':{'angles_step_degrees':STEP_DEG,'tested_poses':int(legal.size),
                         'legal_poses':int(legal.sum()),'closed_legal':bool(legal[start]),
                         'reachable_poses_from_closed':len(previous),
                         'maximum_reachable_lid_degrees':max((phis[i] for i,j in previous),default=None),
                         'flat_open_legal':bool(legal[finish]),'connected_route_found':bool(route),
                         'route':route,'inter_pose_collision_not_excluded':True,
                         'edge_refinement_subdivisions':15,
                         'route_edges_refined':bool(route),
                         'edge_refinement_collisions':[] if route else None,
                         'transition_edges_checked':edges_checked,'rejected_transition_edges':rejected_edges,
                         'first_rejected_intermediate_pose':first_rejected_pose,
                         'short_link_14mm_negative_witness_collides':short_link_collides,
                         'zero_rim_gap_start_motion_collision_witnesses':no_gap_witnesses,
                         'section_height_nodes':57,
                         'qualification':'Shell walls, nominal separator, item sections and table only; no latch, hinge mounts, links or rear-slot covers'},
        'packaging_assumptions':{'brush_centre_yz_mm':[-36,33],'brush_diameter_mm':30,
                                 'brush_polygon_sides':64,'brush_proxy':'circumscribed polygon, not rectangular handle corners',
                                 'head_section_yz_mm':[-43.5,21.5,-28.5,46.5],
                                 'tube_section_yz_mm':[-12,4.4,48,48.4],
                                 'tube_length_allowance_mm':180,'hinge_stations_x_mm':[-104,104],
                                 'provisional_each_station_axial_half_span_mm':10,
                                 'station_to_180mm_tube_end_gap_mm':4},
        'open_questions':['3D corners, axial ends and actual clip/socket placement',
                          'Hinge-bearing and link interference including covered rear slots',
                          'Positive pin capture, actuation/stops and hand-guided path usability',
                          'Support-probed slicing of actual shells, hinge mounts and links',
                          'Actual tube/brush fit and printed bearing/strength behavior']}


def main():
    output=Path(sys.argv[1]).resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    report=run()
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='motion_screen'}|{
        'motion_screen':{k:v for k,v in report['motion_screen'].items() if k!='route'},
        'report':str(output)},indent=2))


if __name__=='__main__':
    main()
