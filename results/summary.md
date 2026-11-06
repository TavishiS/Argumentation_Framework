# Experiment summary

## Q1: fraction of strategyproof instances

| p | instances | strategyproof | fraction | condition (book) holds | fraction |
|---|---|---|---|---|---|
| 0.15 | 1000 | 544 | 0.544 | 38 | 0.038 |
| 0.25 | 1000 | 269 | 0.269 | 9 | 0.009 |
| 0.35 | 1000 | 123 | 0.123 | 0 | 0.000 |
| all | 3000 | 936 | 0.312 | 47 | 0.016 |

## Q2 / Q3 counts per reading of the Theorem 5.4 condition

Q2 = condition holds but NOT strategyproof; Q3 = strategyproof but condition fails.

| p | Q2 book | Q3 book | Q2 simple | Q3 simple | Q2 distinct | Q3 distinct |
|---|---|---|---|---|---|---|
| 0.15 | 0 | 506 | 0 | 506 | 0 | 444 |
| 0.25 | 0 | 260 | 0 | 260 | 0 | 248 |
| 0.35 | 0 | 123 | 0 | 123 | 0 | 121 |
| all | 0 | 889 | 0 | 889 | 0 | 813 |

## 2x2 contingency (book reading): rows = condition, columns = strategyproof

| p | cond holds & SP | cond holds & not SP | cond fails & SP | cond fails & not SP |
|---|---|---|---|---|
| 0.15 | 38 | 0 | 506 | 456 |
| 0.25 | 9 | 0 | 260 | 731 |
| 0.35 | 0 | 0 | 123 | 877 |
| all | 47 | 0 | 889 | 2064 |

## Q3 breakdown (book reading)

- total 889: 884 with an explicit conflict inside a type, 5 with only an indirect odd path

Reasons, indirect odd path only:

- 5 x hiding only ever lowers the agent's utility

Reasons, explicit conflict:

- 407 x hiding only ever lowers the agent's utility
- 385 x hiding can free one of the agent's own arguments, but it always costs at least as many others (compensation, as in Example 5.11)
- 92 x hiding never changes the agent's utility (whatever it hides, its accepted arguments stay the same, e.g. they are decided by unhideable or never-accepted arguments of other agents)
- 5 x cancelling argument

