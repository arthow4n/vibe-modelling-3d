"""Explain retained side-push evidence in SVG; never build CAD or launch a solve."""
import html
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import cairosvg

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'
NS = 'http://www.w3.org/2000/svg'
BLUE, ORANGE, INK = '#4187b5', '#e49b43', '#172b3a'


def text(x, y, value, size=19, color=INK, weight='normal'):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}">{html.escape(value)}</text>')


def rect(x, y, w, h, fill='white', stroke='#d6e0e7', radius=16):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def arrow(x1, y1, x2, y2, color=ORANGE):
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="4" marker-end="url(#push)"/>'


def page(title, subtitle, height):
    return [f'<svg xmlns="{NS}" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img">',
        '<title>'+html.escape(title)+'</title>',
        '<desc>'+html.escape(subtitle)+'</desc>',
        '<defs><marker id="push" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="#e49b43"/></marker></defs>',
        '<g font-family="DejaVu Sans, sans-serif">',rect(0,0,1200,height,'#f3f6f8',radius=0),
        text(35,52,title,32,weight='bold'),text(35,88,subtitle,18)]


def save(name, items, inputs):
    metadata = dict(source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        for name in ['short_lap_explained.py',*inputs]},
        scope='Explanatory diagrams from retained evidence; no new simulation or physical test.')
    items += ['</g>','<metadata>'+html.escape(json.dumps(metadata))+'</metadata>','</svg>']
    path = OUT/(name+'.svg')
    content = '\n'.join(items)
    path.write_text('\n'.join(line.rstrip() for line in content.splitlines())+'\n')
    ET.parse(path)
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))
    print(path,flush=True)


def test_map(push):
    items = page('What was actually tried on the dental box',
        'Computer studies of steady pushes and rocking. No physical knocks or impact simulation were performed.',1210)
    items += [rect(35,120,545,450),rect(600,120,565,450),
        text(60,157,'1  Where the computer pushed',23,weight='bold'),
        text(625,157,'2  Which directions were studied',23,weight='bold')]
    # Schematic full profile. The solved body is cropped 16 mm below the seam.
    items += [rect(135,220,90,280,'#edf4f9',BLUE,12),
        rect(135,220,90,96,'#fae7cc',ORANGE,12),
        '<rect x="142" y="284" width="76" height="32" fill="none" stroke="#4187b5" stroke-width="3" stroke-dasharray="6 4"/>',
        '<path d="M130,316 H230" stroke="#172b3a" stroke-width="2"/>',
        '<rect x="112" y="330" width="136" height="10" fill="#617581"/>',
        '<rect x="130" y="341" width="100" height="165" fill="#f3f6f8" opacity=".8"/>',
        arrow(60,235,128,235),text(60,207,'Side push',17),
        text(270,238,'Lid / cap',21,ORANGE,'bold'),text(270,268,'90 mm from seam to tip',17),
        text(270,302,'30 mm overlap',19,BLUE,'bold'),
        text(270,338,'Body held here',19,weight='bold'),
        text(270,366,'16 mm below the seam',17),
        text(65,465,'Faded lower body: omitted from this contact model.',16),
        text(65,501,'The lid could lift as it moved sideways.',18),
        text(65,536,'Simplified drawing; contents and inertia were omitted.',16)]
    # Top view of the sleeve and cap: single positive X/Y loading directions.
    items += [text(625,192,'Looking down the long axis (schematic)',17),
        rect(790,262,165,114,'#fae7cc',ORANGE,25),
        rect(802,274,141,90,'#edf4f9',BLUE,21),
        rect(796,311,12,17,BLUE,BLUE,2),rect(937,311,12,17,BLUE,BLUE,2),
        arrow(658,319,777,319),text(625,248,'Widthwise / end push (X)',18),
        arrow(872,205,872,251),text(975,238,'Broad-face',18),text(975,263,'push (Y)',18),
        text(805,410,'Two end catches',19,BLUE,'bold'),
        text(625,458,'Only centered +X and +Y were driven.',18),
        text(625,489,'Mirror-half models reduced the calculation.',17),
        text(625,532,'No diagonal or corner impact was simulated.',17)]
    items += [rect(35,595,1130,355),text(60,634,'3  What each study actually tells us',23,weight='bold')]
    rows = [
        ('Rigid rocking (CAD)', 'Both rocking axes, with small initial side shifts.', 'Shows which tooth or guide touches first; says nothing about hit strength.'),
        ('Widthwise steady push', f'{push["full_fixture_signed_lateral_reaction_N"]:.2f} N ≈ holding {push["full_fixture_signed_lateral_reaction_N"]/9.80665:.2f} kg.', 'One catch nearly clear; the other still catches. See the second diagram.'),
        ('Broad-face steady push', 'Last complete frame: about 0.003 N, mostly taking up play.', 'Higher-load output was incomplete, so it gives no useful force rating.'),
        ('Earlier simplified checks', '2 N side-bearing stiffness; about 11.2 N centered pull estimate.', 'Different load cases and assumptions; these were not sideways knock tests.'),
        ('Different solver setups', 'Full / half model, seating first, shifted cap, coarser steps.', 'These are calculation attempts, not extra knocks that the box survived.'),
    ]
    for i,(name,description,meaning) in enumerate(rows):
        y = 676+i*57
        items += [text(60,y,name,18,weight='bold'),text(330,y,description,17),text(330,y+24,meaning,16,'#526573')]
    items += [rect(35,975,550,190,'#fff3dd','#efc477'),rect(605,975,560,190,'#eaf1f7'),
        text(60,1013,'Still untested',22,weight='bold'),
        text(60,1048,'Actual bag knocks • impact timing • corners',18),
        text(60,1080,'Return to fully latched after a side push',18),
        text(60,1112,'Printed material, friction and loaded contents',18),
        text(630,1013,'Practical decision now',22,weight='bold'),
        text(630,1048,'Keep the existing 30 mm prototype.',19),
        text(630,1080,'This numerical branch is finished.',18),
        text(630,1112,'Reopen for evidence that can change the design.',17)]
    save('sideways_test_map',items,['short_lap_lateral.py','notes/short_lap/rocking.json',
        'notes/short_lap/lateral_capture_seated_x_0.2.json','notes/short_lap/lateral_capture_seated_y_0.14.json',
        'notes/short_lap/reinforced.json','notes/short_lap/reinforced_side.json'])


def result(push, baseline):
    force = push['full_fixture_signed_lateral_reaction_N']
    items = page('What the sideways-push result means',
        'One complete simulation snapshot. Remaining catch geometry is shown; impact strength is untested.',1100)
    items += [rect(35,120,1130,126,'#eaf1f7'),
        text(60,162,f'{force:.1f} N ≈ the force needed to hold up {force/9.80665:.2f} kg',27,weight='bold'),
        text(60,198,'Imagine holding the body steady and pushing the far end of the lid sideways.',19),
        text(60,226,f'The lid tip moved {push["roof_drive_mm"]:.2f} mm sideways and rose about {push["snapshot_quality"]["observations"]["roof"]["mean_mm"][2]:.2f} mm on average in this model.',17)]
    # Reuse the actual deformed native section. Remove its technical supertitle,
    # retain geometry, axis scale, body/cap colors and both catch zooms unchanged.
    ET.register_namespace('',NS)
    ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
    native = ET.parse(OUT/'lateral_seated_x_0.2.svg').getroot()
    figure = native.find(f'.//{{{NS}}}g[@id="figure_1"]')
    title = figure.find(f'{{{NS}}}g[@id="text_43"]')
    if title is None:
        raise ValueError('Expected retained figure title; inspect changed drawing before reuse')
    figure.remove(title)
    # Cover only the original title band; keep its glyph definitions available.
    ET.SubElement(native,f'{{{NS}}}rect',x='0',y='85',width='864',height='16',fill='white')
    for x,label in ((212,'Full lid + held body section'),(515,'Left catch (−X)'),(754,'Right catch (+X)')):
        node = ET.SubElement(native,f'{{{NS}}}text',x=str(x),y='97',
            attrib={'text-anchor':'middle','font-family':'DejaVu Sans','font-size':'11.5'})
        node.text = label
    native.attrib.update(x='35',y='267',width='1130',height='454',viewBox='0 85 864 347')
    items += [ET.tostring(native,encoding='unicode'),
        text(60,749,'Blue = body and teeth. Orange = lid. This is the actual simulated shape; catch views are magnified.',17),
        rect(35,775,1130,250),text(60,811,'How much extra inward movement would let each tooth pass?',22,weight='bold'),
        text(60,842,'Longer bar = more remaining capture in this fixed shape. All bars use the same scale.',17)]
    values = [('Before pushing (one catch)',baseline['catches']['-1']['extra_retraction_above_current_contact_mm'],BLUE),
        ('After pushing: left catch',push['catches']['-1']['extra_retraction_above_current_contact_mm'],ORANGE),
        ('After pushing: right catch',push['catches']['1']['extra_retraction_above_current_contact_mm'],'#34798a')]
    for i,(name,value,color) in enumerate(values):
        y = 865+45*i
        items += [text(60,y+20,name,18),rect(390,y,600,25,'#e7edf1','none',4),
            rect(390,y,600*value/.55,25,color,'none',4),text(1010,y+20,f'{value:.3f} mm',18,weight='bold')]
    items += [text(60,1060,'Almost no capture remains on the left. The right still catches; complete opening and return were not established.',17),
        text(60,1086,'Sampled geometric clearance, about 0.01 mm radial resolution. No mesh/contact sensitivity or printed validation.',15,'#526573')]
    save('sideways_result_explained',items,['notes/short_lap/lateral_capture_seated_x_0.2.json',
        'notes/short_lap/lateral_capture_seated_x_0.02.json','notes/short_lap/lateral_seated_x_0.2.svg'])


def main():
    push = json.loads((OUT/'lateral_capture_seated_x_0.2.json').read_text())
    baseline = json.loads((OUT/'lateral_capture_seated_x_0.02.json').read_text())
    test_map(push)
    result(push,baseline)


if __name__ == '__main__':
    main()
