import unittest

from argframe import ArgumentationFramework


class TestFramework(unittest.TestCase):
    def setUp(self):
        # chain a -> b -> c, self-attacker d
        self.af = ArgumentationFramework("abcd", [("a", "b"), ("b", "c"), ("d", "d")])

    def test_validation(self):
        with self.assertRaises(ValueError):
            ArgumentationFramework("ab", [("a", "z")])
        with self.assertRaises(ValueError):
            self.af.is_conflict_free({"zzz"})

    def test_attackers_and_plus(self):
        self.assertEqual(self.af.attackers("b"), frozenset("a"))
        self.assertEqual(self.af.plus({"a", "b"}), frozenset("bc"))
        self.assertEqual(self.af.plus(set()), frozenset())

    def test_conflict_free(self):
        self.assertTrue(self.af.is_conflict_free(set()))
        self.assertTrue(self.af.is_conflict_free({"a", "c"}))
        self.assertFalse(self.af.is_conflict_free({"a", "b"}))
        self.assertFalse(self.af.is_conflict_free({"d"}))   # self-attack

    def test_defends(self):
        self.assertTrue(self.af.defends({"a"}, "a"))        # no attackers
        self.assertTrue(self.af.defends({"a"}, "c"))        # a kills b
        self.assertFalse(self.af.defends(set(), "c"))
        self.assertFalse(self.af.defends({"a"}, "d"))

    def test_characteristic(self):
        self.assertEqual(self.af.characteristic(set()), frozenset("a"))
        self.assertEqual(self.af.characteristic({"a"}), frozenset("ac"))

    def test_admissible_complete(self):
        self.assertTrue(self.af.is_admissible(set()))
        self.assertTrue(self.af.is_admissible({"a", "c"}))
        self.assertFalse(self.af.is_admissible({"c"}))
        self.assertFalse(self.af.is_complete(set()))
        self.assertTrue(self.af.is_complete({"a", "c"}))
        self.assertFalse(self.af.is_complete({"a"}))

    def test_restrict(self):
        sub = self.af.restrict("ab")
        self.assertEqual(sub.arguments, frozenset("ab"))
        self.assertEqual(sub.attacks, frozenset([("a", "b")]))

    def test_from_dict_and_eq(self):
        af2 = ArgumentationFramework.from_dict(
            {"arguments": list("abcd"), "attacks": [["a", "b"], ["b", "c"], ["d", "d"]]})
        self.assertEqual(af2, self.af)


if __name__ == "__main__":
    unittest.main()
