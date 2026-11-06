"""Frameworks from Rahwan, "Argumentation among Agents" (Ch. 5), plus edge cases.

Expected values come from the text where it states them, otherwise from hand
derivation (noted in comments). They are never copied from the code's output.

Each entry of EXAMPLES: {"arguments", "attacks", "expected"} where expected
maps semantics name -> list of expected extensions (as frozensets).
"""

from argframe.framework import ArgumentationFramework


def fs(*xs):
    return frozenset(xs)


E = frozenset()

# ---- Figure 5.1 (Examples 5.5, 5.6, 5.8; grounded trace p.184) -------------
FIG_5_1 = {
    "arguments": ["α1", "α2", "α3", "α4", "α5"],
    "attacks": [("α3", "α2"), ("α2", "α1"), ("α5", "α4"), ("α4", "α1")],
    "expected": {
        "grounded": [fs("α1", "α3", "α5")],
        "complete": [fs("α1", "α3", "α5")],           # Ex 5.6
        "preferred": [fs("α1", "α3", "α5")],          # Ex 5.8
        "stable": [fs("α1", "α3", "α5")],             # by hand: S+ = {α2, α4} = A \ S
        "semi_stable": [fs("α1", "α3", "α5")],
    },
    # Ex 5.5: these are all the admissible sets (checked by hand)
    "admissible": [E, fs("α3"), fs("α5"), fs("α3", "α5"), fs("α1", "α3", "α5")],
    "grounded_trace": [E, fs("α3", "α5"), fs("α1", "α3", "α5"), fs("α1", "α3", "α5")],
}

# ---- Figure 5.2 (Examples 5.7, 5.8) ---------------------------------------
FIG_5_2 = {
    "arguments": ["α1", "α2", "α3"],
    "attacks": [("α1", "α2"), ("α2", "α1")],
    "expected": {
        "grounded": [fs("α3")],                                    # p.184
        "complete": [fs("α3"), fs("α1", "α3"), fs("α2", "α3")],    # Ex 5.7
        "preferred": [fs("α1", "α3"), fs("α2", "α3")],             # Ex 5.8
        "stable": [fs("α1", "α3"), fs("α2", "α3")],                # by hand
        "semi_stable": [fs("α1", "α3"), fs("α2", "α3")],
    },
}

# ---- Figure 5.3(i): grounded extension {a, c, e} (p.188) -------------------
FIG_5_3 = {
    "arguments": ["a", "b", "c", "d", "e"],
    "attacks": [("b", "a"), ("c", "b"), ("d", "b"), ("c", "d"), ("d", "c"), ("e", "d")],
    "expected": {
        "grounded": [fs("a", "c", "e")],
        "complete": [fs("a", "c", "e")],   # by hand: unique, adding b or d causes conflict
        "preferred": [fs("a", "c", "e")],
        "stable": [fs("a", "c", "e")],     # S+ = {b, d} = A \ S
        "semi_stable": [fs("a", "c", "e")],
    },
}

# ---- Strategic examples (Examples 5.10 and 5.11) ---------------------------
EX_5_10_ATTACKS = [("α1", "α2"), ("α2", "α3"), ("α3", "α4"), ("α3", "α5")]
EX_5_10_TYPES = [fs("α1", "α4", "α5"), fs("α2"), fs("α3")]   # agents x, y, z

EX_5_11_ATTACKS = EX_5_10_ATTACKS + [("α6", "α3")]
EX_5_11_TYPES = [fs("α1", "α4", "α5", "α6"), fs("α2"), fs("α3")]

# ---- Edge cases (all derived by hand) --------------------------------------
THREE_CYCLE = {
    "arguments": ["a", "b", "c"],
    "attacks": [("a", "b"), ("b", "c"), ("c", "a")],
    "expected": {"grounded": [E], "complete": [E], "preferred": [E],
                 "stable": [], "semi_stable": [E]},
}

SELF_ATTACK = {
    "arguments": ["a"],
    "attacks": [("a", "a")],
    "expected": {"grounded": [E], "complete": [E], "preferred": [E],
                 "stable": [], "semi_stable": [E]},
}

FOUR_CYCLE = {
    "arguments": ["a", "b", "c", "d"],
    "attacks": [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")],
    "expected": {"grounded": [E],
                 "complete": [E, fs("a", "c"), fs("b", "d")],
                 "preferred": [fs("a", "c"), fs("b", "d")],
                 "stable": [fs("a", "c"), fs("b", "d")],
                 "semi_stable": [fs("a", "c"), fs("b", "d")]},
}

# a <-> b, b -> c, c -> c : preferred {a},{b} but only {b} is stable/semi-stable
PREF_NOT_SEMI = {
    "arguments": ["a", "b", "c"],
    "attacks": [("a", "b"), ("b", "a"), ("b", "c"), ("c", "c")],
    "expected": {"grounded": [E],
                 "complete": [E, fs("a"), fs("b")],
                 "preferred": [fs("a"), fs("b")],
                 "stable": [fs("b")],
                 "semi_stable": [fs("b")]},
}

EMPTY_AF = {
    "arguments": [],
    "attacks": [],
    "expected": {"grounded": [E], "complete": [E], "preferred": [E],
                 "stable": [E], "semi_stable": [E]},
}

EXAMPLES = {
    "Figure 5.1": FIG_5_1,
    "Figure 5.2": FIG_5_2,
    "Figure 5.3(i)": FIG_5_3,
    "3-cycle": THREE_CYCLE,
    "self-attack": SELF_ATTACK,
    "4-cycle": FOUR_CYCLE,
    "preferred != semi-stable": PREF_NOT_SEMI,
    "empty": EMPTY_AF,
}


def build(example: dict) -> ArgumentationFramework:
    return ArgumentationFramework(example["arguments"], example["attacks"])
