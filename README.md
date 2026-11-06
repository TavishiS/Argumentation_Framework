# Argumentation Engine and Strategic Argumentation

Assignment 3 (Autonomous Systems). Implementation of

1. **Part 1** – Dung-style abstract argumentation frameworks: conflict-freeness, defence, the
   characteristic function, admissible / complete / grounded / preferred / stable / semi-stable
   extensions, legal (in/out/undec) labellings and argument status.
2. **Part 2** – the grounded direct argumentation mechanism, best responses, an exact
   strategyproofness check (Theorem 5.3), the sufficient graph condition (Theorem 5.4) and a
   random experiment over 3000 instances.

All definitions follow Rahwan, *Argumentation among Agents* (Ch. 5, `docs/chapter5.pdf`).

## Requirements and quick start

Python 3.8+ (developed on 3.12). The engine uses only the standard library; `matplotlib` is needed
only for the plots (`pip install -r requirements.txt`).

```bash
python3 -m unittest discover -s tests -v      # 52 tests
python3 demo.py                               # demonstration (saved copy: results/demo_output.txt)
python3 experiments/run_experiments.py        # 3000 random instances -> results/instances.jsonl (~4 s)
python3 experiments/analyse.py                # tables, plots, annotated Q2/Q3 instances
```

Run everything from the project root. Experiment options:
`--ps 0.15 0.25 0.35 --per-p 1000 --seed 42`.

## Assignment item → code

| Assignment item | Where |
|---|---|
| P1.1 framework class | `argframe/framework.py` → `ArgumentationFramework(arguments, attacks)` |
| P1.2 conflict-free | `ArgumentationFramework.is_conflict_free(S)` |
| P1.3 S defends argument | `ArgumentationFramework.defends(S, a)` |
| P1.4 characteristic function | `ArgumentationFramework.characteristic(S)` |
| P1.5 admissible / complete | `is_admissible(S)`, `is_complete(S)` |
| P1.6A grounded | `semantics.grounded_extension(af)` (and `grounded_trace` for F^k(∅)) |
| P1.6B complete extensions | `semantics.complete_extensions(af)` |
| P1.6C preferred, stable, semi-stable | `preferred_extensions`, `stable_extensions`, `semi_stable_extensions`, `all_extensions` |
| P1.6D labellings | `labelling.legal_labellings(af)`, `is_legal_labelling`, `extensions_via_labellings` (Table 5.1) |
| P1.6E acceptance status | `acceptance.acceptance_status(af, a, semantics)`, `acceptance_report` |
| P2.1 mechanism | `strategic.grounded_mechanism(attacks, reports)` |
| P2.2 best responses | `strategic.best_responses(attacks, types, i, reports)` |
| P2.3 Theorem 5.3 check | `strategic.satisfies_theorem_5_3(attacks, types)` (alias `is_strategyproof`) |
| P2.4 Theorem 5.4 check | `strategic.theorem_5_4_condition(attacks, types, mode)` |
| Experiments | `argframe/generator.py`, `experiments/run_experiments.py`, `experiments/analyse.py` |

Book examples (Figures 5.1–5.3, Examples 5.10, 5.11) and edge cases with their expected results:
`examples/book_examples.py`, tested in `tests/test_book_examples.py`.

## Design notes and conventions

* **Arguments** are any hashable values; **attacks** are `(attacker, target)` pairs; self-attacks are
  allowed. Functions return frozensets, and lists of extensions are sorted (by size, then
  lexicographically), so output is deterministic.
* **Acceptance status** (Def. 5.8) – skeptical = in every extension; credulous = in some but not all;
  rejected = in none. If the chosen semantics has no extension (e.g. stable on an odd cycle), every
  argument is reported *rejected*.
* **Mechanism** – agents may only hide arguments. The outcome is the grounded extension of the
  framework induced by the union of revealed arguments (global attacks restricted to it). Utility of
  agent *i* is `|A_i ∩ outcome|`.
* **Theorem 5.3 check** is exhaustive: for every agent and every combination of subsets revealed by
  the others, truthful revelation must be a best response. Outcomes are memoised by the revealed
  union, so each instance needs at most 2^n grounded computations.
* **Theorem 5.4 condition** – "no α₁, α₂ ∈ A_i with an odd-length path α₁ ↪ α₂, and A_i
  conflict-free", evaluated on the full graph. Cycles are handled by a BFS over (vertex, parity)
  states. The text leaves the exact reading open, so three modes are provided:
  * `book` (default): paths are *walks* (vertices may repeat), α₁ = α₂ is allowed (an odd cycle
    through an argument counts), and A_i must be conflict-free;
  * `simple`: only odd-length *simple* paths between distinct arguments (plus conflict-freeness);
  * `distinct`: walks, α₁ ≠ α₂, no separate conflict-free requirement (the assignment's literal
    "two arguments α, β").

  The experiments record all three; Q2/Q3 in the report use `book` and give the others as a
  sensitivity check.

## Misprints in the chapter (handled in code, tests and report)

1. Example 5.10 lists `u_y = 1` and `u_z = 0` with the argument sets swapped. With A_y = {α2},
   A_z = {α3} and outcome {α1, α3}, the definition gives **u_y = 0, u_z = 1**.
2. The discussion after Example 5.11 names α5 as the argument that cancels the indirect
   self-defeat. It is **α6**: it is unattacked and defeats α3, so α3 is never accepted while α6 is
   revealed.

## Layout

```
argframe/        framework.py semantics.py labelling.py acceptance.py strategic.py generator.py
examples/        book_examples.py
experiments/     run_experiments.py analyse.py
tests/           unit, book-example and randomised brute-force cross-check tests
results/         instances.jsonl summary.csv summary.md q2_q3_examples.md plots/ demo_output.txt
docs/chapter5.pdf
demo.py   REPORT.md
```
