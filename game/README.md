# Attendance game results

Run the commands below from the [repository root](../README.md) after setup.

## Original one-day payoff model

### Three-person costs at π = 0.10, β = 0.04, L = 10, c = 0.05

| Arrangement | Extra group cost per day | Share of Nash-to-minimum gap closed |
|---|---:|---:|
| Independent symmetric Nash (each attends with probability 0.6954) | 0.150 | — |
| Fair lottery over the three two-attendee profiles | 0.122 | 56.0% |
| Best correlated equilibrium | 0.112356 | 75.3% |
| Lowest-cost profile, ignoring incentives (one attends) | 0.100 | 100% |

### Selected parameter combinations at β = 0.04, L = 10

| $\pi$ | $c$ | Independent Nash | Fair two-attendee lottery | Rotation NE? | Best CE | Unconstrained minimum |
|---:|---:|---:|---:|:---:|---:|---:|
| 0.10 | 0.02 | 0.060 | 0.092 | No | 0.040 | 0.040 |
| 0.10 | 0.05 | 0.150 | 0.122 | Yes | 0.112 | 0.100 |
| 0.10 | 0.12 | 0.216 | 0.192 | No | 0.216 | 0.192 |
| 0.50 | 0.05 | 0.150 | 0.250 | No | 0.100 | 0.100 |
| 0.50 | 0.12 | 0.360 | 0.320 | Yes | 0.267 | 0.240 |

### Small-network costs at π = 0.10, β = 0.04, L = 10, c = 0.05

| Graph | People | Edges | Best pure Nash | Best CE | Social minimum | CE gap closed | Expected active edges under CE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Path | 4 | 3 | 0.122000 | 0.112356 | 0.100000 | 43.8% | 0.561617 |
| Star | 5 | 4 | 0.050000 | 0.050000 | 0.050000 | — | 0 |
| Triangle with a leaf | 4 | 4 | 0.122000 | 0.122000 | 0.100000 | 0.0% | 1.000000 |
| Path | 6 | 5 | 0.172000 | 0.158590 | 0.150000 | 61.0% | 0.390451 |

### Reproduce the original game tables

```bash
.venv/bin/python game/game.py
.venv/bin/python game/game.py --cost-grid-output game/reproduced_cost_grid.txt
.venv/bin/python game/network_game.py --summary
```

[Full original parameter grid](cost_grid.txt) · [Original model and results](game_results.md)

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
