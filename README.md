# Reproduce the SIS experiments and attendance game

Run these commands from the repository directory. Python 3.14 and the versions in `requirements.txt` were used for the reported results.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p reproduced
```

## Model checks and Figures 1–3

```bash
.venv/bin/python sis_experiment.py --sanity
.venv/bin/python sis_experiment.py --figure single --plot-path reproduced/sis_single_run.png
.venv/bin/python sis_experiment.py --figure fixed-phase --plot-path reproduced/sis_mean_1000_runs.png
.venv/bin/python sis_experiment.py --figure varied-phase --plot-path reproduced/sis_mean_1000_runs_startdate.png
```

## Seven schedules at beta = 0.04

```bash
.venv/bin/python -u sis_experiment.py --beta 0.04 --worlds 20 --runs-per-world 50 --plot-path reproduced/sis_mean_multiworld_controls_beta004.png | tee reproduced/sis_beta004.txt
```

## Beta sweep and 14-day growth thresholds

```bash
.venv/bin/python -u sis_experiment.py --sweep --worlds 20 --runs-per-world 50 --plot-path reproduced/sis_beta_sweep_20w50r.png | tee reproduced/beta_sweep_20w50r.txt
.venv/bin/python sis_experiment.py --thresholds --worlds 20
```

## Three-person attendance game

```bash
.venv/bin/python game.py
```
