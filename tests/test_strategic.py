import itertools
import unittest

from argframe import (grounded_mechanism, utility, best_responses, satisfies_theorem_5_3,
                      is_strategyproof, theorem_5_4_condition, is_strategyproof_by_theorem_5_4)
from argframe.strategic import subsets, odd_walk, odd_simple_path, _successors
from examples.book_examples import (EX_5_10_ATTACKS, EX_5_10_TYPES, EX_5_11_ATTACKS,
                                    EX_5_11_TYPES, fs)

X, Y, Z = 0, 1, 2


class TestMechanism(unittest.TestCase):
    def test_example_5_10_truthful(self):
        out = grounded_mechanism(EX_5_10_ATTACKS, EX_5_10_TYPES)
        self.assertEqual(out, fs("α1", "α3"))
        # utilities by definition (the book's text swaps y's and z's values)
        self.assertEqual(utility(EX_5_10_TYPES[X], out), 1)
        self.assertEqual(utility(EX_5_10_TYPES[Y], out), 0)
        self.assertEqual(utility(EX_5_10_TYPES[Z], out), 1)

    def test_example_5_10_withholding_alpha1(self):
        out = grounded_mechanism(EX_5_10_ATTACKS, [fs("α4", "α5"), fs("α2"), fs("α3")])
        self.assertEqual(out, fs("α2", "α4", "α5"))
        self.assertEqual(utility(EX_5_10_TYPES[X], out), 2)

    def test_only_revealed_arguments_and_attacks_count(self):
        # a -> b -> c but b is hidden: a and c are both unattacked
        self.assertEqual(grounded_mechanism([("a", "b"), ("b", "c")], [fs("a"), fs("c")]),
                         fs("a", "c"))
        self.assertEqual(grounded_mechanism([], [fs(), fs()]), fs())
        self.assertEqual(grounded_mechanism([("a", "a")], [fs("a")]), fs())


class TestBestResponses(unittest.TestCase):
    def test_example_5_10_x(self):
        u, best = best_responses(EX_5_10_ATTACKS, EX_5_10_TYPES, X,
                                 [fs(), fs("α2"), fs("α3")])
        self.assertEqual(u, 2)
        self.assertEqual(best, [fs("α4", "α5")])

    def test_reports_of_agent_itself_ignored(self):
        a = best_responses(EX_5_10_ATTACKS, EX_5_10_TYPES, X, [fs("α1"), fs("α2"), fs("α3")])
        b = best_responses(EX_5_10_ATTACKS, EX_5_10_TYPES, X, [fs(), fs("α2"), fs("α3")])
        self.assertEqual(a, b)

    def test_ties_are_all_returned(self):
        u, best = best_responses([("a", "a")], [fs("a")], 0, [fs()])
        self.assertEqual(u, 0)
        self.assertEqual(set(best), {fs(), fs("a")})
        self.assertEqual(len(best), 2)

    def test_truthful_best_when_no_attacks(self):
        u, best = best_responses([], [fs("a", "b")], 0, [fs()])
        self.assertEqual((u, best), (2, [fs("a", "b")]))

    def test_subsets_count(self):
        self.assertEqual(len(subsets("abc")), 8)


class TestTheorem53(unittest.TestCase):
    def test_example_5_10_not_strategyproof(self):
        ok, w = satisfies_theorem_5_3(EX_5_10_ATTACKS, EX_5_10_TYPES)
        self.assertFalse(ok)
        self.assertEqual(w["agent"], X)
        self.assertEqual(w["truthful_utility"], 1)
        self.assertEqual(w["better_utility"], 2)
        self.assertEqual(w["better_report"], fs("α4", "α5"))
        self.assertEqual(w["others_reports"], {Y: fs("α2"), Z: fs("α3")})

    def test_example_5_11_strategyproof(self):
        ok, w = satisfies_theorem_5_3(EX_5_11_ATTACKS, EX_5_11_TYPES)
        self.assertTrue(ok)
        self.assertIsNone(w)
        self.assertEqual(is_strategyproof(EX_5_11_ATTACKS, EX_5_11_TYPES), (True, None))

    def test_alpha6_is_the_cancelling_argument(self):
        # Book misprint: the text says alpha5; it is alpha6. Whenever alpha6 is
        # revealed, alpha3 is never accepted (alpha6 -> alpha3 and alpha6 unattacked).
        others = [fs("α1", "α4", "α5"), fs("α2"), fs("α3")]
        for r1 in subsets(others[0]):
            for r2 in subsets(others[1]):
                for r3 in subsets(others[2]):
                    out = grounded_mechanism(EX_5_11_ATTACKS, [r1 | {"α6"}, r2, r3])
                    self.assertNotIn("α3", out)
                    self.assertIn("α6", out)
        # without alpha6 (never revealed) we are back to Example 5.10
        ok, _ = satisfies_theorem_5_3(EX_5_11_ATTACKS, EX_5_10_TYPES)
        self.assertFalse(ok)

    def test_self_attack_is_strategyproof(self):
        self.assertTrue(satisfies_theorem_5_3([("a", "a")], [fs("a")])[0])

    def test_hiding_own_self_attacker_pays(self):
        # agent 0 holds a and b with a -> a, a -> b. Revealing a kills b? a is out
        # (self-attack) so b is attacked by a non-accepted argument... GE: a unattacked
        # by others but attacked by itself: not in; b attacked by a: not in. Hiding a
        # makes b unattacked -> in. So manipulation pays.
        ok, w = satisfies_theorem_5_3([("a", "a"), ("a", "b")], [fs("a", "b"), fs("c")])
        self.assertFalse(ok)
        self.assertEqual(w["better_report"], fs("b"))
        self.assertEqual((w["truthful_utility"], w["better_utility"]), (0, 1))


class TestTheorem54(unittest.TestCase):
    def test_example_5_10_fails(self):
        holds, w = theorem_5_4_condition(EX_5_10_ATTACKS, EX_5_10_TYPES)
        self.assertFalse(holds)
        self.assertEqual(w["agent"], X)
        self.assertEqual(w["kind"], "odd_path")
        self.assertEqual((w["alpha1"], w["alpha2"]), ("α1", "α4"))
        self.assertEqual(w["path"], ["α1", "α2", "α3", "α4"])     # length 3 (odd)
        self.assertFalse(is_strategyproof_by_theorem_5_4(EX_5_10_ATTACKS, EX_5_10_TYPES))

    def test_example_5_11_condition_fails_yet_strategyproof(self):
        holds, w = theorem_5_4_condition(EX_5_11_ATTACKS, EX_5_11_TYPES)
        self.assertFalse(holds)                                    # α1 ↪ α4, α1 ↪ α5
        self.assertTrue(satisfies_theorem_5_3(EX_5_11_ATTACKS, EX_5_11_TYPES)[0])

    def test_acyclic_condition_holds(self):
        attacks = [("a1", "a2"), ("a2", "a3")]
        types = [fs("a1", "a3"), fs("a2")]
        self.assertTrue(theorem_5_4_condition(attacks, types)[0])
        self.assertTrue(satisfies_theorem_5_3(attacks, types)[0])

    def test_explicit_conflict_detected(self):
        holds, w = theorem_5_4_condition([("a", "b")], [fs("a", "b")])
        self.assertFalse(holds)
        self.assertEqual(w["kind"], "conflict")

    def test_self_attack_detected_in_book_mode(self):
        self.assertFalse(theorem_5_4_condition([("a", "a")], [fs("a")], "book")[0])
        # 'distinct' reading ignores a == b, so a lone self-attacker is not flagged
        self.assertTrue(theorem_5_4_condition([("a", "a")], [fs("a")], "distinct")[0])

    def test_walk_vs_simple_path_cycles(self):
        # alpha -> x -> beta plus the odd cycle x -> y -> z -> x.
        # Simple paths alpha ~> beta: only alpha,x,beta (length 2, even).
        # Walks alpha ~> beta of odd length exist (go around the cycle once: 5).
        attacks = [("al", "x"), ("x", "be"), ("x", "y"), ("y", "z"), ("z", "x")]
        types = [fs("al", "be"), fs("x"), fs("y"), fs("z")]
        self.assertFalse(theorem_5_4_condition(attacks, types, "book")[0])
        self.assertTrue(theorem_5_4_condition(attacks, types, "simple")[0])
        h, w = theorem_5_4_condition(attacks, types, "distinct")
        self.assertFalse(h)
        self.assertEqual((w["alpha1"], w["alpha2"]), ("al", "be"))
        self.assertEqual(len(w["path"]) - 1, 5)

    def test_cycles_terminate(self):
        succ = _successors([("a", "b"), ("b", "a"), ("b", "c")])
        self.assertEqual(odd_walk(succ, "a", "b"), ["a", "b"])
        self.assertIsNone(odd_walk(succ, "a", "a"))     # only even closed walks
        self.assertEqual(odd_walk(succ, "b", "c"), ["b", "c"])
        self.assertIsNone(odd_walk(succ, "a", "c"))     # every a ~> c walk has even length
        self.assertIsNone(odd_simple_path(succ, "a", "a"))

    def test_odd_simple_path(self):
        succ = _successors([("a", "b"), ("b", "c"), ("c", "d")])
        self.assertEqual(odd_simple_path(succ, "a", "d"), ["a", "b", "c", "d"])
        self.assertIsNone(odd_simple_path(succ, "a", "c"))
        self.assertIsNone(odd_simple_path(succ, "d", "a"))

    def test_bad_mode(self):
        with self.assertRaises(ValueError):
            theorem_5_4_condition([], [fs("a")], "nope")


if __name__ == "__main__":
    unittest.main()
