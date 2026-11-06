"""Demonstration of every required function, on the examples from Rahwan, Ch. 5.

Run:  python3 demo.py        (output is also saved in results/demo_output.txt)
"""

import random

from argframe import (ArgumentationFramework, acceptance_report, all_extensions,
                      best_responses, format_labelling, grounded_extension,
                      grounded_mechanism, grounded_trace, is_legal_labelling,
                      legal_labellings, random_instance, satisfies_theorem_5_3,
                      theorem_5_4_condition, utility)
from argframe.framework import format_set
from examples.book_examples import (EX_5_10_ATTACKS, EX_5_10_TYPES, EX_5_11_ATTACKS,
                                    EX_5_11_TYPES, FIG_5_1, FIG_5_2, FIG_5_3, build, fs)

AG = "xyz"


def header(t):
    print("\n" + "=" * 72 + f"\n{t}\n" + "=" * 72)


def sets(L):
    return "[" + ", ".join(format_set(S) for S in L) + "]"


def part1_figure(name, ex, probe_sets=()):
    header(f"PART 1 - {name}")
    af = build(ex)
    print(af)
    for S in probe_sets:
        print(f"S = {format_set(S)}: conflict-free={af.is_conflict_free(S)}, "
              f"F(S)={format_set(af.characteristic(S))}, admissible={af.is_admissible(S)}, "
              f"complete={af.is_complete(S)}")
    print("grounded trace F^k({}):", " -> ".join(format_set(S) for S in grounded_trace(af)))
    print("grounded extension:", format_set(grounded_extension(af)))
    for sem, exts in all_extensions(af).items():
        print(f"  {sem:12s}: {sets(exts)}")
    print("legal labellings (Definition 5.6):")
    for L in legal_labellings(af):
        assert is_legal_labelling(af, L)
        print("  ", format_labelling(L))
    for sem in ("grounded", "preferred"):
        print(f"acceptance under {sem}:", acceptance_report(af, sem))
    return af


def part1():
    af = part1_figure("Figure 5.1 (Examples 5.5, 5.6, 5.8)", FIG_5_1,
                      [fs("α3", "α5"), fs("α3"), fs("α1", "α3", "α5"), fs("α1", "α3")])
    print("S={α3,α5} defends α1:", af.defends(fs("α3", "α5"), "α1"))
    part1_figure("Figure 5.2 (Example 5.7)", FIG_5_2, [fs("α3"), fs("α1", "α3")])
    part1_figure("Figure 5.3(i) (grounded extension {a, c, e}, p.188)", FIG_5_3)


def show_agents(attacks, types, reports=None):
    reports = reports or types
    out = grounded_mechanism(attacks, reports)
    print("  revealed:", "; ".join(f"{AG[i]}={format_set(r)}" for i, r in enumerate(reports)))
    print("  outcome :", format_set(out), " utilities:",
          ", ".join(f"u_{AG[i]}={utility(t, out)}" for i, t in enumerate(types)))
    return out


def part2():
    header("PART 2 - Example 5.10: grounded mechanism where hiding pays")
    print("attacks:", ", ".join(f"{a}->{b}" for a, b in EX_5_10_ATTACKS))
    print("types  :", "; ".join(f"{AG[i]}={format_set(t)}" for i, t in enumerate(EX_5_10_TYPES)))
    print("truthful reports (note: the book's text swaps u_y and u_z; by definition u_y=0, u_z=1):")
    show_agents(EX_5_10_ATTACKS, EX_5_10_TYPES)
    print("x withholds α1:")
    show_agents(EX_5_10_ATTACKS, EX_5_10_TYPES, [fs("α4", "α5"), fs("α2"), fs("α3")])
    u, best = best_responses(EX_5_10_ATTACKS, EX_5_10_TYPES, 0, [fs(), fs("α2"), fs("α3")])
    print(f"x's best responses vs truthful y,z: utility {u}, reports {sets(best)}")
    ok, w = satisfies_theorem_5_3(EX_5_10_ATTACKS, EX_5_10_TYPES)
    print("Theorem 5.3 (strategyproof)?", ok)
    print("  witness: agent", AG[w["agent"]], "reports", format_set(w["better_report"]),
          f"(utility {w['truthful_utility']} -> {w['better_utility']})")
    holds, wit = theorem_5_4_condition(EX_5_10_ATTACKS, EX_5_10_TYPES)
    print("Theorem 5.4 condition holds?", holds, "-", wit["alpha1"], "indirectly defeats",
          wit["alpha2"], "via odd path", " -> ".join(wit["path"]))

    header("PART 2 - Example 5.11: strategyproof although the Theorem 5.4 condition fails")
    print("attacks:", ", ".join(f"{a}->{b}" for a, b in EX_5_11_ATTACKS))
    print("types  :", "; ".join(f"{AG[i]}={format_set(t)}" for i, t in enumerate(EX_5_11_TYPES)))
    show_agents(EX_5_11_ATTACKS, EX_5_11_TYPES)
    print("Theorem 5.3 (strategyproof)?", satisfies_theorem_5_3(EX_5_11_ATTACKS, EX_5_11_TYPES)[0])
    holds, wit = theorem_5_4_condition(EX_5_11_ATTACKS, EX_5_11_TYPES)
    print("Theorem 5.4 condition holds?", holds, "-", wit["alpha1"], "indirectly defeats",
          wit["alpha2"], "via", " -> ".join(wit["path"]))
    print("The cancelling argument is α6 (the book's text says α5, a misprint): α6 is unattacked and")
    print("defeats α3, so α3 is never accepted when α6 is revealed.")
    print("Without α6 in x's type (α6 never revealed) we are back to Example 5.10:")
    print("  Theorem 5.3 holds?", satisfies_theorem_5_3(EX_5_11_ATTACKS, EX_5_10_TYPES)[0])

    header("PART 2 - an instance satisfying the Theorem 5.4 condition")
    attacks = [("a1", "a2"), ("a2", "a3")]
    types = [fs("a1", "a3"), fs("a2")]
    print("attacks: a1->a2, a2->a3; types: x={a1,a3}, y={a2}")
    print("Theorem 5.4 condition:", theorem_5_4_condition(attacks, types)[0],
          "| Theorem 5.3 (strategyproof):", satisfies_theorem_5_3(attacks, types)[0])

    header("PART 2 - cycles: walks vs simple paths (condition readings)")
    attacks = [("al", "x"), ("x", "be"), ("x", "y"), ("y", "z"), ("z", "x")]
    types = [fs("al", "be"), fs("x"), fs("y"), fs("z")]
    print("attacks: al->x, x->be, odd cycle x->y->z->x; types: {al,be},{x},{y},{z}")
    for mode in ("book", "simple", "distinct"):
        h, w = theorem_5_4_condition(attacks, types, mode)
        extra = "" if h else f"  (witness {w['alpha1']} ~> {w['alpha2']}: {' -> '.join(w['path'])})"
        print(f"  mode={mode:9s} condition holds: {h}{extra}")

    header("MINI EXPERIMENT (50 random instances per p, fixed seeds)")
    for p in (0.15, 0.25, 0.35):
        rng = random.Random(f"demo/{p}")
        sp = cond = bad = 0
        for _ in range(50):
            _, attacks, types = random_instance(rng, p)
            s = satisfies_theorem_5_3(attacks, types)[0]
            c = theorem_5_4_condition(attacks, types)[0]
            sp += s
            cond += c
            bad += c and not s
        print(f"  p={p}: strategyproof {sp}/50, condition holds {cond}/50, "
              f"condition-but-manipulable {bad}")


if __name__ == "__main__":
    part1()
    part2()
