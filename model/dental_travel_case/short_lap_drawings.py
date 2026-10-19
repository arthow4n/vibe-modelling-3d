"""Actual-CAD sections explain the short guide, snap barrier and recovery track."""
import html
import json
import cairosvg
import short_lap_design as design
import short_lap_reinforced as refinement
import m1_design as base
from closure_research_drawings import canvas, label, section, BLUE, ORANGE, RED
from closure_research_checks import hashes
from short_lap_checks import OUT


def draw():
    p = refinement.build(refinement.SELECTED_OVERLAP)
    d = p['dimensions']
    items = canvas(f'Slim box: {d.lap:g} mm guide, small end-wall snaps',1190)
    label(items,25,78,'Actual CAD sections. Blue = body, orange = cap. No hinge or separate cantilever arms.',18)
    for i,(lift,title) in enumerate(((0,'Closed'),(d.lap+6,'Open: full mouth exposed'))):
        x0 = 130+i*220
        xf = lambda v,x0=x0:(x0+1.2*v.x,480-1.2*v.z)
        section(items,p['body'].val(),'XZ',(0,0,0),xf,BLUE)
        section(items,p['cap'].val().translate((0,0,lift)),'XZ',(0,0,0),xf,ORANGE)
        label(items,x0-90,520,title,17)
    label(items,25,559,f'Exterior: {d.length:g} × {d.width:g} × {d.depth:g} mm',18)
    label(items,25,590,f'Central mouth: {d.sleeve_width-2*d.sleeve_wall:g} × {d.sleeve_depth-2*d.sleeve_wall:g} mm',18)
    label(items,25,623,'Two parts; end snaps flex with the surrounding walls.',17)
    label(items,25,653,'Recessed pulling grips sit on the broad faces.',17)
    label(items,25,683,'Individual passage checked; loaded packing still needs a trial.',16)
    label(items,565,122,'One end catch — same scale in all three views',19)
    clip = base.box(d.width/2-1,0,d.latch_z-2,10,4,14).val()
    for i,(lift,title) in enumerate(((0,'Seated'),(1,'Against lip'),(6,'Past snap'))):
        x0 = 565+i*205
        xf = lambda v,x0=x0:(x0+20+16*(v.x-(d.width/2-4)),175+16*(d.latch_z+4-v.z))
        cap = p['cap'].val().translate((0,0,lift))
        section(items,p['body'].val().intersect(clip),'XZ',(0,0,0),xf,BLUE)
        section(items,cap.intersect(clip),'XZ',(0,0,0),xf,ORANGE)
        common = p['body'].val().intersect(cap)
        if common.Volume() > 1e-5:
            section(items,common.intersect(clip),'XZ',(0,0,0),xf,RED)
        label(items,x0,155,title,17)
        label(items,x0,405,f'Cap lift {lift:g} mm',16)
    label(items,560,455,'Red = blocked rigid geometry; real wall flex is needed.',17)
    label(items,560,485,'Body bends inward / cap spreads outward to cross the lip.',16)
    label(items,560,515,'Below the lip, a relief track lets the bump recover.',17)
    label(items,560,545,'The snap has cleared by the sampled 6 mm lift.',17)
    label(items,560,585,'A shorter overlap reduces guided sliding, but is not automatically',16)
    label(items,560,611,'easier or quieter: changed stiffness changes the snap.',16)
    label(items,560,643,'The cap still needs to clear the projecting brush head.',16)
    comparison = json.loads((OUT/'comparison.json').read_text())
    label(items,25,750,'Overlap tradeoff — conditional elastic model, not measured holding force',21)
    for x,text in ((25,'Lap'),(150,'Centered pull peak'),(400,'Ideal sudden-release threshold'),(750,'Worst roof play*')):
        label(items,x,788,text,17)
    for i,lap in enumerate(design.OVERLAPS):
        row = comparison['cases'][str(lap)]
        path = row['paths']['0.0']
        play = max([e['roof_center_lateral_motion_mm'] for axis in ('x','y') for e in row['guide'][axis]]+
                   [row['guide']['diagonal']['roof_center_lateral_motion_mm']])
        for x,text in ((25,f'{lap:g} mm'),(150,f'{path["peak_force_N"]:.1f} N'),
                       (400,f'{path["undamped_seated_release_force_N"]:.1f} N'),(750,f'{play:.2f} mm')):
            label(items,x,827+i*38,text,18)
    refined = json.loads((OUT/'refinement.json').read_text())
    path = refined['paths']['0.0']
    play = max([e['roof_center_lateral_motion_mm'] for axis in ('x','y') for e in refined['guide'][axis]]+
               [refined['guide']['diagonal']['roof_center_lateral_motion_mm']])
    label(items,25,950,f'First 24 mm refinement: {path["peak_force_N"]:.1f} N pull / {path["undamped_seated_release_force_N"]:.1f} N energy threshold / {play:.2f} mm roof play',18)
    final = json.loads((OUT/'reinforced.json').read_text())
    path = final['paths']['0.0']
    play = max([e['roof_center_lateral_motion_mm'] for axis in ('x','y') for e in final['guide'][axis]]+
               [final['guide']['diagonal']['roof_center_lateral_motion_mm']])
    label(items,25,988,f'Selected {d.lap:g} mm reinforced: {path["peak_force_N"]:.1f} N pull / {path["undamped_seated_release_force_N"]:.1f} N energy threshold / {play:.2f} mm roof play',19)
    label(items,25,1030,'*Guide-only rigid prescribed rocking; snaps omitted. Loaded stiffness and unrestricted peel are separate questions.',16)
    label(items,25,1064,'Force: E1200 MPa, nominal fit, two engaged catches, frictionless independent radial springs; full cap included.',16)
    label(items,25,1098,'Selected walls: 2 mm sleeve / 2.7 mm receiving band. Bump: 0.6 mm. Guide gap: 0.10 mm per side.',16)
    label(items,25,1140,'Printed force, snap recovery, noise, impact, creep and full-box retention remain physical checks.',17)
    metadata = hashes(('short_lap_drawings.py','short_lap_design.py','closure_research_design.py',
                       'short_lap_refinement.py','short_lap_reinforced.py','m1_design.py','closure_research_drawings.py',
                       'notes/short_lap/comparison.json','notes/short_lap/refinement.json','notes/short_lap/reinforced.json'))
    items.append('<metadata>'+html.escape(json.dumps(metadata))+'</metadata></svg>')
    path = OUT/'sections.svg'
    path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


if __name__ == '__main__':
    draw()
