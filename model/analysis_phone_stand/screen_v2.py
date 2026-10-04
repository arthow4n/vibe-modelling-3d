"""Whole-stand statics and stock-pin screens, not material calibration."""
import json
import math
from pathlib import Path
import v2_components as d

def screen():
    cases=[]
    # Ignore the stand's mass: conservative tipping and grip screens for phone alone.
    # The central 130 x 246 rectangle is inside the actual wider rear footprint.
    W=d.PHONE_MASS_KG*9.81
    for angle in d.ANGLES:
        t=math.radians(angle)
        for landscape in (False,True):
            width,height=(d.PHONE_HEIGHT,d.PHONE_WIDTH) if landscape else (d.PHONE_WIDTH,d.PHONE_HEIGHT)
            def world(u,v):
                return (d.PIVOT_Y+(u-d.PIVOT_LOCAL_Y)*math.cos(t)-(v-d.PIVOT_LOCAL_Z)*math.sin(t),
                        d.PIVOT_Z+(u-d.PIVOT_LOCAL_Y)*math.sin(t)+(v-d.PIVOT_LOCAL_Z)*math.cos(t))
            cy,cz=world(height/2,d.PHONE_THICKNESS/2)
            ty,tz=world(height-10,d.PHONE_THICKNESS)
            normal_tap=2.0
            sideways=.5
            Fy=normal_tap*math.sin(t)
            downward=normal_tap*math.cos(t)
            vertical=W+downward
            cop_y=(W*cy+downward*ty+Fy*tz)/vertical
            cop_x=(downward*(width/2-5)+sideways*tz)/vertical
            minimum_margin=min(cop_y-d.BASE_FRONT_Y,d.BASE_REAR_Y-cop_y,65-cop_x)
            assert minimum_margin>0
            cases.append(dict(angle_deg=angle,landscape=landscape,
                phone_bottom_height_mm=world(0,0)[1],
                tap_N=normal_tap,sideways_N=sideways,centre_of_pressure_mm=[cop_x,cop_y],
                tipping_margin_mm=minimum_margin,
                required_friction_coefficient_phone_only=math.hypot(Fy,sideways)/vertical))
    # Each M5 pin: a conservative 15 N, one shear plane, 6 mm printed bearing.
    # Screw root diameter assumed 4.0 mm; not a thread solve or grade qualification.
    pin=dict(load_per_pin_N=15,nominal_bearing_MPa=15/(5*6),
             nominal_steel_single_shear_MPa=15/(math.pi*4**2/4),
             minimum_jam_nut_thread_projection_mm=(d.CRADLE_BOSS_INNER_X+.1-2*d.NUT_THICKNESS)-(d.PROP_INNER_X+d.PROP_WIDTH-d.PIN_LENGTH),
             scope='Geometric load screen; no stock screw grade, tightening torque, creep or loosening qualification')
    assert pin['minimum_jam_nut_thread_projection_mm']>0
    report={'cases':cases,'pins':pin,
        'limits':'Static provisional taps only. Stand mass ignored. Actual desk/case friction, impacts and print stiffness unmeasured.'}
    (Path(__file__).parent/'notes/v2_statics.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':screen()
