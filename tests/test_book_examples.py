import itertools
import unittest

from argframe import (all_extensions, grounded_trace, admissible_sets,
                      legal_labellings, is_legal_labelling)
from examples.book_examples import EXAMPLES, FIG_5_1, FIG_5_2, build, fs


def powerset(items):
    items = list(items)
    for r in range(len(items) + 1):
        for c in itertools.combinations(items, r):
            yield frozenset(c)


class TestExpectedExtensions(unittest.TestCase):
    def test_all_examples_all_semantics(self):
        for name, ex in EXAMPLES.items():
            af = build(ex)
            got = all_extensions(af)
            for sem, expected in ex["expected"].items():
                with self.subTest(example=name, semantics=sem):
                    self.assertEqual(set(got[sem]), set(expected))
                    self.assertEqual(len(got[sem]), len(expected))


class TestFigure51(unittest.TestCase):
    def setUp(self):
        self.af = build(FIG_5_1)

    def test_defense_p182(self):
        self.assertTrue(self.af.defends(fs("α3", "α5"), "α1"))
        self.assertFalse(self.af.defends(fs("α3"), "α1"))

    def test_example_5_5_admissible(self):
        self.assertEqual(set(admissible_sets(self.af)), set(FIG_5_1["admissible"]))
        for S in FIG_5_1["admissible"]:
            self.assertTrue(self.af.is_admissible(S))
        self.assertFalse(self.af.is_admissible(fs("α1")))
        self.assertFalse(self.af.is_admissible(fs("α1", "α3")))

    def test_example_5_6(self):
        self.assertEqual(self.af.characteristic(fs("α3")), fs("α3", "α5"))
        self.assertEqual(self.af.characteristic(fs("α5")), fs("α3", "α5"))
        self.assertEqual(self.af.characteristic(fs("α1", "α3", "α5")), fs("α1", "α3", "α5"))
        for S in (fs("α3", "α5"), fs("α3"), fs("α5")):
            self.assertTrue(self.af.is_admissible(S))
            self.assertFalse(self.af.is_complete(S))
        self.assertTrue(self.af.is_complete(fs("α1", "α3", "α5")))

    def test_grounded_trace_p184(self):
        self.assertEqual(grounded_trace(self.af), FIG_5_1["grounded_trace"])


class TestFigure52(unittest.TestCase):
    def test_three_labellings(self):
        af = build(FIG_5_2)
        labs = legal_labellings(af)
        self.assertEqual(len(labs), 3)
        for L in labs:
            self.assertTrue(is_legal_labelling(af, L))
        as_tuples = {tuple(L[a] for a in ("α1", "α2", "α3")) for L in labs}
        self.assertEqual(as_tuples, {("undec", "undec", "in"),   # L^G
                                     ("in", "out", "in"),        # L1
                                     ("out", "in", "in")})       # L2


class TestBruteForceOnExamples(unittest.TestCase):
    def test_labellings_match_brute_force(self):
        for name, ex in EXAMPLES.items():
            af = build(ex)
            args = sorted(af.arguments)
            brute = []
            for vals in itertools.product(("in", "out", "undec"), repeat=len(args)):
                L = dict(zip(args, vals))
                if is_legal_labelling(af, L):
                    brute.append(L)
            with self.subTest(example=name):
                self.assertEqual(len(brute), len(legal_labellings(af)))
                self.assertEqual(
                    {frozenset(a for a, v in L.items() if v == "in") for L in brute},
                    set(all_extensions(af)["complete"]))


if __name__ == "__main__":
    unittest.main()
