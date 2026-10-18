"""Space-first closure research, not an adopted full-case revision.

Three same-size tip-snap samples and one sliding-lid sample. Full reference
shells make the crops and contents checks honest; only samples are published.
All dimensions in mm. No exports or evidence writes during construction.
"""
from dataclasses import dataclass
import cadquery as cq
import m1_design as base


@dataclass(frozen=True)
class Dimensions:
    width: float = 77.
    depth: float = 51.2
    length: float = 264.
    seam: float = 174.
    lap: float = 78.
    wall: float = 2.
    floor: float = 2.
    corner: float = 6.
    end_radius: float = 4.
    clearance: float = .15
    sleeve_wall: float = 1.6
    detent: float = .65
    axial_play: float = .20
    tip_offset: float = 3.
    bump_width: float = 10.

    @property
    def sleeve_width(self):return self.width-2*(self.wall+self.clearance)
    @property
    def sleeve_depth(self):return self.depth-2*(self.wall+self.clearance)
    @property
    def sleeve_corner(self):return self.corner-self.wall-self.clearance
    @property
    def latch_z(self):return self.seam+self.lap-self.tip_offset


D=Dimensions()
KINDS=('shell_broad','shell_end','perimeter_bead','slide_wall')


def validate(kind):
    if kind not in KINDS:raise ValueError('Unknown research closure: '+str(kind))


def plain_shells(d):
    outer=base.prism(d.width,d.depth,d.corner,0,d.seam)
    outer=base.rounded_print_end(outer,d,top=False).edges('>Z').fillet(.6)
    sleeve=base.prism(d.sleeve_width,d.sleeve_depth,d.sleeve_corner,d.seam-.5,d.lap+.5)
    sleeve=sleeve.edges('>Z').chamfer(.4)
    inner=cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (d.floor,d.width-4,d.depth-4,d.corner-2),
            (d.seam-6,d.width-4,d.depth-4,d.corner-2),
            (d.seam,d.sleeve_width-3.2,d.sleeve_depth-3.2,d.sleeve_corner-1.6),
            (d.seam+d.lap+1,d.sleeve_width-3.2,d.sleeve_depth-3.2,d.sleeve_corner-1.6))],ruled=True))
    inner=inner.edges('<Z').fillet(2)
    body=outer.union(sleeve).cut(inner).clean()
    upper=base.prism(d.width,d.depth,d.corner,d.seam,d.length-d.seam)
    upper=base.rounded_print_end(upper,d,top=True).edges('<Z').fillet(.6)
    cavity=base.prism(d.width-4,d.depth-4,d.corner-2,d.seam-1,d.length-d.floor-d.seam+1)
    cavity=cavity.edges('>Z').fillet(2)
    return body,upper.cut(cavity).clean()


def local_bump(radius,z,width,projection,*,pocket=False,play=.2):
    """Ramped lower and upper faces: a deliberately pull-open snap, no square lock."""
    # A pocket adds axial/radial clearance but preserves the same ramp directions.
    p=projection+(.15 if pocket else 0)
    dz=play if pocket else 0
    pts=[(radius-.2,z-1.2-dz),(radius+p,z-.25-dz),
         (radius+p,z+.25+dz),(radius-.2,z+1.5+dz)]
    return (cq.Workplane('YZ',origin=(-width/2,0,0)).polyline(pts).close().extrude(width))


def tip_shell(kind,d,*,runout=True):
    body,cap=plain_shells(d)
    z=d.latch_z
    if kind=='perimeter_bead':
        levels=((z-1.2,0),(z-.25,d.detent),(z+.25,d.detent),(z+1.5,0))
        def ring(extra,play):
            wires=[base.rounded_wire(d.sleeve_width+2*(p+extra),d.sleeve_depth+2*(p+extra),
                      d.sleeve_corner+p+extra,h+(-play if h<z else play)) for h,p in levels]
            shape=cq.Workplane(obj=cq.Solid.makeLoft(wires,ruled=True))
            return shape.cut(base.prism(d.sleeve_width-3.2,d.sleeve_depth-3.2,d.sleeve_corner-1.6,z-3,6))
        bump=ring(0,0)
        pocket=ring(.15,d.axial_play)
    else:
        radial=d.sleeve_depth/2 if kind=='shell_broad' else d.sleeve_width/2
        bump=local_bump(radial,z,d.bump_width,d.detent)
        pocket=local_bump(radial,z,d.bump_width+.6,d.detent,pocket=True,play=d.axial_play)
        if kind=='shell_end':
            bump=bump.rotate((0,0,0),(0,0,1),90)
            pocket=pocket.rotate((0,0,0),(0,0,1),90)
        plane='XZ' if kind=='shell_broad' else 'YZ'
        bump=bump.union(bump.mirror(plane))
        pocket=pocket.union(pocket.mirror(plane))
    body=body.union(bump).clean()
    cap=cap.cut(pocket).clean()
    # A tip catch otherwise rubs through almost the entire 78mm withdrawal.
    # A recessed track BELOW a short retaining lip lets it recover after the
    # initial snap. The lip is deliberately preserved between the two recesses.
    if runout:
        top=z-3.2
        if kind=='perimeter_bead':
            track=base.prism(d.sleeve_width+2*(d.detent+.15),d.sleeve_depth+2*(d.detent+.15),
                             d.sleeve_corner+d.detent+.15,d.seam-1,top-d.seam+1)
        else:
            radial=d.sleeve_depth/2 if kind=='shell_broad' else d.sleeve_width/2
            track=base.box(0,radial+.3,(d.seam-1+top)/2,d.bump_width+.6,1.0,top-d.seam+1)
            if kind=='shell_end':track=track.rotate((0,0,0),(0,0,1),90)
            track=track.union(track.mirror('XZ' if kind=='shell_broad' else 'YZ'))
        cap=cap.cut(track).clean()
    return dict(dimensions=d,body=body,cap=cap,plain_body=plain_shells(d)[0],
                kind=kind,bump=bump,pocket=pocket)


def slide(length,*,gentle_ramps=True):
    """Broad-face opening; coordinates X width, Y length, Z depth/print-up.

    3.2mm side walls contain the sliding grooves. A small detent uses the
    uncut sidewall's elasticity, with no independent spring or closed guard.
    """
    if length<30:raise ValueError('Slide specimen must preserve both ends and detent')
    outer=base.prism(77,length,4,0,49.2).translate((0,length/2,0))
    inner=base.prism(70.6,length-4,1.2,2,50).translate((0,length/2,0))
    body=outer.cut(inner)
    # Each undercut is reached from the open end along Y; upper/lower slopes
    # let both specimen parts print without a horizontal rail overhang.
    slot_points=[(33.6,45.7),(35.5,45.7),(36.8,47.2),(36.8,47.95),(35.4,49.4),(33.6,49.4)]
    key_points=[(33.85,46.0),(35.25,46.0),(36.55,47.45),(36.55,47.70),
                (35.05,49.2),(33.85,49.2)]
    slots=(cq.Workplane('XZ',origin=(0,length-2,0)).polyline(slot_points).close().extrude(length))
    key=(cq.Workplane('XZ',origin=(0,length-2.4,0)).polyline(key_points).close().extrude(length-2.8))
    lid=base.prism(77,length,4,49.2,2).translate((0,length/2,0))
    teeth=[]
    for sign in (-1,1):
        s=slots if sign==1 else slots.mirror('YZ')
        k=key if sign==1 else key.mirror('YZ')
        body=body.cut(s)
        # Ramped tooth and a wider receiving depression, both in the rail wall.
        tooth_outline=([(35.5,8.0),(36.55,8.0),(37.10,9.75),(37.10,10.25),(36.55,12.0),(35.5,12.0)]
                       if gentle_ramps else [(35.5,8.8),(37.10,9.75),(37.10,10.25),(35.5,11.2)])
        tooth=(cq.Workplane('XY',origin=(0,0,47.0)).polyline(tooth_outline)
            .close().extrude(1.0))
        recess_outline=([(35.3,7.7),(36.7,7.7),(37.25,9.5),(37.25,10.5),(36.7,12.3),(35.3,12.3)]
                        if gentle_ramps else [(36.3,8.5),(37.25,9.5),(37.25,10.5),(36.3,11.5)])
        recess=(cq.Workplane('XY',origin=(0,0,46.8)).polyline(recess_outline)
            .close().extrude(1.4))
        if sign==-1:tooth=tooth.mirror('YZ');recess=recess.mirror('YZ')
        lid=lid.union(k)
        teeth.append(tooth)
        track=base.box(sign*36.775,3,47.5,.95,8,1.4)
        body=body.cut(recess).cut(track)
    plain_lid=lid.clean()
    for tooth in teeth:lid=lid.union(tooth)
    return dict(kind='slide_wall',body=body.clean(),cap=lid.clean(),length=length,
                plain_body=outer.cut(inner),plain_cap=plain_lid,slots=slots)


def build(kind, d=D):
    validate(kind)
    if kind=='slide_wall':return slide(d.length)
    return tip_shell(kind,d)


def sample(kind):
    validate(kind)
    if kind=='slide_wall':
        parts=slide(70.)
        body=parts['body']
        cap=parts['cap'].rotate((0,35,51.2),(1,35,51.2),180).translate((110,0,-51.2))
        assembly=cq.Assembly(name='R4_slide_wall_test')
        assembly.add(body,name='body');assembly.add(cap,name='lid')
        return dict(**parts,result=assembly)
    parts=build(kind)
    bottom=D.seam-16
    crop=base.box(0,0,(bottom+D.seam+D.lap)/2,82,56,D.seam+D.lap-bottom)
    body=parts['body'].intersect(crop)
    assembly=cq.Assembly(name=kind+'_test')
    assembly.add(body.translate((0,0,-bottom)),name='body_joint')
    assembly.add(base.print_cap(parts['cap'],D.length),name='cap')
    return dict(**{k:v for k,v in parts.items() if k!='body'},body=body,
                body_bottom_mm=bottom,result=assembly)
