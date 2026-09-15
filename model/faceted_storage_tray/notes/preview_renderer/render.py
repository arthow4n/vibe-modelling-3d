"""Orthographic shaded STL preview with a depth buffer; no mesh changes."""
from pathlib import Path
import numpy as np
from PIL import Image
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--input",type=Path)
parser.add_argument("--output",type=Path)
parser.add_argument("--view",choices=["iso","front"],default="iso")
args = parser.parse_args()

root = Path(__file__).resolve().parents[2]
dtype = np.dtype([('normal','<f4',(3,)), ('vertices','<f4',(3,3)), ('attribute','<u2')])
data = np.fromfile(args.input or root/'faceted_storage_tray.stl', dtype=dtype, offset=84)
triangles = data['vertices'].astype(float)
normals = np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
normals /= np.linalg.norm(normals,axis=1)[:,None]
light = np.array([-0.6,-0.7,1.0]); light /= np.linalg.norm(light)
fill = np.array([1.0,0.2,0.7]); fill /= np.linalg.norm(fill)
brightness = 0.30+0.42*np.maximum(0,normals@light)+0.30*np.maximum(0,normals@fill)
colors = (255*brightness[:,None]*np.array([0.83,0.87,0.91])).astype(np.uint8)
view = np.array([1.,-1.4,0.8] if args.view=="iso" else [0.,-1.,0.]); view /= np.linalg.norm(view)
right = np.cross([0,0,1],view); right /= np.linalg.norm(right)
up = np.cross(view,right)
projected = triangles @ np.array([right,-up,view]).T
lo = projected[:,:,:2].min(axis=(0,1)); hi = projected[:,:,:2].max(axis=(0,1))
scale = 1300/(hi-lo).max()
projected[:,:,:2] = (projected[:,:,:2]-lo)*scale+45
width,height = np.ceil((hi-lo)*scale+90).astype(int)
pixels = np.full((height,width,3),255,dtype=np.uint8)
depth = np.full((height,width),-np.inf)
for triangle,color in zip(projected,colors):
    x0,y0 = np.maximum(0,np.floor(triangle[:,:2].min(axis=0)).astype(int))
    x1,y1 = np.minimum([width-1,height-1],np.ceil(triangle[:,:2].max(axis=0)).astype(int))
    x,y = np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
    a,b,c = triangle
    den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-10:
        continue
    u = ((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
    v = ((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
    w = 1-u-v
    z = u*a[2]+v*b[2]+w*c[2]
    region = depth[y0:y1+1,x0:x1+1]
    mask = (u>=-1e-8)&(v>=-1e-8)&(w>=-1e-8)&(z>region)
    region[mask] = z[mask]
    pixels[y0:y1+1,x0:x1+1][mask] = color
Image.fromarray(pixels).save(args.output or root/'renders/print/shaded_preview.png')
