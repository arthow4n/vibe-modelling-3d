"""Nominal socket-cap screw/nut envelopes, for inspection and tool checks only.

Smooth shafts/bores omit threads. Match actual stock head sizes before fitting.
"""
import math
import cadquery as cq


def screw(diameter,length,head_diameter,head_height,hex_flats):
    shaft=cq.Workplane('XY').circle(diameter/2).extrude(length)
    head=cq.Workplane('XY',origin=(0,0,-head_height)).circle(head_diameter/2).extrude(head_height)
    socket=(cq.Workplane('XY',origin=(0,0,-head_height-0.01))
            .polygon(6,2*hex_flats/math.sqrt(3)).extrude(head_height/2+0.01))
    return shaft.union(head).cut(socket).val()


def nut(flats,thickness,bore):
    return (cq.Workplane('XY').polygon(6,2*flats/math.sqrt(3)).circle(bore/2)
            .extrude(thickness).val())


def hardware(p,diameter):
    from mounting_clamp import bolt_position,gap_angle
    items={}
    for i,a in enumerate(p.mount_angles,1):
        x,y=bolt_position(p,a,diameter)
        items[f'M3_head_{i}']=screw(3,p.mount_screw_length,5.5,3,2.5).translate((x,-y,p.hood_standoff-p.mount_tab_thickness))
        start,end=bolt_position(p,a,p.clamp_min_diameter),bolt_position(p,a,p.clamp_max_diameter)
        theta=math.degrees(math.atan2(end[1]-start[1],end[0]-start[0]))
        seat=p.hood_standoff+p.mount_bearing
        items[f'M3_nut_{i}']=nut(5.5,2.4,3.4).rotate((0,0,0),(0,0,1),-theta).translate((x,-y,seat))
    r=diameter/2;half=(r+p.clamp_wall/2)*math.sin(gap_angle(p,diameter)/2)
    outside=half+p.clamp_ear_wall
    items['M4_head']=screw(4,25,7,4,3).rotate((0,0,0),(1,0,0),90).translate((r+p.clamp_bolt_offset,outside+p.clamp_head_standoff,8))
    # Hex point along installed Z, to match the captured flats.
    items['M4_nut']=nut(7,3.2,4.4).rotate((0,0,0),(0,0,1),90).rotate((0,0,0),(1,0,0),90).translate((r+p.clamp_bolt_offset,-outside+2,8))
    return items
