"""T08/T16 full-pair plan; retain historic user intent and physical unknowns."""
from functools import cache
from product_verification import (UserRequirement as U, UserSource as S, Question as Q,
    Plan, DesignDecision, Hypothesis, assertion_check, protect_recorded_intent, Check, Evidence, Status)
import t_skin_design as d
import t_skin_checks as c
SOURCE='README.md#t08t16-with-m1--2026-10-21'


def make_t_skin_plan(name,original,root):
    v=d.variant_named(name)
    requirements=original+(
        U('t_skin.pair','Provide T08/T16 complete cup/pad pairs for the existing test shell, with compact M1 markings.',
          S(SOURCE,'After choosing T08 and T16 as the next prints and reviewing marking SVGs, user asks to create the boxes with M1 to prepare for printing.')),
        U('t_skin.marking','Minimize marking footprint while keeping IDs visible and protecting the structure being tested.',
          S('notes/marking_options.md','User reports existing bottom text too big/deep and asks to preserve the functional skin; later selects M1 compact corner text.')),
        U('t_skin.corners','Keep corners solid for a reasonable distance to reduce corner print defects.',
          S('notes/surface_decoupling.md','User requests solid corner regions to avoid defects near corners; no numerical distance is specified.')),
    )
    protect_recorded_intent(root,requirements)
    scope={'variant':name,'phase':'full-T-skin-M1-pair','material':'TPU-uncalibrated',
           'wall_skin_mm':v.skin,'wall_gap_mm':.6,'floor_total_mm':1.6,'layer_mm':.2}
    @cache
    def parts(): return c.parts(name)
    questions=(
        Q('fit','study.enclosure','Full pair clears the established shell and pad insertion path; 0.2 mm squeeze is explicit.','CAD'),
        Q('skins','study.coverage','Continuous skins cover floor, pad and four walls.','CAD'),
        Q('flat','study.flat','The complete contents cavity has planar contact faces without marking protrusions.','CAD'),
        Q('both','study.two_skins','Both skins survive core/label subtraction.','CAD'),
        Q('ties','study.variants','Separated B-style ties and posts retain open core spaces.','CAD'),
        Q('corner','t_skin.corners','All wall channels stop 4 mm before tangent ends; floor and pad corners are solid.','CAD'),
        Q('label','t_skin.marking','Matching M1 IDs are recessed one layer and fully backed by local solid corners, outside the central floor.','CAD'),
        Q('pair','t_skin.pair','The delivered pair has current matching source/STEP/STL and reviewed wall, gap and label paths.','slicer'),
        Q('classic','support.classic','Actual supplied TPU process uses Classic at ordinary widths without thin-wall recovery.','slicer'),
        Q('physical','t_skin.pair','Print and install the full cup/pad without breakage; verify fit and readability.','physical'),
        Q('legible','t_skin.marking','Both compact IDs are visible on printed black TPU.','physical'),
        Q('corner-print','t_skin.corners','Solid corners print cleanly in the full cup.','physical'),
        Q('quiet','study.quiet_priority','Compare damping against approved B/S with the same nut and shell.','physical'),
        Q('finish','surface.finish','User compares object-facing appearance against approved B/S.','physical'),
        Q('artifacts','surface.finish','Characterize remaining seam/string artifacts separately.','physical'),
        Q('damping','surface.damping','Thicker upright skins retain useful damping.','physical'),
        Q('comparison','study.research','Compare T08/T16 physically with cavity-size difference explicit.','physical'),
        Q('installation','support.integrity','Insert and handle without tears or detached ties.','physical'),
    )
    groups=(
        ('t-fit',(('study.enclosure','fit'),),lambda:c.fit(name,parts())),
        ('t-skins',(('study.coverage','skins'),('study.flat','flat'),('study.two_skins','both')),lambda:c.skins(name,parts())),
        ('t-cores',(('study.variants','ties'),('t_skin.corners','corner')),lambda:c.cores(name,parts())),
        ('t-labels',(('t_skin.marking','label'),),lambda:c.labels(name,parts())),
        ('t-publication',(('t_skin.pair','pair'),('support.classic','classic')),lambda:c.publication(name)),
    )
    checks=tuple(assertion_check(id,targets,run,'t_skin_checks.py / t_skin_design.py',scope) for id,targets,run in groups)
    import json
    def damping_feedback():
        r=json.loads((root/'notes/t_skin/physical_feedback.json').read_text())[name]
        accepted=r['decision']=='approved-new-golden-standard'
        return (Evidence('t-physical-damping',(('study.quiet_priority','quiet'),('surface.damping','damping')),
            Status.PASS if accepted else Status.FAIL,
            'User approves T08 damping as equivalent to earlier approved models and calls it the golden standard.' if accepted else 'User rejects T16: too firm and somewhat noisier.',
            'notes/t_skin/physical_feedback.json',{**scope,'exact_print_settings':'unknown','reported_batch':'2f56b7c'}),)
    checks+=(Check('t-physical-damping',(('study.quiet_priority','quiet'),('surface.damping','damping')),damping_feedback),)
    if name=='T08':
        checks+=(Check('t-physical-finish',(('surface.finish','finish'),),lambda:(Evidence('t-physical-finish',
            (('surface.finish','finish'),),Status.PASS,'User reports T08 visually much better than approved B/S.',
            'notes/t_skin/physical_feedback.json',scope),)),)
    return Plan(name,requirements,scope,checks,(),questions=questions,
        decisions=(DesignDecision('full-pair','Retain 34 mm cup, B 1.6 mm horizontal sandwiches/.8 mm posts and .2 mm squeeze. Change upright skins to .8/1.6 around .6 gap; solid 4 mm wall-end lands and 10 x 6.5 mm floor/pad label corner seats. M1 strokes .8, .2 recess, widened .6 inter-glyph spacing within the accepted reserved footprint.',SOURCE),),
        hypotheses=(Hypothesis('guard-paths','Thicker skins may reduce joint marks; actual damping, finish, strength and readability remain physical.',SOURCE),))
