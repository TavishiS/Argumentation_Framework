# Report – Argumentation Engine and Strategic Argumentation

Source for all definitions and theorems: Rahwan, *Argumentation among Agents*, Ch. 5 (`docs/chapter5.pdf`).
Every number below is produced by the code in this repository (`results/summary.csv`,
`results/q2_q3_examples.md`); the experiment is fully reproducible (seed 42).

## 1. What was built

**Part 1 – engine** (`argframe/framework.py, semantics.py, labelling.py, acceptance.py`)

* `ArgumentationFramework(A, ⇀)` with `is_conflict_free`, `defends`, `characteristic` (F),
  `is_admissible`, `is_complete` (Definitions 5.2–5.5).
* Grounded extension (least fixed point of F by iteration from ∅), all complete extensions
  (backtracking over conflict-free sets), preferred (⊆-maximal complete), stable (S⁺ = A∖S) and
  semi-stable (complete with ⊆-maximal S ∪ S⁺) extensions (Definition 5.7).
* All legal in/out/undec labellings (Definition 5.6), cross-checked against Table 5.1.
* Skeptical / credulous / rejected status (Definition 5.8) under any of the five semantics.

**Part 2 – strategic argumentation** (`argframe/strategic.py`)

* `grounded_mechanism`: grounded extension of the framework induced by the union of the revealed sets.
* `best_responses`: enumerates all 2^|A_i| reports of agent *i* against fixed reports of the others and
  returns every utility-maximising report.
* `satisfies_theorem_5_3`: exact, exhaustive strategyproofness test (every agent × every combination
  of the others' subsets × every hidden subset), returning a concrete profitable deviation when it fails.
* `theorem_5_4_condition`: the odd-path condition on the full graph. Cycles are handled with a BFS over
  (vertex, parity) states, which terminates on any graph.

## 2. Validation

* 52 unit/property tests (`python3 -m unittest discover -s tests`), all passing.
* The expected values of Figures 5.1, 5.2, 5.3(i) and Examples 5.5–5.8, 5.10, 5.11 come from the
  chapter text (or were derived by hand), never from the code's own output. Edge cases: 3-cycle (no
  stable extension), self-attack, 4-cycle, a framework where preferred ≠ semi-stable, empty framework.
* Randomised cross-checks on hundreds of random frameworks: complete extensions against brute force over
  all 2ⁿ subsets; legal labellings against brute force over all 3ⁿ labellings; extensions derived from
  labellings (Table 5.1) against the direct definitions; the memoised Theorem 5.3 check against a naive
  one that calls the mechanism every time; odd-walk and odd-simple-path search against exhaustive
  enumeration.

**Misprints in the chapter.** (1) Example 5.10: the utilities of y and z are written with each other's
argument sets; by the definition u_y = 0 and u_z = 1. (2) After Example 5.11 the text says α5 cancels the
indirect self-defeat; it is α6 (unattacked, defeats α3). The code and tests follow the definitions.

**Examples from the chapter reproduced** (`python3 demo.py`, `results/demo_output.txt`): grounded
trace ∅ → {α3,α5} → {α1,α3,α5} (Fig. 5.1); three complete extensions/labellings for Fig. 5.2;
grounded extension {a,c,e} for Fig. 5.3(i); in Example 5.10 x's unique best response is {α4,α5}
(utility 2 vs 1), so the mechanism is not strategyproof; Example 5.11 is strategyproof even though the
Theorem 5.4 condition fails.

## 3. Experiment

3 agents; n ∈ {6,7,8} arguments uniformly; every ordered pair (including self-attacks) is an attack with
probability p ∈ {0.15, 0.25, 0.35}; arguments assigned uniformly at random to the 3 agents (redrawn until
each agent has at least one); 1000 instances per p, 3000 in total. For each instance the exact
Theorem 5.3 test and the Theorem 5.4 condition were evaluated.

### Q1 – fraction of strategyproof instances

| p | instances | strategyproof | fraction | Thm 5.4 condition holds |
|---|---|---|---|---|
| 0.15 | 1000 | 544 | **0.544** | 38 (0.038) |
| 0.25 | 1000 | 269 | **0.269** | 9 (0.009) |
| 0.35 | 1000 | 123 | **0.123** | 0 (0.000) |
| all | 3000 | 936 | 0.312 | 47 (0.016) |

![fraction strategyproof](results/plots/strategyproof_fraction.png)

Strategyproofness becomes rare quickly as the graph gets denser: more attacks create more chains
α₁ ⇀ … ⇀ α₂ among one agent's arguments, and every such chain is a chance for hiding to pay.

### Q2 – condition holds but strategyproofness fails

| p | cond holds & SP | cond holds & not SP | cond fails & SP | cond fails & not SP |
|---|---|---|---|---|
| 0.15 | 38 | **0** | 506 | 456 |
| 0.25 | 9 | **0** | 260 | 731 |
| 0.35 | 0 | **0** | 123 | 877 |
| all | 47 | **0** | 889 | 2064 |

**There are no such instances**, under any of the three readings of the condition (`book`, `simple`,
`distinct`; see README). That is what Theorem 5.4 predicts: the condition is *sufficient* for
strategyproofness, so it can never hold for a manipulable instance. It is also a useful end-to-end check of
the implementation: 47 (book reading) instances satisfying the condition were each verified strategyproof
by the exhaustive Theorem 5.3 search, which shares no code with the path search.

The reading matters only a little on random data: `simple` gives exactly the same counts as `book`,
and `distinct` (which ignores conflict-freeness and α₁ = α₂) holds on 123 instances instead of 47, still
with zero counterexamples. The readings can differ on specific graphs, e.g. α⇀x⇀β plus an odd cycle
x⇀y⇀z⇀x, with agents {α,β}, {x}, {y}, {z}: the only simple α→β path has length 2, but an odd *walk*
(through the cycle, length 5) exists. The `book` and `distinct` readings reject this instance, `simple`
accepts it (the instance happens to be strategyproof, so no reading is contradicted; this is why the
code treats cycles via walks).

### Q3 – strategyproof although the condition fails

889 of 3000 instances (29.6%; 52.6% / 26.2% / 12.3% of the condition-failing instances for
p = 0.15 / 0.25 / 0.35). So the condition is far from necessary, as the chapter says with Example 5.11.
Why they are strategyproof (full list: `results/q2_q3_examples.md`):

* **884 instances violate the condition through an explicit conflict inside one agent's own type**
  (an attack between two of its arguments, or a self-attack). An internal conflict does not by itself make
  hiding profitable, because hiding one of two conflicting arguments gives up the argument that was
  hidden to free the other: at best a tie. The recorded reasons (an instance can have several):
  hiding only ever lowers utility (407); hiding frees one of the agent's own arguments but costs at least
  as many others (385); hiding never changes the agent's utility (92); and 5 contain a cancelling argument
  in the sense of Example 5.11.
  * Instance p=0.15 #158: only attack a2⇀a6, with a2, a6 ∈ A_x. a6 is out; hiding a2 frees a6 but loses
    a2 (3 → 3, a tie); hiding a6 changes nothing (it is out anyway); hiding a1 or a4 loses an accepted
    argument.
  * Instance p=0.15 #9: a3⇀a5, a5⇀a5 with a3, a5 ∈ A_x. a5 is never accepted, so hiding it changes
    nothing, and hiding a3 loses it.
* **5 instances have only an indirect odd path** (every type conflict-free), e.g. p=0.25 #804 with
  A_z = {a1, a6} and attacks a2⇀a1, a4⇀a2, a4⇀a3, a6⇀a2, a6⇀a4. Path a6 ⇀ a4 ⇀ a2 ⇀ a1 is odd, so the
  condition fails, but a6 also defeats a2 directly (even path a6 ⇀ a2 ⇀ a1: a6 *defends* a1). Truthfully
  both are accepted (u_z = 2). Against truthful x and y, hiding a6 lets a4 in, but a4 still defeats a2, so a1 stays in and z only
  loses a6 (u = 1). In all five cases the best deviation only lowers utility; in four of them walks of
  both parities link the violating pair (the fifth is a closed odd walk a2 → a7 → a8 → a2), so attack
  and defence effects can cancel.
* **Example 5.11** is the textbook case: x holds α1, α4, α5, α6 with α1 ↪ α4, α1 ↪ α5, yet α6 (unattacked,
  defeats α3, wrongly called α5 in the text) keeps α3 out whatever is revealed, so α1, α4, α5 are accepted
  regardless and x's best response is to reveal everything. Removing α6 gives back Example 5.10, which is
  manipulable.

## 4. Limitations

* Only 6–8 arguments and 3 agents, as specified; fractions have a sampling error of up to about ±3 percentage points
  (95% interval, 1000 instances per p).
* Types are a partition of the arguments in the experiment; the code also accepts overlapping types.
* "Explicit conflict" vs "indirect only" in Q3 is classified from the graph; the "reason" tags
  are computed by exhaustive enumeration of the agent's deviations, but they are descriptions of
  the observed behaviour, not proofs.
