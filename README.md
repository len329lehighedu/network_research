# Network research

This repository studies epidemic spread under attendance schedules and the incentives to follow attendance recommendations.

| Directory | Contents |
|---|---|
| [`reports/`](reports/README.md) | Five reports in communication-log order, with complete tables and reproduction commands |
| [`network_sis/`](network_sis/README.md) | SIS simulation code and saved community data |
| [`game/`](game/README.md) | Attendance game code and saved results |
| [`graphs/`](graphs/) | Saved simulation figures |
| [`pdfs/`](pdfs/) | Model derivations and research notes |

## Setup

From the repository root, use Python 3.14 and install the pinned dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```
