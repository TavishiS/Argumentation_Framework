"""Summarise results/instances.jsonl: tables, plots and annotated example instances.

Usage (from the project root):  python3 experiments/analyse.py
Outputs: results/summary.csv, results/summary.md, results/plots/*.png,
         results/q2_q3_examples.md
"""

import csv
import itertools
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from argframe import grounded_mechanism, theorem_5_4_condition, utility  # noqa: E402
from argframe.framework import sorted_args  # noqa: E402
from argframe.strategic import subsets  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
MODES = ("book", "simple", "distinct")
AGENT_NAMES = "xyz"


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def fmt(S):
    return "{" + ", ".join(sorted_args(S)) + "}"


def instance_parts(rec):
    attacks = [tuple(a) for a in rec["attacks"]]
    types = [frozenset(t) for t in rec["types"]]
    return attacks, types


# ---------------------------------------------------------------------------
# Why is a strategyproof instance strategyproof although the condition fails?
# ---------------------------------------------------------------------------

def classify_strategyproof(attacks, types, witness):
    """Empirical + structural tags explaining why truth-telling is still dominant
    for the agent named in the Theorem 5.4 violation."""
    i = witness["agent"]
    Ai = types[i]
    others = [j for j in range(len(types)) if j != i]
    changes_utility = frees_own = loses = False
    for combo in itertools.product(*(subsets(types[j]) for j in others)):
        profile = list(types)
        for j, c in zip(others, combo):
            profile[j] = c
        truthful = grounded_mechanism(attacks, profile)
        u_true = utility(Ai, truthful)
        for S in subsets(Ai):
            if not S:
                continue
            profile[i] = Ai - S
            dev = grounded_mechanism(attacks, profile)
            u_dev = utility(Ai, dev)
            if u_dev != u_true:
                changes_utility = True
            if u_dev < u_true:
                loses = True
            if (dev & Ai) - truthful:
                frees_own = True
    tags = []
    if not changes_utility:
        tags.append("hiding never changes the agent's utility (whatever it hides, its accepted "
                    "arguments stay the same, e.g. they are decided by unhideable or "
                    "never-accepted arguments of other agents)")
    if frees_own:
        tags.append("hiding can free one of the agent's own arguments, but it always costs "
                    "at least as many others (compensation, as in Example 5.11)")
    if changes_utility and not frees_own:
        tags.append("hiding only ever lowers the agent's utility")
    # structural: an interior vertex of the odd path is defeated by an unattacked own argument
    attackers = defaultdict(set)
    for a, b in attacks:
        attackers[b].add(a)
    interior = witness["path"][1:-1]
    for v in interior:
        for g in sorted_args(Ai):
            if (g, v) in set(attacks) and not attackers[g] and g not in witness["path"]:
                tags.append(f"cancelling argument: {g} (unattacked, owned by the agent) defeats "
                            f"{v} on the odd path, as α6 does in Example 5.11")
    return tags


def describe_instance(rec, show_manipulation=False):
    attacks, types = instance_parts(rec)
    truthful = grounded_mechanism(attacks, types)
    lines = [f"- n={rec['n']}, p={rec['p']}, index={rec['index']}",
             f"  - arguments: {', '.join(rec['arguments'])}",
             f"  - attacks: {', '.join(f'{a}->{b}' for a, b in attacks) or '(none)'}",
             "  - types: " + "; ".join(f"{AGENT_NAMES[i]}={fmt(t)}" for i, t in enumerate(types)),
             f"  - grounded outcome (all truthful): {fmt(truthful)}; utilities: "
             + ", ".join(f"{AGENT_NAMES[i]}={utility(t, truthful)}" for i, t in enumerate(types))]
    return lines, attacks, types


# ---------------------------------------------------------------------------

def main():
    recs = load(os.path.join(RESULTS, "instances.jsonl"))
    ps = sorted({r["p"] for r in recs})
    os.makedirs(os.path.join(RESULTS, "plots"), exist_ok=True)

    rows = []
    for p in ps:
        rs = [r for r in recs if r["p"] == p]
        row = {"p": p, "instances": len(rs),
               "strategyproof": sum(r["strategyproof"] for r in rs)}
        row["sp_fraction"] = row["strategyproof"] / len(rs)
        for m in MODES:
            c = [r for r in rs if r["cond_" + m]]
            row[f"cond_{m}"] = len(c)
            row[f"cond_{m}_fraction"] = len(c) / len(rs)
            row[f"q2_{m}"] = sum(1 for r in rs if r["cond_" + m] and not r["strategyproof"])
            row[f"q3_{m}"] = sum(1 for r in rs if r["strategyproof"] and not r["cond_" + m])
        rows.append(row)
    total = {"p": "all", "instances": len(recs),
             "strategyproof": sum(r["strategyproof"] for r in recs)}
    total["sp_fraction"] = total["strategyproof"] / len(recs)
    for m in MODES:
        total[f"cond_{m}"] = sum(r["cond_" + m] for r in recs)
        total[f"cond_{m}_fraction"] = total[f"cond_{m}"] / len(recs)
        total[f"q2_{m}"] = sum(1 for r in recs if r["cond_" + m] and not r["strategyproof"])
        total[f"q3_{m}"] = sum(1 for r in recs if r["strategyproof"] and not r["cond_" + m])
    rows.append(total)

    with open(os.path.join(RESULTS, "summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # ---- markdown tables ---------------------------------------------------
    md = ["# Experiment summary", "",
          "## Q1: fraction of strategyproof instances", "",
          "| p | instances | strategyproof | fraction | condition (book) holds | fraction |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['p']} | {r['instances']} | {r['strategyproof']} | {r['sp_fraction']:.3f} "
                  f"| {r['cond_book']} | {r['cond_book_fraction']:.3f} |")
    md += ["", "## Q2 / Q3 counts per reading of the Theorem 5.4 condition", "",
           "Q2 = condition holds but NOT strategyproof; Q3 = strategyproof but condition fails.", "",
           "| p | " + " | ".join(f"Q2 {m} | Q3 {m}" for m in MODES) + " |",
           "|---|" + "---|---|" * len(MODES)]
    for r in rows:
        md.append(f"| {r['p']} | " + " | ".join(f"{r['q2_' + m]} | {r['q3_' + m]}" for m in MODES) + " |")
    md += ["", "## 2x2 contingency (book reading): rows = condition, columns = strategyproof", "",
           "| p | cond holds & SP | cond holds & not SP | cond fails & SP | cond fails & not SP |",
           "|---|---|---|---|---|"]
    for p in ps + ["all"]:
        rs = recs if p == "all" else [r for r in recs if r["p"] == p]
        k = Counter((r["cond_book"], r["strategyproof"]) for r in rs)
        md.append(f"| {p} | {k[(True, True)]} | {k[(True, False)]} | {k[(False, True)]} | {k[(False, False)]} |")

    # ---- Q2 / Q3 example file ---------------------------------------------
    ex = ["# Q2 and Q3 instances", ""]

    ex += ["## Q2: condition holds but mechanism is NOT strategyproof", ""]
    for m in MODES:
        q2 = [r for r in recs if r["cond_" + m] and not r["strategyproof"]]
        ex.append(f"### reading `{m}`: {len(q2)} instance(s)")
        ex.append("")
        for r in sorted(q2, key=lambda r: (r["n"], len(r["attacks"])))[:10]:
            lines, attacks, types = describe_instance(r)
            w = r["witness_5_3"]
            lines.append(f"  - profitable deviation: agent {AGENT_NAMES[w['agent']]} reveals "
                         f"{fmt(w['better_report'])} instead of its type "
                         f"(utility {w['truthful_utility']} -> {w['better_utility']})")
            ex += lines
        ex.append("")

    # Q3 (book reading)
    q3 = [r for r in recs if r["strategyproof"] and not r["cond_book"]]
    tag_counter = Counter()
    annotated = []
    for r in q3:
        attacks, types = instance_parts(r)
        tags = classify_strategyproof(attacks, types, r["witness_5_4_book"])
        r["_tags"] = tags
        for t in tags:
            tag_counter[t.split(":")[0] if t.startswith("cancelling") else t] += 1
        annotated.append(r)
    def explicit_conflict(r):
        attacks, types = instance_parts(r)
        aset = set(attacks)
        return any((a, b) in aset for t in types for a in t for b in t)

    for r in annotated:
        r["_explicit"] = explicit_conflict(r)
    n_expl = sum(r["_explicit"] for r in annotated)
    n_indirect = len(annotated) - n_expl
    kind_tags = {True: Counter(), False: Counter()}
    for r in annotated:
        for t in r["_tags"]:
            kind_tags[r["_explicit"]][t.split(":")[0] if t.startswith("cancelling") else t] += 1

    ex += [f"## Q3: strategyproof although the Theorem 5.4 condition fails (book reading): {len(q3)} instances", "",
           f"- {n_expl} violate it through an explicit conflict inside one agent's own type "
           f"(an attack between two of its arguments, or a self-attack);",
           f"- {n_indirect} violate it only through an indirect odd-length path (every type is conflict-free).",
           ""]
    md += ["", "## Q3 breakdown (book reading)", "",
           f"- total {len(q3)}: {n_expl} with an explicit conflict inside a type, "
           f"{n_indirect} with only an indirect odd path", ""]
    for explicit, title in ((False, "indirect odd path only"), (True, "explicit conflict")):
        md.append(f"Reasons, {title}:")
        md.append("")
        for t, c in kind_tags[explicit].most_common():
            md.append(f"- {c} x {t}")
        md.append("")
        ex += [f"### Explanation tags: {title} (an instance can carry several)", ""]
        for t, c in kind_tags[explicit].most_common():
            ex.append(f"- {c} x {t}")
        ex.append("")
    for explicit, title, k in ((False, "Smallest examples: indirect odd path only", 12),
                               (True, "Smallest examples: explicit conflict", 4)):
        ex += [f"### {title}", ""]
        sel = [r for r in annotated if r["_explicit"] == explicit]
        for r in sorted(sel, key=lambda r: (r["n"], len(r["attacks"]), r["p"], r["index"]))[:k]:
            lines, attacks, types = describe_instance(r)
            w = r["witness_5_4_book"]
            lines.append(f"  - condition violated by agent {AGENT_NAMES[w['agent']]}: "
                         + (f"explicit conflict {w['alpha1']}->{w['alpha2']}" if w["kind"] == "conflict" else
                            f"{w['alpha1']} indirectly defeats {w['alpha2']} via odd path "
                            f"{' -> '.join(w['path'])}"))
            for t in r["_tags"]:
                lines.append(f"  - why still strategyproof: {t}")
            ex += lines
        ex.append("")

    with open(os.path.join(RESULTS, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(RESULTS, "q2_q3_examples.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(ex) + "\n")

    # ---- plots -------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    per_p = [r for r in rows if r["p"] != "all"]
    xs = list(range(len(per_p)))
    width = 0.38
    fig, ax = plt.subplots(figsize=(6, 4))
    b1 = ax.bar([x - width / 2 for x in xs], [r["sp_fraction"] for r in per_p], width,
                label="strategyproof (Thm 5.3)")
    b2 = ax.bar([x + width / 2 for x in xs], [r["cond_book_fraction"] for r in per_p], width,
                label="Thm 5.4 condition holds")
    ax.set_xticks(xs)
    ax.set_xticklabels([str(r["p"]) for r in per_p])
    ax.set_xlabel("attack probability p")
    ax.set_ylabel("fraction of instances")
    ax.set_ylim(0, 1)
    ax.bar_label(b1, fmt="%.3f", fontsize=8)
    ax.bar_label(b2, fmt="%.3f", fontsize=8)
    ax.legend()
    ax.set_title("Strategyproofness vs. attack probability")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "plots", "strategyproof_fraction.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    cats = ["cond & SP", "cond & not SP", "not cond & SP", "not cond & not SP"]
    bottoms = [0] * len(per_p)
    for cat, key in zip(cats, [(True, True), (True, False), (False, True), (False, False)]):
        vals = [sum(1 for r in recs if r["p"] == row["p"] and (r["cond_book"], r["strategyproof"]) == key)
                / row["instances"] for row in per_p]
        ax.bar(xs, vals, bottom=bottoms, label=cat)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax.set_xticks(xs)
    ax.set_xticklabels([str(r["p"]) for r in per_p])
    ax.set_xlabel("attack probability p")
    ax.set_ylabel("fraction of instances")
    ax.legend(fontsize=8)
    ax.set_title("Condition (Thm 5.4) vs. strategyproofness")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "plots", "contingency.png"), dpi=150)
    plt.close(fig)

    print("\n".join(md))
    print(f"\nwrote summary.csv, summary.md, q2_q3_examples.md, plots/ in {RESULTS}")


if __name__ == "__main__":
    main()
