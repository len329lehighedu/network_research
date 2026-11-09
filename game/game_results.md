# Three-person attendance game: one-day results

Three people know one another and choose to attend (A) or stay home (H). Nobody knows anyone's infection status, including their own. Initial infections are independent with probability $\pi$. An attending susceptible person can be infected by each infected attending peer with probability $\beta$; staying home costs $c$, and infection costs $L$. The numbers below are **expected costs above the common baseline $3L\pi$**.

At $\pi=0.1$, $\beta=0.04$, $L=10$, and $c=0.05$:

| Arrangement | Extra group cost per day | Share of Nash-to-minimum gap closed |
|---|---:|---:|
| Independent symmetric Nash (each attends with probability 0.6954) | 0.150 | — |
| Fair lottery over the three two-attendee profiles | 0.122 | 56.0% |
| Best correlated equilibrium | 0.112356 | 75.3% |
| Lowest-cost profile, ignoring incentives (one attends) | 0.100 | 100% |

The fair two-attendee lottery is an equilibrium at these parameters. The lower-cost one-attendee profiles are not: a person told to stay home would rather attend. The best correlated equilibrium sometimes recommends that two people stay home while satisfying the recommendation-obedience constraints.

## Selected values from the parameter grid

Here $\beta=0.04$ and $L=10$ throughout. “Rotation NE?” indicates whether the fair two-attendee lottery is an equilibrium; its cost remains computable when the answer is No.

| $\pi$ | $c$ | Independent Nash | Fair two-attendee lottery | Rotation NE? | Best CE | Unconstrained minimum |
|---:|---:|---:|---:|:---:|---:|---:|
| 0.10 | 0.02 | 0.060 | 0.092 | No | 0.040 | 0.040 |
| 0.10 | 0.05 | 0.150 | 0.122 | Yes | 0.112 | 0.100 |
| 0.10 | 0.12 | 0.216 | 0.192 | No | 0.216 | 0.192 |
| 0.50 | 0.05 | 0.150 | 0.250 | No | 0.100 | 0.100 |
| 0.50 | 0.12 | 0.360 | 0.320 | Yes | 0.267 | 0.240 |

At $\pi=0.1$, the two-attendee lottery is an equilibrium for $0.036 \leq c \leq 0.071856$. Its incentive status changes outside that interval. 

## Small contact networks (4–6 people)

The one-day game now uses each person's graph neighbors as possible workplace contacts. At $\pi=0.1$, $\beta=0.04$, $L=10$, and $c=0.05$, costs below are **group totals above $nL\pi$**. “Best pure Nash” is the lowest-cost pure equilibrium on that graph; its gap to the social minimum is the denominator for “CE gap closed.” This is a different benchmark from the independent mixed Nash in the three-person table above.

| Graph | People | Edges | Best pure Nash | Best CE | Social minimum | CE gap closed | Expected active edges under CE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Path | 4 | 3 | 0.122000 | 0.112356 | 0.100000 | 43.8% | 0.561617 |
| Star | 5 | 4 | 0.050000 | 0.050000 | 0.050000 | — | 0 |
| Triangle with a leaf | 4 | 4 | 0.122000 | 0.122000 | 0.100000 | 0.0% | 1.000000 |
| Path | 6 | 5 | 0.172000 | 0.158590 | 0.150000 | 61.0% | 0.390451 |

Reproduction: run from the repository root: `.venv/bin/python game/network_game.py --summary`.
