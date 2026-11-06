import unittest

from argframe import ArgumentationFramework, acceptance_status, acceptance_report
from examples.book_examples import FIG_5_1, FIG_5_2, THREE_CYCLE, build

S, C, R = "skeptically accepted", "credulously accepted", "rejected"


class TestAcceptance(unittest.TestCase):
    def test_fig_5_1(self):
        af = build(FIG_5_1)
        for sem in ("grounded", "complete", "preferred", "stable", "semi_stable"):
            rep = acceptance_report(af, sem)
            self.assertEqual(rep, {"α1": S, "α2": R, "α3": S, "α4": R, "α5": S})

    def test_fig_5_2_preferred(self):
        af = build(FIG_5_2)
        self.assertEqual(acceptance_report(af, "preferred"), {"α1": C, "α2": C, "α3": S})

    def test_fig_5_2_grounded(self):
        af = build(FIG_5_2)
        self.assertEqual(acceptance_report(af, "grounded"), {"α1": R, "α2": R, "α3": S})

    def test_fig_5_2_complete(self):
        af = build(FIG_5_2)
        self.assertEqual(acceptance_report(af, "complete"), {"α1": C, "α2": C, "α3": S})

    def test_no_extensions_means_rejected(self):
        af = build(THREE_CYCLE)
        self.assertEqual(acceptance_report(af, "stable"), {"a": R, "b": R, "c": R})

    def test_errors(self):
        af = ArgumentationFramework("a", [])
        with self.assertRaises(ValueError):
            acceptance_status(af, "a", "bogus")
        with self.assertRaises(ValueError):
            acceptance_status(af, "zz")


if __name__ == "__main__":
    unittest.main()
