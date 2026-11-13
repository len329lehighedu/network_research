# Reproduce the SIS experiments and attendance game

Run commands from the repository root. The reported results used Python 3.14 and the versions in `requirements.txt`. Existing figures are in `graphs/`; reproduction commands use new filenames there.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## SIS model checks and Figures 1–3

```bash
.venv/bin/python network_sis/sis_experiment.py --sanity
.venv/bin/python network_sis/sis_experiment.py --figure single --plot-path graphs/reproduced_sis_single_run.png
.venv/bin/python network_sis/sis_experiment.py --figure fixed-phase --plot-path graphs/reproduced_sis_mean_1000_runs.png
.venv/bin/python network_sis/sis_experiment.py --figure varied-phase --plot-path graphs/reproduced_sis_mean_1000_runs_startdate.png
```

## Seven schedules at beta = 0.04

```bash
.venv/bin/python -u network_sis/sis_experiment.py --beta 0.04 --worlds 20 --runs-per-world 50 --plot-path graphs/reproduced_sis_mean_multiworld_controls_beta004.png | tee network_sis/reproduced_beta004.txt
```

## Beta sweep and 14-day growth thresholds

```bash
.venv/bin/python -u network_sis/sis_experiment.py --sweep --worlds 20 --runs-per-world 50 --plot-path graphs/reproduced_sis_beta_sweep_20w50r.png | tee network_sis/reproduced_beta_sweep_20w50r.txt
.venv/bin/python network_sis/sis_experiment.py --thresholds --worlds 20
```

## Three-person attendance game

```bash
.venv/bin/python game/game.py
.venv/bin/python game/game.py --cost-grid-output game/reproduced_cost_grid.txt
.venv/bin/python game/network_game.py --summary
```

The concise game results are in [game/game_results.md](game/game_results.md).

## Community-network experiment

Recalculate tables from the saved trajectories:

```bash
.venv/bin/python network_sis/analyze_weekly_advantage.py network_sis/beta0085_20w50r.npz --deterministic --linearized
```

See [network_sis/community_result.md](network_sis/community_result.md) for the complete results and commands to regenerate trajectories.

## Contact value and attendance incentives

### Community experiment settings

| People | Communities | Days | Worlds | Runs per world and schedule | Infection cost per person-day | Recovery probability per day | Home cost per day | Private cost per new infection | Bootstrap draws per comparison |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 200 | 8 × 25 | 84 | 20 | 50 | 10 | 0.20 | 0.05 | 50 | 1,000 |

### Break-even contact value under full compliance

| β | Daily: Whole vs. Random | Daily: Whole vs. Even | Weekly: Whole vs. Random | Weekly: Whole vs. Even |
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

### Person-days with a profitable unilateral deviation at break-even

| Split | Home → attend | Home → attend, k > 0 | Attend → home | Scheduled home with k = 0 |
|---|---:|---:|---:|---:|
| Whole | 83.8–100.0% | 76.4–100.0% | 0.0–27.3% | 31.5% |
| Random or Even | 88.6–100.0% | 88.4–100.0% | 0.0–11.4% | 1.1–1.3% |

### Break-even values and deviations at β = 0.085 with paired 95% world intervals

| Switching | Alternative | v* [95% CI] | Whole: home → attend, k > 0 | Alternative: home → attend, k > 0 | Whole: attend → home |
|---|---|---:|---:|---:|---:|
| Daily | Random | 0.465 [0.425, 0.509] | 86.3% [84.9, 87.4] | 100.0% [100.0, 100.0] | 15.1% [13.7, 16.6] |
| Daily | Even | 0.456 [0.421, 0.495] | 85.3% [84.2, 86.6] | 100.0% [100.0, 100.0] | 16.2% [14.8, 17.3] |
| Weekly | Random | 0.371 [0.338, 0.406] | 80.7% [79.4, 82.2] | 99.9% [99.7, 100.0] | 21.4% [19.8, 23.4] |
| Weekly | Even | 0.358 [0.331, 0.386] | 79.4% [78.2, 80.3] | 99.9% [99.8, 100.0] | 23.5% [22.0, 24.8] |

### Reproduce the community tables

```bash
PYTHONPATH=.:network_sis .venv/bin/python reproduce_contact_value_tables.py \
  --community-dir network_sis
```

```bash
# Regenerate the SIS archives in a separate directory and rebuild the tables.
(
  set -e
  community_data=$(mktemp -d)
  for code in 0040 0050 0060 0070 0080 0085 0090 0100 0110 0120; do
    .venv/bin/python -u network_sis/network_communities.py \
      --beta "0.${code#0}" --worlds 20 --runs-per-world 50 \
      --save-data "$community_data/beta${code}_20w50r.npz"
  done
  PYTHONPATH=.:network_sis .venv/bin/python reproduce_contact_value_tables.py \
    --community-dir "$community_data"
)
```

## Connected network atlas

### Experiment settings

| Network sizes | Connected structures by size | Cases | β | Infection cost per person-day | Recovery probability per day | Contact value per participant |
|---|---|---:|---:|---:|---:|---:|
| 4, 5, 6 | 6, 21, 112 | 556 | 0.04 | 10 | 0.20 | 0.14 |

### Group cost comparisons by parameter pair

| π | c | CE improves on best pure Nash | CE improves on lowest-cost independent Nash found | CE reaches social minimum |
|---:|---:|---:|---:|---:|
| 0.10 | 0.05 | 65/139 | 65/139 | 70/139 |
| 0.10 | 0.12 | 32/139 | 32/139 | 14/139 |
| 0.50 | 0.05 | 0/139 | 0/139 | 139/139 |
| 0.50 | 0.12 | 0/139 | 0/139 | 139/139 |
| **Total** | | **97/556** | **97/556** | **362/556** |

### CE gains by number of pure Nash equilibria at π = 0.10

| π | c | Pure equilibria per network | CE improves on best pure Nash |
|---:|---:|---|---:|
| 0.10 | 0.05 | One | 4/29 |
| 0.10 | 0.05 | Multiple | 61/110 |
| 0.10 | 0.12 | One | 0/104 |
| 0.10 | 0.12 | Multiple | 32/35 |

### Atlas 42 costs above the infection baseline at π = 0.10, c = 0.05

| Atlas 42 outcome | Expected group cost | Highest expected individual cost |
|---|---:|---:|
| Unique pure Nash (`AAAAH`) | 0.210000 | 0.050000 |
| Lowest-cost independent Nash found | 0.210000 | — |
| Optimal CE, averaged over graph symmetries | 0.191455 | 0.050000 |
| Social minimum | 0.150000 | — |

| CE comparison with best pure Nash | Value |
|---|---:|
| Group cost reduction above baseline | 0.018545 |
| Group cost reduction relative to best pure Nash | 8.8% |
| Share of the gap to the social minimum closed | 30.9% |

### Reproduce the atlas tables

```bash
# Summarize the saved 556 cases.
PYTHONPATH=game .venv/bin/python reproduce_contact_value_tables.py \
  --atlas-csv game/atlas_contact_value_4_6.csv
```

```bash
# Solve the full atlas grid again and summarize the new CSV.
atlas_data=$(mktemp -d)
.venv/bin/python game/network_game.py --sizes 4 5 6 \
  --atlas-output "$atlas_data/atlas_contact_value_4_6.csv" &&
PYTHONPATH=game .venv/bin/python reproduce_contact_value_tables.py \
  --atlas-csv "$atlas_data/atlas_contact_value_4_6.csv"
```

## Community-network detailed results

### Infected person-days per run

| β | Switch (days) | Whole | Random | Even |
|---:|---:|---:|---:|---:|
| 0.040 | 1 | 115.72 | 70.40 | 65.47 |
| 0.040 | 7 | 117.18 | 70.91 | 68.15 |
| 0.050 | 1 | 171.93 | 86.52 | 78.92 |
| 0.050 | 7 | 170.81 | 86.09 | 77.06 |
| 0.060 | 1 | 278.00 | 103.24 | 95.52 |
| 0.060 | 7 | 285.92 | 103.90 | 92.54 |
| 0.070 | 1 | 528.22 | 131.27 | 114.25 |
| 0.070 | 7 | 471.49 | 128.30 | 111.30 |
| 0.080 | 1 | 970.91 | 173.55 | 136.54 |
| 0.080 | 7 | 836.35 | 161.99 | 140.15 |
| 0.085 | 1 | 1,300.92 | 199.98 | 151.57 |
| 0.085 | 7 | 1,058.23 | 180.48 | 156.26 |
| 0.090 | 1 | 1,651.46 | 229.62 | 176.23 |
| 0.090 | 7 | 1,346.92 | 198.17 | 171.60 |
| 0.100 | 1 | 2,567.53 | 330.33 | 230.24 |
| 0.100 | 7 | 1,958.13 | 272.41 | 228.37 |
| 0.110 | 1 | 3,567.51 | 438.01 | 312.48 |
| 0.110 | 7 | 2,680.15 | 362.08 | 292.83 |
| 0.120 | 1 | 4,436.56 | 615.51 | 438.05 |
| 0.120 | 7 | 3,387.65 | 497.51 | 387.83 |

### β = 0.085: break-even components

| Switch | Comparison | Extra infected person-days | Extra active edge-days | v* |
|---|---|---:|---:|---:|
| Daily | Whole–random | 1,100.936 | 11,844.0 | 0.464765 |
| Daily | Whole–even | 1,149.349 | 12,591.6 | 0.456395 |
| Weekly | Whole–random | 877.753 | 11,844.0 | 0.370548 |
| Weekly | Whole–even | 901.974 | 12,591.6 | 0.358165 |

### Scheduled-home slots with zero attending contacts

| Split | Share with k=0 |
|---|---:|
| Whole | 0.31525 |
| Random | 0.013 |
| Even | 0.011 |

### β = 0.085: obedience point estimates for both splits

| Switch | Comparison | v* | Whole home | Whole home, k>0 | Whole attend | Comparison home | Comparison home, k>0 | Comparison attend |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Daily | Random | 0.464765 | 0.906 | 0.863 | 0.151 | 1.000 | 1.000 | 0.000 |
| Daily | Even | 0.456395 | 0.899 | 0.853 | 0.162 | 1.000 | 1.000 | 0.000 |
| Weekly | Random | 0.370548 | 0.868 | 0.807 | 0.214 | 0.999 | 0.999 | 0.001 |
| Weekly | Even | 0.358165 | 0.859 | 0.794 | 0.235 | 0.999 | 0.999 | 0.001 |

### β sweep: paired-world bootstrap intervals (40 cases)

| β | Switch (days) | Comparison | v* [95% interval] | Whole home, k>0 [95% interval] | Comparison home, k>0 [95% interval] | Whole attend [95% interval] |
|---:|---:|---|---:|---:|---:|---:|
| 0.040 | 1 | random | 0.019 [0.017,0.021] | 0.895 [0.888,0.899] | 0.890 [0.886,0.899] | 0.209 [0.200,0.214] |
| 0.040 | 1 | even | 0.020 [0.018,0.022] | 0.895 [0.890,0.900] | 0.900 [0.892,0.904] | 0.203 [0.199,0.210] |
| 0.040 | 7 | random | 0.020 [0.017,0.022] | 0.891 [0.885,0.896] | 0.894 [0.886,0.899] | 0.194 [0.190,0.201] |
| 0.040 | 7 | even | 0.019 [0.017,0.021] | 0.891 [0.884,0.896] | 0.891 [0.884,0.901] | 0.199 [0.190,0.203] |
| 0.050 | 1 | random | 0.036 [0.031,0.041] | 0.857 [0.831,0.860] | 0.887 [0.875,0.903] | 0.246 [0.234,0.254] |
| 0.050 | 1 | even | 0.037 [0.033,0.041] | 0.858 [0.836,0.862] | 0.900 [0.887,0.907] | 0.243 [0.232,0.254] |
| 0.050 | 7 | random | 0.036 [0.033,0.039] | 0.846 [0.834,0.859] | 0.884 [0.879,0.897] | 0.234 [0.226,0.238] |
| 0.050 | 7 | even | 0.037 [0.034,0.040] | 0.857 [0.844,0.862] | 0.902 [0.891,0.907] | 0.230 [0.224,0.237] |
| 0.060 | 1 | random | 0.074 [0.067,0.081] | 0.808 [0.803,0.829] | 0.914 [0.908,0.928] | 0.273 [0.257,0.279] |
| 0.060 | 1 | even | 0.072 [0.066,0.079] | 0.808 [0.800,0.820] | 0.921 [0.912,0.934] | 0.273 [0.263,0.283] |
| 0.060 | 7 | random | 0.077 [0.067,0.088] | 0.810 [0.800,0.823] | 0.917 [0.905,0.929] | 0.265 [0.244,0.268] |
| 0.060 | 7 | even | 0.077 [0.067,0.087] | 0.810 [0.799,0.823] | 0.925 [0.913,0.937] | 0.265 [0.244,0.269] |
| 0.070 | 1 | random | 0.168 [0.148,0.189] | 0.834 [0.812,0.851] | 0.985 [0.965,0.994] | 0.236 [0.199,0.266] |
| 0.070 | 1 | even | 0.164 [0.146,0.183] | 0.829 [0.809,0.841] | 0.988 [0.970,0.995] | 0.237 [0.213,0.270] |
| 0.070 | 7 | random | 0.145 [0.132,0.159] | 0.799 [0.786,0.817] | 0.959 [0.943,0.977] | 0.257 [0.239,0.283] |
| 0.070 | 7 | even | 0.143 [0.131,0.155] | 0.799 [0.783,0.812] | 0.964 [0.948,0.976] | 0.261 [0.253,0.289] |
| 0.080 | 1 | random | 0.337 [0.307,0.379] | 0.847 [0.831,0.867] | 1.000 [0.999,1.000] | 0.180 [0.156,0.202] |
| 0.080 | 1 | even | 0.331 [0.304,0.366] | 0.840 [0.827,0.855] | 1.000 [1.000,1.000] | 0.181 [0.170,0.207] |
| 0.080 | 7 | random | 0.285 [0.261,0.314] | 0.810 [0.799,0.825] | 0.996 [0.993,0.998] | 0.216 [0.203,0.240] |
| 0.080 | 7 | even | 0.276 [0.254,0.301] | 0.797 [0.789,0.812] | 0.997 [0.994,0.999] | 0.240 [0.218,0.252] |
| 0.085 | 1 | random | 0.465 [0.425,0.509] | 0.863 [0.849,0.874] | 1.000 [1.000,1.000] | 0.151 [0.137,0.166] |
| 0.085 | 1 | even | 0.456 [0.421,0.495] | 0.853 [0.842,0.866] | 1.000 [1.000,1.000] | 0.162 [0.148,0.173] |
| 0.085 | 7 | random | 0.371 [0.338,0.406] | 0.807 [0.794,0.822] | 0.999 [0.997,1.000] | 0.214 [0.198,0.234] |
| 0.085 | 7 | even | 0.358 [0.331,0.386] | 0.794 [0.782,0.803] | 0.999 [0.998,1.000] | 0.235 [0.220,0.248] |
| 0.090 | 1 | random | 0.600 [0.564,0.645] | 0.863 [0.846,0.877] | 1.000 [1.000,1.000] | 0.142 [0.124,0.158] |
| 0.090 | 1 | even | 0.586 [0.553,0.624] | 0.851 [0.834,0.862] | 1.000 [1.000,1.000] | 0.157 [0.140,0.172] |
| 0.090 | 7 | random | 0.485 [0.449,0.520] | 0.807 [0.794,0.822] | 1.000 [0.999,1.000] | 0.207 [0.189,0.223] |
| 0.090 | 7 | even | 0.467 [0.435,0.495] | 0.790 [0.775,0.802] | 1.000 [0.999,1.000] | 0.231 [0.212,0.242] |
| 0.100 | 1 | random | 0.944 [0.879,1.014] | 0.889 [0.860,0.931] | 1.000 [1.000,1.000] | 0.069 [0.027,0.111] |
| 0.100 | 1 | even | 0.928 [0.863,0.994] | 0.878 [0.848,0.911] | 1.000 [1.000,1.000] | 0.086 [0.044,0.125] |
| 0.100 | 7 | random | 0.712 [0.669,0.759] | 0.800 [0.785,0.817] | 1.000 [1.000,1.000] | 0.193 [0.173,0.211] |
| 0.100 | 7 | even | 0.687 [0.647,0.726] | 0.771 [0.762,0.790] | 1.000 [1.000,1.000] | 0.222 [0.204,0.234] |
| 0.110 | 1 | random | 1.321 [1.261,1.382] | 0.999 [0.972,1.000] | 1.000 [1.000,1.000] | 0.000 [0.000,0.001] |
| 0.110 | 1 | even | 1.293 [1.236,1.343] | 0.989 [0.948,1.000] | 1.000 [1.000,1.000] | 0.000 [0.000,0.004] |
| 0.110 | 7 | random | 0.979 [0.922,1.032] | 0.791 [0.770,0.828] | 1.000 [1.000,1.000] | 0.151 [0.105,0.191] |
| 0.110 | 7 | even | 0.948 [0.902,0.992] | 0.764 [0.745,0.788] | 1.000 [1.000,1.000] | 0.191 [0.155,0.219] |
| 0.120 | 1 | random | 1.613 [1.553,1.671] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] |
| 0.120 | 1 | even | 1.588 [1.528,1.641] | 1.000 [1.000,1.000] | 1.000 [1.000,1.000] | 0.000 [0.000,0.000] |
| 0.120 | 7 | random | 1.220 [1.165,1.275] | 0.805 [0.761,0.868] | 1.000 [1.000,1.000] | 0.061 [0.023,0.121] |
| 0.120 | 7 | even | 1.191 [1.138,1.242] | 0.774 [0.737,0.817] | 1.000 [1.000,1.000] | 0.098 [0.047,0.154] |

### Community-network baseline at β = 0.085

#### 1. Stochastic scenario outcomes

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

#### 2. Rotating versus its contact-matched control

| Split | Switch | Control − Rotating: mean infected [95% world CI] | Rotating − control: extinction [95% world CI] |
|---|---:|---:|---:|
| Whole | Daily | +5.78 [5.15, 6.44] | +0.052 [0.019, 0.084] |
| Whole | Weekly | +5.01 [4.29, 5.70] | +0.097 [0.061, 0.132] |
| Random | Daily | −0.23 [−0.44, −0.02] | −0.009 [−0.039, 0.022] |
| Random | Weekly | −0.07 [−0.26, 0.10] | −0.004 [−0.018, 0.010] |
| Even | Daily | +0.11 [−0.01, 0.23] | +0.003 [−0.012, 0.018] |
| Even | Weekly | +0.17 [−0.06, 0.39] | +0.008 [−0.000, 0.017] |

#### 3. Early-growth thresholds

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

#### 4. Weekly versus daily switching in the stochastic model

| Split | Policy | Daily − weekly: mean infected, days 1–84 [95% world CI] | Weekly − daily: extinction by day 84 [95% world CI] |
|---|---|---:|---:|
| Whole | Rotating | +2.89 [2.22, 3.59] | +0.168 [0.132, 0.203] |
| Whole | Matched On-Off | +3.67 [2.93, 4.41] | +0.123 [0.085, 0.163] |
| Random | Rotating | +0.23 [0.07, 0.40] | +0.030 [0.010, 0.052] |
| Random | Matched On-Off | +0.07 [−0.06, 0.21] | +0.025 [0.007, 0.044] |
| Even | Rotating | −0.06 [−0.15, 0.04] | +0.010 [0.002, 0.018] |
| Even | Matched On-Off | −0.11 [−0.23, 0.00] | +0.005 [−0.013, 0.022] |

##### Runs with infection still present

| Split | Policy | Day-84 survivors: daily / weekly | Mean infected among day-84 survivors: daily / weekly | Daily − weekly: day-84 conditional mean [95% world CI] | Daily − weekly: daily conditional mean over days 1–84 [95% world CI] | Eligible paired worlds |
|---|---|---:|---:|---:|---:|---:|
| Whole | Rotating | 831 / 663 | 19.45 / 13.53 | +5.95 [5.27, 6.69] | +1.82 [1.28, 2.36] | 20/20 |
| Whole | Matched On-Off | 883 / 760 | 30.70 / 23.80 | +6.88 [5.57, 8.22] | +2.17 [1.66, 2.71] | 20/20 |
| Random | Rotating | 60 / 30 | 3.93 / 3.77 | −0.25 [−2.19, 1.52] | +0.05 [−0.29, 0.43] | 12/20 |
| Random | Matched On-Off | 51 / 26 | 4.10 / 3.31 | +0.55 [−0.90, 1.93] | −0.31 [−0.62, 0.02] | 12/20 |
| Even | Rotating | 24 / 14 | 2.38 / 3.21 | −1.68 [−3.45, −0.23] | −0.43 [−0.84, −0.03] | 11/20 |
| Even | Matched On-Off | 27 / 22 | 2.96 / 3.05 | +0.24 [−0.74, 1.40] | −0.28 [−0.71, 0.18] | 7/20 |

#### 5. Deterministic and linearized checks

| Split | Policy | Deterministic SIS: daily − weekly mean infected, days 1–84 [95% world CI] | Linearized: daily − weekly, % of daily mass [95% world CI] |
|---|---|---:|---:|
| Whole | Rotating | +0.90 [0.75, 1.07] | −39.13% [−39.90%, −38.44%] |
| Whole | Matched On-Off | +1.08 [0.94, 1.24] | −39.22% [−39.90%, −38.57%] |
| Random | Rotating | −0.27 [−0.29, −0.24] | −20.24% [−21.46%, −19.12%] |
| Random | Matched On-Off | −0.29 [−0.32, −0.27] | −19.07% [−19.85%, −18.34%] |
| Even | Rotating | −0.22 [−0.23, −0.21] | −17.60% [−18.15%, −17.07%] |
| Even | Matched On-Off | −0.25 [−0.27, −0.24] | −18.04% [−18.59%, −17.50%] |

### Reproduce community-network baseline tables

```bash
PYTHONPATH=.:network_sis .venv/bin/python - <<'PY'
from network_sis.network_communities import (
    load_community_data, summarize_community_results,
    summarize_matched_comparisons, print_community_scenario_table,
    print_community_comparison_table,
    run_community_threshold_experiment, print_community_threshold_table,
)

paths, contacts, _ = load_community_data('network_sis/beta0085_20w50r.npz')
print_community_scenario_table(summarize_community_results(paths, contacts))
print_community_comparison_table(summarize_matched_comparisons(paths, contacts))
print_community_threshold_table(run_community_threshold_experiment(20))
PY

.venv/bin/python network_sis/analyze_weekly_advantage.py \
  network_sis/beta0085_20w50r.npz --deterministic --linearized
```

### Reproduce contact-value and bootstrap tables

```bash
MPLCONFIGDIR=/private/tmp/mpl-community-check PYTHONPATH=.:network_sis .venv/bin/python - <<'PY'
import numpy as np
from network_sis.community_obedience import (
    welfare_break_even_v, bootstrap_pair_obedience,
)

files = (
    ('0040', .04), ('0050', .05), ('0060', .06),
    ('0070', .07), ('0080', .08), ('0085', .085),
    ('0090', .09), ('0100', .10), ('0110', .11), ('0120', .12),
)

with np.load('network_sis/beta0085_20w50r.npz', allow_pickle=False) as data:
    print('| Split | Mean active edge-days over 84 days |')
    print('|---|---:|')
    for split in ('whole', 'random', 'even'):
        value = data[f'contacts_{split}_rotating_1'].mean()
        print(f'| {split} | {value:,.1f} |')

print('| β | Switch (days) | Whole | Random | Even |')
print('|---:|---:|---:|---:|---:|')
for tag, beta in files:
    with np.load(f'network_sis/beta{tag}_20w50r.npz', allow_pickle=False) as data:
        for switch_days in (1, 7):
            infected = [
                data[f'paths_{split}_rotating_{switch_days}'][:, :, 1:].sum(axis=2).mean()
                for split in ('whole', 'random', 'even')
            ]
            print(f'| {beta:.3f} | {switch_days} | ' +
                  ' | '.join(f'{value:,.2f}' for value in infected) + ' |')

with np.load('network_sis/beta0085_20w50r.npz', allow_pickle=False) as data:
    print('| Switch | Comparison | Extra infected person-days | Extra active edge-days | v* |')
    print('|---|---|---:|---:|---:|')
    for switch_days in (1, 7):
        for comparison in ('random', 'even'):
            a = data[f'paths_whole_rotating_{switch_days}'][:, :, 1:].sum(axis=2).mean()
            b = data[f'paths_{comparison}_rotating_{switch_days}'][:, :, 1:].sum(axis=2).mean()
            ca = data[f'contacts_whole_rotating_{switch_days}'].mean()
            cb = data[f'contacts_{comparison}_rotating_{switch_days}'].mean()
            value = welfare_break_even_v(data, 'whole', comparison, switch_days, L_day=10)
            print(f'| {switch_days} | whole–{comparison} | {a-b:,.3f} | {ca-cb:,.1f} | {value:.6f} |')

print('| β | Daily whole–random | Daily whole–even | Weekly whole–random | Weekly whole–even |')
print('|---:|---:|---:|---:|---:|')
for tag, beta in files:
    with np.load(f'network_sis/beta{tag}_20w50r.npz', allow_pickle=False) as data:
        assert np.isclose(float(data['beta']), beta)
        values = [
            welfare_break_even_v(data, 'whole', comparison, switch_days, L_day=10)
            for switch_days in (1, 7)
            for comparison in ('random', 'even')
        ]
        print(f'| {beta:.3f} | ' + ' | '.join(f'{value:.4f}' for value in values) + ' |')

print('| β | Switch | Comparison | v* [95%] | Whole home k>0 [95%] | Comparison home k>0 [95%] | Whole attend [95%] |')
print('|---:|---:|---|---:|---:|---:|---:|')
for tag, beta in files:
    with np.load(f'network_sis/beta{tag}_20w50r.npz', allow_pickle=False) as data:
        for switch_days in (1, 7):
            for comparison in ('random', 'even'):
                result = bootstrap_pair_obedience(
                    data, comparison, switch_days, L_day=10, c=.05,
                    draws=1000, seed=417,
                )
                v_low, v_high = np.quantile(result['v_draws'], [.025, .975])
                whole = result['point_shares']['whole']
                other = result['point_shares'][comparison]
                def interval(split, metric):
                    return np.quantile(result['share_draws'][split][metric], [.025, .975])
                wh_low, wh_high = interval('whole', 'home_k_positive')
                oh_low, oh_high = interval(comparison, 'home_k_positive')
                wa_low, wa_high = interval('whole', 'attend')
                print(
                    f'| {beta:.3f} | {switch_days} | {comparison} | '
                    f'{result["v_point"]:.3f} [{v_low:.3f}, {v_high:.3f}] | '
                    f'{whole["home_k_positive"]:.3f} [{wh_low:.3f}, {wh_high:.3f}] | '
                    f'{other["home_k_positive"]:.3f} [{oh_low:.3f}, {oh_high:.3f}] | '
                    f'{whole["attend"]:.3f} [{wa_low:.3f}, {wa_high:.3f}] |'
                )
                if np.isclose(beta, .085):
                    print(
                        f'β={beta:.3f}, switch={switch_days}, comparison={comparison}: '
                        f'whole home={whole["home"]:.3f}, '
                        f'comparison home={other["home"]:.3f}, '
                        f'comparison attend={other["attend"]:.3f}, '
                        f'whole home k=0={whole["home_k_zero"]:.5f}, '
                        f'comparison home k=0={other["home_k_zero"]:.5f}'
                    )
PY
```
