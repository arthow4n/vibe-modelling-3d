"""Explicit variant coverage; preserve reported I success within its PLA scope."""
from functools import cache
from pathlib import Path
from product_verification import (UserRequirement as U, UserSource as S, Question as Q,
    Plan, DesignDecision, Hypothesis, Directive, assertion_check, cli, protect_recorded_intent, Check, Evidence, Status)

ROOT = Path(__file__).resolve().parent
SOURCE = 'README.md#user-intent'
REQUIREMENTS = (
    U('study.enclosure','One small closable PETG enclosure accepts interchangeable separately printed TPU liners and a loose metal nut.',
      S(SOURCE,'User requests one small PETG exterior, closable, with TPU inserts and space to shake a stock metal nut.')),
    U('study.coverage','The floor, ceiling and all four interior walls have TPU damping coverage.',
      S(SOURCE,'User explicitly requires damping on the bottom, top, and all four walls.')),
    U('study.flat','All object-contact interior faces are flat; damping structures are inside the liner.',
      S(SOURCE,'User clarification: the interior needs to be flat for the objects, while the liner may have structures inside.')),
    U('study.variants','Several permanently labeled CAD-defined internal damping configurations can be printed together.',
      S(SOURCE,'User asks for labeled variants, explicit CAD structures rather than infill, and a batch print; additional variants are welcome.')),
    U('study.research','Use research to inform a reusable damping experiment and compare variants by shaking the same metal nut.',
      S(SOURCE,'User requests research on effective damping structures and plans to report which liner performs best.')),
    U('study.quiet_priority','Prioritize maximum quietness in a thin liner and recommend a focused print batch with a solid control and the most promising candidates.',
      S(SOURCE,'User follow-up: maximize quietness while keeping it thin; provide a STEP set focused on more confident candidates and retain control A.')),
)
QUESTIONS = (
    Q('fit','study.enclosure','Cup and pad fit the actual shell and each other; one 12 mm proxy can travel 14 mm on each axis inside the 26 mm clear cavity.', 'CAD'),
    Q('closure','study.enclosure','Two M3 nut installation paths clear and nuts bear under solid pocket roofs; screw bores clear a 3 mm shaft.', 'CAD'),
    Q('handling','study.enclosure','Printed cup/pad can be swapped and the screw closure stays tight during shaking.', 'physical'),
    Q('six-skins','study.coverage','Continuous minimum 0.6 mm TPU witnesses cover every face of the shaking cavity.', 'CAD'),
    Q('flat-faces','study.flat','The full 26 mm cubic shaking space is free of protrusions, with planar TPU at all six boundaries.', 'CAD'),
    Q('cores','study.variants','Structured variants retain explicit air channels behind floor, ceiling and four side skins; control A is intentionally solid.', 'CAD'),
    Q('labels','study.variants','A 6 mm exterior recessed letter is present on both cup and pad, and the selected batch names each matching cup/pad pair.', 'CAD'),
    Q('printed-labels','study.variants','Letters remain readable and flat skins/hidden bridges print intact.', 'physical'),
    Q('selected-layout','study.quiet_priority','Recommended plate contains exactly A, E, H and I, one cup/pad pair each, excluding lower-priority designs.', 'CAD'),
    Q('compliance','study.quiet_priority','An input-associated linear web screen characterizes H/I relative to E, including lateral-end sensitivity, without acoustic promotion.', 'analytical'),
    Q('quiet-winner','study.quiet_priority','A user shake comparison establishes acceptable quietness; predicted compliance is not acoustic evidence.', 'physical'),
    Q('noise','study.research','User compares repeated directional nut shaking and identifies quieter usable configurations.', 'physical'),
    Q('reported-comparison','study.research','User reports subjective damping differences among printed A/E/H/I in the actual shell material.', 'physical'),
)


def compliance_evidence(scope):
    import json
    from execution.identity import digest
    path=ROOT/'notes/compliance_screen.json'
    status=Status.UNKNOWN
    message='Missing or stale compliance screen; quietness remains physical.'
    if path.exists():
        r=json.loads(path.read_text())
        expected=('design.py','compliance_screen.py')
        if set(r['source_sha256'])==set(expected) and all(digest(ROOT/n)==r['source_sha256'][n] for n in expected):
            rows=r['results']
            valid=(r['category']=='analytical-initial-compliance-screen' and
              r['relative_refinement_limit']==.005 and
              all(rows[n]['relative_to_E'] > 0 and rows[n]['relative_64_128_change'] < .005 for n in ('H','I')) and
              0 < rows['I']['relative_to_E'] < 1 and 0 < rows['I']['tangential_free_relative_to_E'] < 1)
            status=Status.PASS if valid else Status.FAIL
            message='Input-associated isolated-web linear screen: I below E; H approximately E; lateral-restraint sensitivity retained. Omits skins, corners, nonlinear TPU, impact and acoustics.'
    return (Evidence('compliance',(('study.quiet_priority','compliance'),),status,message,'notes/compliance_screen.json',scope),)


def physical_feedback(variant):
    """A letter association is not an exact print hash or a TPU calibration."""
    import json
    from execution.identity import digest
    r=json.loads((ROOT/'notes/physical_feedback_2026_10_16.json').read_text())
    if variant not in r['observations'] or not all(digest(ROOT/n)==r['source_sha256'][n] for n in ('design.py','selection.py')):
        return ()
    scope={'revision':'quiet-selection-r2','variant':variant,'shell':'PLA','liner':'TPU-hardness-unknown'}
    evidence=[Evidence('user-comparison',(('study.research','reported-comparison'),),Status.PASS,
        r['observations'][variant]+' Subjective user comparison; exact files/settings unknown.',r['reference'],scope)]
    if variant=='I':
        evidence.append(Evidence('user-approval',(('study.quiet_priority','quiet-winner'),),Status.PASS,
            'I explicitly approved, much quieter than E/H in the reported PLA shell.',r['reference'],scope))
    return tuple(evidence)


def thin_plan(variant):
    import thin_checks as c
    import thin_design as d
    d.variant_named(variant)
    protect_recorded_intent(ROOT,REQUIREMENTS)
    scope={'revision':'thin-I-r3','variant':variant,'shell':'PLA-reused','liner':'TPU95A-assumed-unprinted'}
    @cache
    def parts():
        return c.candidate(variant)
    questions=(
        Q('fit','study.enclosure','Cup/pad clear the existing shell, each other and installation travel; expanded flat cavity admits a moving 12 mm nut proxy.','CAD'),
        Q('handling','study.enclosure','Printed pair swaps, seats and stays retained during shaking.','physical'),
        Q('six-skins','study.coverage','Six continuous flat skins retain the declared 0.4 or 0.6 mm thickness.','CAD'),
        Q('flat-faces','study.flat','The expanded cubic shaking cavity is free of protrusions.','CAD'),
        Q('cores','study.variants','Air channels and chevron material remain behind all six faces.','CAD'),
        Q('labels','study.variants','Both parts bear matching recessed I30/I24/I20 labels with material above the recess.','CAD'),
        Q('printed-labels','study.variants','Labels remain readable, thin skins and web bridges print intact.','physical'),
        Q('thin-selection','study.quiet_priority','One batch contains exactly three I-derived pairs at 3.0, 2.4 and 2.0 mm, 25/40/50 percent thinner than approved I.','CAD'),
        Q('quiet-winner','study.quiet_priority','User compares against approved 4 mm I and finds an acceptable thickness/quietness tradeoff.','physical'),
        Q('noise','study.research','Same-shell/nut comparison includes shake intensity and axis; larger cavity is acknowledged.','physical'),
    )
    groups=(
        ('fit',(('study.enclosure','fit'),),lambda:c.fit(variant,parts())),
        ('skins',(('study.coverage','six-skins'),('study.flat','flat-faces')),lambda:c.skins(variant,parts())),
        ('cores',(('study.variants','cores'),),lambda:c.cores(variant,parts())),
        ('labels',(('study.variants','labels'),),lambda:c.labels(variant,parts())),
        ('thin-selection',(('study.quiet_priority','thin-selection'),),c.selection),
    )
    checks=tuple(assertion_check(id,targets,run,'thin_checks.py / thin_design.py',scope) for id,targets,run in groups)
    return Plan(variant,REQUIREMENTS,scope,checks,(),questions=questions,
        decisions=(DesignDecision('thickness-ladder','Reuse outer 34 mm cup and existing shell; expand cavity instead of adding rigid fillers. Thin skins and webs; retain I centreline slope and pitch.','README.md#thinner-i-experiment'),),
        hypotheses=(Hypothesis('thin-quietness','Reduced core stroke may cause bottoming; shorter webs can stiffen despite thinner sections. Original I approval does not transfer.','README.md#thinner-i-experiment'),),
        directives=(Directive('approved-I-thinning','Preserve approved I; deliver three much thinner derivatives for printing.',S('README.md#user-print-feedback--2026-10-16','User reports I much more damping, explicitly approves it, and requests two or three much thinner I variants.')),))


def make_plan(variant):
    if variant in ('I30','I24','I20'):
        return thin_plan(variant)
    if variant not in tuple("ABCDEFGHI"):
        raise ValueError(variant)
    import checks as c
    protect_recorded_intent(ROOT,REQUIREMENTS)
    scope={'revision':'quiet-selection-r2','variant':variant,'shell':'PLA' if variant in ('A','E','H','I') else 'PETG-unprinted','liner':'TPU-hardness-unknown'}
    @cache
    def parts():
        return c.candidate(variant)
    groups=(
        ('fit',(('study.enclosure','fit'),),lambda:c.fit_checks(parts())),
        ('closure',(('study.enclosure','closure'),),lambda:c.closure_checks(parts()[0])),
        ('skins',(('study.coverage','six-skins'),('study.flat','flat-faces')),lambda:c.skin_checks(parts())),
        ('cores',(('study.variants','cores'),),lambda:c.core_checks(variant,parts())),
        ('labels',(('study.variants','labels'),),lambda:c.label_checks(variant,parts())),
        ('selected-layout',(('study.quiet_priority','selected-layout'),),c.selection_checks),
    )
    checks=tuple(assertion_check(id,targets,run,'checks.py / design.py / selection.py',scope) for id,targets,run in groups)
    checks += (Check('compliance', (('study.quiet_priority','compliance'),), lambda: compliance_evidence(scope)),)
    return Plan(variant,REQUIREMENTS,scope,checks,physical_feedback(variant),questions=QUESTIONS,
      decisions=(DesignDecision('core-scale','4 mm liner sandwich with 0.8 mm outer backing; 0.8 mm inner skin except F/G/H/I at 0.6 mm. Same 26 mm cavity.', 'README.md'),),
      hypotheses=(Hypothesis('quietness','Thinner or bending-biased webs may reduce impact transmission, but small nut impacts may not activate buckling; skins, corners and printing may dominate.', 'README.md#research'),))


if __name__=='__main__':
    raise SystemExit(cli(make_plan,('A','B','C','D','E','F','G','H','I','I30','I24','I20')))
