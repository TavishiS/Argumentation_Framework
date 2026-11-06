"""Argument labellings (Rahwan, Ch. 5, Definition 5.6 and Table 5.1)."""

from typing import Dict, List

from .framework import ArgumentationFramework, sorted_args, sort_key
from .semantics import complete_extensions

IN, OUT, UNDEC = "in", "out", "undec"

Labelling = Dict  # argument -> "in" | "out" | "undec"


def extension_to_labelling(af: ArgumentationFramework, S) -> Labelling:
    """in = S, out = S^+, undec = everything else."""
    S = frozenset(S)
    out = af.plus(S)
    return {a: IN if a in S else OUT if a in out else UNDEC for a in sorted_args(af.arguments)}


def labelling_to_extension(L: Labelling):
    return frozenset(a for a, v in L.items() if v == IN)


def is_legal_labelling(af: ArgumentationFramework, L: Labelling) -> bool:
    """Definition 5.6, checked directly.

    L must be total over A with values in {in, out, undec} and satisfy
      L(a) = out  <=>  some attacker of a is in
      L(a) = in   <=>  all attackers of a are out
    (undec otherwise).
    """
    if set(L) != set(af.arguments) or any(v not in (IN, OUT, UNDEC) for v in L.values()):
        return False
    for a in af.arguments:
        attackers = af.attackers(a)
        some_in = any(L[b] == IN for b in attackers)
        all_out = all(L[b] == OUT for b in attackers)
        if (L[a] == OUT) != some_in:
            return False
        if (L[a] == IN) != all_out:
            return False
    return True


def legal_labellings(af: ArgumentationFramework) -> List[Labelling]:
    """6D. All legal labellings, one per complete extension (same order)."""
    return [extension_to_labelling(af, S) for S in complete_extensions(af)]


def _members(L: Labelling, value: str) -> frozenset:
    return frozenset(a for a, v in L.items() if v == value)


def extensions_via_labellings(af: ArgumentationFramework) -> dict:
    """Derive extensions from the labellings using Table 5.1 (independent cross-check).

    grounded: minimal in; preferred: maximal in; semi-stable: minimal undec;
    stable: empty undec.
    """
    labs = legal_labellings(af)
    ins = [_members(L, IN) for L in labs]
    undecs = [_members(L, UNDEC) for L in labs]
    grounded = [ins[i] for i in range(len(labs))
                if not any(ins[j] < ins[i] for j in range(len(labs)))]
    preferred = [ins[i] for i in range(len(labs))
                 if not any(ins[i] < ins[j] for j in range(len(labs)))]
    semi_stable = [ins[i] for i in range(len(labs))
                   if not any(undecs[j] < undecs[i] for j in range(len(labs)))]
    stable = [ins[i] for i in range(len(labs)) if not undecs[i]]
    return {"grounded": grounded, "preferred": preferred,
            "semi_stable": semi_stable, "stable": stable}


def format_labelling(L: Labelling) -> str:
    return ", ".join(f"{a}={L[a]}" for a in sorted(L, key=sort_key))
