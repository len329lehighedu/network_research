"""Stage 4: daily CE vs lookahead CE (belief DP and Monte Carlo) on the 10-person network.

Same network, parameters, start cases, evaluation seed and paired bootstrap as
game/run_multiday_benchmark.py, so the daily CE numbers are comparable with
the benchmark. Three recommenders, all seeing only (day, prevalence):
    daily_ce          the benchmark's daily CE lottery at every (t, k)
    lookahead_belief  method 1: belief_backward_induction
    lookahead_mc      method 2: monte_carlo_policy_iteration, started from method 1,
                      trained on its own seed (never the evaluation root_seed)
With --exact-belief, two more, using the exact-count belief (exact_count_transition):
    lookahead_exact     method 1 with the exact-count belief
    lookahead_exact_mc  method 2 started from (and falling back to) lookahead_exact

Run from the repository root:
    PYTHONPATH=.:game .venv/bin/python reinforcement_learning/run_lookahead_benchmark.py \
        --v 0.14 --behavior v1 --output reinforcement_learning/data/lookahead_v1_v014.csv
Writes the CSV (one row per start case, replicate and policy) and an .npz with
the belief and Monte Carlo value tables and visit counts next to it.
"""

import argparse
import csv
from itertools import combinations
from pathlib import Path

import numpy as np

from multiday_game import make_two_community_graph, paired_payoff_difference_ci, summarize_policy_replicates
from reinforcement_learning.lookahead_ce import (
    belief_backward_induction,
    compare_tables_replicates,
    daily_ce_lottery_table,
    exact_count_transition,
    monte_carlo_policy_iteration,
)


def main():
    parser = argparse.ArgumentParser(description="Compare daily CE with lookahead CE on the 10-person network.")
    parser.add_argument("--runs", type=int, default=500)
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--v", type=float, default=0.14)
    parser.add_argument("--behavior", choices=("v1", "v2"), default="v1")
    parser.add_argument("--iterations", type=int, default=3, help="Monte Carlo policy-iteration rounds.")
    parser.add_argument("--episodes", type=int, default=5000, help="Training episodes per round.")
    parser.add_argument("--min-visits", type=int, default=200)
    parser.add_argument("--train-seed", type=int, default=2026)
    parser.add_argument("--exact-belief", action="store_true",
                        help="Also run lookahead_exact and lookahead_exact_mc.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"{args.output} exists; saved data is never overwritten, pick a new name.")

    graph, _ = make_two_community_graph()
    n_people = graph.number_of_nodes()
    # Benchmark values (game/run_multiday_benchmark.py).
    beta, gamma, L_day, c, v = 0.04, 0.2, 10.0, 0.05, args.v
    root_seed = 123
    policies = ("daily_ce", "lookahead_belief", "lookahead_mc")
    if args.exact_belief:
        policies += ("lookahead_exact", "lookahead_exact_mc")
        transition = exact_count_transition(graph, beta, gamma)

    # The two tables that do not depend on the start case.
    daily = daily_ce_lottery_table(graph, args.days, beta, L_day, gamma, c, v)
    belief_values, belief = belief_backward_induction(graph, args.days, beta, L_day, gamma, c, v)

    all_rows, saved_tables = [], {"belief_values": belief_values}
    if args.exact_belief:
        exact_values, exact = belief_backward_induction(graph, args.days, beta, L_day, gamma, c, v,
                                                        transition=transition)
        saved_tables["exact_values"] = exact_values
    for initial_case in (4, 0):
        infected = np.zeros(n_people, dtype=bool)
        infected[initial_case] = True
        print(f"\nInitial infection: node {initial_case}, v={v:g}, behavior={args.behavior}", flush=True)

        # Method 2 learns on episodes from this start, so it gets its own table per case.
        mc_values, mc, history = monte_carlo_policy_iteration(
            graph, infected, args.days, args.iterations, args.episodes, args.train_seed,
            beta, gamma, L_day, c, v, behavior=args.behavior, min_visits=args.min_visits)
        saved_tables[f"mc_values_case{initial_case}"] = mc_values
        saved_tables[f"mc_counts_case{initial_case}"] = np.stack([counts for _, counts, _ in history])
        changed = sum(not np.allclose(mc[t][k], belief[t][k], atol=1e-6)
                      for t in range(args.days) for k in range(n_people + 1))
        print(f"lookahead_mc table differs from lookahead_belief in {changed} of "
              f"{args.days * (n_people + 1)} cells", flush=True)

        tables = {"daily_ce": daily, "lookahead_belief": belief, "lookahead_mc": mc}
        if args.exact_belief:
            exact_mc_values, exact_mc, exact_history = monte_carlo_policy_iteration(
                graph, infected, args.days, args.iterations, args.episodes, args.train_seed,
                beta, gamma, L_day, c, v, behavior=args.behavior, min_visits=args.min_visits,
                transition=transition)
            saved_tables[f"exact_mc_values_case{initial_case}"] = exact_mc_values
            saved_tables[f"exact_mc_counts_case{initial_case}"] = np.stack([counts for _, counts, _ in exact_history])
            for name, table in (("lookahead_exact", exact), ("lookahead_exact_mc", exact_mc)):
                changed = sum(not np.allclose(table[t][k], daily[t][k], atol=1e-6)
                              for t in range(args.days) for k in range(n_people + 1))
                print(f"{name} table differs from daily_ce in {changed} of "
                      f"{args.days * (n_people + 1)} cells", flush=True)
            tables.update(lookahead_exact=exact, lookahead_exact_mc=exact_mc)

        rows = compare_tables_replicates(
            graph, infected, tables,
            args.runs, root_seed, beta, gamma, L_day, c, v, behavior=args.behavior)

        for row in rows:
            all_rows.append({
                "initial_case": initial_case, "days": args.days, "root_seed": root_seed,
                "beta": beta, "gamma": gamma, "L_day": L_day, "c": c, "v": v,
                "behavior": args.behavior, "iterations": args.iterations, "episodes": args.episodes,
                "min_visits": args.min_visits, "train_seed": args.train_seed,
                "exact_belief": args.exact_belief,
                **row,
            })

        for policy, summary in summarize_policy_replicates(rows).items():
            print(f"{policy}: infected person-days={summary['infected_person_days']:.2f}, "
                  f"group payoff={summary['group_payoff']:.2f}, follow rate={summary['follow_rate']:.3f}")

        # Same bootstrap seed and draws as the benchmark, per start case.
        bootstrap_rng = np.random.default_rng(456)
        for policy_a, policy_b in combinations(policies, 2):
            mean, lower, upper = paired_payoff_difference_ci(rows, policy_b, policy_a, bootstrap_rng, draws=2000)
            print(f"{policy_b} - {policy_a}: {mean:.2f} [{lower:.2f}, {upper:.2f}]")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    np.savez(args.output.with_suffix(".npz"), **saved_tables)
    print(f"\nSaved {len(all_rows)} rows to {args.output} and value tables to {args.output.with_suffix('.npz')}")


if __name__ == "__main__":
    main()
