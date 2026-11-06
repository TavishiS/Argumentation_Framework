"""Argument status (Rahwan, Ch. 5, Definition 5.8)."""

from typing import Dict

from .framework import ArgumentationFramework, sorted_args
from .semantics import all_extensions

SKEPTICAL = "skeptically accepted"
CREDULOUS = "credulously accepted"
REJECTED = "rejected"

SEMANTICS = ("grounded", "complete", "preferred", "stable", "semi_stable")


def acceptance_status(af: ArgumentationFramework, a, semantics: str = "preferred") -> str:
    """6E. Status of `a` w.r.t. the extensions of the chosen semantics.

    skeptically accepted: a is in every extension (and at least one extension
    exists); credulously accepted: in some but not all; rejected: in none.
    If the semantics has no extension at all (e.g. stable on an odd cycle),
    no argument belongs to one, so every argument is rejected.
    """
    if semantics not in SEMANTICS:
        raise ValueError(f"unknown semantics {semantics!r}; choose from {SEMANTICS}")
    if a not in af.arguments:
        raise ValueError(f"unknown argument {a!r}")
    exts = all_extensions(af)[semantics]
    containing = sum(1 for E in exts if a in E)
    if exts and containing == len(exts):
        return SKEPTICAL
    if containing > 0:
        return CREDULOUS
    return REJECTED


def acceptance_report(af: ArgumentationFramework, semantics: str = "preferred") -> Dict:
    return {a: acceptance_status(af, a, semantics) for a in sorted_args(af.arguments)}
