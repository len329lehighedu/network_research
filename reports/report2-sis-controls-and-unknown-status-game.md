# Report 2 — SIS controls, thresholds, and the unknown-status game

**Communication log:** Second results email, PDF pp. 7–11.

The SIS runs use independent streams for the network, group split, initial infections, and epidemic simulation. The seven-schedule comparison uses 20 worlds, 50 runs per world and schedule, an 84-day horizon, β = 0.04, and γ = 0.20. `On–Off half` removes half the edges before applying the corresponding On–Off schedule.

## Complete schedule comparison at β = 0.04

| Schedule | Extinct by day 84 | Mean infected on day 84 | Mean infected, days 1–84 [95% world CI] | Mean active edge-days |
|---|---:|---:|---:|---:|
| Full | 1.1% | 63.40 | 49.72 [47.74, 51.62] | 67,065.6 |
| On–Off daily | 96.2% | 0.12 | 2.01 [1.87, 2.14] | 33,532.8 |
| On–Off weekly | 98.7% | 0.04 | 2.06 [1.96, 2.17] | 33,532.8 |
| Rotating daily | 100.0% | 0.00 | 0.81 [0.78, 0.84] | 16,907.1 |
| Rotating weekly | 100.0% | 0.00 | 0.86 [0.82, 0.89] | 16,907.1 |
| On–Off half daily | 100.0% | 0.00 | 0.83 [0.80, 0.85] | 16,751.7 |
| On–Off half weekly | 100.0% | 0.00 | 0.84 [0.82, 0.87] | 16,751.7 |

| Contrast, first minus second | Difference in mean infected | 95% paired world CI |
|---|---:|---:|
| On–Off weekly − daily | +0.054 | [−0.072, 0.181] |
| Rotating weekly − daily | +0.042 | [0.005, 0.080] |
| On–Off daily − Rotating daily | +1.192 | [1.063, 1.327] |
| On–Off weekly − Rotating weekly | +1.204 | [1.110, 1.306] |
| On–Off half daily − Rotating daily | +0.015 | [−0.027, 0.053] |
| On–Off half weekly − Rotating weekly | −0.011 | [−0.058, 0.035] |

## Early-growth thresholds

| Schedule | Daily threshold [95% world CI] | Weekly threshold [95% world CI] |
|---|---:|---:|
| Full | 0.0221 [0.0218, 0.0224] | — |
| On–Off | 0.0498 [0.0491, 0.0505] | 0.0498 [0.0491, 0.0505] |
| Rotating | 0.0849 [0.0836, 0.0862] | 0.0849 [0.0836, 0.0862] |
| On–Off half | 0.0874 [0.0862, 0.0888] | 0.0874 [0.0862, 0.0888] |

[Threshold derivation](../pdfs/threshold_prove.pdf) · [Seven-schedule figure](../graphs/sis_mean_multiworld_controls_beta004.png)

## Complete beta sweep

The interval estimates below are from the sweep output. The separate β = 0.04 table above preserves the intervals from the email.

| beta | schedule | mean infected, days 1–84 [95% world CI] | extinct by day 84 [95% world CI] |
|---:|---|---:|---:|
| 0.02 | full, 1 day | 2.48 [2.26, 2.69] | 0.935 [0.912, 0.956] |
| 0.02 | on_off, 1 day | 0.84 [0.81, 0.87] | 1.000 [1.000, 1.000] |
| 0.02 | on_off, 7 day | 0.86 [0.83, 0.89] | 0.999 [0.997, 1.000] |
| 0.02 | rotating, 1 day | 0.60 [0.58, 0.61] | 1.000 [1.000, 1.000] |
| 0.02 | rotating, 7 day | 0.62 [0.60, 0.64] | 1.000 [1.000, 1.000] |
| 0.02 | on_off_half, 1 day | 0.62 [0.61, 0.63] | 1.000 [1.000, 1.000] |
| 0.02 | on_off_half, 7 day | 0.63 [0.61, 0.64] | 1.000 [1.000, 1.000] |
| 0.03 | full, 1 day | 16.03 [14.58, 17.49] | 0.228 [0.192, 0.265] |
| 0.03 | on_off, 1 day | 1.21 [1.15, 1.27] | 0.998 [0.995, 1.000] |
| 0.03 | on_off, 7 day | 1.26 [1.20, 1.31] | 0.998 [0.994, 1.000] |
| 0.03 | rotating, 1 day | 0.68 [0.66, 0.70] | 1.000 [1.000, 1.000] |
| 0.03 | rotating, 7 day | 0.72 [0.69, 0.75] | 1.000 [1.000, 1.000] |
| 0.03 | on_off_half, 1 day | 0.71 [0.69, 0.72] | 1.000 [1.000, 1.000] |
| 0.03 | on_off_half, 7 day | 0.72 [0.70, 0.75] | 1.000 [1.000, 1.000] |
| 0.04 | full, 1 day | 49.72 [47.66, 51.57] | 0.011 [0.004, 0.021] |
| 0.04 | on_off, 1 day | 2.01 [1.87, 2.14] | 0.962 [0.950, 0.973] |
| 0.04 | on_off, 7 day | 2.06 [1.96, 2.17] | 0.987 [0.979, 0.994] |
| 0.04 | rotating, 1 day | 0.81 [0.78, 0.84] | 1.000 [1.000, 1.000] |
| 0.04 | rotating, 7 day | 0.86 [0.82, 0.89] | 1.000 [1.000, 1.000] |
| 0.04 | on_off_half, 1 day | 0.83 [0.80, 0.85] | 1.000 [1.000, 1.000] |
| 0.04 | on_off_half, 7 day | 0.84 [0.82, 0.87] | 1.000 [1.000, 1.000] |
| 0.05 | full, 1 day | 73.84 [72.00, 75.53] | 0.000 [0.000, 0.000] |
| 0.05 | on_off, 1 day | 3.97 [3.65, 4.29] | 0.802 [0.775, 0.829] |
| 0.05 | on_off, 7 day | 4.20 [3.95, 4.45] | 0.836 [0.803, 0.868] |
| 0.05 | rotating, 1 day | 0.97 [0.93, 1.02] | 0.998 [0.995, 1.000] |
| 0.05 | rotating, 7 day | 1.05 [0.99, 1.11] | 1.000 [1.000, 1.000] |
| 0.05 | on_off_half, 1 day | 1.00 [0.96, 1.03] | 1.000 [1.000, 1.000] |
| 0.05 | on_off_half, 7 day | 1.01 [0.98, 1.05] | 0.998 [0.995, 1.000] |
| 0.06 | full, 1 day | 90.37 [88.80, 91.82] | 0.000 [0.000, 0.000] |
| 0.06 | on_off, 1 day | 9.75 [8.82, 10.73] | 0.422 [0.377, 0.468] |
| 0.06 | on_off, 7 day | 9.19 [8.40, 9.97] | 0.550 [0.505, 0.597] |
| 0.06 | rotating, 1 day | 1.20 [1.14, 1.26] | 0.998 [0.995, 1.000] |
| 0.06 | rotating, 7 day | 1.27 [1.19, 1.35] | 0.996 [0.992, 0.999] |
| 0.06 | on_off_half, 1 day | 1.18 [1.14, 1.24] | 0.996 [0.991, 1.000] |
| 0.06 | on_off_half, 7 day | 1.23 [1.18, 1.29] | 0.999 [0.997, 1.000] |
| 0.07 | full, 1 day | 102.52 [101.15, 103.76] | 0.000 [0.000, 0.000] |
| 0.07 | on_off, 1 day | 20.53 [18.66, 22.34] | 0.141 [0.112, 0.174] |
| 0.07 | on_off, 7 day | 18.68 [17.46, 19.98] | 0.261 [0.228, 0.293] |
| 0.07 | rotating, 1 day | 1.50 [1.42, 1.59] | 0.985 [0.978, 0.992] |
| 0.07 | rotating, 7 day | 1.56 [1.46, 1.65] | 0.992 [0.986, 0.997] |
| 0.07 | on_off_half, 1 day | 1.49 [1.42, 1.57] | 0.990 [0.984, 0.996] |
| 0.07 | on_off_half, 7 day | 1.52 [1.46, 1.60] | 0.993 [0.986, 0.998] |
| 0.08 | full, 1 day | 111.80 [110.56, 112.93] | 0.000 [0.000, 0.000] |
| 0.08 | on_off, 1 day | 35.84 [33.73, 37.90] | 0.035 [0.024, 0.046] |
| 0.08 | on_off, 7 day | 30.66 [28.82, 32.42] | 0.104 [0.085, 0.125] |
| 0.08 | rotating, 1 day | 1.95 [1.81, 2.09] | 0.967 [0.954, 0.979] |
| 0.08 | rotating, 7 day | 2.05 [1.90, 2.21] | 0.974 [0.964, 0.984] |
| 0.08 | on_off_half, 1 day | 2.03 [1.89, 2.17] | 0.961 [0.946, 0.975] |
| 0.08 | on_off_half, 7 day | 2.03 [1.92, 2.13] | 0.971 [0.962, 0.980] |
| 0.09 | full, 1 day | 118.96 [117.82, 119.99] | 0.000 [0.000, 0.000] |
| 0.09 | on_off, 1 day | 49.81 [47.58, 51.89] | 0.011 [0.002, 0.023] |
| 0.09 | on_off, 7 day | 42.74 [40.95, 44.46] | 0.060 [0.045, 0.075] |
| 0.09 | rotating, 1 day | 2.89 [2.66, 3.11] | 0.888 [0.865, 0.911] |
| 0.09 | rotating, 7 day | 2.73 [2.48, 2.98] | 0.936 [0.919, 0.952] |
| 0.09 | on_off_half, 1 day | 2.74 [2.56, 2.96] | 0.919 [0.894, 0.941] |
| 0.09 | on_off_half, 7 day | 2.77 [2.60, 2.93] | 0.931 [0.913, 0.948] |
| 0.10 | full, 1 day | 124.71 [123.66, 125.65] | 0.000 [0.000, 0.000] |
| 0.10 | on_off, 1 day | 61.72 [59.90, 63.42] | 0.005 [0.001, 0.009] |
| 0.10 | on_off, 7 day | 52.26 [50.50, 53.99] | 0.049 [0.036, 0.062] |
| 0.10 | rotating, 1 day | 3.94 [3.54, 4.31] | 0.801 [0.760, 0.843] |
| 0.10 | rotating, 7 day | 3.63 [3.32, 3.95] | 0.875 [0.850, 0.899] |
| 0.10 | on_off_half, 1 day | 3.98 [3.76, 4.21] | 0.803 [0.774, 0.830] |
| 0.10 | on_off_half, 7 day | 3.84 [3.58, 4.11] | 0.844 [0.814, 0.872] |
| 0.11 | full, 1 day | 129.53 [128.55, 130.40] | 0.000 [0.000, 0.000] |
| 0.11 | on_off, 1 day | 71.97 [70.17, 73.63] | 0.002 [0.000, 0.005] |
| 0.11 | on_off, 7 day | 60.14 [58.35, 61.83] | 0.035 [0.024, 0.046] |
| 0.11 | rotating, 1 day | 6.31 [5.67, 6.92] | 0.624 [0.570, 0.682] |
| 0.11 | rotating, 7 day | 5.25 [4.73, 5.81] | 0.757 [0.704, 0.805] |
| 0.11 | on_off_half, 1 day | 6.55 [6.05, 7.05] | 0.593 [0.550, 0.637] |
| 0.11 | on_off_half, 7 day | 5.59 [5.16, 6.03] | 0.726 [0.694, 0.757] |
| 0.12 | full, 1 day | 133.49 [132.57, 134.30] | 0.000 [0.000, 0.000] |
| 0.12 | on_off, 1 day | 79.92 [78.13, 81.53] | 0.002 [0.000, 0.005] |
| 0.12 | on_off, 7 day | 66.29 [64.65, 67.82] | 0.031 [0.021, 0.041] |
| 0.12 | rotating, 1 day | 9.04 [8.03, 10.07] | 0.403 [0.342, 0.465] |
| 0.12 | rotating, 7 day | 7.48 [6.74, 8.22] | 0.585 [0.533, 0.635] |
| 0.12 | on_off_half, 1 day | 9.63 [8.93, 10.40] | 0.422 [0.378, 0.464] |
| 0.12 | on_off_half, 7 day | 8.08 [7.56, 8.60] | 0.559 [0.519, 0.597] |

[Saved sweep output](../network_sis/data/beta_sweep_20w50r.txt) · [Sweep figure](../network_sis/data/sis_beta_sweep_20w50r.png)

## Unknown-status game: all eight action profiles

At π = 0.10, β = 0.04, infection cost 10, and home cost 0.05, the [unknown-status model](../pdfs/payoff_new.pdf) gives the following values. The column titled Fair lottery assigns equal probability to each pure Nash profile.

| Profile | Group payoff | Pure Nash | Fair lottery probability | Symmetric optimal CE probability |
|---|---:|:---:|---:|---:|
| AAA | −3.215568 | No | 0 | 0 |
| AAH | −3.122000 | Yes | 1/3 | 0.187206 |
| AHA | −3.122000 | Yes | 1/3 | 0.187206 |
| AHH | −3.100000 | No | 0 | 0.146128 |
| HAA | −3.122000 | Yes | 1/3 | 0.187206 |
| HAH | −3.100000 | No | 0 | 0.146128 |
| HHA | −3.100000 | No | 0 | 0.146128 |
| HHH | −3.150000 | No | 0 | 0 |

The optimal CE improves expected group payoff from −3.122000 to −3.112356. Each player attends with probability 0.520539. At π = 0.10, the two-attendee rotation is supported on pure Nash equilibria for c in [0.036000, 0.071856].

## Reproduce

Run from the repository root. [Report 1](report1-initial-sis-and-payoffs.md#reproduce-the-figures-with-the-current-seed-scheme) contains the figure commands.

### Seven schedules at beta = 0.04

```bash
.venv/bin/python -u network_sis/sis_experiment.py --beta 0.04 --worlds 20 --runs-per-world 50 --plot-path graphs/reproduced_sis_mean_multiworld_controls_beta004.png | tee network_sis/data/reproduced_beta004.txt
```

### Beta sweep and 14-day growth thresholds

```bash
.venv/bin/python -u network_sis/sis_experiment.py --sweep --worlds 20 --runs-per-world 50 --plot-path network_sis/data/reproduced_sis_beta_sweep_20w50r.png | tee network_sis/data/reproduced_beta_sweep_20w50r.txt
.venv/bin/python network_sis/sis_experiment.py --thresholds --worlds 20
```

```bash
.venv/bin/python game/game.py
```
