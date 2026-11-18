import argparse
import csv
from itertools import combinations
from pathlib import Path

import numpy as np

from multiday_game import (
    make_two_community_graph,
    paired_payoff_difference_ci,
    run_policy_replicates,
    summarize_policy_replicates,
)


def main():
    parser = argparse.ArgumentParser(description="Run the multiday attendance benchmark.")
    parser.add_argument("--runs", type=int, default=500)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--v", type=float, default=0.14)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--update-prob", type=float, default=1.0,
        help="Daily probability of reconsidering attendance without recommendations.",
    )
    parser.add_argument("--behavior", choices=("legacy", "v1", "v2"), default="legacy")
    parser.add_argument("--rotation-belief", choices=("schedule", "last_same_phase"), default="schedule")
    args = parser.parse_args()
    if not 0.0 <= args.update_prob <= 1.0:
        parser.error("--update-prob must be between 0 and 1.")
    if args.runs < 2 or args.days < 1:
        parser.error("Use at least two runs and one day.")

    graph, groups = make_two_community_graph()
    n_people = graph.number_of_nodes()
    params = dict(beta=0.04, gamma=0.2, L_day=10, c=0.05, v=args.v, update_prob=args.update_prob,
                  behavior=args.behavior, rotation_belief=args.rotation_belief)
    policies = ("daily_ce", "fixed_rotation", "no_recommendation")
    root_seed = 123
    all_rows = []

    for initial_case in (4, 0):
        infected = np.zeros(n_people, dtype=bool)
        infected[initial_case] = True
        print(f"\nInitial infection: node {initial_case}, v={args.v:g}", flush=True)

        rows = run_policy_replicates(
            graph, groups, infected,
            days=args.days, n_replicates=args.runs, root_seed=root_seed,
            **params,
        )

        # Store the settings alongside every replicate so the CSV is self-contained.
        for row in rows:
            all_rows.append({
                "initial_case": initial_case,
                "days": args.days,
                "root_seed": root_seed,
                **params,  # includes behavior and rotation_belief
                **row,
            })

        for policy, summary in summarize_policy_replicates(rows).items():
            print(
                f"{policy}: infected person-days={summary['infected_person_days']:.2f}, "
                f"group payoff={summary['group_payoff']:.2f}"
            )

        # Reproduce the same paired bootstrap for each initial case.
        bootstrap_rng = np.random.default_rng(456)
        for policy_a, policy_b in combinations(policies, 2):
            mean, lower, upper = paired_payoff_difference_ci(
                rows, policy_a, policy_b, bootstrap_rng, draws=2000
            )
            print(f"{policy_a} - {policy_b}: {mean:.2f} [{lower:.2f}, {upper:.2f}]")

    # Write one row per initial case, replicate, and policy.
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nSaved {len(all_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()