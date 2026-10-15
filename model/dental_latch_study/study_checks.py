"""Local geometry questions only; run with ./execute.py from repository root."""
from design import F, baseline, block, components, flat_leaf, m1


def overlap(a, b):
    return a.intersect(b).val().Volume()


def check_pair(name, male, keeper, withdrawal, released):
    tolerance = 1e-6  # mm³ Boolean noise, not a manufacturing tolerance
    assert overlap(male, keeper) < tolerance, name+": seated interference"
    obstruction = overlap(male, keeper.translate(withdrawal))
    assert obstruction > .001, name+": missing positive shoulder"
    assert overlap(released, keeper) < tolerance, name+": pressed interference"
    for step in range(31):
        travel = tuple(v*step for v in withdrawal)
        assert overlap(released, keeper.translate(travel)) < tolerance, (
            name+f": released path blocked at step {step}")
    print(f"{name}: seated clear; withdrawal obstructs by {obstruction:.4f} mm³; "
          "31 pressed withdrawal poses clear (sampled, not continuous proof).")


def main():
    a = baseline()
    d = m1.D
    crop = block(-d.width/2-1, -d.width/2+11, -12, 12,
                 d.beam_root-10, d.seam+20)
    released = m1.body_fixed(d).union(m1.tongue(d, d.release)).intersect(crop)
    check_pair("A", a["leaf_fixture"], a["keeper"], (0, 0, 1), released)
    b = components("B-flat-PLA")
    check_pair("B", b["leaf_fixture"], b["keeper"], (1, 0, 0),
               flat_leaf(F.travel))
    # A retained shoulder must still obstruct at the .25 mm lower-rail play limit.
    assert overlap(b["leaf_fixture"].translate((0, -.25, 0)),
                   b["keeper"].translate((1, 0, 0))) > .001
    # Test the holding feature itself: remove the tooth, and withdrawal must clear.
    bare = b["leaf_fixture"].cut(block(F.shoulder-.01, F.length+.01,
                                      0, F.projection+.01, -1, F.breadth+1))
    assert overlap(bare, b["keeper"].translate((1, 0, 0))) < 1e-6
    # Compare geometric strain demand without assigning an unmeasured PLA modulus.
    length = d.beam_length-1
    contact = d.press_z-(d.beam_root+1)
    press = d.release*2*contact/(3*length-contact)
    strain_a = 3*d.beam_thickness*press/(2*contact**2)
    effective_b = F.length-F.root_radius
    strain_b = 3*F.thickness*F.travel/(2*effective_b**2)
    print(f"Analytical root strain demand: A {100*strain_a:.3f}%; "
          f"B {100*strain_b:.3f}% (R2 excluded from B effective span). "
          "Neither is a PLA allowable or a fatigue prediction.")


if __name__ == "__main__":
    main()
