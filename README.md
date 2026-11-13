# Network research

This repository studies epidemic spread under attendance schedules and the incentives to follow attendance recommendations.

| Directory | Contents |
|---|---|
| [`network_sis/`](network_sis/README.md) | SIS simulations, schedule comparisons, community results, and commands to reproduce the tables and figures |
| [`game/`](game/README.md) | Attendance games, Nash and correlated equilibria, network atlas results, and reproduction commands |
| [`graphs/`](graphs/) | Saved simulation figures |
| [`pdfs/`](pdfs/) | Model derivations and research notes |

## Setup

From the repository root, use Python 3.14 and install the pinned dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```
