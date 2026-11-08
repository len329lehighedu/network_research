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
.venv/bin/python - <<'PY'
from network_communities import load_community_data

paths, contacts, settings = load_community_data(
    "community_results/beta0085_20w50r.npz"
)
print(settings)
print(paths[("whole", "rotating", 7)].shape)
print(contacts[("whole", "rotating", 7)])
PY
```

Recalculate the weekly, survivor, deterministic, and linearized tables **from the saved data and the same seeded worlds**, without rerunning stochastic epidemic trajectories:

```bash
.venv/bin/python analyze_weekly_advantage.py \
  community_results/beta0085_20w50r.npz \
  --deterministic --linearized
```

To regenerate all stochastic trajectories from scratch, write to a separate output path so the archived data remains available for comparison:

```bash
mkdir -p reproduced
.venv/bin/python -u network_communities.py \
  --worlds 20 --runs-per-world 50 --beta 0.085 \
  --save-data reproduced/beta0085_20w50r.npz
```

The early-growth threshold table can be regenerated separately:

```bash
.venv/bin/python - <<'PY'
from network_communities import (
    print_community_threshold_table,
    run_community_threshold_experiment,
)

print_community_threshold_table(run_community_threshold_experiment(20))
PY
```

The code is in [`network_communities.py`](../network_communities.py), [`analyze_weekly_advantage.py`](../analyze_weekly_advantage.py), and [`sis_experiment.py`](../sis_experiment.py). Results at β = 0.085 describe this experiment; they are not a sweep over β for the community network.
