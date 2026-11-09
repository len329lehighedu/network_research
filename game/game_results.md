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
