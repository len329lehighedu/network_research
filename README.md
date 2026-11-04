# SIS attendance schedule simulation

This project compares five attendance patterns on a stochastic SIS contact network. The original learning script, `sis_simulation.py`, is preserved with its comments. Use `sis_experiment.py` as the clean, reproducible entry point.

## Setup and run

The reported run used Python 3.14.0 and the package versions in `requirements.txt`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python sis_experiment.py --sanity
python sis_experiment.py --worlds 2 --runs-per-world 3
python sis_experiment.py
```

The quick run checks the shape of the output. The default run simulates 20 random worlds, 50 epidemic runs per world, and all five schedules. It prints a summary and saves `sis_mean_multiworld.png`.

## Model and comparison

- Each world has 200 people in an undirected Erdős–Rényi network with expected degree 8. Ten people start infected. A fresh network, random 100/100 group split, and set of initial cases are drawn for each world.
- A day is one time step. A susceptible attendee with `k` infected attending neighbors is infected with probability `1 - (1 - beta)**k`, with `beta = 0.04`. Each infected person recovers to susceptible with probability `gamma = 0.20`, including when staying home. Both events use the start-of-day states, so newly infected people transmit starting the next day.
- Full attendance has everyone on site daily. On-Off alternates everyone on site and everyone at home. Rotating alternates the two fixed groups. The latter two use either 1-day or 7-day switches. Over the 84-day horizon, each hybrid schedule has exactly 50% attendance for every starting phase; Full has 100%.
- Each run starts at a phase of the 14-day schedule given by `global_rep % 14`. Within each world, all five schedules use the same network, groups, initial cases, and phase; transmission/recovery seeds differ by schedule and run.
- There are no off-site contacts or outside infection introductions. Once infection reaches zero, it remains zero. Runs that fade out are retained through day 84. The summary reports the fraction extinct by day 84, mean infected on day 84, and mean infected over days 1–84 including zeros.

`python sis_experiment.py --sanity` verifies exact attendance, demonstrates recovery followed by reinfection, and compares low (`beta = 0.001`) with high (`beta = 0.08`) transmission under Full attendance.

With the pinned dependencies and default settings, the 20-world run produced:

| Schedule | Extinct by day 84 | Mean infected, days 1–84 |
| --- | ---: | ---: |
| Full | 0.008 | 49.02 |
| On-Off daily | 0.964 | 2.02 |
| On-Off weekly | 0.969 | 2.03 |
| Rotating daily | 1.000 | 0.87 |
| Rotating weekly | 1.000 | 0.85 |

The `1.000` entries mean that all 1,000 sampled runs in those scenarios faded out by day 84; they do not establish a true extinction probability of exactly one.

## Interpretation limits

This SIS model is a teaching baseline. It has no latent period, lasting immunity, household contacts, persistent contacts while at home, or empirical time-varying contact network. The telecommuting study by [Mauras et al. (2021)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009264) uses a different disease and contact model and reports outbreak metrics. Both studies find less spread under Rotating than On-Off. The paper finds a small weekly advantage; this SIS experiment shows near-equal daily and weekly averages. These model differences have not been isolated one at a time, so the precise cause of that difference remains unknown.
