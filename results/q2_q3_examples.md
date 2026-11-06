# Q2 and Q3 instances

## Q2: condition holds but mechanism is NOT strategyproof

### reading `book`: 0 instance(s)


### reading `simple`: 0 instance(s)


### reading `distinct`: 0 instance(s)


## Q3: strategyproof although the Theorem 5.4 condition fails (book reading): 889 instances

- 884 violate it through an explicit conflict inside one agent's own type (an attack between two of its arguments, or a self-attack);
- 5 violate it only through an indirect odd-length path (every type is conflict-free).

### Explanation tags: indirect odd path only (an instance can carry several)

- 5 x hiding only ever lowers the agent's utility

### Explanation tags: explicit conflict (an instance can carry several)

- 407 x hiding only ever lowers the agent's utility
- 385 x hiding can free one of the agent's own arguments, but it always costs at least as many others (compensation, as in Example 5.11)
- 92 x hiding never changes the agent's utility (whatever it hides, its accepted arguments stay the same, e.g. they are decided by unhideable or never-accepted arguments of other agents)
- 5 x cancelling argument

### Smallest examples: indirect odd path only

- n=6, p=0.25, index=804
  - arguments: a1, a2, a3, a4, a5, a6
  - attacks: a2->a1, a4->a2, a4->a3, a6->a2, a6->a4
  - types: x={a4}; y={a2, a3, a5}; z={a1, a6}
  - grounded outcome (all truthful): {a1, a3, a5, a6}; utilities: x=0, y=2, z=2
  - condition violated by agent z: a6 indirectly defeats a1 via odd path a6 -> a4 -> a2 -> a1
  - why still strategyproof: hiding only ever lowers the agent's utility
- n=6, p=0.25, index=30
  - arguments: a1, a2, a3, a4, a5, a6
  - attacks: a3->a1, a3->a4, a3->a5, a3->a6, a5->a4, a6->a3
  - types: x={a3}; y={a1, a5}; z={a2, a4, a6}
  - grounded outcome (all truthful): {a2}; utilities: x=0, y=0, z=1
  - condition violated by agent z: a6 indirectly defeats a4 via odd path a6 -> a3 -> a5 -> a4
  - why still strategyproof: hiding only ever lowers the agent's utility
- n=6, p=0.25, index=716
  - arguments: a1, a2, a3, a4, a5, a6
  - attacks: a1->a6, a2->a4, a2->a5, a5->a3, a5->a4, a5->a6, a6->a2, a6->a3
  - types: x={a1, a2, a3}; y={a5}; z={a4, a6}
  - grounded outcome (all truthful): {a1, a2, a3}; utilities: x=3, y=0, z=0
  - condition violated by agent x: a1 indirectly defeats a2 via odd path a1 -> a6 -> a2 -> a5 -> a6 -> a2
  - why still strategyproof: hiding only ever lowers the agent's utility
- n=7, p=0.15, index=972
  - arguments: a1, a2, a3, a4, a5, a6, a7
  - attacks: a1->a5, a3->a4, a4->a6, a5->a6, a6->a1, a7->a5
  - types: x={a4, a5}; y={a1, a7}; z={a2, a3, a6}
  - grounded outcome (all truthful): {a2, a3, a6, a7}; utilities: x=0, y=1, z=3
  - condition violated by agent x: a4 indirectly defeats a5 via odd path a4 -> a6 -> a1 -> a5
  - why still strategyproof: hiding only ever lowers the agent's utility
- n=8, p=0.25, index=563
  - arguments: a1, a2, a3, a4, a5, a6, a7, a8
  - attacks: a1->a2, a1->a6, a1->a7, a2->a3, a2->a7, a3->a5, a4->a1, a4->a5, a4->a7, a6->a3, a7->a8, a8->a2, a8->a4, a8->a5
  - types: x={a2, a4, a6}; y={a1, a3, a8}; z={a5, a7}
  - grounded outcome (all truthful): {}; utilities: x=0, y=0, z=0
  - condition violated by agent x: a2 indirectly defeats a2 via odd path a2 -> a7 -> a8 -> a2
  - why still strategyproof: hiding only ever lowers the agent's utility

### Smallest examples: explicit conflict

- n=6, p=0.15, index=158
  - arguments: a1, a2, a3, a4, a5, a6
  - attacks: a2->a6
  - types: x={a1, a2, a4, a6}; y={a3}; z={a5}
  - grounded outcome (all truthful): {a1, a2, a3, a4, a5}; utilities: x=3, y=1, z=1
  - condition violated by agent x: explicit conflict a2->a6
  - why still strategyproof: hiding can free one of the agent's own arguments, but it always costs at least as many others (compensation, as in Example 5.11)
- n=6, p=0.15, index=9
  - arguments: a1, a2, a3, a4, a5, a6
  - attacks: a3->a5, a5->a5
  - types: x={a1, a3, a5, a6}; y={a2}; z={a4}
  - grounded outcome (all truthful): {a1, a2, a3, a4, a6}; utilities: x=3, y=1, z=1
  - condition violated by agent x: explicit conflict a3->a5
  - why still strategyproof: hiding only ever lowers the agent's utility
- n=6, p=0.15, index=49
  - arguments: a1, a2, a3, a4, a5, a6
  - attacks: a1->a6, a3->a2
  - types: x={a1, a6}; y={a4, a5}; z={a2, a3}
  - grounded outcome (all truthful): {a1, a3, a4, a5}; utilities: x=1, y=2, z=1
  - condition violated by agent x: explicit conflict a1->a6
  - why still strategyproof: hiding can free one of the agent's own arguments, but it always costs at least as many others (compensation, as in Example 5.11)
- n=6, p=0.15, index=82
  - arguments: a1, a2, a3, a4, a5, a6
  - attacks: a1->a1, a1->a4
  - types: x={a3, a6}; y={a2, a4}; z={a1, a5}
  - grounded outcome (all truthful): {a2, a3, a5, a6}; utilities: x=2, y=1, z=1
  - condition violated by agent z: explicit conflict a1->a1
  - why still strategyproof: hiding only ever lowers the agent's utility

