"""Abstract argumentation frameworks (Rahwan, Ch. 5, Definitions 5.1-5.5).

An argumentation framework is a pair AF = <A, ->> where A is a finite set of
arguments and -> (the defeat / attack relation) is a subset of A x A.
Arguments may be any hashable value; the examples use strings.
"""

from typing import FrozenSet, Hashable, Iterable, Tuple

Argument = Hashable
Attack = Tuple[Argument, Argument]


def sort_key(x):
    """Deterministic ordering for arguments of arbitrary (mixed) types."""
    return (type(x).__name__, str(x))


def sorted_args(items: Iterable[Argument]) -> list:
    return sorted(items, key=sort_key)


def sorted_sets(sets: Iterable[FrozenSet[Argument]]) -> list:
    """Sort a collection of argument sets by size, then lexicographically."""
    return sorted(sets, key=lambda s: (len(s), [sort_key(a) for a in sorted_args(s)]))


class ArgumentationFramework:
    """Definition 5.1: AF = <A, ->>.

    Self-attacks (a, a) are allowed. Every attack must mention known arguments.
    """

    def __init__(self, arguments: Iterable[Argument], attacks: Iterable[Attack] = ()):
        self.arguments: FrozenSet[Argument] = frozenset(arguments)
        attacks = frozenset((a, b) for a, b in attacks)
        for a, b in attacks:
            if a not in self.arguments or b not in self.arguments:
                raise ValueError(f"attack ({a!r}, {b!r}) mentions an unknown argument")
        self.attacks: FrozenSet[Attack] = attacks

        attackers = {a: set() for a in self.arguments}
        attacked_by = {a: set() for a in self.arguments}
        for a, b in attacks:
            attackers[b].add(a)
            attacked_by[a].add(b)
        self._attackers = {a: frozenset(s) for a, s in attackers.items()}
        self._attacked_by = {a: frozenset(s) for a, s in attacked_by.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "ArgumentationFramework":
        """Build from {"arguments": [...], "attacks": [[a, b], ...]}."""
        return cls(data["arguments"], [tuple(x) for x in data["attacks"]])

    def __repr__(self) -> str:
        args = ", ".join(map(str, sorted_args(self.arguments)))
        atts = ", ".join(f"{a}->{b}" for a, b in sorted(self.attacks, key=lambda t: (sort_key(t[0]), sort_key(t[1]))))
        return f"AF(A={{{args}}}, attacks={{{atts}}})"

    def __eq__(self, other) -> bool:
        return (isinstance(other, ArgumentationFramework)
                and self.arguments == other.arguments and self.attacks == other.attacks)

    def __hash__(self) -> int:
        return hash((self.arguments, self.attacks))

    # ----- basic accessors -------------------------------------------------

    def _check(self, S: Iterable[Argument]) -> FrozenSet[Argument]:
        S = frozenset(S)
        unknown = S - self.arguments
        if unknown:
            raise ValueError(f"unknown arguments: {sorted_args(unknown)}")
        return S

    def attackers(self, a: Argument) -> FrozenSet[Argument]:
        """a^- = {b in A | b -> a}."""
        self._check([a])
        return self._attackers[a]

    def attacked_by(self, a: Argument) -> FrozenSet[Argument]:
        """{b in A | a -> b}."""
        self._check([a])
        return self._attacked_by[a]

    def plus(self, S: Iterable[Argument]) -> FrozenSet[Argument]:
        """S^+ = {b in A | a -> b for some a in S}."""
        S = self._check(S)
        out = set()
        for a in S:
            out |= self._attacked_by[a]
        return frozenset(out)

    def range(self, S: Iterable[Argument]) -> FrozenSet[Argument]:
        """S u S^+ (used by semi-stable semantics)."""
        S = self._check(S)
        return S | self.plus(S)

    def restrict(self, subset: Iterable[Argument]) -> "ArgumentationFramework":
        """The sub-framework induced by `subset` (attacks restricted to subset x subset)."""
        R = self._check(subset)
        return ArgumentationFramework(R, ((a, b) for a, b in self.attacks if a in R and b in R))

    # ----- Definitions 5.2 - 5.5 -------------------------------------------

    def is_conflict_free(self, S: Iterable[Argument]) -> bool:
        """Def 5.2: S is conflict-free iff S n S^+ = {} (no a, b in S with a -> b)."""
        S = self._check(S)
        return not (S & self.plus(S))

    def defends(self, S: Iterable[Argument], a: Argument) -> bool:
        """Def 5.2: S defends a iff a^- is a subset of S^+."""
        S = self._check(S)
        return self.attackers(a) <= self.plus(S)

    def characteristic(self, S: Iterable[Argument]) -> FrozenSet[Argument]:
        """Def 5.3: F(S) = {a in A | S defends a}."""
        S = self._check(S)
        S_plus = self.plus(S)
        return frozenset(a for a in self.arguments if self._attackers[a] <= S_plus)

    def is_admissible(self, S: Iterable[Argument]) -> bool:
        """Def 5.4: S is conflict-free and S is a subset of F(S)."""
        S = self._check(S)
        return self.is_conflict_free(S) and S <= self.characteristic(S)

    def is_complete(self, S: Iterable[Argument]) -> bool:
        """Def 5.5: S is conflict-free and S = F(S)."""
        S = self._check(S)
        return self.is_conflict_free(S) and S == self.characteristic(S)


def format_set(S: Iterable[Argument]) -> str:
    return "{" + ", ".join(map(str, sorted_args(S))) + "}"
