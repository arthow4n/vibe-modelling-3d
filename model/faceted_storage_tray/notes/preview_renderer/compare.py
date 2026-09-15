"""Render actual exported alternatives with identical lighting, then label a sheet."""
from pathlib import Path
import json
import subprocess
import sys
from PIL import Image,ImageDraw,ImageFont,ImageOps
root = Path(__file__).resolve().parents[2]
configs = json.loads((root/'notes/variants.json').read_text())
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font = ImageFont.truetype(font_path,22)
small = ImageFont.truetype(font_path,17)
sheet = Image.new('RGB',(1500,2220),'#eeeeeb')
draw = ImageDraw.Draw(sheet)
draw.text((30,16),'FACET EXPLORATION  |  Same 220 mm interior, eight exterior patterns',fill='#222222',font=font)
for index,config in enumerate(configs):
    name = config['name']; folder = root/'variants'/name
    for view in ['iso','front']:
        subprocess.run([sys.executable,str(Path(__file__).with_name('render.py')),
                        '--input',str(folder/(name+'.stl')),'--output',str(folder/(view+'.png')),
                        '--view',view],check=True)
    x,y = 20+(index%2)*745,65+(index//2)*535
    draw.rounded_rectangle((x,y,x+725,y+515),radius=12,fill='white')
    title = name.replace('_',' ').upper()
    width = 164/config['panels']
    draw.text((x+18,y+12),title,fill='#222222',font=font)
    text = f"{config['panels']}/side | {width:.1f} x 27 mm | {config['relief']:.1f} mm relief"
    if config['ridge']:
        text += ' | long ridge'
    draw.text((x+18,y+44),text,fill='#555555',font=small)
    for view,box,offset in [('iso',(685,330),(20,73)),('front',(685,105),(20,399))]:
        im = ImageOps.contain(Image.open(folder/(view+'.png')),box)
        sheet.paste(im,(x+offset[0]+(box[0]-im.width)//2,y+offset[1]+(box[1]-im.height)//2))
    print('Rendered',name,flush=True)
sheet.save(root/'renders/print/comparison.png')
