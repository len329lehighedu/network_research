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
    """Group outcomes by behavior, belief, contact value and initial infection node."""
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

                # Old CSVs have no behavior columns, so they count as legacy/schedule.
                group = (
                    row.get("behavior", "legacy"),
                    row.get("rotation_belief", "schedule"),
                    float(row["v"]),
                    int(row["initial_case"]),
                )
                replicate = int(row["replicate"])
                policy = row["policy"]
                key = (*group, replicate, policy)
                if key in seen:
                    raise ValueError(f"{path}: duplicate observation {key}.")
                seen.add(key)

                follow_rate = row["follow_rate"]
                willingness = row.get("final_mean_willingness", "")
                groups.setdefault(group, []).append({
                    "replicate": replicate,
                    "policy": policy,
                    **{metric: float(row[metric]) for metric in OUTCOMES},
                    "follow_rate": float(follow_rate) if follow_rate else None,
                    # Empty means the policy has no willingness.
                    "final_mean_willingness": float(willingness) if willingness else None,
                    # Older CSVs have no day-0 or day-7 columns, so those count as missing.
                    **{
                        column: float(row[column]) if row.get(column) else None
                        for column in ("willingness_d0", "willingness_d7")
                    },
                })

    if not groups:
        raise ValueError("No benchmark observations found.")
    return groups, dict(zip(SETTINGS, expected_settings, strict=True))


def print_table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for row in rows:
        print("| " + " | ".join(map(str, row)) + " |")


def bootstrap_mean_ci(values, rng, draws=2000):
    """Return the mean of values and its 95% percentile bootstrap interval."""
    values = np.asarray(values, dtype=float)
    means = np.array([
        values[rng.integers(0, len(values), len(values))].mean() for _ in range(draws)
    ])
    return values.mean(), *np.percentile(means, [2.5, 97.5])


def print_willingness_path_table(paths):
    """Compare the fixed-rotation willingness path under v2 and v2_shuffled."""
    # Collect each fixed-rotation replicate's willingness on days 0, 7, and 14,
    # keyed by (behavior, v, initial case, replicate). The day-7 column exists
    # only in CSVs written after it was added.
    paths_by_key = {}
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["policy"] != "fixed_rotation" or row["rotation_belief"] != "schedule":
                    continue
                if row["behavior"] not in ("v2", "v2_shuffled"):
                    continue
                key = (row["behavior"], float(row["v"]), int(row["initial_case"]), int(row["replicate"]))
                paths_by_key[key] = tuple(
                    float(row[column])
                    for column in ("willingness_d0", "willingness_d7", "final_mean_willingness")
                )

    rows = []
    cells = sorted({(v, case) for _, v, case, _ in paths_by_key}, key=lambda cell: (cell[0], -cell[1]))
    for v, case in cells:
        # Pair the two behaviors by replicate. Both start from the same willingness
        # stream, so a replicate has the same day-0 willingness under each.
        replicates = sorted(
            {r for b, vv, cc, r in paths_by_key if (b, vv, cc) == ("v2", v, case)}
            & {r for b, vv, cc, r in paths_by_key if (b, vv, cc) == ("v2_shuffled", v, case)}
        )
        if len(replicates) < 2:
            raise ValueError(f"Need v2 and v2_shuffled replicates for v={v:g}, node {case}.")
        path = {
            behavior: np.array([paths_by_key[behavior, v, case, r] for r in replicates])
            for behavior in ("v2", "v2_shuffled")
        }
        if not np.allclose(path["v2"][:, 0], path["v2_shuffled"][:, 0]):
            raise ValueError(f"Day-0 willingness differs between behaviors for v={v:g}, node {case}.")

        # One bootstrap stream per cell, used in a fixed order: v2, v2_shuffled, difference.
        rng = np.random.default_rng(456)
        change = {behavior: values[:, 2] - values[:, 0] for behavior, values in path.items()}
        change_ci = {behavior: bootstrap_mean_ci(change[behavior], rng) for behavior in ("v2", "v2_shuffled")}
        difference = bootstrap_mean_ci(change["v2"] - change["v2_shuffled"], rng)

        for behavior in ("v2", "v2_shuffled"):
            mean_change, lower, upper = change_ci[behavior]
            d0, d7, d14 = path[behavior].mean(axis=0)
            rows.append((
                behavior, f"{v:.2f}", case, len(replicates), f"{d0:.3f}", f"{d7:.3f}", f"{d14:.3f}",
                f"{mean_change:+.3f} [{lower:+.3f}, {upper:+.3f}]",
                f"{difference[0]:+.3f} [{difference[1]:+.3f}, {difference[2]:+.3f}]" if behavior == "v2" else "",
            ))

    print("### Fixed-rotation willingness under v2 and v2_shuffled\n")
    print_table(("Behavior", "v", "Initial case", "Runs", "Day 0", "Day 7", "Day 14",
                 "Day 14 − day 0", "v2 − v2_shuffled (day 14 − day 0)"), rows)


def print_benchmark_tables(groups, infection_cost, home_cost):
    outcome_rows = []
    contrast_rows = []
    breakdown_rows = []
    policy_pairs = tuple(combinations(POLICIES, 2))

    for behavior, belief, v, initial_case in sorted(
        groups, key=lambda group: (group[0], group[1], group[2], -group[3])
    ):
        rows = groups[behavior, belief, v, initial_case]
        summaries = summarize_policy_replicates(rows)
        if summaries.keys() != LABELS.keys():
            raise ValueError(
                f"Expected all three policies for {behavior}/{belief}, v={v:g}, node {initial_case}."
            )
        label = (behavior, belief, f"{v:.2f}", initial_case)

        for policy in reversed(POLICIES):
            summary = summaries[policy]
            follow_rate = summary["follow_rate"]
            willingness = summary["final_mean_willingness"]
            outcome_rows.append((
                *label,
                LABELS[policy],
                summary["n_replicates"],
                *(f"{summary[metric]:.2f}" for metric in OUTCOMES),
                "N/A" if follow_rate is None else f"{follow_rate:.1%}",
                "N/A" if willingness is None else f"{willingness:.3f}",
            ))

        # Match the bootstrap seed and contrast order used by the simulation CLI.
        rng = np.random.default_rng(456)
        contrasts = []
        for policy_a, policy_b in policy_pairs:
            mean, lower, upper = paired_payoff_difference_ci(rows, policy_a, policy_b, rng)
            contrasts.append(f"{mean:+.2f} [{lower:.2f}, {upper:.2f}]")
            a, b = summaries[policy_a], summaries[policy_b]
            contact_benefit = 2 * v * (a["active_edge_days"] - b["active_edge_days"])
            infection_savings = infection_cost * (b["infected_person_days"] - a["infected_person_days"])
            home_savings = home_cost * (a["attendance_person_days"] - b["attendance_person_days"])
            breakdown_rows.append((
                *label,
                f"{LABELS[policy_a]} − {LABELS[policy_b]}",
                *(f"{value + 0.0:+.2f}" for value in (contact_benefit, infection_savings, home_savings, mean)),
            ))
        contrast_rows.append((*label, *contrasts))

    print("### Mean outcomes per run\n")
    print_table(("Behavior", "Belief", "v", "Initial case", "Policy", "Runs", "Infected person-days",
                 "Attendance person-days", "Active edge-days", "Group payoff", "Follow rate",
                 "Final mean willingness"), outcome_rows)

    print("\n### Payoff differences with 95% paired bootstrap intervals\n")
    print_table(("Behavior", "Belief", "v", "Initial case",
                 *(f"{LABELS[a]} − {LABELS[b]}" for a, b in policy_pairs)), contrast_rows)

    print("\n### Breakdown of mean payoff differences\n")
    print("Each component is the contribution to the payoff of the first policy minus the second. "
          "Positive values favor the first policy. Totals use unrounded values.\n")
    print_table(("Behavior", "Belief", "v", "Initial case", "Comparison", "Contact benefit", "Infection cost savings",
                 "Home cost savings", "Group payoff difference"), breakdown_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_paths", metavar="CSV", type=Path, nargs="+")
    parser.add_argument(
        "--willingness-path", action="store_true",
        help="Print the fixed-rotation willingness table for v2 versus v2_shuffled instead.",
    )
    args = parser.parse_args()
    if args.willingness_path:
        print_willingness_path_table(args.csv_paths)
        return
    groups, settings = load_benchmark_groups(args.csv_paths)
    print_benchmark_tables(groups, settings["L_day"], settings["c"])


if __name__ == "__main__":
    main()
