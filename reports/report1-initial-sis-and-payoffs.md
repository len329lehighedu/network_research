# Report 1 — Initial SIS experiments and known-status payoffs

**Communication log:** First results email, PDF pp. 2–5.

## Experiment setup

| Population | Network | Expected degree | Initial infections | Days | β | γ | Attendance per 50% schedule | Full attendance |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 200 | Erdős–Rényi | 8 | 10 | 84 | 0.04 | 0.20 | 8,400 person-days | 16,800 person-days |

Infection and recovery use the start-of-day state. The model has no outside infections, so zero infections is absorbing. Figure 4 averages 50 runs per schedule over each of 20 worlds.

## Figure 4 — Complete five-schedule table as sent

| Schedule | Mean infected, days 1–84 | Extinct by day 84 |
|---|---:|---:|
| Full attendance | 49.02 | 0.8% |
| On–Off daily | 2.02 | 96.4% |
| On–Off weekly | 2.03 | 96.9% |
| Rotating daily | 0.87 | 100.0% |
| Rotating weekly | 0.85 | 100.0% |

## Figures from the original email

| Figure | Design | Archived figure |
|---:|---|---|
| 1 | One stochastic run at phase zero | [Single run](../graphs/sis_single_run.png) |
| 2 | 1,000 runs per schedule, fixed starting phase | [Fixed phase](../graphs/sis_mean_1000_runs.png) |
| 3 | 1,000 runs per schedule, starting phase varied across the 14-day cycle | [Varied phase](../graphs/sis_mean_1000_runs_startdate.png) |
| 4 | 20 worlds × 50 runs per schedule, five schedules | [Multiple worlds](../graphs/sis_mean_multiworld.png) |

| Figure 3 contrast, weekly minus daily | Mean infected difference | 95% interval |
|---|---:|---:|
| On–Off | +0.122 | [−0.036, 0.279] |
| Rotating | −0.011 | [−0.049, 0.027] |

The email records 73 people still infected under full attendance on day 84 of Figure 1. The other four schedules reached zero in that run. Figure 2 shows mean infection of 2.41 for daily On–Off and 3.74 for weekly On–Off, with the two Rotating curves close together. Under varying phase, the corresponding On–Off means were 2.22 and 2.34 and the Rotating means were 0.84 and 0.83. The archived figures contain the full displayed curves.

## Findings and payoff setup

Rotating reduced mean infection relative to On–Off in the initial model, qualitatively consistent with the telecommuting study discussed in the email. The two varied-phase intervals did not clearly distinguish daily and weekly switching. Sample extinction fractions describe the observed runs.

The [original payoff derivation](../pdfs/network_research.pdf) fixes initial status to one known infected person and two susceptible people on a triangle. At β = 0.04, γ = 0.20, infection cost 10, and home cost 0.20, the infected person prefers to attend and the two susceptible people prefer to stay home. The initial email also refers to a separate five-paper literature table. A copy of that table was not located in the repository.

## Reproduce the figures with the current seed scheme

```bash
.venv/bin/python network_sis/sis_experiment.py --sanity
.venv/bin/python network_sis/sis_experiment.py --figure single --plot-path graphs/reproduced_sis_single_run.png
.venv/bin/python network_sis/sis_experiment.py --figure fixed-phase --plot-path graphs/reproduced_sis_mean_1000_runs.png
.venv/bin/python network_sis/sis_experiment.py --figure varied-phase --plot-path graphs/reproduced_sis_mean_1000_runs_startdate.png
```

The commands use the later independent seed streams. The original figures and five-schedule figures above are the historical results from the email. See [Report 2](report2-sis-controls-and-unknown-status-game.md) for the later seven-schedule experiment and sweep.
