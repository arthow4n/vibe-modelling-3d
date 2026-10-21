"""Thinner T08-derived pairs; approval of T08 does not qualify smaller gaps."""
from functools import cache
from product_verification import (UserRequirement as U,UserSource as S,Question as Q,
    Plan,DesignDecision,Hypothesis,assertion_check,protect_recorded_intent)
import thin_gap_design as d
import thin_gap_checks as c
SOURCE='README.md#thinner-t08-follow-up'


def make_thin_gap_plan(name,original,root):
    v=d.variant_named(name)
    requirements=original+(
        U('thin_gap.pairs','Create one or two thinner T08-derived full test pairs for the existing box if ordinary slicing supports them.',
          S(SOURCE,'User approves T08 as new golden standard, rejects T16 as too firm/noisier, and requests one or two thinner variants considering line width for quick printing.')),
        U('thin_gap.finish','Preserve T08\'s improved appearance while exploring less occupied space.',
          S(SOURCE,'User reports T08 visually much better than B/S and asks how far thinner the T08 idea can go.')),
    )
    protect_recorded_intent(root,requirements)
    scope={'variant':name,'phase':'thinner-T08-air-gap','skin_mm':.8,'gap_mm':v.gap,'wall_mm':v.wall,
           'material':'TPU-uncalibrated','layer_mm':.2}
    @cache
    def parts():return c.parts(name)
    qs=(Q('fit','study.enclosure','Full cup/pad fits existing shell and insertion path.','CAD'),
        Q('skins','study.coverage','Floor, pad and four walls retain continuous skins, flat contents surfaces, solid corners and fully backed M1 IDs.','CAD'),
        Q('flat','study.flat','Expanded contents cavity has no protrusions.','CAD'),
        Q('both','study.two_skins','Both upright skins remain 0.8 mm.','CAD'),
        Q('core','study.variants','Short ties retain the declared open upright gap and unchanged horizontal post core.','CAD'),
        Q('paths','thin_gap.pairs','Delivered source/STEP/STL pair retains skins, air channel, ties, roof and legible label paths under Classic.','slicer'),
        Q('classic','support.classic','Actual supplied setup uses Classic and ordinary widths without recovery.','slicer'),
        Q('physical','thin_gap.pairs','Printed full pair survives installation and is usable.','physical'),
        Q('finish','thin_gap.finish','Printed appearance remains as good as T08.','physical'),
        Q('quiet','study.quiet_priority','Printed damping remains useful compared with approved T08.','physical'),
        Q('damping','surface.damping','Reduced gap does not bottom out or fuse in actual use.','physical'),
        Q('integrity','support.integrity','Skin/tie/corner integrity survives printing and insertion.','physical'),
        Q('compare','study.research','Compare with T08 in the same fixture, with larger contents width acknowledged.','physical'),
        Q('appearance','surface.finish','Compare seam/string artifacts and visible structure physically.','physical'))
    groups=(('thin-geometry',(('study.enclosure','fit'),('study.coverage','skins'),('study.flat','flat'),('study.two_skins','both'),('study.variants','core')),lambda:c.geometry(name,parts())),
            ('thin-publication',(('thin_gap.pairs','paths'),('support.classic','classic')),lambda:c.publication(name)))
    checks=tuple(assertion_check(i,t,f,'thin_gap_checks.py / thin_gap_design.py',scope) for i,t,f in groups)
    return Plan(name,requirements,scope,checks,(),questions=qs,
      decisions=(DesignDecision('keep-skins','Preserve approved T08 builder/exports, 0.8 mm skins, .8 mm ties, floor/pad and M1/corner construction. Reduce upright gap to .4/.2 mm, giving total 2.0/1.8 mm. Labels L20/L18 encode total wall, not skin.','notes/thin_gap/README.md'),),
      hypotheses=(Hypothesis('thin-limit','Keeping skins may retain visual hiding, but smaller gap reduces available cushioning stroke and may fuse. Sliced air is not physical clearance or a proven minimum.',SOURCE),))
