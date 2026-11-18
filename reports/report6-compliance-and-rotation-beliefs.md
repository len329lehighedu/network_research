# Report 6 — Compliance behavior and rotation beliefs in the multiday benchmark

**Communication log:** Reply to the Report 5 results email (PDF pp. 25–30), next steps 1, 2 and 4 (step 3 deferred). This report is prepared for the next reply.

## Inputs

| Network | Initial case nodes | Days | Runs per initial case, policy, v, and scenario | β | γ | Infection cost per person-day | Home cost per day | Simulation seed | Bootstrap seed | Bootstrap draws |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Two five-person cliques joined by edge (4, 5) | 4 (bridge), 0 (within group) | 14 | 500 | 0.04 | 0.20 | 10 | 0.05 | 123 | 456 | 2,000 |

| Scenario | Starting willingness | Peer imitation | Rotation forecast of attending neighbors |
|---|---|---|---|
| Report 5 (legacy) | Evenly spaced from 0 to 1 by person index | Yes | Announced schedule |
| V1, schedule | 0 for everyone | No | Announced schedule |
| V1, last same phase | 0 for everyone | No | Actual actions on the most recent day with the same schedule |
| V2, schedule | Independent Uniform[0, 1) draw per person and replicate | Yes | Announced schedule |
| V2, last same phase | Independent Uniform[0, 1) draw per person and replicate | Yes | Actual actions on the most recent day with the same schedule |

Last same phase uses actual actions from two days earlier (the rotation alternates daily) and falls back to the schedule on days 0–1.

## Daily CE and no recommendation (identical in all five scenarios)

| v | Initial case | Daily CE infected person-days | Daily CE group payoff | No recommendation group payoff | Daily CE − No recommendation |
|---|---|---:|---:|---:|---:|
| 0.00 | 4 | 3.92 | -41.13 | -60.31 | +19.19 [15.51, 22.72] |
| 0.00 | 0 | 3.77 | -39.59 | -57.38 | +17.79 [14.46, 21.16] |
| 0.14 | 4 | 4.09 | 11.06 | 3.95 | +7.11 [3.44, 10.77] |
| 0.14 | 0 | 3.79 | 15.48 | 7.25 | +8.23 [4.58, 11.93] |
| 0.28 | 4 | 7.71 | 65.67 | 63.52 | +2.15 [-0.12, 4.76] |
| 0.28 | 0 | 7.03 | 74.97 | 73.27 | +1.71 [-0.84, 4.67] |

## Fixed rotation − No recommendation

| v | Initial case | Report 5 (legacy) | V1, schedule | V1, last same phase | V2, schedule | V2, last same phase |
|---|---|---:|---:|---:|---:|---:|
| 0.00 | 4 | +16.63 [12.61, 20.56] | +19.67 [16.05, 23.26] | +11.34 [7.25, 15.47] | +12.18 [7.99, 16.37] | +10.77 [6.73, 14.87] |
| 0.00 | 0 | +9.55 [6.84, 12.42] | +4.78 [3.02, 6.80] | -0.53 [-4.59, 3.29] | +5.69 [1.77, 9.80] | +5.22 [0.98, 9.21] |
| 0.14 | 4 | -12.37 [-15.46, -9.35] | +4.13 [2.69, 5.79] | +1.44 [-2.48, 5.01] | -14.75 [-18.85, -10.71] | -16.02 [-20.49, -11.46] |
| 0.14 | 0 | -14.65 [-17.32, -11.95] | +1.44 [0.65, 2.45] | -3.00 [-7.18, 0.89] | -14.20 [-18.53, -9.72] | -14.81 [-19.41, -10.22] |
| 0.28 | 4 | -31.47 [-36.02, -26.70] | +2.58 [-0.52, 5.63] | +1.39 [-1.35, 4.12] | -25.89 [-31.08, -20.68] | -26.39 [-31.32, -21.14] |
| 0.28 | 0 | -40.28 [-44.43, -36.10] | +1.26 [-1.71, 4.28] | +0.44 [-2.91, 3.58] | -34.08 [-38.12, -29.96] | -34.28 [-38.78, -30.06] |

## Daily CE − Fixed rotation

| v | Initial case | Report 5 (legacy) | V1, schedule | V1, last same phase | V2, schedule | V2, last same phase |
|---|---|---:|---:|---:|---:|---:|
| 0.00 | 4 | +2.56 [1.33, 4.07] | -0.49 [-0.52, -0.45] | +7.85 [5.62, 10.41] | +7.01 [5.00, 9.30] | +8.42 [6.16, 10.93] |
| 0.00 | 0 | +8.24 [6.16, 10.52] | +13.01 [10.22, 16.11] | +18.32 [14.66, 22.44] | +12.11 [9.26, 15.19] | +12.57 [9.71, 15.81] |
| 0.14 | 4 | +19.48 [16.75, 22.41] | +2.98 [-0.41, 6.51] | +5.67 [1.94, 9.97] | +21.85 [18.68, 25.39] | +23.12 [19.75, 26.58] |
| 0.14 | 0 | +22.88 [20.35, 25.60] | +6.79 [3.15, 10.64] | +11.23 [6.98, 15.98] | +22.43 [19.46, 25.72] | +23.05 [20.18, 26.02] |
| 0.28 | 4 | +33.62 [29.59, 37.69] | -0.43 [-2.79, 2.05] | +0.76 [-1.31, 3.00] | +28.04 [23.08, 33.02] | +28.54 [23.70, 33.52] |
| 0.28 | 0 | +41.99 [38.48, 45.34] | +0.44 [-2.02, 3.28] | +1.26 [-1.07, 3.86] | +35.79 [31.71, 39.78] | +35.99 [31.89, 39.91] |

## Fixed rotation outcomes

| Scenario | v | Initial case | Infected person-days | Attendance person-days | Active edge-days | Group payoff | Follow rate | Final mean willingness |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Report 5 (legacy) | 0.00 | 4 | 4.13 | 91.91 | 156.87 | -43.68 | 65.5% | N/A |
| Report 5 (legacy) | 0.00 | 0 | 4.53 | 90.16 | 149.86 | -47.83 | 67.9% | N/A |
| Report 5 (legacy) | 0.14 | 4 | 5.08 | 93.97 | 159.73 | -8.42 | 61.5% | N/A |
| Report 5 (legacy) | 0.14 | 0 | 4.73 | 91.87 | 150.95 | -7.40 | 65.7% | N/A |
| Report 5 (legacy) | 0.28 | 4 | 7.52 | 106.78 | 194.45 | 32.05 | 67.3% | N/A |
| Report 5 (legacy) | 0.28 | 0 | 6.79 | 103.92 | 183.34 | 32.99 | 70.7% | N/A |
| V1, schedule | 0.00 | 4 | 3.92 | 110.79 | 220.98 | -40.64 | 36.1% | 0.000 |
| V1, schedule | 0.00 | 0 | 5.10 | 108.34 | 214.86 | -52.60 | 34.9% | 0.000 |
| V1, schedule | 0.14 | 4 | 5.50 | 111.77 | 230.47 | 8.08 | 31.0% | 0.000 |
| V1, schedule | 0.14 | 0 | 5.46 | 112.08 | 231.09 | 8.69 | 31.2% | 0.000 |
| V1, schedule | 0.28 | 4 | 8.44 | 129.25 | 269.68 | 66.10 | 42.9% | 0.000 |
| V1, schedule | 0.28 | 0 | 7.76 | 130.51 | 272.54 | 74.53 | 43.7% | 0.000 |
| V1, last same phase | 0.00 | 4 | 4.75 | 110.81 | 224.05 | -48.98 | 48.1% | 0.000 |
| V1, last same phase | 0.00 | 0 | 5.64 | 109.31 | 220.47 | -57.91 | 48.1% | 0.000 |
| V1, last same phase | 0.14 | 4 | 5.76 | 111.49 | 230.20 | 5.39 | 45.6% | 0.000 |
| V1, last same phase | 0.14 | 0 | 5.87 | 111.40 | 229.94 | 4.25 | 45.4% | 0.000 |
| V1, last same phase | 0.28 | 4 | 8.34 | 126.82 | 266.05 | 64.91 | 49.5% | 0.000 |
| V1, last same phase | 0.28 | 0 | 7.65 | 128.33 | 269.27 | 73.71 | 49.7% | 0.000 |
| V2, schedule | 0.00 | 4 | 4.57 | 92.09 | 150.13 | -48.14 | 65.7% | 0.375 |
| V2, schedule | 0.00 | 0 | 4.93 | 91.62 | 148.63 | -51.70 | 66.5% | 0.397 |
| V2, schedule | 0.14 | 4 | 5.17 | 93.89 | 154.18 | -10.79 | 62.9% | 0.368 |
| V2, schedule | 0.14 | 0 | 4.89 | 95.18 | 157.77 | -6.95 | 63.1% | 0.363 |
| V2, schedule | 0.28 | 4 | 6.97 | 108.71 | 194.49 | 37.63 | 66.0% | 0.298 |
| V2, schedule | 0.28 | 0 | 6.87 | 108.96 | 195.39 | 39.19 | 66.3% | 0.297 |
| V2, last same phase | 0.00 | 4 | 4.70 | 89.08 | 146.79 | -49.55 | 69.3% | 0.394 |
| V2, last same phase | 0.00 | 0 | 4.96 | 88.80 | 146.36 | -52.16 | 69.9% | 0.405 |
| V2, last same phase | 0.14 | 4 | 5.21 | 91.44 | 151.59 | -12.06 | 68.6% | 0.392 |
| V2, last same phase | 0.14 | 0 | 4.88 | 93.02 | 155.53 | -7.56 | 68.1% | 0.377 |
| V2, last same phase | 0.28 | 4 | 6.94 | 107.29 | 193.20 | 37.13 | 68.4% | 0.303 |
| V2, last same phase | 0.28 | 0 | 6.82 | 107.79 | 194.28 | 38.99 | 68.3% | 0.301 |

## Fixed rotation − No recommendation, decomposition

| Scenario | v | Initial case | Contact benefit | Infection cost savings | Home cost savings | Group payoff difference |
|---|---|---|---:|---:|---:|---:|
| Report 5 (legacy) | 0.00 | 4 | +0.00 | +17.50 | -0.87 | +16.63 |
| Report 5 (legacy) | 0.00 | 0 | +0.00 | +10.54 | -0.99 | +9.55 |
| Report 5 (legacy) | 0.14 | 4 | -19.55 | +7.94 | -0.77 | -12.37 |
| Report 5 (legacy) | 0.14 | 0 | -22.37 | +8.62 | -0.90 | -14.65 |
| Report 5 (legacy) | 0.28 | 4 | -40.67 | +10.22 | -1.02 | -31.47 |
| Report 5 (legacy) | 0.28 | 0 | -48.89 | +9.86 | -1.25 | -40.28 |
| V1, schedule | 0.00 | 4 | +0.00 | +19.60 | +0.07 | +19.67 |
| V1, schedule | 0.00 | 0 | +0.00 | +4.86 | -0.08 | +4.78 |
| V1, schedule | 0.14 | 4 | +0.26 | +3.74 | +0.12 | +4.13 |
| V1, schedule | 0.14 | 0 | +0.07 | +1.26 | +0.11 | +1.44 |
| V1, schedule | 0.28 | 4 | +1.46 | +1.02 | +0.10 | +2.58 |
| V1, schedule | 0.28 | 0 | +1.06 | +0.12 | +0.08 | +1.26 |
| V1, last same phase | 0.00 | 4 | +0.00 | +11.26 | +0.08 | +11.34 |
| V1, last same phase | 0.00 | 0 | +0.00 | -0.50 | -0.03 | -0.53 |
| V1, last same phase | 0.14 | 4 | +0.19 | +1.14 | +0.11 | +1.44 |
| V1, last same phase | 0.14 | 0 | -0.25 | -2.82 | +0.07 | -3.00 |
| V1, last same phase | 0.28 | 4 | -0.57 | +1.98 | -0.02 | +1.39 |
| V1, last same phase | 0.28 | 0 | -0.77 | +1.24 | -0.03 | +0.44 |
| V2, schedule | 0.00 | 4 | +0.00 | +13.04 | -0.86 | +12.18 |
| V2, schedule | 0.00 | 0 | +0.00 | +6.60 | -0.91 | +5.69 |
| V2, schedule | 0.14 | 4 | -21.10 | +7.12 | -0.77 | -14.75 |
| V2, schedule | 0.14 | 0 | -20.46 | +7.00 | -0.74 | -14.20 |
| V2, schedule | 0.28 | 4 | -40.65 | +15.68 | -0.92 | -25.89 |
| V2, schedule | 0.28 | 0 | -42.15 | +9.06 | -1.00 | -34.08 |
| V2, last same phase | 0.00 | 4 | +0.00 | +11.78 | -1.01 | +10.77 |
| V2, last same phase | 0.00 | 0 | +0.00 | +6.28 | -1.06 | +5.22 |
| V2, last same phase | 0.14 | 4 | -21.82 | +6.70 | -0.89 | -16.02 |
| V2, last same phase | 0.14 | 0 | -21.09 | +7.12 | -0.85 | -14.81 |
| V2, last same phase | 0.28 | 4 | -41.37 | +15.98 | -0.99 | -26.39 |
| V2, last same phase | 0.28 | 0 | -42.77 | +9.54 | -1.05 | -34.28 |

Brackets: 95% paired bootstrap intervals. Positive differences favor the first policy. Final mean willingness: average across players at the end of day 14 (not recorded in the Report 5 CSVs).

## Step 1b checks

### Imitation versus a shuffled-payoff baseline

V2 shuffled is identical to V2, except that before each imitation update the day's payoffs are randomly permuted across players. The permutation keeps the payoff values and ties but removes the link between a player's behavior and the payoff they are compared on. Both start from the same willingness draw, so replicates are paired.

Fixed-rotation mean willingness on days 0, 7, and 14 (schedule forecast):

| Behavior | v | Initial case | Runs | Day 0 | Day 7 | Day 14 | Day 14 − day 0 | v2 − v2_shuffled (day 14 − day 0) |
|---|---|---|---|---|---|---|---|---|
| v2 | 0.00 | 4 | 500 | 0.499 | 0.449 | 0.375 | -0.124 [-0.139, -0.108] | -0.128 [-0.149, -0.106] |
| v2_shuffled | 0.00 | 4 | 500 | 0.499 | 0.502 | 0.503 | +0.004 [-0.011, +0.019] |  |
| v2 | 0.00 | 0 | 500 | 0.499 | 0.465 | 0.397 | -0.102 [-0.118, -0.085] | -0.101 [-0.123, -0.082] |
| v2_shuffled | 0.00 | 0 | 500 | 0.499 | 0.497 | 0.499 | -0.000 [-0.017, +0.015] |  |
| v2 | 0.14 | 4 | 500 | 0.499 | 0.437 | 0.368 | -0.131 [-0.147, -0.114] | -0.138 [-0.162, -0.114] |
| v2_shuffled | 0.14 | 4 | 500 | 0.499 | 0.503 | 0.506 | +0.007 [-0.010, +0.023] |  |
| v2 | 0.14 | 0 | 500 | 0.499 | 0.428 | 0.363 | -0.136 [-0.153, -0.117] | -0.125 [-0.149, -0.102] |
| v2_shuffled | 0.14 | 0 | 500 | 0.499 | 0.484 | 0.488 | -0.011 [-0.028, +0.006] |  |
| v2 | 0.28 | 4 | 500 | 0.499 | 0.347 | 0.298 | -0.201 [-0.215, -0.187] | -0.217 [-0.240, -0.196] |
| v2_shuffled | 0.28 | 4 | 500 | 0.499 | 0.509 | 0.515 | +0.016 [-0.001, +0.032] |  |
| v2 | 0.28 | 0 | 500 | 0.499 | 0.353 | 0.297 | -0.202 [-0.217, -0.188] | -0.215 [-0.237, -0.194] |
| v2_shuffled | 0.28 | 0 | 500 | 0.499 | 0.504 | 0.512 | +0.013 [-0.004, +0.029] |  |

Brackets: 95% bootstrap intervals over replicates (2,000 draws, seed 456); the last column pairs V2 and V2 shuffled by replicate. The V2 row at v = 0.28 uses the first 500 replicates of the 2,000-run file.

### More replicates for intervals that include zero

Same settings with 2,000 runs per initial case. The first 500 replicates of each 2,000-run file reproduce the 500-run CSV exactly.

| Scenario | v | Initial case | Contrast | 500 runs | 2000 runs |
|---|---|---|---|---:|---:|
| V1, schedule | 0.14 | 4 | Daily CE − No recommendation | +7.11 [3.44, 10.77] | +9.58 [7.32, 11.79] |
| V1, schedule | 0.14 | 4 | Daily CE − Fixed rotation | +2.98 [-0.41, 6.51] | +4.39 [2.42, 6.45] |
| V1, schedule | 0.14 | 4 | Fixed rotation − No recommendation | +4.13 [2.69, 5.79] | +5.18 [4.25, 6.17] |
| V1, schedule | 0.14 | 0 | Daily CE − No recommendation | +8.23 [4.58, 11.93] | +8.85 [6.88, 10.89] |
| V1, schedule | 0.14 | 0 | Daily CE − Fixed rotation | +6.79 [3.15, 10.64] | +7.66 [5.71, 9.74] |
| V1, schedule | 0.14 | 0 | Fixed rotation − No recommendation | +1.44 [0.65, 2.45] | +1.19 [0.83, 1.57] |
| V1, schedule | 0.28 | 4 | Daily CE − No recommendation | +2.15 [-0.12, 4.76] | +1.02 [-0.20, 2.29] |
| V1, schedule | 0.28 | 4 | Daily CE − Fixed rotation | -0.43 [-2.79, 2.05] | +0.49 [-0.82, 1.96] |
| V1, schedule | 0.28 | 4 | Fixed rotation − No recommendation | +2.58 [-0.52, 5.63] | +0.53 [-1.02, 2.07] |
| V1, schedule | 0.28 | 0 | Daily CE − No recommendation | +1.71 [-0.84, 4.67] | -0.48 [-1.55, 0.61] |
| V1, schedule | 0.28 | 0 | Daily CE − Fixed rotation | +0.44 [-2.02, 3.28] | +1.02 [-0.32, 2.45] |
| V1, schedule | 0.28 | 0 | Fixed rotation − No recommendation | +1.26 [-1.71, 4.28] | -1.50 [-2.99, -0.01] |
| V2, schedule | 0.28 | 4 | Daily CE − No recommendation | +2.15 [-0.12, 4.76] | +1.02 [-0.20, 2.29] |
| V2, schedule | 0.28 | 4 | Daily CE − Fixed rotation | +28.04 [23.08, 33.02] | +27.78 [25.23, 30.07] |
| V2, schedule | 0.28 | 4 | Fixed rotation − No recommendation | -25.89 [-31.08, -20.68] | -26.76 [-29.22, -24.33] |
| V2, schedule | 0.28 | 0 | Daily CE − No recommendation | +1.71 [-0.84, 4.67] | -0.48 [-1.55, 0.61] |
| V2, schedule | 0.28 | 0 | Daily CE − Fixed rotation | +35.79 [31.71, 39.78] | +31.67 [29.48, 33.59] |
| V2, schedule | 0.28 | 0 | Fixed rotation − No recommendation | -34.08 [-38.12, -29.96] | -32.16 [-34.28, -29.94] |

Brackets: 95% paired bootstrap intervals (2,000 draws, seed 456).

<!-- TODO(LeMinh): add two sentences here.
1. Why daily CE and no recommendation are identical in every scenario.
2. Why, under V1 at v = 0 with initial case 4, fixed rotation matches daily CE in infected person-days in 500/500 replicates. -->

<details>
<summary>Reproduce the tables</summary>

Saved data, one CSV per scenario and contact value:

| Scenario | v = 0.00 | v = 0.14 | v = 0.28 |
|---|---|---|---|
| Report 5 (legacy) | [CSV](../game/data/multiday_v000.csv) | [CSV](../game/data/multiday_v014.csv) | [CSV](../game/data/multiday_v028.csv) |
| V1, schedule | [CSV](../game/data/multiday_v1_schedule_v000.csv) | [CSV](../game/data/multiday_v1_schedule_v014.csv) | [CSV](../game/data/multiday_v1_schedule_v028.csv) |
| V1, last same phase | [CSV](../game/data/multiday_v1_last_same_phase_v000.csv) | [CSV](../game/data/multiday_v1_last_same_phase_v014.csv) | [CSV](../game/data/multiday_v1_last_same_phase_v028.csv) |
| V2, schedule | [CSV](../game/data/multiday_v2_schedule_v000.csv) | [CSV](../game/data/multiday_v2_schedule_v014.csv) | [CSV](../game/data/multiday_v2_schedule_v028.csv) |
| V2, last same phase | [CSV](../game/data/multiday_v2_last_same_phase_v000.csv) | [CSV](../game/data/multiday_v2_last_same_phase_v014.csv) | [CSV](../game/data/multiday_v2_last_same_phase_v028.csv) |

Print the mean outcomes, payoff contrasts, and decompositions for every scenario and policy from the saved CSVs:

```bash
PYTHONPATH=. .venv/bin/python game/summarize_multiday_benchmark.py \
  game/data/multiday_v0{00,14,28}.csv \
  game/data/multiday_v{1,2}_{schedule,last_same_phase}_v{000,014,028}.csv
```

Regenerate the 12 new CSVs in a separate directory. Each file takes about three minutes, and daily CE takes most of that time.

```bash
(
  set -e
  benchmark_data=$(mktemp -d)
  for behavior in v1 v2; do
    for belief in schedule last_same_phase; do
      for tag in 000 014 028; do
        PYTHONPATH=. .venv/bin/python game/run_multiday_benchmark.py \
          --runs 500 --days 14 --v "${tag:0:1}.${tag:1}" \
          --behavior "$behavior" --rotation-belief "$belief" \
          --output "$benchmark_data/multiday_${behavior}_${belief}_v${tag}.csv"
      done
    done
  done
  PYTHONPATH=. .venv/bin/python game/summarize_multiday_benchmark.py "$benchmark_data"/multiday_*.csv
)
```

Without `--behavior` and `--rotation-belief`, the runner uses the legacy scenario and reproduces the Report 5 CSVs.

Step 1b data: V2 shuffled [v = 0.00](../game/data/multiday_v2_shuffled_schedule_v000.csv) · [0.14](../game/data/multiday_v2_shuffled_schedule_v014.csv) · [0.28](../game/data/multiday_v2_shuffled_schedule_v028.csv); V2 with the day-7 column [v = 0.00](../game/data/multiday_v2_schedule_v000_wpath.csv) · [0.14](../game/data/multiday_v2_schedule_v014_wpath.csv); 2,000 runs [V1, v = 0.14](../game/data/multiday_v1_schedule_v014_r2000.csv) · [V1, v = 0.28](../game/data/multiday_v1_schedule_v028_r2000.csv) · [V2, v = 0.28](../game/data/multiday_v2_schedule_v028_r2000.csv). The `_wpath` files match the Report 6 V2 CSVs in every shared column.

Print the willingness table and the 2,000-run contrasts:

```bash
PYTHONPATH=. .venv/bin/python game/summarize_multiday_benchmark.py --willingness-path \
  game/data/multiday_v2_schedule_v0{00,14}_wpath.csv game/data/multiday_v2_schedule_v028_r2000.csv \
  game/data/multiday_v2_shuffled_schedule_v{000,014,028}.csv
```

```bash
PYTHONPATH=. .venv/bin/python game/summarize_multiday_benchmark.py \
  game/data/multiday_v1_schedule_v0{14,28}_r2000.csv game/data/multiday_v2_schedule_v028_r2000.csv
```

Regenerate the step 1b CSVs in a separate directory. The 500-run files take about three minutes each and the 2,000-run files about twelve.

```bash
(
  set -e
  d=$(mktemp -d)
  run() { PYTHONPATH=. .venv/bin/python game/run_multiday_benchmark.py --days 14 "$@"; }
  for tag in 000 014 028; do
    run --runs 500 --v "${tag:0:1}.${tag:1}" --behavior v2_shuffled --output "$d/multiday_v2_shuffled_schedule_v${tag}.csv"
  done
  for tag in 000 014; do
    run --runs 500 --v "${tag:0:1}.${tag:1}" --behavior v2 --output "$d/multiday_v2_schedule_v${tag}_wpath.csv"
  done
  run --runs 2000 --v 0.14 --behavior v1 --output "$d/multiday_v1_schedule_v014_r2000.csv"
  run --runs 2000 --v 0.28 --behavior v1 --output "$d/multiday_v1_schedule_v028_r2000.csv"
  run --runs 2000 --v 0.28 --behavior v2 --output "$d/multiday_v2_schedule_v028_r2000.csv"
  echo "$d"
)
```

</details>

## Step 2: does looking ahead pay?

Next step 2 asks whether a recommender that plans over the 14 days beats the daily CE. All recommenders below see the same information as the daily CE: the day index t and the start-of-day prevalence k/10. Each one sends a lottery over the 1,024 attendance profiles. People respond to the public lottery and their private signal with the same V1 or V2 rule used above, so they are free to ignore a recommendation.

### Recommenders

| Recommender | Value of tomorrow V_{t+1}(k′) | How it is obtained |
|---|---|---|
| Daily CE | None; each expected new infection is priced at L_day/γ = 50 | The benchmark LP, unchanged |
| Lookahead, independence belief | Backward induction over (t, k) | Planning; tomorrow's k′ predicted by assuming each person is infected independently with probability k/10 |
| Lookahead, independence belief + MC | Monte Carlo average of the realized 14-day return from each visited (t, k) | Learning; 3 rounds of policy iteration × 5,000 training episodes per initial case, training seed 2026 |
| Lookahead, exact-count belief | Backward induction over (t, k) | Planning; tomorrow's k′ predicted by assuming exactly k people are infected and every set of k people is equally likely |
| Lookahead, exact-count belief + MC | Monte Carlo, as above | Learning, started from the exact-count lookahead |

The lookahead LP keeps every obedience constraint of the daily CE and changes only the objective. The new objective is today's expected realized payoff (L_day per infected person at the end of the day, plus contact benefit and home cost) plus E[V_{t+1}(k′)]. The daily CE is therefore a lookahead CE with a hand-made value of tomorrow, L_day/γ per new infection, which ignores onward transmission and the horizon.

In the Monte Carlo rounds, (t, k) cells visited fewer than 200 times keep the planning value. The training episodes never use the evaluation seed 123.

The independence belief overstates recovery. With one infected person and everyone at home, it predicts zero infected tomorrow with probability 0.92^10 ≈ 0.43, while the true probability is γ = 0.20. The exact-count belief removes this error. It was compared against direct simulation on the 10-person network and differs from it by at most 0.007 in any transition probability.

### Group payoff, lookahead − daily CE

| v | Initial case | Daily CE group payoff | Independence belief | Independence belief + MC | Exact-count belief | Exact-count belief + MC |
|---|---|---:|---:|---:|---:|---:|
| 0.00 | 4 | -41.13 | +0.00 [0.00, 0.00] | +0.00 [0.00, 0.00] | +0.00 [0.00, 0.00] | +0.00 [0.00, 0.00] |
| 0.00 | 0 | -39.59 | +0.00 [0.00, 0.00] | +0.00 [0.00, 0.00] | +0.00 [0.00, 0.00] | +0.00 [0.00, 0.00] |
| 0.14 | 4 | 11.06 | -0.79 [-2.77, 1.13] | -0.65 [-2.76, 1.22] | -0.63 [-2.50, 1.34] | +0.31 [-1.54, 2.13] |
| 0.14 | 0 | 15.48 | +0.02 [-0.26, 0.23] | +0.03 [-0.24, 0.23] | +0.26 [0.18, 0.34] | +0.20 [0.13, 0.28] |
| 0.28 | 4 | 65.67 | -0.39 [-1.54, 0.47] | -0.39 [-1.47, 0.47] | -0.54 [-1.66, 0.38] | -0.33 [-1.31, 0.49] |
| 0.28 | 0 | 74.97 | -0.63 [-1.73, 0.15] | -0.25 [-0.79, 0.21] | -0.61 [-1.68, 0.12] | -0.61 [-1.68, 0.13] |

Brackets: 95% paired bootstrap intervals over the 500 replicates (2,000 draws, seed 456). The daily CE column reproduces the daily CE rows of the table above exactly.

V1 and V2 give identical numbers, because every recommender keeps the follow rate at 1.000. Under V2 nobody's willingness matters when every recommendation pays to follow. The table therefore covers both behaviors.

Two further paired contrasts have intervals that exclude zero:
- Exact-count belief + MC − exact-count belief = +0.94 [0.26, 1.77] at v = 0.14, initial case 4.
- Exact-count belief + MC − exact-count belief = −0.06 [−0.08, −0.05] at v = 0.14, initial case 0.

### Values of tomorrow

V_0(k): expected 14-day group payoff from day 0 with k people infected.

| v | Value | k = 0 | k = 1 | k = 2 | k = 3 |
|---|---|---:|---:|---:|---:|
| 0.14 | Independence belief | 82.3 | 25.2 | -22.0 | -67.1 |
| 0.14 | Monte Carlo under independence-belief policy, case 4 / case 0 | 82.3 | 12.6 / 14.3 | — | — |
| 0.14 | Exact-count belief | 82.3 | 13.8 | -36.8 | -83.0 |
| 0.14 | Monte Carlo under exact-count policy, case 4 / case 0 | 82.3 | 12.8 / 14.2 | — | — |
| 0.28 | Independence belief | 164.6 | 94.0 | 37.7 | -13.0 |
| 0.28 | Monte Carlo under independence-belief policy, case 4 / case 0 | 164.6 | 67.3 / 73.4 | — | — |
| 0.28 | Exact-count belief | 164.6 | 73.6 | 14.1 | -37.6 |
| 0.28 | Monte Carlo under exact-count policy, case 4 / case 0 | 164.6 | 66.9 / 73.0 | — | — |

—: fewer than 200 visits, so the planning value is kept. The exact-count planning values agree with the learned values, while the independence belief overstates V_0(1) by 11 to 21.

The marginal cost of one more infected person is V_t(1) − V_t(2). It falls toward zero at the horizon, because a late infection has fewer days left to cost anything. Under the exact-count belief:

| v | t = 0 | t = 3 | t = 6 | t = 9 | t = 11 | t = 13 |
|---|---:|---:|---:|---:|---:|---:|
| 0.14 | 50.6 | 47.7 | 42.2 | 32.5 | 22.5 | 8.6 |
| 0.28 | 59.6 | 56.3 | 51.4 | 43.6 | 34.6 | 17.2 |

### Where the recommendations differ from the daily CE

The table lists the reached (t, k) cells where the expected attendance or the expected number of active edges differs from the daily CE. Visits are counts out of 5,000 episodes in the last Monte Carlo round, initial case 4.

| v | t | k | Visits | Daily CE: attendance, active edges | Exact-count belief | Exact-count belief + MC |
|---|---:|---:|---:|---|---|---|
| 0.14 | 9 | 1 | 679 | 2.51, 0.51 | 4.00, 2.00 | 2.51, 0.51 |
| 0.14 | 10–13 | 1 | 287–563 | 2.51, 0.51 | 4.37, 2.74 | 4.37, 2.74 |
| 0.14 | 12–13 | 2 | 7–10 | 2.00, 0.00 | 2.32, 0.32 | 2.32, 0.32 |
| 0.28 | 10–13 | 2 | 317–489 | 2.53, 0.53 | 4.39, 2.78 | 4.39, 2.78 |
| 0.28 | 11–13 | 3 | 28–33 | 2.00, 0.00 | 2.43, 0.43 | 2.43, 0.43 |
| 0.28 | 12–13 | 4 | 1 | 2.00, 0.00 | 2.29, 0.29 | 2.29, 0.29 |

At v = 0 the lookahead tables differ from the daily CE in 126 of the 154 cells. Every difference is a choice of which two people attend in a profile with no active contact, so the outcomes are identical. Other differing cells (mostly k ≥ 4) are never reached in training. The independence-belief tables differ from the daily CE on the same late days.

### Summary

- Looking ahead changes the recommendation only in the last four to five days. There, the true marginal cost of an infection drops below the daily CE's price of 50, so the lookahead allows more contact.
- On days 0–8 the daily CE price is close to the true marginal cost, or the LP picks the same vertex despite the gap (v = 0.28), and every recommender sends the same lottery.
- Few runs still have infected people on those late days. The largest gain over the daily CE is +0.26 (1.7% of the group payoff), and it does not hold for the other initial case.
- Monte Carlo learning mainly worked as a diagnostic. It exposed the independence belief's error, and once the belief was corrected, learning changed the expected attendance in only one reached cell: (t = 9, k = 1) at v = 0.14, which it moved back to the daily CE lottery.
- On this network, with these parameters, looking ahead does not pay. Larger β, smaller γ, or larger and more clustered networks, where onward transmission is a larger part of the cost, have not been tested.

<details>
<summary>Reproduce the step 2 tables</summary>

Saved data. Each `.csv` has one row per initial case, replicate and recommender. Each `.npz` holds the planning and Monte Carlo value tables and the visit counts.

| Behavior | v = 0.00 | v = 0.14 | v = 0.28 |
|---|---|---|---|
| V1 | [CSV](../reinforcement_learning/data/lookahead_exact_v1_v000.csv) | [CSV](../reinforcement_learning/data/lookahead_exact_v1_v014.csv) | [CSV](../reinforcement_learning/data/lookahead_exact_v1_v028.csv) |
| V2 | [CSV](../reinforcement_learning/data/lookahead_exact_v2_v000.csv) | [CSV](../reinforcement_learning/data/lookahead_exact_v2_v014.csv) | [CSV](../reinforcement_learning/data/lookahead_exact_v2_v028.csv) |

The earlier `lookahead_{v1,v2}_v*.csv` files contain only the first three recommenders. Their rows match the corresponding rows of these files exactly. The full console output of the runs is in [lookahead_exact_log.txt](../reinforcement_learning/data/lookahead_exact_log.txt), which prints every pairwise contrast.

Regenerate the six files in a separate directory. Each file takes about ten minutes.

```bash
(
  set -e
  d=$(mktemp -d)
  for behavior in v1 v2; do
    for tag in 000 014 028; do
      PYTHONPATH=.:game .venv/bin/python reinforcement_learning/run_lookahead_benchmark.py \
        --exact-belief --runs 500 --days 14 --v "${tag:0:1}.${tag:1}" --behavior "$behavior" \
        --output "$d/lookahead_exact_${behavior}_v${tag}.csv"
    done
  done
  echo "$d"
)
```

Print the payoff table from the saved CSVs:

```bash
PYTHONPATH=.:game .venv/bin/python - reinforcement_learning/data/lookahead_exact_v1_v0{00,14,28}.csv <<'PY'
import csv, sys
from itertools import combinations
import numpy as np
from multiday_game import paired_payoff_difference_ci

policies = ("daily_ce", "lookahead_belief", "lookahead_mc", "lookahead_exact", "lookahead_exact_mc")
for path in sys.argv[1:]:
    rows = [{"initial_case": r["initial_case"], "policy": r["policy"], "replicate": int(r["replicate"]),
             "group_payoff": float(r["group_payoff"])} for r in csv.DictReader(open(path))]
    for case in ("4", "0"):
        case_rows = [r for r in rows if r["initial_case"] == case]
        print(f"\n{path} initial case {case}")
        rng = np.random.default_rng(456)
        for a, b in combinations(policies, 2):
            mean, lower, upper = paired_payoff_difference_ci(case_rows, b, a, rng, draws=2000)
            print(f"  {b} - {a}: {mean:+.2f} [{lower:.2f}, {upper:.2f}]")
PY
```

Print the value tables and the differing cells. This rebuilds the daily CE and exact-count tables (a few seconds) and re-solves the final Monte Carlo table from the saved values.

```bash
PYTHONPATH=.:game .venv/bin/python - <<'PY'
import numpy as np
from multiday_game import make_two_community_graph
from network_game import active_contacts, all_action_profiles
from reinforcement_learning.lookahead_ce import (belief_backward_induction, daily_ce_lottery_table,
                                                 exact_count_transition, solve_lookahead_ce)

graph, _ = make_two_community_graph()
beta, gamma, L_day, c, days = 0.04, 0.2, 10.0, 0.05, 14
profiles = all_action_profiles(graph)
attend = np.array([p.count("A") for p in profiles])
edges = np.array([active_contacts(graph, p) for p in profiles])
transition = exact_count_transition(graph, beta, gamma)
for v, tag in ((0.0, "000"), (0.14, "014"), (0.28, "028")):
    saved = np.load(f"reinforcement_learning/data/lookahead_exact_v1_v{tag}.npz")
    daily = daily_ce_lottery_table(graph, days, beta, L_day, gamma, c, v)
    _, exact = belief_backward_induction(graph, days, beta, L_day, gamma, c, v, transition=transition)
    print(f"\nv={v}  V_0(k), k=0..3: independence {saved['belief_values'][0, :4].round(1)}  "
          f"exact {saved['exact_values'][0, :4].round(1)}")
    for case in (4, 0):
        print(f"  case {case}: MC {saved[f'mc_values_case{case}'][0, :4].round(1)}  "
              f"exact MC {saved[f'exact_mc_values_case{case}'][0, :4].round(1)}")
    V = saved["exact_values"]
    print("  exact V_t(1) - V_t(2), t=0..13:", (V[:days, 1] - V[:days, 2]).round(1))
    mc_values = saved["exact_mc_values_case4"]
    visits = saved["exact_mc_counts_case4"][-1]
    print("  case 4 differing cells (t, k, visits: daily | exact | exact MC; attendance, active edges)")
    for t in range(days):
        for k in range(graph.number_of_nodes() + 1):
            mc_lottery, _ = solve_lookahead_ce(graph, k / 10, beta, L_day, gamma, c, v, mc_values[t + 1],
                                               next_counts=transition[k])
            stats = [(np.asarray(q) @ attend, np.asarray(q) @ edges) for q in (daily[t][k], exact[t][k], mc_lottery)]
            if visits[t, k] > 0 and any(abs(s[0] - stats[0][0]) > 1e-3 or abs(s[1] - stats[0][1]) > 1e-3
                                        for s in stats):
                print(f"    {t:2d} {k} {int(visits[t, k]):5d}: " + " | ".join(f"{a:.2f} {e:.2f}" for a, e in stats))
PY
```

</details>

## Step 4 (supplement): CE gain and the largest independent set

Next step 3, scaling the lookahead recommender to a 200-person network, was conditional on step 2 finding a gain from looking ahead. Step 2 found none, so step 3 is deferred.

Next step 4 asks for one regression of the CE gain on the largest independent set α, controlling for the number of edges and the network size. The data are the 139 connected networks with four to six people from Report 5, at π = 0.10, β = 0.04, γ = 0.20, infection cost per day 10, and contact value 0.14. **CE gain** is the best pure Nash group cost minus the best CE group cost; gains of at most $10^{-9}$ count as 0, as in Report 5. Network size enters as dummies for five and six people, with four people as the baseline. At π = 0.50 no network has a CE gain, so that slice is not used.

Model: CE gain = b₀ + b₁ α + b₂ edges + b₃ [n = 5] + b₄ [n = 6] + error, by ordinary least squares.

| c | Term | Coefficient | HC1 SE | 95% CI | Networks | CE improves |
|---|---|---:|---:|---|---:|---:|
| 0.05 | Intercept | +0.050373 | 0.004973 | [+0.040626, +0.060120] | 139 | 65 |
| 0.05 | α | -0.016117 | 0.001388 | [-0.018839, -0.013396] | 139 | 65 |
| 0.05 | Edges | -0.002847 | 0.000478 | [-0.003783, -0.001910] | 139 | 65 |
| 0.05 | n = 5 | +0.015319 | 0.003233 | [+0.008982, +0.021656] | 139 | 65 |
| 0.05 | n = 6 | +0.029406 | 0.003937 | [+0.021689, +0.037123] | 139 | 65 |
| 0.12 | Intercept | -0.052484 | 0.019811 | [-0.091315, -0.013654] | 139 | 32 |
| 0.12 | α | +0.004043 | 0.006299 | [-0.008302, +0.016389] | 139 | 32 |
| 0.12 | Edges | +0.010655 | 0.002023 | [+0.006690, +0.014621] | 139 | 32 |
| 0.12 | n = 5 | -0.003638 | 0.009045 | [-0.021366, +0.014090] | 139 | 32 |
| 0.12 | n = 6 | -0.024815 | 0.012723 | [-0.049753, +0.000123] | 139 | 32 |

HC1: heteroskedasticity-robust standard errors with the n/(n − p) small-sample correction. 95% CI: coefficient ± 1.96 SE. Coefficients and SEs match statsmodels `OLS(...).fit(cov_type="HC1")`.

- At c = 0.05, one more person in the largest independent set lowers the CE gain by 0.016, holding edges and size fixed. The mean CE gain over the 139 networks is 0.0099, so the effect is large relative to the outcome. This agrees with the stratified Report 5 tables, where CE helps more often when α ≤ 2.
- At c = 0.12, the α coefficient is not distinguishable from 0. Report 5 shows that at this home cost the 104 networks with a single pure Nash all have zero gain, so equilibrium multiplicity, not α, separates the networks.
- The 139 networks are every connected graph with four to six nodes, not a sample. The intervals describe the uncertainty of the linear fit, not sampling error. 74 of the 139 outcomes are exactly 0 at c = 0.05, and 107 at c = 0.12.

<details>
<summary>Reproduce the step 4 table</summary>

Uses the saved atlas results [game/atlas_contact_value_4_6.csv](../game/atlas_contact_value_4_6.csv). Running the module prints the sanity checks, the statsmodels comparison, and the table.

```bash
PYTHONPATH=. .venv/bin/python network_sis/atlas_network_features.py
```

</details>
