# Report 6 — Compliance behavior and rotation beliefs in the multiday benchmark

**Communication log:** Follow-up to the [Report 5 multiday benchmark](report5-deviation-curves-and-multiday-game.md#multiday-attendance-benchmark). This report is prepared for the next reply.

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
  game/data/multiday_v000.csv game/data/multiday_v014.csv game/data/multiday_v028.csv \
  game/data/multiday_v1_*.csv game/data/multiday_v2_*.csv
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

</details>
