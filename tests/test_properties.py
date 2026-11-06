"""Randomised cross-checks of the optimised code against brute force."""

import itertools
import random
import unittest

from argframe import (ArgumentationFramework, all_extensions, grounded_extension,
                      legal_labellings, is_legal_labelling, extensions_via_labellings,
                      grounded_mechanism, utility, best_responses, satisfies_theorem_5_3,
                      is_strategyproof, theorem_5_4_condition, random_instance)
from argframe.strategic import (subsets, odd_walk, odd_simple_path, _successors,
                                _attackers_map, _grounded_fast)


def random_af(rng, max_n=7):
    n = rng.randint(0, max_n)
    args = list(range(n))
    p = rng.choice([0.1, 0.2, 0.3, 0.5])
    attacks = [(a, b) for a in args for b in args if rng.random() < p]
    return ArgumentationFramework(args, attacks)


def subsets(items):
    items = list(items)
    for r in range(len(items) + 1):
        for c in itertools.combinations(items, r):
            yield frozenset(c)


def maximal(sets):
    return {S for S in sets if not any(S < T for T in sets)}


def minimal(sets):
    return {S for S in sets if not any(T < S for T in sets)}


class TestPart1Properties(unittest.TestCase):
    N = 300

    def test_against_brute_force(self):
        rng = random.Random(12345)
        for _ in range(self.N):
            af = random_af(rng)
            ext = all_extensions(af)

            # brute-force definitions over all 2^n subsets
            complete = {S for S in subsets(af.arguments) if af.is_complete(S)}
            self.assertEqual(set(ext["complete"]), complete)
            self.assertEqual(len(ext["complete"]), len(complete))
            self.assertEqual(set(ext["preferred"]), maximal(complete))
            stable = {S for S in subsets(af.arguments)
                      if af.is_conflict_free(S) and af.plus(S) == af.arguments - S}
            self.assertEqual(set(ext["stable"]), stable)
            ranges = {S: af.range(S) for S in complete}
            semi = {S for S in complete if not any(ranges[S] < ranges[T] for T in complete)}
            self.assertEqual(set(ext["semi_stable"]), semi)

            # grounded = minimal complete = intersection of complete
            g = grounded_extension(af)
            self.assertEqual({g}, minimal(complete))
            self.assertEqual(g, frozenset.intersection(*complete))
            for P in ext["preferred"]:
                self.assertLessEqual(g, P)

            # hierarchy
            self.assertLessEqual(set(ext["stable"]), set(ext["semi_stable"]))
            self.assertLessEqual(set(ext["semi_stable"]), set(ext["preferred"]))
            self.assertLessEqual(set(ext["preferred"]), set(ext["complete"]))
            if ext["stable"]:
                self.assertEqual(set(ext["semi_stable"]), set(ext["stable"]))
            self.assertTrue(ext["preferred"])   # at least one preferred always exists

    def test_labellings_brute_force_and_table_5_1(self):
        rng = random.Random(777)
        for _ in range(self.N // 3):
            af = random_af(rng, max_n=6)
            args = sorted(af.arguments)
            brute = []
            for vals in itertools.product(("in", "out", "undec"), repeat=len(args)):
                L = dict(zip(args, vals))
                if is_legal_labelling(af, L):
                    brute.append(L)
            labs = legal_labellings(af)
            self.assertEqual(len(brute), len(labs))
            key = lambda L: tuple(sorted(L.items()))
            self.assertEqual({key(L) for L in brute}, {key(L) for L in labs})

            ext = all_extensions(af)
            via = extensions_via_labellings(af)
            self.assertEqual(set(via["grounded"]), set(ext["grounded"]))
            self.assertEqual(set(via["preferred"]), set(ext["preferred"]))
            self.assertEqual(set(via["semi_stable"]), set(ext["semi_stable"]))
            self.assertEqual(set(via["stable"]), set(ext["stable"]))


class TestPart2Properties(unittest.TestCase):
    N = 300

    @staticmethod
    def instances(seed, n, n_choices=(4, 5, 6)):
        rng = random.Random(seed)
        for _ in range(n):
            p = rng.choice([0.1, 0.2, 0.3, 0.4])
            yield random_instance(rng, p, n_choices=n_choices)

    @staticmethod
    def naive_strategyproof(attacks, types):
        """Direct transcription of Theorem 5.3 calling the mechanism every time."""
        for i, Ai in enumerate(types):
            others = [j for j in range(len(types)) if j != i]
            for combo in itertools.product(*(subsets(types[j]) for j in others)):
                profile = list(types)
                for j, c in zip(others, combo):
                    profile[j] = c
                base = utility(Ai, grounded_mechanism(attacks, profile))
                for S in subsets(Ai):
                    profile[i] = Ai - S
                    if utility(Ai, grounded_mechanism(attacks, profile)) > base:
                        return False
        return True

    def test_fast_grounded_equals_mechanism(self):
        for args, attacks, types in self.instances(1, 100):
            att = _attackers_map(attacks)
            for R in subsets(args):
                self.assertEqual(_grounded_fast(R, att), grounded_mechanism(attacks, [R]))

    def test_memoised_check_equals_naive(self):
        for args, attacks, types in self.instances(2, self.N):
            self.assertEqual(is_strategyproof(attacks, types)[0],
                             self.naive_strategyproof(attacks, types))

    def test_best_response_consistency(self):
        for args, attacks, types in self.instances(3, 60, n_choices=(4, 5)):
            sp, w = satisfies_theorem_5_3(attacks, types)
            if not sp:
                # the witness really is a profitable deviation
                i = w["agent"]
                profile = [w["others_reports"].get(j, types[i]) for j in range(len(types))]
                profile[i] = types[i]
                self.assertEqual(utility(types[i], grounded_mechanism(attacks, profile)),
                                 w["truthful_utility"])
                profile[i] = w["better_report"]
                self.assertEqual(utility(types[i], grounded_mechanism(attacks, profile)),
                                 w["better_utility"])
                self.assertGreater(w["better_utility"], w["truthful_utility"])
            else:
                for i in range(len(types)):
                    others = [j for j in range(len(types)) if j != i]
                    for combo in itertools.product(*(subsets(types[j]) for j in others)):
                        profile = list(types)
                        for j, c in zip(others, combo):
                            profile[j] = c
                        _, best = best_responses(attacks, types, i, profile)
                        self.assertIn(types[i], best)

    def test_theorem_5_4_is_sufficient(self):
        """Condition (book reading) => strategyproof, on random instances."""
        checked = 0
        for args, attacks, types in self.instances(4, self.N):
            if theorem_5_4_condition(attacks, types, "book")[0]:
                checked += 1
                self.assertTrue(satisfies_theorem_5_3(attacks, types)[0],
                                (attacks, types))
        self.assertGreater(checked, 0)

    def test_walk_mode_equals_brute_force_walks(self):
        for args, attacks, types in self.instances(5, 100):
            n = len(args)
            succ = _successors(attacks)
            reach = {a: {a: True} for a in args}   # walks of length k as sets
            cur = {a: {a} for a in args}
            odd = {a: set() for a in args}
            for k in range(1, 2 * n + 1):
                cur = {a: {y for x in cur[a] for y in succ.get(x, ())} for a in args}
                if k % 2 == 1:
                    for a in args:
                        odd[a] |= cur[a]
            for a in args:
                for b in args:
                    self.assertEqual(odd_walk(succ, a, b) is not None, b in odd[a])

    def test_simple_path_equals_brute_force(self):
        for args, attacks, types in self.instances(6, 100, n_choices=(4, 5, 6)):
            succ = _successors(attacks)
            for a in args:
                for b in args:
                    if a == b:
                        continue
                    found = False
                    others = [x for x in args if x not in (a, b)]
                    for r in range(len(others) + 1):
                        for mid in itertools.permutations(others, r):
                            path = [a, *mid, b]
                            if len(path) % 2 == 0 and all(
                                    y in succ.get(x, ()) for x, y in zip(path, path[1:])):
                                found = True
                    self.assertEqual(odd_simple_path(succ, a, b) is not None, found)

    def test_generator_shape(self):
        rng = random.Random(0)
        for _ in range(200):
            args, attacks, types = random_instance(rng, 0.25)
            self.assertIn(len(args), (6, 7, 8))
            self.assertEqual(len(types), 3)
            self.assertTrue(all(types))
            self.assertEqual(frozenset().union(*types), frozenset(args))
            self.assertEqual(sum(len(t) for t in types), len(args))
            self.assertTrue(set(attacks) <= {(a, b) for a in args for b in args})


if __name__ == "__main__":
    unittest.main()
