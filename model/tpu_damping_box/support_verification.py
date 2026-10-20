"""Four-pair phase: CAD/path evidence never clears physical installation or noise."""
from functools import cache
from product_verification import (UserRequirement as U, UserSource as S, Question as Q,
    Plan, DesignDecision, Hypothesis, assertion_check, protect_recorded_intent)
import support_design as d
import support_checks as c

SOURCE='README.md#four-printable-support-pairs--2026-10-20'


def make_support_plan(name, original_requirements, root):
    v=d.variant_named(name)
    requirements=original_requirements
    protect_recorded_intent(root,requirements)
    scope={'variant':name,'phase':'four-complete-support-pairs','material':'TPU-uncalibrated',
           'layer_mm':.2,'wall_generator':'classic','total_mm':v.thickness}
    @cache
    def parts():
        return c.parts(name)
    questions=(
        Q('fit','study.enclosure','Existing 34 mm cup envelope and pad pocket clear installation/removal; intentional 0.2 mm pad squeeze is explicit.','CAD'),
        Q('skins','study.coverage','Both skins cover floor, roof and all walls; the full clear cavity is free of protrusions.','CAD'),
        Q('flat','study.flat','Contact planes remain flat and labeling is confined to exterior recesses.','CAD'),
        Q('both','study.two_skins','Continuous outside and contact skins survive CAD core subtraction.','CAD'),
        Q('cores','study.variants','A retains open frame interiors; B retains separated ties, and all designs retain air channels and corner voids.','CAD'),
        Q('labels','support.four','Both parts have matching large recessed IDs, with declared geometry and thickness selection.','CAD'),
        Q('classic','support.classic','The actual slice effective settings record Classic for each delivered pair.','slicer'),
        Q('paths','support.four','Current paired exports and Classic slices retain thin skins, open cores, supports and legible label paths.','slicer'),
        Q('installation','support.integrity','Print and insert/remove each full cup/pad; reject tears, splits or support detachment.','physical'),
        Q('quietness','study.quiet_priority','Compare quietness against printed S16 in the same shell with the same nut and handling.','physical'),
        Q('comparison','study.research','User compares the four support pairs; cavity size and process differences remain explicit.','physical'),
        Q('finish','surface.finish','The separate F0–F7 finish study remains untested; this phase does not settle surface waviness.','physical'),
        Q('damping','surface.damping','New support geometry retains useful damping in a physical comparison.','physical'),
    )
    groups=(
        ('support-fit',(('study.enclosure','fit'),),lambda:c.fit(name,parts())),
        ('support-skins',(('study.coverage','skins'),('study.flat','flat'),('study.two_skins','both')),lambda:c.skins(name,parts())),
        ('support-cores',(('study.variants','cores'),),lambda:c.cores(name,parts())),
        ('support-labels',(('support.four','labels'),),lambda:c.labels(name,parts())),
        ('support-classic',(('support.classic','classic'),),lambda:c.classic(name)),
        ('support-publication',(('support.four','paths'),),lambda:c.publication(name)),
    )
    checks=tuple(assertion_check(id,targets,run,'support_checks.py / support_design.py',scope)
                 for id,targets,run in groups)
    return Plan(name,requirements,scope,checks,(),questions=questions,
        decisions=(DesignDecision('support-sizes',
            'A: .3 mm upright skins/parallel rails, .6 mm cross-links and .4 mm horizontal skins, square internal openings .4/.8 mm. B: .8/.1.6 mm ties at identical 4.4 mm pitch in length and height. Both retain explicit CAD voids. Pads add .2 mm axial squeeze on a whole-layer grid.',SOURCE),),
        hypotheses=(Hypothesis('integrity-damping',
            'Frames may improve continuous routing; short ties may reduce solid core volume. Neither routing, printed bonding nor useful damping follows from geometry or slicer acceptance.',SOURCE),))
