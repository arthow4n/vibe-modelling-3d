"""Shared D/E/F user intent; CAD motion is distinct from physical retention."""
from pathlib import Path
from product_verification import (UserRequirement as U, UserSource as S, Question as Q,
                                  Plan, assertion_check, cli, protect_recorded_intent)
ROOT=Path(__file__).resolve().parent
SOURCE='notes/hand_lock_decisions.md#user-correction-and-authorized-phase'
REQUIREMENTS=(
    U('connector.material','Every supplied connector component is printed in PLA or PETG, without metal or a spring-dependent gate',
      S(SOURCE,'Ditch all other materials; hand-openable connector, originally rigid PLA/PETG without spring/bending dependency')),
    U('connector.operation','Either end opens by hand without winding or turning the attached loop',
      S(SOURCE,'Connect cord and existing key ring; easy independent removal, now explicitly hand-operated')),
    U('connector.retention','Both closed ends should resist shaking off in normal use',
      S(SOURCE,'Smartly opened by hand but does not easily shake off')),
)
QUESTIONS=(
    Q('rigid','connector.material','CAD uses discrete rigid moving parts and solid printed screw cores; material behavior is not assumed calibrated','CAD'),
    Q('path','connector.operation','Sampled intended gate motion clears the body; other end remains bridged and nominal loading mouth clears a cord-section witness','CAD'),
    Q('assembly','connector.operation','Proposed frame approach is clear at sampled offsets and screws fit without forbidden overlap','CAD'),
    Q('hand','connector.operation','Complete printed connector can actually be assembled and operated comfortably by hand','physical'),
    Q('obstruction','connector.retention','Closed geometry obstructs a direct non-operating pull','CAD'),
    Q('shake','connector.retention','Printed connector stays closed under unloaded shaking, key rubbing and normal use','physical'),
)


def make_plan(variant):
    if variant!='D':raise ValueError(variant)
    protect_recorded_intent(ROOT,REQUIREMENTS)
    from d_checks import check_motion, check_assembly
    scope={'variant':variant,'phase':'unprinted mechanism prototype','material':'PLA-or-PETG-unqualified'}
    checks=(
        assertion_check('D.motion',(('connector.operation','path'),('connector.retention','obstruction')),
                        check_motion,'d_checks.py#check_motion',scope),
        assertion_check('D.assembly',(('connector.operation','assembly'),('connector.material','rigid')),
                        check_assembly,'d_checks.py#check_assembly',scope),
    )
    return Plan(variant,REQUIREMENTS,scope,checks,questions=QUESTIONS)


if __name__=='__main__':
    raise SystemExit(cli(make_plan,('D',)))
