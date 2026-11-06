"""Strategic argumentation: the grounded direct argumentation mechanism
(Rahwan, Ch. 5, Definitions 5.21-5.22, Theorems 5.3 and 5.4).

Conventions
-----------
attacks : iterable of (attacker, target) pairs -- the global defeat relation R.
types   : list of frozensets, types[i] = A_i, the arguments agent i can reveal.
reports : list of frozensets, reports[i] = A_i^o (subset of types[i]) revealed by agent i.
Agents may only hide arguments (Sigma_i = 2^{A_i}).
Utility of agent i (acceptability maximising) = |A_i  n  outcome|.
"""

import itertools
from collections import deque
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

from .framework import ArgumentationFramework, sort_key, sorted_args, sorted_sets
from .semantics import grounded_extension

Report = FrozenSet


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def subsets(items: Iterable) -> List[FrozenSet]:
    """All subsets of `items` (including empty set and the full set), sorted by size."""
    items = sorted_args(frozenset(items))
    out = []
    for r in range(len(items) + 1):
        out.extend(frozenset(c) for c in itertools.combinations(items, r))
    return out


def _attackers_map(attacks: Iterable[Tuple]) -> Dict:
    att: Dict = {}
    for a, b in attacks:
        att.setdefault(b, set()).add(a)
        att.setdefault(a, set())
    return {k: frozenset(v) for k, v in att.items()}


def _grounded_fast(R: FrozenSet, att: Dict) -> FrozenSet:
    """Grounded extension of the framework induced by R, by iterating F from {}.

    Equivalent to grounded_mechanism but avoids building framework objects;
    used inside the exhaustive strategyproofness search. Cross-checked against
    grounded_mechanism in the tests.
    """
    S: FrozenSet = frozenset()
    while True:
        out = {b for b in R if att.get(b, frozenset()) & S}
        new = frozenset(a for a in R if (att.get(a, frozenset()) & R) <= out)
        if new == S:
            return S
        S = new


def utility(agent_args: Iterable, outcome: Iterable) -> int:
    """Acceptability-maximising utility: number of the agent's arguments accepted."""
    return len(frozenset(agent_args) & frozenset(outcome))


# --------------------------------------------------------------------------
# Part 2, item 1: the mechanism
# --------------------------------------------------------------------------

def grounded_mechanism(attacks: Iterable[Tuple], reports: Sequence[Iterable]) -> FrozenSet:
    """g(A_1^o, ..., A_I^o) = grounded extension of <A_1^o u ... u A_I^o, R>.

    The defeat relation is the global one restricted to the revealed arguments.
    """
    R = frozenset().union(*(frozenset(r) for r in reports)) if reports else frozenset()
    att = [(a, b) for a, b in attacks if a in R and b in R]
    return grounded_extension(ArgumentationFramework(R, att))


# --------------------------------------------------------------------------
# Part 2, item 2: best responses
# --------------------------------------------------------------------------

def best_responses(attacks: Iterable[Tuple], types: Sequence[Iterable], i: int,
                   reports: Sequence[Iterable]) -> Tuple[int, List[FrozenSet]]:
    """Enumerate every subset of A_i that agent i could reveal, given the fixed
    reports of the others (reports[i] is ignored), and return
    (maximal utility, list of all maximising reports).
    """
    attacks = list(attacks)
    types = [frozenset(t) for t in types]
    reports = [frozenset(r) for r in reports]
    best_u = -1
    best: List[FrozenSet] = []
    for S in subsets(types[i]):
        profile = list(reports)
        profile[i] = S
        u = utility(types[i], grounded_mechanism(attacks, profile))
        if u > best_u:
            best_u, best = u, [S]
        elif u == best_u:
            best.append(S)
    return best_u, sorted_sets(best)


# --------------------------------------------------------------------------
# Part 2, item 3: Theorem 5.3 (exact characterisation of strategyproofness)
# --------------------------------------------------------------------------

def satisfies_theorem_5_3(attacks: Iterable[Tuple], types: Sequence[Iterable]):
    """Check the condition of Theorem 5.3 by exhaustive search.

    For every agent i, every S subset of A_i and every combination A_-i of
    subsets revealed by the other agents:
        |A_i n GE(A_i u A_-i)|  >=  |A_i n GE((A_i \\ S) u A_-i)|.
    Equivalently: revealing all of A_i is a best response against every
    combination of the others' reports.

    Returns (True, None) if the mechanism is strategyproof, otherwise
    (False, witness) where witness is a dict describing a profitable deviation.
    """
    attacks = list(attacks)
    types = [frozenset(t) for t in types]
    att = _attackers_map(attacks)
    cache: Dict[FrozenSet, FrozenSet] = {}

    def ge(R: FrozenSet) -> FrozenSet:
        if R not in cache:
            cache[R] = _grounded_fast(R, att)
        return cache[R]

    for i, Ai in enumerate(types):
        others = [j for j in range(len(types)) if j != i]
        for combo in itertools.product(*(subsets(types[j]) for j in others)):
            U = frozenset().union(*combo) if combo else frozenset()
            truthful_out = ge(Ai | U)
            u_true = len(Ai & truthful_out)
            for S in subsets(Ai):
                rep = Ai - S
                dev_out = ge(rep | U)
                u_dev = len(Ai & dev_out)
                if u_dev > u_true:
                    reports = {j: c for j, c in zip(others, combo)}
                    return False, {
                        "agent": i,
                        "others_reports": reports,
                        "truthful_report": Ai,
                        "truthful_utility": u_true,
                        "truthful_outcome": truthful_out,
                        "better_report": rep,
                        "better_utility": u_dev,
                        "better_outcome": dev_out,
                    }
    return True, None


is_strategyproof = satisfies_theorem_5_3


# --------------------------------------------------------------------------
# Part 2, item 4: Theorem 5.4 (sufficient graph-theoretic condition)
# --------------------------------------------------------------------------

def _successors(attacks: Iterable[Tuple]) -> Dict:
    succ: Dict = {}
    for a, b in attacks:
        succ.setdefault(a, set()).add(b)
        succ.setdefault(b, set())
    return {k: sorted(v, key=sort_key) for k, v in succ.items()}


def odd_walk(succ: Dict, source, target) -> Optional[List]:
    """Shortest odd-length directed *walk* source -> target (vertices may repeat),
    or None. BFS over (vertex, parity) states, so it terminates on cyclic graphs.
    The returned vertex list [source, ..., target] has an odd number of edges.
    source == target is allowed (an odd closed walk, e.g. a self-attack or an
    odd cycle through source).
    """
    start = (source, 0)
    parent = {start: None}
    queue = deque([start])
    while queue:
        node, par = queue.popleft()
        for nxt in succ.get(node, ()):
            state = (nxt, 1 - par)
            if state in parent:
                continue
            parent[state] = (node, par)
            if nxt == target and state[1] == 1:
                path = [state]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                return [v for v, _ in reversed(path)]
            queue.append(state)
    return None


def odd_simple_path(succ: Dict, source, target) -> Optional[List]:
    """An odd-length directed *simple* path source -> target (no repeated vertex,
    source != target), found by exhaustive DFS; None if there is none."""
    if source == target:
        return None
    path = [source]
    on_path = {source}

    def dfs(node):
        for nxt in succ.get(node, ()):
            if nxt in on_path:
                continue
            path.append(nxt)
            on_path.add(nxt)
            if nxt == target and (len(path) - 1) % 2 == 1:
                return True
            if nxt != target and dfs(nxt):
                return True
            # nxt == target with even length: cannot extend past target (simple path
            # would have to leave and re-enter it), so just backtrack.
            path.pop()
            on_path.remove(nxt)
        return False

    return list(path) if dfs(source) else None


CONDITION_MODES = ("book", "simple", "distinct")


def theorem_5_4_condition(attacks: Iterable[Tuple], types: Sequence[Iterable],
                          mode: str = "book"):
    """Check the sufficient condition of Theorem 5.4 on the FULL graph.

    The condition holds iff for every agent i, A_i is conflict-free and there
    are no alpha1, alpha2 in A_i with alpha1 indirectly defeating alpha2
    (an odd-length directed path alpha1 -> ... -> alpha2 in the whole graph).

    mode:
      "book"     (default) path = walk (vertices may repeat; BFS on (vertex, parity)),
                 alpha1 = alpha2 allowed (so an odd cycle through an argument counts),
                 and A_i must be conflict-free.
      "simple"   only odd-length simple paths between distinct alpha1 != alpha2
                 (A_i must still be conflict-free).
      "distinct" walks, but alpha1 != alpha2 and no separate conflict-free requirement.

    Returns (holds, witness); witness is None when the condition holds, otherwise a
    dict {"agent", "kind": "conflict"|"odd_path", "alpha1", "alpha2", "path"}.
    """
    if mode not in CONDITION_MODES:
        raise ValueError(f"mode must be one of {CONDITION_MODES}")
    attacks = list(attacks)
    types = [frozenset(t) for t in types]
    succ = _successors(attacks)
    attack_set = set(attacks)

    for i, Ai in enumerate(types):
        members = sorted_args(Ai)
        if mode in ("book", "simple"):
            for a in members:
                for b in members:
                    if (a, b) in attack_set:
                        return False, {"agent": i, "kind": "conflict",
                                       "alpha1": a, "alpha2": b, "path": [a, b]}
        for a in members:
            for b in members:
                if mode == "book":
                    path = odd_walk(succ, a, b)
                elif mode == "distinct":
                    path = odd_walk(succ, a, b) if a != b else None
                else:
                    path = odd_simple_path(succ, a, b)
                if path is not None:
                    return False, {"agent": i, "kind": "odd_path",
                                   "alpha1": a, "alpha2": b, "path": path}
    return True, None


def is_strategyproof_by_theorem_5_4(attacks, types, mode: str = "book") -> bool:
    """True if the sufficient condition of Theorem 5.4 holds (hence strategyproof)."""
    return theorem_5_4_condition(attacks, types, mode)[0]
