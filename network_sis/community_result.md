# Community-network results

## 1. Stochastic scenario outcomes
| Split | Policy | Switch | Mean infected, days 1–84 [95% world CI] | Extinct by day 84 [95% world CI] | Mean active contact days |
|---|---|---:|---:|---:|---:|
| Whole | Rotating | Daily | 15.49 [14.22, 16.88] | 0.169 [0.131, 0.209] | 28,612.5 |
| Whole | Rotating | Weekly | 12.60 [11.63, 13.67] | 0.337 [0.295, 0.379] | 28,612.5 |
| Whole | Matched On-Off | Daily | 21.27 [20.03, 22.54] | 0.117 [0.092, 0.143] | 28,612.5 |
| Whole | Matched On-Off | Weekly | 17.60 [16.29, 18.98] | 0.240 [0.199, 0.282] | 28,612.5 |
| Random | Rotating | Daily | 2.38 [2.15, 2.63] | 0.940 [0.916, 0.961] | 16,768.5 |
| Random | Rotating | Weekly | 2.15 [1.96, 2.36] | 0.970 [0.956, 0.982] | 16,768.5 |
| Random | Matched On-Off | Daily | 2.15 [1.96, 2.35] | 0.949 [0.929, 0.966] | 16,768.5 |
| Random | Matched On-Off | Weekly | 2.08 [1.89, 2.29] | 0.974 [0.963, 0.984] | 16,768.5 |
| Even | Rotating | Daily | 1.80 [1.70, 1.91] | 0.976 [0.970, 0.982] | 16,020.9 |
| Even | Rotating | Weekly | 1.86 [1.74, 1.99] | 0.986 [0.980, 0.992] | 16,020.9 |
| Even | Matched On-Off | Daily | 1.92 [1.82, 2.02] | 0.973 [0.962, 0.984] | 16,020.9 |
| Even | Matched On-Off | Weekly | 2.03 [1.86, 2.20] | 0.978 [0.966, 0.988] | 16,020.9 |

## 2. Rotating versus its contact-matched control

Positive values mean Rotating has fewer infections or more fadeout than its control.

| Split | Switch | Control − Rotating: mean infected [95% world CI] | Rotating − control: extinction [95% world CI] |
|---|---:|---:|---:|
| Whole | Daily | +5.78 [5.15, 6.44] | +0.052 [0.019, 0.084] |
| Whole | Weekly | +5.01 [4.29, 5.70] | +0.097 [0.061, 0.132] |
| Random | Daily | −0.23 [−0.44, −0.02] | −0.009 [−0.039, 0.022] |
| Random | Weekly | −0.07 [−0.26, 0.10] | −0.004 [−0.018, 0.010] |
| Even | Daily | +0.11 [−0.01, 0.23] | +0.003 [−0.012, 0.018] |
| Even | Weekly | +0.17 [−0.06, 0.39] | +0.008 [−0.000, 0.017] |

## 3. Early-growth thresholds

| Split | Policy | Mean β threshold [95% world CI] |
|---|---|---:|
| Whole | Rotating | 0.0567 [0.0559, 0.0574] |
| Whole | Matched On-Off | 0.0577 [0.0570, 0.0583] |
| Random | Rotating | 0.0833 [0.0810, 0.0855] |
| Random | Matched On-Off | 0.0877 [0.0860, 0.0894] |
| Even | Rotating | 0.0890 [0.0873, 0.0905] |
| Even | Matched On-Off | 0.0905 [0.0892, 0.0917] |

| Split | Matched-control threshold − Rotating threshold [95% world CI] |
|---|---:|
| Whole | +0.0010 [+0.0006, +0.0014] |
| Random | +0.0044 [+0.0023, +0.0063] |
| Even | +0.0015 [−0.0006, +0.0036] |


## 4. Weekly versus daily switching in the stochastic model

Positive values indicate fewer infections or more extinction under weekly switching. Differences and intervals are paired by world.

| Split | Policy | Daily − weekly: mean infected, days 1–84 [95% world CI] | Weekly − daily: extinction by day 84 [95% world CI] |
|---|---|---:|---:|
| Whole | Rotating | +2.89 [2.22, 3.59] | +0.168 [0.132, 0.203] |
| Whole | Matched On-Off | +3.67 [2.93, 4.41] | +0.123 [0.085, 0.163] |
| Random | Rotating | +0.23 [0.07, 0.40] | +0.030 [0.010, 0.052] |
| Random | Matched On-Off | +0.07 [−0.06, 0.21] | +0.025 [0.007, 0.044] |
| Even | Rotating | −0.06 [−0.15, 0.04] | +0.010 [0.002, 0.018] |
| Even | Matched On-Off | −0.11 [−0.23, 0.00] | +0.005 [−0.013, 0.022] |

### Runs with infection still present

| Split | Policy | Day-84 survivors: daily / weekly | Mean infected among day-84 survivors: daily / weekly | Daily − weekly: day-84 conditional mean [95% world CI] | Daily − weekly: daily conditional mean over days 1–84 [95% world CI] | Eligible paired worlds |
|---|---|---:|---:|---:|---:|---:|
| Whole | Rotating | 831 / 663 | 19.45 / 13.53 | +5.95 [5.27, 6.69] | +1.82 [1.28, 2.36] | 20/20 |
| Whole | Matched On-Off | 883 / 760 | 30.70 / 23.80 | +6.88 [5.57, 8.22] | +2.17 [1.66, 2.71] | 20/20 |
| Random | Rotating | 60 / 30 | 3.93 / 3.77 | −0.25 [−2.19, 1.52] | +0.05 [−0.29, 0.43] | 12/20 |
| Random | Matched On-Off | 51 / 26 | 4.10 / 3.31 | +0.55 [−0.90, 1.93] | −0.31 [−0.62, 0.02] | 12/20 |
| Even | Rotating | 24 / 14 | 2.38 / 3.21 | −1.68 [−3.45, −0.23] | −0.43 [−0.84, −0.03] | 11/20 |
| Even | Matched On-Off | 27 / 22 | 2.96 / 3.05 | +0.24 [−0.74, 1.40] | −0.28 [−0.71, 0.18] | 7/20 |


## 5. Deterministic and linearized checks

| Split | Policy | Deterministic SIS: daily − weekly mean infected, days 1–84 [95% world CI] | Linearized: daily − weekly, % of daily mass [95% world CI] |
|---|---|---:|---:|
| Whole | Rotating | +0.90 [0.75, 1.07] | −39.13% [−39.90%, −38.44%] |
| Whole | Matched On-Off | +1.08 [0.94, 1.24] | −39.22% [−39.90%, −38.57%] |
| Random | Rotating | −0.27 [−0.29, −0.24] | −20.24% [−21.46%, −19.12%] |
| Random | Matched On-Off | −0.29 [−0.32, −0.27] | −19.07% [−19.85%, −18.34%] |
| Even | Rotating | −0.22 [−0.23, −0.21] | −17.60% [−18.15%, −17.07%] |
| Even | Matched On-Off | −0.25 [−0.27, −0.24] | −18.04% [−18.59%, −17.50%] |


## Reproduction

[`beta0085_20w50r.npz`](beta0085_20w50r.npz) stores all 12 trajectory arrays with shape **(world, run, day) = (20, 50, 85)**, one active-contact-day array per scenario with shape **(20,)**, and the model settings. It is a NumPy data archive for scripts, rather than a document to open manually. From the repository root, inspect it with:

```bash
PYTHONPATH=network_sis .venv/bin/python - <<'PY'
from network_communities import load_community_data

paths, contacts, settings = load_community_data(
    "network_sis/beta0085_20w50r.npz"
)
print(settings)
print(paths[("whole", "rotating", 7)].shape)
print(contacts[("whole", "rotating", 7)])
PY
```

Recalculate the weekly, survivor, deterministic, and linearized tables **from the saved data and the same seeded worlds**, without rerunning stochastic epidemic trajectories:

```bash
.venv/bin/python network_sis/analyze_weekly_advantage.py \
  network_sis/beta0085_20w50r.npz \
  --deterministic --linearized
```

To regenerate all stochastic trajectories from scratch, write to a separate output path so the archived data remains available for comparison:

```bash
.venv/bin/python -u network_sis/network_communities.py \
  --worlds 20 --runs-per-world 50 --beta 0.085 \
  --save-data network_sis/reproduced_beta0085_20w50r.npz
```

The early-growth threshold table can be regenerated separately:

```bash
PYTHONPATH=network_sis .venv/bin/python - <<'PY'
from network_communities import (
    print_community_threshold_table,
    run_community_threshold_experiment,
)

print_community_threshold_table(run_community_threshold_experiment(20))
PY
```

The code is in [`network_communities.py`](network_communities.py), [`analyze_weekly_advantage.py`](analyze_weekly_advantage.py), and [`sis_experiment.py`](sis_experiment.py). The tables above use β = 0.085. The contact-value sweep below uses additional saved community-network simulations.

## 6. Contact-value welfare and obedience sweep (point estimates)

The archived community trajectories now cover β = 0.04, 0.05, 0.06, 0.07, 0.08, 0.085, 0.09, 0.10, 0.11, and 0.12. Each `betaXXXX_20w50r.npz` contains 20 worlds, 50 runs per world, 84 simulated days, and the same 12 scenarios. The seeded worlds, group splits, initial infections, and run phases follow the same procedure at every β. The additional archives were generated on 2026-11-12; β = 0.085 is the earlier archive.

Use $v$ per person per active contact day, $c=0.05$ per scheduled day at home excluding contact value, $L_{\mathrm{day}}=10$ per infected person-day, and $\gamma=0.2$. For private obedience, the new-infection cost is approximated by $L_{\mathrm{day}}/\gamma$, with prevalence from the start of the decision day. For welfare, infected person-days are summed over saved days 1–84, matching the original outcome table. An active edge-day contributes $2v$ to welfare. Because every rotating split schedules 100 people home per day, the $c$ term cancels in split comparisons.

For `whole` against split $B$, the mean-welfare break-even value is

\[
v^*_{\mathrm{whole},B}=\frac{L_{\mathrm{day}}\left(\overline{I}_{\mathrm{whole}}-\overline{I}_{B}\right)}{2\left(\overline{C}_{\mathrm{whole}}-\overline{C}_{B}\right)},
\]

where $\overline{I}$ is mean infected person-days per run and $\overline{C}$ is mean active edge-days per world. These are point estimates, not confidence intervals.

| β | Daily: whole–random $v^*$ | Daily: whole–even $v^*$ | Weekly: whole–random $v^*$ | Weekly: whole–even $v^*$ |
|---:|---:|---:|---:|---:|
| 0.040 | 0.0191 | 0.0200 | 0.0195 | 0.0195 |
| 0.050 | 0.0361 | 0.0369 | 0.0358 | 0.0372 |
| 0.060 | 0.0738 | 0.0725 | 0.0768 | 0.0768 |
| 0.070 | 0.1676 | 0.1644 | 0.1449 | 0.1430 |
| 0.080 | 0.3366 | 0.3313 | 0.2847 | 0.2765 |
| 0.085 | 0.4648 | 0.4564 | 0.3705 | 0.3582 |
| 0.090 | 0.6002 | 0.5858 | 0.4849 | 0.4667 |
| 0.100 | 0.9444 | 0.9281 | 0.7116 | 0.6869 |
| 0.110 | 1.3211 | 1.2925 | 0.9786 | 0.9480 |
| 0.120 | 1.6131 | 1.5878 | 1.2201 | 1.1912 |

At each pair's own $v^*$, the calculated private deviation shares over scheduled person-days have the following ranges across all 10 β values and both switching frequencies:

| Split | Scheduled home: all $k$ | Scheduled home: $k>0$ only | Scheduled attending: all $k$ | Scheduled home with $k=0$ |
|---|---:|---:|---:|---:|
| Whole | 0.838–1.000 | 0.764–1.000 | 0.000–0.273 | 0.315 |
| Random or even | 0.886–1.000 | 0.884–1.000 | 0.000–0.114 | approximately 0.013 or 0.011 |

For a scheduled-home person with $k=0$, attendance gain equals $c>0$, regardless of $v$ and β. The high home-deviation shares also persist when these zero-contact slots are excluded. These shares are predictions from unilateral payoff comparisons along trajectories simulated under full schedule compliance; they are **person-day shares**, not shares of unique people or outcomes after people actually deviate. The `1.000` and `0.000` displays in the exploratory terminal output were rounded to three decimals.

### Paired-world bootstrap uncertainty

An exploratory paired bootstrap used 1,000 resamples of the 20 worlds (seed 417) for each of the 10 β values, two switching frequencies, and two comparisons. Each resample recomputed its own $v^*$ from the sampled worlds, then evaluated both splits' deviation shares at that same $v^*$. Intervals below are pointwise percentile 95% intervals; they are not adjusted for the 40 comparisons.

At β = 0.085, the four paired comparisons are:

| Switch | Comparison | $v^*$ [95% interval] | Whole: home deviation, $k>0$ [95% interval] | Comparison: home deviation, $k>0$ [95% interval] | Whole: attend deviation [95% interval] |
|---|---|---:|---:|---:|---:|
| Daily | Random | 0.465 [0.425, 0.509] | 0.863 [0.849, 0.874] | 1.000 [1.000, 1.000] | 0.151 [0.137, 0.166] |
| Daily | Even | 0.456 [0.421, 0.495] | 0.853 [0.842, 0.866] | 1.000 [1.000, 1.000] | 0.162 [0.148, 0.173] |
| Weekly | Random | 0.371 [0.338, 0.406] | 0.807 [0.794, 0.822] | 0.999 [0.997, 1.000] | 0.214 [0.198, 0.234] |
| Weekly | Even | 0.358 [0.331, 0.386] | 0.794 [0.782, 0.803] | 0.999 [0.998, 1.000] | 0.235 [0.220, 0.248] |

Across all 40 comparisons, the point estimates for Whole's home-deviation share conditional on $k>0$ range from 0.764 to 1.000. The smallest lower endpoint of their pointwise 95% intervals is 0.737 (β = 0.12, weekly, Whole–Even). For Random or Even, the corresponding point estimates range from 0.884 to 1.000, and the smallest lower interval endpoint is 0.875. The pattern therefore persists after excluding zero-contact slots and allowing the break-even value to vary with sampled worlds.

At $v=v^*$, mean welfare is equal by construction. For values just above $v^*$, Whole has higher estimated welfare under full compliance; home-deviation incentives are nondecreasing in $v$. This is evidence of a welfare–obedience tension within the specified model, not a prediction of epidemic outcomes after noncompliance. Before a paper table, increase bootstrap draws and decide whether to report a unique-person measure in addition to person-day shares.
