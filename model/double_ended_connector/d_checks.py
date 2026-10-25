"""Targeted CAD intent checks for D; physical locking force remains unknown."""
from d_design import (parts, configuration, gate_pose, STROKE, STEM_X,
                      STEM_Y, NOSE_Y, NOSE_RADIUS)
from lock_geometry import box, along_y


def check_motion():
    p=parts(); frame=p['lower'].union(p['upper'])
    stem=along_y(p['stem'],STEM_X,STEM_Y)
    body=frame.union(stem).union(stem.rotate((0,0,0),(1,0,0),180))
    results=[]
    bottom=gate_pose(p['barrel'],STROKE,-1)
    assert bottom.intersect(body).val().Volume()<.001, 'Closed lower gate interferes'
    # Pair overlap tolerance is a kernel roundoff allowance, not print clearance.
    for travel in (0.,1.,2.,3.,4.,5.,6.,7.,8.):
        a=configuration(top_travel=travel,bottom_travel=STROKE)
        overlap=a.shape('barrel_top').intersect(body.val()).Volume()
        assert overlap<.001, (travel,'barrel_top',overlap)
        results.append(travel)
    # Fixed-position axial yanking should encounter thread/keeper material.
    closed=gate_pose(p['barrel'],STROKE,1)
    blocked=closed.translate((0,.7,0)).intersect(body).val().Volume()
    assert blocked>.05, ('keeper does not block',blocked)
    # A 3.2 mm cord section can pass through the open nominal mouth. The
    # local opening box is independent of the barrel construction dimensions.
    opening=box(STEM_X,22,0,3.2,3.2,4.0)
    open_gate=gate_pose(p['barrel'],0,1)
    assert opening.intersect(body.union(open_gate)).val().Volume()<.001
    # Opposite mouth is still physically bridged in the open configuration.
    assert gate_pose(p['barrel'],STROKE,-1).val().isInside((STEM_X+4.8,-23.,0),1e-6)
    # Free nose section can enter a 7.6 mm across-flats bore without stretching.
    assert 2*NOSE_RADIUS<7.6
    return {'helical_travel_samples_mm':results,'forbidden_overlap_limit_mm3':.001,
            'axial_pull_obstruction_mm3':blocked,'open_mouth_witness':'3.2 x 3.2 x 4 mm clear'}


def check_assembly():
    p=parts()
    # Upper frame approaches from above; no closed annulus has to be forced
    # over an integral horn. Screws are fitted after frame closure.
    for dz in (12.,6.,3.,1.,.2,0.):
        upper=p['upper'].translate((0,0,dz))
        for sign in (1,-1):
            sleeve=gate_pose(p['barrel'],0.,sign)
            shank=along_y(p['stem'],STEM_X,STEM_Y)
            if sign==-1:shank=shank.rotate((0,0,0),(1,0,0),180)
            assert upper.intersect(sleeve).val().Volume()<.001, ('frame / open barrel',dz,sign)
            assert upper.intersect(shank).val().Volume()<.001, ('frame / keyed stem',dz,sign)
    # Install each barrel AXIALLY over the keyed root before fitting the frame.
    shank=along_y(p['stem'],STEM_X,STEM_Y)
    for travel in (-18.,-12.,-8.,-4.,0.):
        sleeve=gate_pose(p['barrel'],travel,1)
        assert sleeve.intersect(shank).val().Volume()<.001, ('barrel preassembly',travel)
    frame=p['upper'].union(p['lower'])
    assert shank.translate((0,.6,0)).intersect(frame).val().Volume()>.02, 'Root not axially captured'
    # Known hollow-core regression: the actual delivered screw must have
    # material down its axis, including threaded and head sections.
    for z in (-6.,-4.5,-3.,0.,1.,3.):
        assert p['screw'].val().isInside((0,0,z),1e-6), ('Hollow screw',z)
    closed=configuration(top_travel=STROKE,bottom_travel=STROKE)
    for screw in ('screw_bottom','screw_top'):
        for frame in ('lower','upper'):
            assert closed.shape(screw).intersect(closed.shape(frame)).Volume()<.001, ('screw clearance',screw,frame)
    return {'upper_frame_approach_mm':[12.,6.,3.,1.,.2,0.],
            'solid_screw_axis_witnesses':6,'printed_components':8}


if __name__=='__main__':
    import json
    print(json.dumps({'motion':check_motion(),'assembly':check_assembly()},indent=2))
