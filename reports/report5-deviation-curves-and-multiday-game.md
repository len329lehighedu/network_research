# Report 5 — Deviation curves, network features, and the multiday benchmark

**Communication log:** Follow-up requests, PDF pp. 24–25. Results sent in the fifth results email, pp. 25–30.

- [Deviation shares](#deviations-from-zero-contact-value-to-welfare-break-even)
- [Network features and bowtie](#network-features-and-recommendation-gains)
- [Multiday benchmark and sensitivity](#multiday-attendance-benchmark)

## Deviations from zero contact value to welfare break-even

Source: [saved β = 0.085 archive](../network_sis/data/beta0085_20w50r.npz). Each comparison uses 20 worlds, 50 runs per world, and 84 days, with γ = 0.2, infection cost per day 10, and home cost 0.05. Attendance schedules and SIS trajectories remain fixed as $v$ changes. Each pair uses its own welfare break-even value $v^*$.

Shares are fractions of scheduled person-days. **Home all** and **Home k>0** measure the incentive to attend on a home day. **Attend** and **Attend k>0** measure the incentive to stay home on an attendance day. A column marked **k>0** uses the corresponding person-days with at least one attending neighbor. **Home k=0** is the share of home slots without an attending neighbor. The endpoint table in the email uses the $v/v^*=0$ and $v/v^*=1$ rows below.

### Daily switching: whole versus random (`v* = 0.464765`)

| Split | v/v* | v | Home all | Home k>0 | Attend | Home k=0 | Attend k>0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Whole | 0 | 0.0000 | 0.382 | 0.097 | 0.920 | 0.315 | 0.920 |
| Whole | 0.25 | 0.1162 | 0.482 | 0.244 | 0.806 | 0.315 | 0.806 |
| Whole | 0.50 | 0.2324 | 0.658 | 0.501 | 0.542 | 0.315 | 0.542 |
| Whole | 0.75 | 0.3486 | 0.805 | 0.715 | 0.317 | 0.315 | 0.317 |
| Whole | 1 | 0.4648 | 0.906 | 0.863 | 0.151 | 0.315 | 0.151 |
| Random | 0 | 0.0000 | 0.567 | 0.561 | 0.434 | 0.013 | 0.439 |
| Random | 0.25 | 0.1162 | 0.846 | 0.844 | 0.154 | 0.013 | 0.156 |
| Random | 0.50 | 0.2324 | 0.981 | 0.981 | 0.019 | 0.013 | 0.019 |
| Random | 0.75 | 0.3486 | 0.999 | 0.999 | 0.001 | 0.013 | 0.001 |
| Random | 1 | 0.4648 | 1.000 | 1.000 | 0.000 | 0.013 | 0.000 |

### Daily switching: whole versus even (`v* = 0.456395`)

| Split | v/v* | v | Home all | Home k>0 | Attend | Home k=0 | Attend k>0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Whole | 0 | 0.0000 | 0.382 | 0.097 | 0.920 | 0.315 | 0.920 |
| Whole | 0.25 | 0.1141 | 0.482 | 0.244 | 0.816 | 0.315 | 0.816 |
| Whole | 0.50 | 0.2282 | 0.658 | 0.501 | 0.573 | 0.315 | 0.573 |
| Whole | 0.75 | 0.3423 | 0.802 | 0.711 | 0.327 | 0.315 | 0.327 |
| Whole | 1 | 0.4564 | 0.899 | 0.853 | 0.162 | 0.315 | 0.162 |
| Even | 0 | 0.0000 | 0.627 | 0.623 | 0.369 | 0.011 | 0.374 |
| Even | 0.25 | 0.1141 | 0.882 | 0.880 | 0.116 | 0.011 | 0.117 |
| Even | 0.50 | 0.2282 | 0.991 | 0.991 | 0.008 | 0.011 | 0.008 |
| Even | 0.75 | 0.3423 | 1.000 | 1.000 | 0.000 | 0.011 | 0.000 |
| Even | 1 | 0.4564 | 1.000 | 1.000 | 0.000 | 0.011 | 0.000 |

### Weekly switching: whole versus random (`v* = 0.370548`)

| Split | v/v* | v | Home all | Home k>0 | Attend | Home k=0 | Attend k>0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Whole | 0 | 0.0000 | 0.448 | 0.193 | 0.836 | 0.315 | 0.836 |
| Whole | 0.25 | 0.0926 | 0.534 | 0.319 | 0.728 | 0.315 | 0.728 |
| Whole | 0.50 | 0.1853 | 0.666 | 0.512 | 0.553 | 0.315 | 0.553 |
| Whole | 0.75 | 0.2779 | 0.779 | 0.677 | 0.366 | 0.315 | 0.366 |
| Whole | 1 | 0.3705 | 0.868 | 0.807 | 0.214 | 0.315 | 0.214 |
| Random | 0 | 0.0000 | 0.618 | 0.613 | 0.382 | 0.013 | 0.388 |
| Random | 0.25 | 0.0926 | 0.817 | 0.815 | 0.183 | 0.013 | 0.186 |
| Random | 0.50 | 0.1853 | 0.938 | 0.937 | 0.062 | 0.013 | 0.063 |
| Random | 0.75 | 0.2779 | 0.990 | 0.990 | 0.010 | 0.013 | 0.010 |
| Random | 1 | 0.3705 | 0.999 | 0.999 | 0.001 | 0.013 | 0.001 |

### Weekly switching: whole versus even (`v* = 0.358165`)

| Split | v/v* | v | Home all | Home k>0 | Attend | Home k=0 | Attend k>0 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Whole | 0 | 0.0000 | 0.448 | 0.193 | 0.836 | 0.315 | 0.836 |
| Whole | 0.25 | 0.0895 | 0.533 | 0.318 | 0.731 | 0.315 | 0.731 |
| Whole | 0.50 | 0.1791 | 0.662 | 0.506 | 0.555 | 0.315 | 0.555 |
| Whole | 0.75 | 0.2686 | 0.770 | 0.664 | 0.368 | 0.315 | 0.368 |
| Whole | 1 | 0.3582 | 0.859 | 0.794 | 0.235 | 0.315 | 0.235 |
| Even | 0 | 0.0000 | 0.650 | 0.646 | 0.346 | 0.011 | 0.352 |
| Even | 0.25 | 0.0895 | 0.831 | 0.829 | 0.166 | 0.011 | 0.168 |
| Even | 0.50 | 0.1791 | 0.943 | 0.942 | 0.056 | 0.011 | 0.057 |
| Even | 0.75 | 0.2686 | 0.993 | 0.993 | 0.007 | 0.011 | 0.007 |
| Even | 1 | 0.3582 | 0.999 | 0.999 | 0.001 | 0.011 | 0.001 |

At $v=0$, the home cost already gives some players an incentive to attend. Across all four comparisons, increasing $v$ to break-even raises the home deviation share among Whole’s $k>0$ slots by 60.1–76.6 percentage points. These are unilateral incentives under the scheduled attendance of the other players.

![Deviation shares at five sampled contact values](../network_sis/obedience_v_curves.png)

<details>
<summary>Reproduce the deviation tables and figure</summary>

From the repository root, run the following command. It reads the saved archive and prints the five sampled points for all four comparisons.

```sh
PYTHONPATH=.:network_sis .venv/bin/python - <<'PY'
import numpy as np
from network_sis.community_obedience import (
    collect_all_world_thresholds,
    deviation_counts_from_thresholds,
    welfare_break_even_v,
)

fractions = (0, 0.25, 0.5, 0.75, 1)
with np.load('network_sis/data/beta0085_20w50r.npz', allow_pickle=False) as data:
    for switch_days in (1, 7):
        for comparison in ('random', 'even'):
            v_star = welfare_break_even_v(
                data, 'whole', comparison, switch_days, L_day=10,
            )
            print(f'whole–{comparison}, switch={switch_days}, v*={v_star:.6f}')
            for split_name in ('whole', comparison):
                thresholds = collect_all_world_thresholds(
                    data, split_name, switch_days, L_day=10, c=0.05,
                )
                for fraction in fractions:
                    v = fraction * v_star
                    counts = deviation_counts_from_thresholds(thresholds, v)
                    home_all = counts['home_deviations'] / counts['home_slots']
                    home_positive = (
                        counts['home_positive_deviations']
                        / counts['home_positive_slots']
                    )
                    attend = counts['attend_deviations'] / counts['attend_slots']
                    home_zero = counts['home_zero_slots'] / counts['home_slots']
                    attend_positive = counts['attend_deviations'] / len(thresholds[1])
                    print(
                        f'{split_name:6s} {fraction:.2f} {v:.4f} '
                        f'{home_all:.3f} {home_positive:.3f} '
                        f'{attend:.3f} {home_zero:.3f} {attend_positive:.3f}'
                    )
PY
```

```sh
.venv/bin/python network_sis/plot_obedience_v_curves.py --output-dir "$(mktemp -d)"
```

</details>

## Network features and recommendation gains

The email’s feature comparison draws from the grouped tables below. We evaluate the same 139 connected networks with four to six people at π = 0.10 and home costs of 0.05 and 0.12. Other parameters are β = 0.04, γ = 0.20, infection cost per day 10, and contact value 0.14. **CE gain** is the best pure Nash group cost minus the best CE group cost. A difference greater than $10^{-9}$ counts as a gain. The largest independent set $\alpha$ is the largest set of people who can attend together without activating an edge.

### Feature tables at c = 0.05

#### Pure Nash count, all 139 networks

| Pure Nash count | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 29 | 4 | 0.138 | 0.001460 |
| 2 | 49 | 18 | 0.367 | 0.007337 |
| 3 | 25 | 17 | 0.680 | 0.013128 |
| 4 | 15 | 7 | 0.467 | 0.010655 |
| 5 | 9 | 8 | 0.889 | 0.025111 |
| 6 | 6 | 6 | 1.000 | 0.022765 |
| 7 | 4 | 3 | 0.750 | 0.020516 |
| 10 | 1 | 1 | 1.000 | 0.020613 |
| 15 | 1 | 1 | 1.000 | 0.021024 |

#### Edges, by network size

| People | Edges | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 3 | 2 | 1 | 0.500 | 0.008912 |
| 4 | 4 | 2 | 0 | 0.000 | 0.000000 |
| 4 | 5 | 1 | 0 | 0.000 | 0.000000 |
| 4 | 6 | 1 | 1 | 1.000 | 0.019837 |
| 5 | 4 | 3 | 0 | 0.000 | 0.000000 |
| 5 | 5 | 5 | 2 | 0.400 | 0.009565 |
| 5 | 6 | 5 | 3 | 0.600 | 0.012676 |
| 5 | 7 | 4 | 2 | 0.500 | 0.009332 |
| 5 | 8 | 2 | 1 | 0.500 | 0.009166 |
| 5 | 9 | 1 | 0 | 0.000 | 0.000000 |
| 5 | 10 | 1 | 1 | 1.000 | 0.020613 |
| 6 | 5 | 6 | 2 | 0.333 | 0.006598 |
| 6 | 6 | 13 | 6 | 0.462 | 0.008339 |
| 6 | 7 | 19 | 9 | 0.474 | 0.008875 |
| 6 | 8 | 22 | 11 | 0.500 | 0.009200 |
| 6 | 9 | 20 | 9 | 0.450 | 0.010630 |
| 6 | 10 | 14 | 8 | 0.571 | 0.013583 |
| 6 | 11 | 9 | 5 | 0.556 | 0.016266 |
| 6 | 12 | 5 | 2 | 0.400 | 0.008693 |
| 6 | 13 | 2 | 1 | 0.500 | 0.009166 |
| 6 | 14 | 1 | 0 | 0.000 | 0.000000 |
| 6 | 15 | 1 | 1 | 1.000 | 0.021024 |

#### Triangles, by network size

| People | Triangles | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 0 | 3 | 1 | 0.333 | 0.005942 |
| 4 | 1 | 1 | 0 | 0.000 | 0.000000 |
| 4 | 2 | 1 | 0 | 0.000 | 0.000000 |
| 4 | 4 | 1 | 1 | 1.000 | 0.019837 |
| 5 | 0 | 6 | 1 | 0.167 | 0.005000 |
| 5 | 1 | 4 | 2 | 0.500 | 0.010185 |
| 5 | 2 | 4 | 2 | 0.500 | 0.010115 |
| 5 | 3 | 2 | 1 | 0.500 | 0.009752 |
| 5 | 4 | 2 | 1 | 0.500 | 0.008912 |
| 5 | 5 | 1 | 1 | 1.000 | 0.018331 |
| 5 | 7 | 1 | 0 | 0.000 | 0.000000 |
| 5 | 10 | 1 | 1 | 1.000 | 0.020613 |
| 6 | 0 | 19 | 5 | 0.263 | 0.005271 |
| 6 | 1 | 14 | 8 | 0.571 | 0.009038 |
| 6 | 2 | 21 | 11 | 0.524 | 0.011712 |
| 6 | 3 | 12 | 6 | 0.500 | 0.009529 |
| 6 | 4 | 14 | 6 | 0.429 | 0.009093 |
| 6 | 5 | 8 | 5 | 0.625 | 0.016088 |
| 6 | 6 | 7 | 4 | 0.571 | 0.012392 |
| 6 | 7 | 4 | 2 | 0.500 | 0.011630 |
| 6 | 8 | 4 | 2 | 0.500 | 0.018025 |
| 6 | 9 | 1 | 0 | 0.000 | 0.000000 |
| 6 | 10 | 3 | 2 | 0.667 | 0.015160 |
| 6 | 11 | 1 | 1 | 1.000 | 0.017825 |
| 6 | 12 | 1 | 0 | 0.000 | 0.000000 |
| 6 | 13 | 1 | 1 | 1.000 | 0.018331 |
| 6 | 16 | 1 | 0 | 0.000 | 0.000000 |
| 6 | 20 | 1 | 1 | 1.000 | 0.021024 |

#### Maximum degree, by network size

| People | Maximum degree | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 2 | 2 | 1 | 0.500 | 0.008912 |
| 4 | 3 | 4 | 1 | 0.250 | 0.004959 |
| 5 | 2 | 2 | 1 | 0.500 | 0.015000 |
| 5 | 3 | 8 | 3 | 0.375 | 0.007832 |
| 5 | 4 | 11 | 5 | 0.455 | 0.008620 |
| 6 | 2 | 2 | 1 | 0.500 | 0.011181 |
| 6 | 3 | 27 | 14 | 0.519 | 0.011132 |
| 6 | 4 | 49 | 24 | 0.490 | 0.010107 |
| 6 | 5 | 34 | 15 | 0.441 | 0.009788 |

### Largest independent set within equilibrium groups

| People | Pure Nash | α group | Networks | CE improves | Share |
| ---: | --- | --- | ---: | ---: | ---: |
| 5 | One | ≤2 | 1 | 1 | 1.000 |
| 5 | One | ≥3 | 5 | 0 | 0.000 |
| 5 | Multiple | ≤2 | 11 | 8 | 0.727 |
| 5 | Multiple | ≥3 | 4 | 0 | 0.000 |
| 6 | One | ≤2 | 0 | 0 | — |
| 6 | One | ≥3 | 21 | 3 | 0.143 |
| 6 | Multiple | ≤2 | 35 | 28 | 0.800 |
| 6 | Multiple | ≥3 | 56 | 23 | 0.411 |

### Largest independent set at the same edge count

Six-person networks with multiple pure Nash equilibria; only edge counts where both α groups occur are shown.

| Edges | α ≤ 2: CE gains / networks | α ≥ 3: CE gains / networks |
| ---: | ---: | ---: |
| 7 | 1/1 | 8/14 |
| 8 | 4/4 | 5/13 |
| 9 | 7/7 | 1/10 |
| 10 | 7/8 | 1/5 |
| 11 | 5/7 | 0/2 |
| 12 | 2/4 | 0/1 |
| **Total in shared edge strata** | **26/31** | **15/45** |

### Feature checks at c = 0.12

The same 139 networks and game parameters are used, changing only the cost of staying home from 0.05 to 0.12.

#### Pure Nash count, all 139 networks

| Pure Nash count | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 104 | 0 | 0.000 | 0.000000 |
| 2 | 18 | 17 | 0.944 | 0.098018 |
| 3 | 10 | 9 | 0.900 | 0.078146 |
| 4 | 4 | 3 | 0.750 | 0.076427 |
| 5 | 1 | 1 | 1.000 | 0.101288 |
| 7 | 1 | 1 | 1.000 | 0.105410 |
| 15 | 1 | 1 | 1.000 | 0.104095 |

#### Largest independent set among networks with multiple pure Nash

No four-person network has multiple pure Nash at this c.

| People | α | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 1 | 1 | 1 | 1.000 | 0.101288 |
| 5 | 2 | 2 | 2 | 1.000 | 0.103209 |
| 5 | 3 | 1 | 1 | 1.000 | 0.105135 |
| 6 | 1 | 1 | 1 | 1.000 | 0.104095 |
| 6 | 2 | 16 | 14 | 0.875 | 0.080756 |
| 6 | 3 | 13 | 12 | 0.923 | 0.096009 |
| 6 | 4 | 1 | 1 | 1.000 | 0.105135 |

#### Edges among six-person networks with multiple pure Nash

| Edges | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: |
| 7 | 1 | 1 | 1.000 | 0.105135 |
| 8 | 4 | 4 | 1.000 | 0.104161 |
| 9 | 8 | 8 | 1.000 | 0.103109 |
| 10 | 7 | 6 | 0.857 | 0.087717 |
| 11 | 4 | 2 | 0.500 | 0.051723 |
| 12 | 3 | 3 | 1.000 | 0.078410 |
| 13 | 2 | 2 | 1.000 | 0.068574 |
| 14 | 1 | 1 | 1.000 | 0.105410 |
| 15 | 1 | 1 | 1.000 | 0.104095 |

#### Triangles among six-person networks with multiple pure Nash

| Triangles | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 2 | 2 | 1.000 | 0.104813 |
| 3 | 5 | 5 | 1.000 | 0.103706 |
| 4 | 7 | 6 | 0.857 | 0.088362 |
| 5 | 4 | 4 | 1.000 | 0.102549 |
| 6 | 4 | 3 | 0.750 | 0.077366 |
| 7 | 2 | 1 | 0.500 | 0.050605 |
| 8 | 1 | 1 | 1.000 | 0.023499 |
| 9 | 1 | 1 | 1.000 | 0.103682 |
| 10 | 1 | 1 | 1.000 | 0.108048 |
| 12 | 1 | 1 | 1.000 | 0.030421 |
| 13 | 1 | 1 | 1.000 | 0.106727 |
| 16 | 1 | 1 | 1.000 | 0.105410 |
| 20 | 1 | 1 | 1.000 | 0.104095 |

#### Maximum degree among six-person networks with multiple pure Nash

| Maximum degree | Networks | CE improves | Share | Mean CE gain |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 24 | 21 | 0.875 | 0.086921 |
| 5 | 7 | 7 | 1.000 | 0.094764 |

At $c=0.05$, among six-person networks with multiple pure equilibria, CE helps in 28/35 networks with $\alpha\leq2$ and 23/56 with $\alpha\geq3$. The pattern persists within the shared edge counts shown above. The email’s triangle comparison pools the nonzero triangle counts in the six-person rows to obtain 49/93 networks with a gain. At $c=0.12$, equilibrium multiplicity gives the clearest separation and the independent-set pattern weakens.

### Bowtie (atlas 42) by hand

The outer pairs $(0,1)$ and $(2,3)$ share center $4$. At $c=0.05$, the gain from attending with $k$ attending neighbors is $g(k)=0.05+0.14k-45(1-0.996^k)$. Thus $g(0)=0.05$, $g(1)=0.01$, $g(2)=-0.02928$, and $g(4)\approx-0.105692$.

If the center stays home, every outer player prefers to attend. The center then prefers to stay home. If the center attends, each outer pair must have exactly one attendee in equilibrium, since $g(1)>0$ and $g(2)<0$. That would give the center two attending neighbors and an incentive to stay home. The unique pure Nash is therefore `AAAAH`, with group cost $4(0.18-0.14)+0.05=0.21$ above the common infection baseline. The social minimum is $3c=0.15$, with one outer attendee per pair and the center at home.

The symmetric LP optimum assigns equal probability to profiles within each category:

| Category | Attendees | Total probability | Group cost per profile |
|---|---|---:|---:|
| $x$ | One outer player per pair | 0.525610 | 0.150000 |
| $y$ | One outer player per pair and the center | 0.299186 | 0.259280 |
| $z$ | Center alone | 0.175203 | 0.200000 |

The binding obedience constraints are $-0.005x+0.01464y-0.01z=0$ for an outer player receiving `H`, and $-0.02928y+0.05z=0$ for the center receiving `A`. Therefore $z=0.5856y$, $x=1.7568y$, and $y=1/3.3424$. The expected cost is $0.15x+0.25928y+0.20z=0.191455$ to six decimals, a gain of $0.018545$ (8.8%) over pure Nash. An outer player receiving `H` weighs profiles in which they would meet one contact if they switched against profiles in which they would meet two. This makes the lottery obedient while placing 52.6% of its probability on social-minimum profiles.

<details>
<summary>Reproduce the feature tables and bowtie calculation</summary>

The [full atlas CSV](../game/atlas_contact_value_4_6.csv) contains the network-level outcomes. This command joins them to graph features, prints the complete per-network feature data, and solves the bowtie LP.

```bash
PYTHONPATH=. .venv/bin/python game/reproduce_report5_network_features.py \
  --csv game/atlas_contact_value_4_6.csv
```

</details>

## Multiday attendance benchmark

### Experiment settings

| Network | Initial case nodes | Days | Runs per initial case, policy, and v | β | γ | Infection cost per person-day | Home cost per day | Simulation seed | Bootstrap seed | Bootstrap draws |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Two five-person cliques joined by edge (4, 5) | 4 (bridge), 0 (within group) | 14 | 500 | 0.04 | 0.20 | 10 | 0.05 | 123 | 456 | 2,000 |

### Mean outcomes per run

| v | Initial case | Policy | Runs | Infected person-days | Attendance person-days | Active edge-days | Group payoff | Follow rate |
|---|---|---|---|---|---|---|---|---|
| 0.00 | 4 | No recommendation | 500 | 5.88 | 109.30 | 229.53 | -60.31 | N/A |
| 0.00 | 4 | Fixed rotation | 500 | 4.13 | 91.91 | 156.87 | -43.68 | 65.5% |
| 0.00 | 4 | Daily CE | 500 | 3.92 | 101.06 | 191.77 | -41.13 | 100.0% |
| 0.00 | 0 | No recommendation | 500 | 5.59 | 109.92 | 230.83 | -57.38 | N/A |
| 0.00 | 0 | Fixed rotation | 500 | 4.53 | 90.16 | 149.86 | -47.83 | 67.9% |
| 0.00 | 0 | Daily CE | 500 | 3.77 | 102.16 | 194.67 | -39.59 | 100.0% |
| 0.14 | 4 | No recommendation | 500 | 5.88 | 109.30 | 229.53 | 3.95 | N/A |
| 0.14 | 4 | Fixed rotation | 500 | 5.08 | 93.97 | 159.73 | -8.42 | 61.5% |
| 0.14 | 4 | Daily CE | 500 | 4.09 | 102.76 | 192.15 | 11.06 | 100.0% |
| 0.14 | 0 | No recommendation | 500 | 5.59 | 109.92 | 230.83 | 7.25 | N/A |
| 0.14 | 0 | Fixed rotation | 500 | 4.73 | 91.87 | 150.95 | -7.40 | 65.7% |
| 0.14 | 0 | Daily CE | 500 | 3.79 | 104.52 | 196.92 | 15.48 | 100.0% |
| 0.28 | 4 | No recommendation | 500 | 8.54 | 127.18 | 267.08 | 63.52 | N/A |
| 0.28 | 4 | Fixed rotation | 500 | 7.52 | 106.78 | 194.45 | 32.05 | 67.3% |
| 0.28 | 4 | Daily CE | 500 | 7.71 | 126.19 | 256.22 | 65.67 | 100.0% |
| 0.28 | 0 | No recommendation | 500 | 7.77 | 128.88 | 270.65 | 73.27 | N/A |
| 0.28 | 0 | Fixed rotation | 500 | 6.79 | 103.92 | 183.34 | 32.99 | 70.7% |
| 0.28 | 0 | Daily CE | 500 | 7.03 | 127.82 | 260.57 | 74.97 | 100.0% |

### Payoff differences with 95% paired bootstrap intervals

| v | Initial case | Daily CE − Fixed rotation | Daily CE − No recommendation | Fixed rotation − No recommendation |
|---|---|---|---|---|
| 0.00 | 4 | +2.56 [1.33, 4.07] | +19.19 [15.51, 22.72] | +16.63 [12.61, 20.56] |
| 0.00 | 0 | +8.24 [6.16, 10.52] | +17.79 [14.46, 21.16] | +9.55 [6.84, 12.42] |
| 0.14 | 4 | +19.48 [16.75, 22.41] | +7.11 [3.44, 10.77] | -12.37 [-15.46, -9.35] |
| 0.14 | 0 | +22.88 [20.35, 25.60] | +8.23 [4.58, 11.93] | -14.65 [-17.32, -11.95] |
| 0.28 | 4 | +33.62 [29.59, 37.69] | +2.15 [-0.12, 4.76] | -31.47 [-36.02, -26.70] |
| 0.28 | 0 | +41.99 [38.48, 45.34] | +1.71 [-0.84, 4.67] | -40.28 [-44.43, -36.10] |

<details>
<summary>Reproduce the multiday tables</summary>

[CSV for v = 0.00](../game/data/multiday_v000.csv) · [CSV for v = 0.14](../game/data/multiday_v014.csv) · [CSV for v = 0.28](../game/data/multiday_v028.csv)

```bash
PYTHONPATH=. .venv/bin/python game/summarize_multiday_benchmark.py \
  game/data/multiday_v000.csv game/data/multiday_v014.csv game/data/multiday_v028.csv
```

```bash
# Regenerate the benchmark in a separate directory and rebuild the tables.
(
  set -e
  benchmark_data=$(mktemp -d)
  for v in 0.00 0.14 0.28; do
    PYTHONPATH=. .venv/bin/python game/run_multiday_benchmark.py \
      --runs 500 --days 14 --v "$v" --output "$benchmark_data/multiday_v${v/./}.csv"
  done
  PYTHONPATH=. .venv/bin/python game/summarize_multiday_benchmark.py \
    "$benchmark_data"/multiday_v*.csv
)
```

The CSV summary command also prints the contact, infection, and home-cost decomposition for each payoff contrast.

</details>

Each replicate pairs infection and recovery draws by person and day across policies. Daily CE updates recommendations using current prevalence and the one-day payoff. Follow rates are based on actual actions and are defined when a policy gives recommendations.

The mean payoff advantage of daily CE over no recommendation decreases as contact value rises. At $v=0.28$, both intervals for that contrast include zero. Fixed rotation has the fewest infected person-days at $v=0.28$. Daily CE retains more contacts and has higher mean group payoff in those comparisons.

### Sensitivity to attendance revision in the no-recommendation benchmark

At $v=0.28$, each player in the no-recommendation benchmark reconsidered attendance each day with probability $p$. Players who did not reconsider kept their previous action. Daily CE and fixed rotation had identical outcomes across the four settings for every matched replicate. Each setting uses 500 replicates per initial infection site over 14 days.

The CE payoff advantage is the cumulative group payoff under daily CE minus the payoff under no recommendation at the indicated $p$. The change columns subtract the corresponding advantage at $p=1$. Brackets give pointwise 95% bootstrap intervals, with observations paired by replicate for both contrasts.

Saved data by revision probability: [0.25](../game/data/multiday_v028_update025.csv), [0.50](../game/data/multiday_v028_update050.csv), [0.75](../game/data/multiday_v028_update075.csv), and [1.00](../game/data/multiday_v028.csv).

| Daily revision probability $p$ | CE payoff advantage, bridge node 4 | CE payoff advantage, within-community node 0 | Change from $p=1$, bridge node 4 | Change from $p=1$, within-community node 0 |
|---:|---:|---:|---:|---:|
| 0.25 | +7.11 [3.87, 10.43] | +6.75 [3.90, 9.77] | +4.96 [1.50, 8.56] | +5.05 [1.73, 8.62] |
| 0.50 | +2.89 [0.17, 5.61] | +2.83 [0.54, 5.03] | +0.74 [−2.44, 3.93] | +1.13 [−1.71, 3.94] |
| 0.75 | +1.46 [−0.19, 3.21] | +1.31 [−0.38, 3.00] | −0.69 [−3.29, 1.62] | −0.40 [−3.31, 2.16] |
| 1.00 | +2.15 [−0.12, 4.76] | +1.71 [−0.84, 4.67] | Reference | Reference |
