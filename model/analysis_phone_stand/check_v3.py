"""Consequential fit, release, accessory, cable and full-stand static screens."""
import itertools,json,math
from pathlib import Path
import v3_components as d


def overlap(a,b):return a.intersect(b).val().Volume()


def check():
    base,cradle,slider,pin=d.base(),d.cradle(),d.slider(),d.place_pin(d.pin())
    moving=slider.intersect(d.box(-15,0,0,30,150,80))
    records=[]
    for angle in d.ANGLES:
        parts={'base':base,'cradle':d.place_cradle(cradle,angle),'slider':slider,'pin':pin}
        pairs={f'{a}/{b}':overlap(parts[a],parts[b]) for a,b in itertools.combinations(parts,2)}
        for pair,v in pairs.items():assert v<1e-5,(angle,pair,v)
        for landscape in (False,True):
            for label,ref in [('phone',d.phone(angle,landscape)),('ring',d.ring(angle,landscape))]:
                for name,part in parts.items():assert overlap(part,ref)<1e-5,(angle,landscape,label,name)
        plug=d.place_cradle(d.box(-10,d.PHONE_U-30,d.PHONE_V-2,20,30,18),angle)
        for name,part in parts.items():assert overlap(part,plug)<1e-5,(angle,'charging plug',name)
        # Both angular load directions must meet a hard face with the dog engaged.
        for direction in (-1,1):
            blocked=d.place_cradle(cradle,angle+direction*1.0)
            assert overlap(blocked,moving)>1e-3,(angle,'lock does not block',direction)
        records.append(dict(angle=angle,interference_mm3=pairs))
    released=moving.translate((0,-d.RELEASE,0))
    # Head and sprung barb must independently prevent rigid pin withdrawal.
    for direction in (-1,1):
        assert overlap(pin.translate((direction,0,0)),base)>1e-3,('pin not captive',direction)
    for travel in (1,d.RELEASE/2,d.RELEASE):
        q=moving.translate((0,-travel,0))
        assert overlap(q,base)<1e-5,('released slider/base',travel)
        assert overlap(q,pin)<1e-5,('released slider/pin',travel)
    assert overlap(moving.translate((0,-d.RELEASE-.5,0)),pin)>1e-3,'missing release travel stop'
    for angle in range(45,76,2):
        q=d.place_cradle(cradle,angle)
        assert overlap(q,base)<1e-5,('hinge sweep/base',angle)
        assert overlap(q,released)<1e-5,('hinge sweep/released dog',angle)
    # Root insertion is checked without cradle or pin, which are fitted afterwards.
    for offset in (2,5,10,20,40,60,100):
        assert overlap(slider.translate((0,offset,0)),base)<1e-5,('slider insertion',offset)
    # Mass properties are explicitly needed to decide compact-footprint tipping;
    # all final PETG parts must be sliced solid. This is not a generic CAD report.
    density=1.27e-6 # kg/mm3, diagnostic PETG assumption, not user's measured spool.
    stats=[]
    for angle in d.ANGLES:
        parts=[base,d.place_cradle(cradle,angle),slider,pin]
        masses=[p.val().Volume()*density for p in parts]
        centres=[p.val().Center() for p in parts]
        mass=sum(masses);cg=[sum(m*c.toTuple()[i] for m,c in zip(masses,centres))/mass for i in range(3)]
        t=math.radians(angle)
        for landscape in (False,True):
            w,h=(d.PHONE_HEIGHT,d.PHONE_WIDTH) if landscape else (d.PHONE_WIDTH,d.PHONE_HEIGHT)
            def pos(u,v):return (d.PIVOT_Y+u*math.cos(t)-v*math.sin(t),d.PIVOT_Z+u*math.sin(t)+v*math.cos(t))
            py,pz=pos(d.PHONE_U+h/2,d.PHONE_V+d.PHONE_THICKNESS/2)
            ty,tz=pos(d.PHONE_U+h-10,d.PHONE_V+d.PHONE_THICKNESS)
            for normal in (-2.,-.5,2.):
                Fy=normal*math.sin(t);down=normal*math.cos(t);side=.5
                reaction=(mass+d.PHONE_MASS)*9.81+down
                cop_y=(mass*9.81*cg[1]+d.PHONE_MASS*9.81*py+down*ty+Fy*tz)/reaction
                cop_x=(mass*9.81*cg[0]+down*(w/2-5)+side*tz)/reaction
                margin=min(cop_y-3,137-cop_y,52.5-abs(cop_x))
                stats.append(dict(angle=angle,landscape=landscape,normal_N=normal,
                    scenario='diagnostic_outward_pull' if normal==-2 else 'provisional_service',
                    stand_mass_kg=mass,stand_cg_mm=cg,pressure_centre_mm=[cop_x,cop_y],tipping_margin_mm=margin,
                    required_friction=math.hypot(Fy,side)/reaction,phone_bottom_height_mm=pos(d.PHONE_U,d.PHONE_V)[1]))
                if normal!=-2:assert margin>0,('tipping',stats[-1])
    report=dict(scope='Nominal rigid fit and sampled motion; solid-density statics conditional on final print. No material/friction/return qualification.',
                geometry=records,statics=stats,density_kg_mm3=density)
    (Path(__file__).parent/'notes/v3_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':'passed','minimum_service_tipping_margin_mm':min(x['tipping_margin_mm'] for x in stats if x['scenario']=='provisional_service'),'stand_mass_kg':stats[0]['stand_mass_kg']}))

if __name__=='__main__':check()
