"""Extension-based semantics (Rahwan, Ch. 5, Definitions 5.4, 5.5, 5.7).

All functions return frozensets (or lists of frozensets) in a deterministic
order: by size, then lexicographically.
"""

from typing import Dict, FrozenSet, List

from .framework import ArgumentationFramework, sorted_args, sorted_sets

Extension = FrozenSet


def grounded_trace(af: ArgumentationFramework) -> List[Extension]:
    """[F^0(empty), F^1(empty), ...] up to and including the first repeated value."""
    trace = [frozenset()]
    while True:
        nxt = af.characteristic(trace[-1])
        trace.append(nxt)
        if nxt == trace[-2]:
            return trace


def grounded_extension(af: ArgumentationFramework) -> Extension:
    """6A. Least fixed point of F, reached by iterating F from the empty set.

    F is monotone and A is finite, so the iteration terminates.
    """
    return grounded_trace(af)[-1]


def _conflict_free_sets(af: ArgumentationFramework):
    """Yield every conflict-free subset of A (backtracking with pruning)."""
    args = sorted_args(af.arguments)
    n = len(args)

    def rec(i, current):
        if i == n:
            yield frozenset(current)
            return
        a = args[i]
        # exclude a
        yield from rec(i + 1, current)
        # include a if it stays conflict-free (no self-attack, no clash with current)
        if a not in af.attackers(a) and not (af.attackers(a) & current) \
                and not (af.attacked_by(a) & current):
            current.add(a)
            yield from rec(i + 1, current)
            current.remove(a)

    yield from rec(0, set())


def admissible_sets(af: ArgumentationFramework) -> List[Extension]:
    return sorted_sets(S for S in _conflict_free_sets(af) if S <= af.characteristic(S))


def complete_extensions(af: ArgumentationFramework) -> List[Extension]:
    """6B. All conflict-free fixed points of F (Definition 5.5)."""
    return sorted_sets(S for S in _conflict_free_sets(af) if S == af.characteristic(S))


def _maximal(sets: List[Extension]) -> List[Extension]:
    return [S for S in sets if not any(S < T for T in sets)]


def preferred_extensions(af: ArgumentationFramework) -> List[Extension]:
    """Subset-maximal complete extensions."""
    return sorted_sets(_maximal(complete_extensions(af)))


def stable_extensions(af: ArgumentationFramework) -> List[Extension]:
    """Conflict-free sets S with S^+ = A \\ S (every stable extension is complete)."""
    return sorted_sets(S for S in complete_extensions(af)
                       if af.plus(S) == af.arguments - S)


def semi_stable_extensions(af: ArgumentationFramework) -> List[Extension]:
    """Complete extensions whose range S u S^+ is subset-maximal."""
    comp = complete_extensions(af)
    ranges = {S: af.range(S) for S in comp}
    return sorted_sets(S for S in comp
                       if not any(ranges[S] < ranges[T] for T in comp))


def all_extensions(af: ArgumentationFramework) -> Dict[str, List[Extension]]:
    """6C. Every extension type of Definition 5.7 (grounded wrapped in a list)."""
    return {
        "grounded": [grounded_extension(af)],
        "complete": complete_extensions(af),
        "preferred": preferred_extensions(af),
        "stable": stable_extensions(af),
        "semi_stable": semi_stable_extensions(af),
    }
