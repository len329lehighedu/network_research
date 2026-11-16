"""Print Markdown tables from saved multiday benchmark CSVs."""

import argparse
import csv
from itertools import combinations
from pathlib import Path

import numpy as np

from multiday_game import paired_payoff_difference_ci, summarize_policy_replicates


POLICIES = ("daily_ce", "fixed_rotation", "no_recommendation")
LABELS = {
    "daily_ce": "Daily CE",
    "fixed_rotation": "Fixed rotation",
    "no_recommendation": "No recommendation",
}
OUTCOMES = (
    "infected_person_days",
    "attendance_person_days",
    "active_edge_days",
    "group_payoff",
)
SETTINGS = ("days", "root_seed", "beta", "gamma", "L_day", "c")


def load_benchmark_groups(paths):
    """Group outcomes by contact value and initial infection node."""
    groups = {}
    expected_settings = None
    seen = set()
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                settings = tuple(float(row[key]) for key in SETTINGS)
                if expected_settings is None:
                    expected_settings = settings
                if settings != expected_settings:
                    raise ValueError(f"{path}: benchmark settings differ beyond v.")

                group = (float(row["v"]), int(row["initial_case"]))
                replicate = int(row["replicate"])
                policy = row["policy"]
                key = (*group, replicate, policy)
                if key in seen:
                    raise ValueError(f"{path}: duplicate observation {key}.")
                seen.add(key)

                follow_rate = row["follow_rate"]
                groups.setdefault(group, []).append({
                    "replicate": replicate,
                    "policy": policy,
                    **{metric: float(row[metric]) for metric in OUTCOMES},
                    "follow_rate": float(follow_rate) if follow_rate else None,
                })

    if not groups:
        raise ValueError("No benchmark observations found.")
    return groups


def print_table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        print("| " + " | ".join(map(str, row)) + " |")


def print_benchmark_tables(groups):
    outcome_rows = []
    contrast_rows = []
    policy_pairs = tuple(combinations(POLICIES, 2))

    for v, initial_case in sorted(groups, key=lambda group: (group[0], -group[1])):
        rows = groups[v, initial_case]
        summaries = summarize_policy_replicates(rows)
        if summaries.keys() != LABELS.keys():
            raise ValueError(f"Expected all three policies for v={v:g}, node {initial_case}.")
        label = (f"{v:.2f}", initial_case)

        for policy in reversed(POLICIES):
            summary = summaries[policy]
            follow_rate = summary["follow_rate"]
            outcome_rows.append((
                *label,
                LABELS[policy],
                summary["n_replicates"],
                *(f"{summary[metric]:.2f}" for metric in OUTCOMES),
                "N/A" if follow_rate is None else f"{follow_rate:.1%}",
            ))

        # Match the bootstrap seed and contrast order used by the simulation CLI.
        rng = np.random.default_rng(456)
        contrasts = []
        for policy_a, policy_b in policy_pairs:
            mean, lower, upper = paired_payoff_difference_ci(rows, policy_a, policy_b, rng)
            contrasts.append(f"{mean:+.2f} [{lower:.2f}, {upper:.2f}]")
        contrast_rows.append((*label, *contrasts))

    print("### Mean outcomes per run\n")
    print_table(("v", "Initial case", "Policy", "Runs", "Infected person-days",
                 "Attendance person-days", "Active edge-days", "Group payoff", "Follow rate"), outcome_rows)

    print("\n### Payoff differences with 95% paired bootstrap intervals\n")
    print_table(("v", "Initial case", *(f"{LABELS[a]} − {LABELS[b]}" for a, b in policy_pairs)), contrast_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_paths", metavar="CSV", type=Path, nargs="+")
    args = parser.parse_args()
    print_benchmark_tables(load_benchmark_groups(args.csv_paths))


if __name__ == "__main__":
    main()
