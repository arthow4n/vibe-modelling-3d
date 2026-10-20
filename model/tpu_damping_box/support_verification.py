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
    scope={'variant':name,'phase':'four-complete-support-pairs-R2','material':'TPU-uncalibrated',
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
        Q('repo-default','support.repo_defaults','The exact repository default Classic process generates both skins on every upright layer of each corrected layout; its PETG diagnostic material is not a TPU print recipe.','slicer'),
        Q('ordinary','support.ordinary','Every upright layer retains both wall skins in ordinary Classic; thin-wall detection is disabled, and the original batch is a failing control.','slicer'),
        Q('classic','support.classic','The actual slice uses Classic with thin-wall detection OFF and ordinary 0.42/0.45 mm widths.','slicer'),
        Q('paths','support.four','Current paired exports and ordinary Classic slices retain wall skins on every upright layer, open cores, supports and legible R2 label paths; the rejected batch fails the control.','slicer'),
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
        ('support-repo-default',(('support.repo_defaults','repo-default'),),lambda:c.repo_default(name)),
        ('support-publication',(('support.four','paths'),('support.ordinary','ordinary')),lambda:c.publication(name)),
    )
    checks=tuple(assertion_check(id,targets,run,'support_checks.py / support_design.py',scope)
                 for id,targets,run in groups)
    return Plan(name,requirements,scope,checks,(),questions=questions,
        decisions=(DesignDecision('support-sizes',
            'R2: .5 mm continuous upright skins on all four variants; A locally thickens each skin to .7 mm around .2/.6 mm square openings, with .6 mm cross-links. Horizontal A webs are .5 mm wide. B retains .8/1.6 mm ties, now across a .6 mm wall gap. Common ordinary Classic .42/.45 mm widths, thin-wall detection off, same 4.4 mm pitch. Both retain explicit CAD voids. Pads add .2 mm axial squeeze on a whole-layer grid.',SOURCE),),
        hypotheses=(Hypothesis('integrity-damping',
            'Frames may improve continuous routing; short ties may reduce solid core volume. Neither routing, printed bonding nor useful damping follows from geometry or slicer acceptance.',SOURCE),))
