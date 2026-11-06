"""Generate random instances and record strategyproofness + Theorem 5.4 conditions.

Usage (from the project root):
    python3 experiments/run_experiments.py [--ps 0.15 0.25 0.35] [--per-p 1000]
                                           [--seed 42] [--out results/instances.jsonl]
"""

import argparse
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from argframe import random_instance, satisfies_theorem_5_3, theorem_5_4_condition  # noqa: E402
from argframe.framework import sorted_args  # noqa: E402


def jsonable(x):
    if isinstance(x, (set, frozenset)):
        return sorted_args(x)
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    return x


def run(ps, per_p, seed, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    count = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for p in ps:
            rng = random.Random(f"{seed}/{p}")
            for k in range(per_p):
                args, attacks, types = random_instance(rng, p)
                sp, w53 = satisfies_theorem_5_3(attacks, types)
                conds = {m: theorem_5_4_condition(attacks, types, m)
                         for m in ("book", "simple", "distinct")}
                rec = {
                    "p": p, "index": k, "n": len(args),
                    "arguments": args,
                    "attacks": [list(a) for a in attacks],
                    "types": [sorted_args(t) for t in types],
                    "strategyproof": sp,
                    "witness_5_3": jsonable(w53),
                    "cond_book": conds["book"][0],
                    "cond_simple": conds["simple"][0],
                    "cond_distinct": conds["distinct"][0],
                    "witness_5_4_book": jsonable(conds["book"][1]),
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                count += 1
            print(f"p={p}: {per_p} instances done", flush=True)
    print(f"wrote {count} instances to {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ps", type=float, nargs="+", default=[0.15, 0.25, 0.35])
    ap.add_argument("--per-p", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "instances.jsonl"))
    a = ap.parse_args()
    run(a.ps, a.per_p, a.seed, a.out)
