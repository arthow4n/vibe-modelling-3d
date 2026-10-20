"""Display-only cutaways of the four pairs; not printable exports."""
import cadquery as cq
import support_design as d
result = cq.Assembly(name='support_cutaways_display_only')
for i,name in enumerate(d.NAMES):
    v=d.variant_named(name)
    front=d.block(40,20,40,cy=-10)
    result.add(d.cup(name).cut(front),name=f'cut_cup_{name}',
               loc=cq.Location((i*42,0,0)))
    result.add(d.pad_print(name).cut(front),name=f'cut_pad_{name}',
               loc=cq.Location((i*42,42,0)))
