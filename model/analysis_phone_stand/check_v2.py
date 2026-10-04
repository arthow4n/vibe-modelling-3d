"""Decision-specific nominal clearance checks; no printed-fit claims."""
import json
import math
from pathlib import Path
import cadquery as cq
import v2_components as d

def overlap(a,b):
    return a.intersect(b).val().Volume()

def check():
    results=[]
    for u in (d.PIVOT_LOCAL_Y,d.UPPER_CONTACT_Y):
        for side in (-1,1):
            x0=side*38 if side>0 else -50
            shaft=d.cylinder_x(x0,u,d.PIVOT_LOCAL_Z,12,2.5)
            assert overlap(d.cradle(),shaft)<1e-5,('M5 cradle pin',u,side)
            nut=d.hex_x(34.1 if side>0 else -38.1,u,d.PIVOT_LOCAL_Z,4,8)
            assert overlap(d.cradle(),nut)<1e-5,('M5 captive nut',u,side)
            for turn in (0,15,30,45):
                jam=d.hex_x(30.1 if side>0 else -34.1,u,d.PIVOT_LOCAL_Z,4,8)
                jam=jam.rotate((0,u,d.PIVOT_LOCAL_Z),(1,u,d.PIVOT_LOCAL_Z),turn)
                assert overlap(d.cradle(),jam)<1e-5,('M5 jam nut rotation',u,side,turn)
            driver=d.cylinder_x(20 if side>0 else -34.1,u,d.PIVOT_LOCAL_Z,14.1,6.25)
            assert overlap(d.cradle(),driver)<1e-5,('12.5 mm nut driver approach',u,side)
    for angle in d.ANGLES:
        parts={'base':d.base(),'cradle':d.place_cradle(d.cradle(),angle),
               'prop':d.place_prop(d.prop(),angle),'keeper':d.keeper()}
        pairs=[]
        keys=list(parts)
        for i,a in enumerate(keys):
            for b in keys[i+1:]:
                volume=overlap(parts[a],parts[b])
                pairs.append({'parts':[a,b],'interference_mm3':volume})
                assert volume < 1e-5,(angle,a,b,volume)
        for landscape in (False,True):
            phone=d.phone_reference(angle,landscape)
            accessory=d.accessory_reference(angle,landscape)
            for name,part in parts.items():
                for label,reference in [('phone',phone),('accessory',accessory)]:
                    volume=overlap(part,reference)
                    assert volume < 1e-5,(angle,landscape,name,label,volume)
        # A 20 x 30 mm plug extends 30 mm along the phone's lower edge normal.
        # A generous 35-mm-radius bend zone below it occupies the open front bay.
        plug=d.place_cradle(d.box(-10,-30,-2,20,30,18),angle)
        cable=d.box(-12,-35,0,24,70,45)
        for name,part in parts.items():
            assert overlap(part,plug)<1e-5,(angle,name,'plug')
            assert overlap(part,cable)<1e-5,(angle,name,'cable turn')
        y,_=d.prop_pose(angle)
        # Released roof tip is ahead of the round foot by > 0.5 mm.
        released_tip=y-1-d.RELEASE_TRAVEL
        assert y-d.FOOT_RADIUS-released_tip >= .5
        moving=d.keeper().intersect(d.box(-15,0,0,30,220,40))
        for travel in (1,3,5,7):
            released=moving.translate((0,-travel,0))
            assert overlap(released,d.base())<1e-5,(angle,'release base',travel)
            for guide_y in d.GUIDE_YS:
                cap=d.washer().translate((0,guide_y,d.GUIDE_POST_TOP))
                assert overlap(released,cap)<1e-5,(angle,'release cap',travel)
        # Lift the foot above all unused catches while rotating the supported cradle.
        hinge_y=d.PIVOT_Y+78*math.cos(math.radians(angle))
        hinge_z=d.PIVOT_Z+78*math.sin(math.radians(angle))
        raised_z=38
        dz=hinge_z-raised_z
        rear=math.sqrt(d.PROP_LENGTH**2-dz**2)
        beta=math.degrees(math.atan2(dz,-rear))
        raised=d.prop().rotate((0,0,0),(1,0,0),beta).translate((0,hinge_y+rear,raised_z))
        for name,part in parts.items():
            if name!='prop': assert overlap(raised,part)<1e-5,(angle,'raised prop',name)
        results.append({'angle_deg':angle,'seat_y_mm':y,'pairs':pairs,
                        'released_roof_clearance_mm':y-d.FOOT_RADIUS-released_tip})
    report={'checks':results,'scope':'Nominal rigid CAD; accessory envelope is bounded, not universal',
            'phone_mm':[d.PHONE_WIDTH,d.PHONE_HEIGHT,d.PHONE_THICKNESS],
            'manual_release_mm':d.RELEASE_TRAVEL}
    path=Path(__file__).parent/'notes/v2_geometry_checks.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':
    check()
