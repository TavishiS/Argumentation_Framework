"""Random instance generation for the strategic-argumentation experiments."""

import random
from typing import List, Sequence, Tuple


def random_instance(rng: random.Random, p: float, n_choices: Sequence[int] = (6, 7, 8),
                    n_agents: int = 3) -> Tuple[List[str], List[Tuple[str, str]], List[frozenset]]:
    """Return (arguments, attacks, types).

    * n is drawn uniformly from n_choices.
    * Every ordered pair (a, b), INCLUDING self-attacks (a, a), is an attack
      independently with probability p.
    * Each argument goes to one of the agents uniformly at random (so the types
      partition the arguments); redrawn until every agent holds >= 1 argument.
    """
    n = rng.choice(list(n_choices))
    args = [f"a{k}" for k in range(1, n + 1)]
    attacks = [(a, b) for a in args for b in args if rng.random() < p]
    while True:
        owner = [rng.randrange(n_agents) for _ in args]
        if len(set(owner)) == n_agents:
            break
    types = [frozenset(a for a, o in zip(args, owner) if o == i) for i in range(n_agents)]
    return args, attacks, types
