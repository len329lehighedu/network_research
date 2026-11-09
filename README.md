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
