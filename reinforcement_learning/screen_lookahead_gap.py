"""Experiment: where could looking ahead beat the daily CE on the 10-person network?

Screen (no simulation): under the exact-count belief, the value of ANY lottery
table can be computed by backward induction with the lottery held fixed:
    V_t(k) = sum_p q_p [ -L_day E[k' | k, p] + contact(p) ] + sum_k' P(k' | k) V_{t+1}(k')
with q = table[t][k] and P(k' | k) = sum_p q_p T[k, p, k']. We evaluate the daily CE
table this way and compare it with the lookahead table, which is optimal in
this model. The gap V_lookahead_0(1) - V_daily_0(1) is the most looking ahead
can add (in the model) when one person starts infected.

Confirm (simulation): rerun daily CE vs lookahead (and optionally Monte Carlo
policy iteration) on the simulator at chosen (beta, gamma, v), with the same
start cases, evaluation seed and paired bootstrap as the Report 6 step 2 runs.

Run from the repository root:
    PYTHONPATH=.:game .venv/bin/python reinforcement_learning/screen_lookahead_gap.py check
    PYTHONPATH=.:game .venv/bin/python reinforcement_learning/screen_lookahead_gap.py screen \
        --output reinforcement_learning/data/screen_gap.csv
    PYTHONPATH=.:game .venv/bin/python reinforcement_learning/screen_lookahead_gap.py confirm \
        --beta 0.12 --gamma 0.1 --v 0.28 --output reinforcement_learning/data/confirm_b012_g010_v028.csv
"""

import argparse
import csv
import time
from itertools import combinations, product
from pathlib import Path

import numpy as np

from multiday_game import make_two_community_graph, paired_payoff_difference_ci, summarize_policy_replicates
from network_game import active_contacts, all_action_profiles
from reinforcement_learning.lookahead_ce import (
    belief_backward_induction,
    compare_tables_replicates,
    daily_ce_lottery_table,
    exact_count_transition,
    monte_carlo_policy_iteration,
)

DAYS = 14
L_DAY, C = 10.0, 0.05


def evaluate_lottery_table(graph, table, transition, L_day, c, v):
    """Expected payoff and infected person-days of a fixed lottery table, exact-count model.

    Returns (values, infected_days), each (days + 1, N + 1); row `days` is 0.
    infected_days counts end-of-day infected people, as summarize_trajectory does.
    """
    n_people = graph.number_of_nodes()
    days = len(table)
    profiles = all_action_profiles(graph)
    counts = np.arange(n_people + 1)
    # Contact benefit and home cost of each profile, the same terms the LP uses.
    contact_part = np.array([2 * v * active_contacts(graph, p) - c * p.count("H") for p in profiles])

    values = np.zeros((days + 1, n_people + 1))
    infected_days = np.zeros((days + 1, n_people + 1))
    for t in range(days - 1, -1, -1):
        for k in range(n_people + 1):
            q = np.asarray(table[t][k], dtype=float)
            next_dist = q @ transition[k]            # P(k' | k) under this lottery
            expected_infected = next_dist @ counts   # E[k'] = end-of-day infected today
            values[t, k] = -L_day * expected_infected + q @ contact_part + next_dist @ values[t + 1]
            infected_days[t, k] = expected_infected + next_dist @ infected_days[t + 1]
    return values, infected_days


def attendance_and_edges(graph):
    profiles = all_action_profiles(graph)
    return (np.array([p.count("A") for p in profiles]),
            np.array([active_contacts(graph, p) for p in profiles]))


def screen_point(graph, beta, gamma, v, attend, edges):
    """Model values of daily CE and lookahead at one parameter point."""
    transition = exact_count_transition(graph, beta, gamma)
    daily = daily_ce_lottery_table(graph, DAYS, beta, L_DAY, gamma, C, v)
    look_values, lookahead = belief_backward_induction(graph, DAYS, beta, L_DAY, gamma, C, v,
                                                       transition=transition)
    daily_values, daily_infected = evaluate_lottery_table(graph, daily, transition, L_DAY, C, v)
    look_eval, look_infected = evaluate_lottery_table(graph, lookahead, transition, L_DAY, C, v)
    # Cells where the two tables differ in expected attendance or active edges.
    differing = sum(
        abs(np.asarray(daily[t][k]) @ attend - np.asarray(lookahead[t][k]) @ attend) > 1e-3
        or abs(np.asarray(daily[t][k]) @ edges - np.asarray(lookahead[t][k]) @ edges) > 1e-3
        for t in range(DAYS) for k in range(graph.number_of_nodes() + 1))
    return {
        "transition": transition, "daily": daily, "lookahead": lookahead,
        "daily_values": daily_values, "look_values": look_values, "look_eval": look_eval,
        "daily_infected": daily_infected, "look_infected": look_infected, "differing_cells": differing,
    }


def run_check():
    """Sanity checks with expected values derived independently of the evaluator."""
    graph, _ = make_two_community_graph()
    attend, edges = attendance_and_edges(graph)

    # (a) The lookahead table's DP value IS its value: re-evaluating it must give
    #     the exact_values saved by the Report 6 step 2 runs, in every cell.
    for v, tag in ((0.14, "014"), (0.28, "028")):
        saved = np.load(f"reinforcement_learning/data/lookahead_exact_v1_v{tag}.npz")["exact_values"]
        point = screen_point(graph, 0.04, 0.2, v, attend, edges)
        assert np.allclose(point["look_eval"], saved, atol=1e-6), np.abs(point["look_eval"] - saved).max()
        # (d) Lookahead is optimal in the model, so it is never worse than daily CE.
        assert (point["look_values"] >= point["daily_values"] - 1e-6).all()
    print("(a) lookahead table re-evaluates to the saved exact_values; (d) lookahead >= daily everywhere")

    # (b) beta = 0: nobody is infected, k falls as Binomial(k, 0.8) per day, so
    #     E[infected end of day t] from k = 1 is 0.8^t; sum over t = 1..14 is
    #     0.8 (1 - 0.8^14) / 0.2 = 3.8241.
    transition = exact_count_transition(graph, 0.0, 0.2)
    daily = daily_ce_lottery_table(graph, DAYS, 0.0, L_DAY, 0.2, C, 0.14)
    _, infected = evaluate_lottery_table(graph, daily, transition, L_DAY, C, 0.14)
    assert np.isclose(infected[0, 1], 0.8 * (1 - 0.8 ** 14) / 0.2, atol=1e-9), infected[0, 1]
    print(f"(b) beta = 0 infected person-days from k = 1: {infected[0, 1]:.4f} (hand: 3.8241)")

    # (c) Daily CE at the benchmark vs the saved simulation (500 runs, root seed 123).
    #     The exact-count model forgets WHO is infected, so it should sit near the
    #     average of the two start cases; report the gap, do not assert a tolerance.
    simulated = {0.14: (11.06, 15.48, 4.09, 3.79), 0.28: (65.67, 74.97, 7.71, 7.03)}
    for v, (pay4, pay0, inf4, inf0) in simulated.items():
        point = screen_point(graph, 0.04, 0.2, v, attend, edges)
        print(f"(c) v={v}: model daily payoff {point['daily_values'][0, 1]:.2f} vs simulated "
              f"{pay4:.2f} (case 4) / {pay0:.2f} (case 0); infected person-days "
              f"{point['daily_infected'][0, 1]:.2f} vs {inf4:.2f} / {inf0:.2f}")
    print("screen checks done")


def run_screen(args):
    if args.output.exists():
        raise SystemExit(f"{args.output} exists; saved data is never overwritten, pick a new name.")
    graph, _ = make_two_community_graph()
    attend, edges = attendance_and_edges(graph)
    rows = []
    grid = list(product(args.betas, args.gammas, args.vs))
    for i, (beta, gamma, v) in enumerate(grid, 1):
        start = time.time()
        point = screen_point(graph, beta, gamma, v, attend, edges)
        row = {"beta": beta, "gamma": gamma, "v": v, "L_day": L_DAY, "c": C, "days": DAYS}
        for k in (1, 2):
            daily_value = point["daily_values"][0, k]
            gap = point["look_values"][0, k] - daily_value
            row.update({
                f"V_daily_k{k}": daily_value, f"V_lookahead_k{k}": point["look_values"][0, k],
                f"gap_k{k}": gap, f"gap_share_k{k}": gap / max(abs(daily_value), 1e-9),
                f"infected_days_daily_k{k}": point["daily_infected"][0, k],
                f"infected_days_lookahead_k{k}": point["look_infected"][0, k],
            })
        row["differing_cells"] = point["differing_cells"]
        rows.append(row)
        print(f"[{i}/{len(grid)}] beta={beta:g} gamma={gamma:g} v={v:g}: "
              f"daily {row['V_daily_k1']:.2f}, lookahead {row['V_lookahead_k1']:.2f}, "
              f"gap {row['gap_k1']:+.2f} ({100 * row['gap_share_k1']:.1f}%), "
              f"infected-days {row['infected_days_daily_k1']:.2f} -> {row['infected_days_lookahead_k1']:.2f}, "
              f"{row['differing_cells']} cells differ ({time.time() - start:.1f}s)", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    # Points that pass the pre-stated screening rule (from k = 1).
    passing = [r for r in rows if r["gap_k1"] >= args.min_gap and r["gap_share_k1"] >= args.min_share]
    print(f"\nSaved {len(rows)} points to {args.output}")
    print(f"{len(passing)} points pass gap >= {args.min_gap} and gap share >= {100 * args.min_share:.0f}%:")
    for r in sorted(passing, key=lambda r: -r["gap_k1"]):
        print(f"  beta={r['beta']:g} gamma={r['gamma']:g} v={r['v']:g}: gap {r['gap_k1']:+.2f} "
              f"({100 * r['gap_share_k1']:.1f}%), daily {r['V_daily_k1']:.2f}")


def run_confirm(args):
    if args.output.exists():
        raise SystemExit(f"{args.output} exists; saved data is never overwritten, pick a new name.")
    graph, _ = make_two_community_graph()
    beta, gamma, v = args.beta, args.gamma, args.v
    n_people = graph.number_of_nodes()
    root_seed = 123
    transition = exact_count_transition(graph, beta, gamma)
    daily = daily_ce_lottery_table(graph, DAYS, beta, L_DAY, gamma, C, v)
    _, lookahead = belief_backward_induction(graph, DAYS, beta, L_DAY, gamma, C, v, transition=transition)
    policies = ("daily_ce", "lookahead_exact") + (("lookahead_exact_mc",) if args.mc else ())

    all_rows = []
    for initial_case in (4, 0):
        infected = np.zeros(n_people, dtype=bool)
        infected[initial_case] = True
        print(f"\nbeta={beta:g} gamma={gamma:g} v={v:g}, initial infection node {initial_case}", flush=True)
        tables = {"daily_ce": daily, "lookahead_exact": lookahead}
        if args.mc:
            _, tables["lookahead_exact_mc"], _ = monte_carlo_policy_iteration(
                graph, infected, DAYS, args.iterations, args.episodes, args.train_seed,
                beta, gamma, L_DAY, C, v, behavior=args.behavior, min_visits=args.min_visits,
                transition=transition)
        rows = compare_tables_replicates(graph, infected, tables, args.runs, root_seed,
                                         beta, gamma, L_DAY, C, v, behavior=args.behavior)
        for row in rows:
            all_rows.append({"initial_case": initial_case, "beta": beta, "gamma": gamma, "v": v,
                             "L_day": L_DAY, "c": C, "days": DAYS, "root_seed": root_seed,
                             "behavior": args.behavior, **row})
        for policy, s in summarize_policy_replicates(rows).items():
            print(f"{policy}: infected person-days={s['infected_person_days']:.2f}, "
                  f"group payoff={s['group_payoff']:.2f}, follow rate={s['follow_rate']:.3f}")
        bootstrap_rng = np.random.default_rng(456)
        for a, b in combinations(policies, 2):
            mean, lower, upper = paired_payoff_difference_ci(rows, b, a, bootstrap_rng, draws=2000)
            print(f"{b} - {a}: {mean:+.2f} [{lower:.2f}, {upper:.2f}]", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nSaved {len(all_rows)} rows to {args.output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("check", help="Sanity checks of the model evaluator.")

    screen = sub.add_parser("screen", help="Model-only gap map over a (beta, gamma, v) grid.")
    screen.add_argument("--betas", type=float, nargs="+", default=[0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20])
    screen.add_argument("--gammas", type=float, nargs="+", default=[0.10, 0.20])
    screen.add_argument("--vs", type=float, nargs="+", default=[0.0, 0.14, 0.28, 0.42])
    screen.add_argument("--min-gap", type=float, default=1.0)
    screen.add_argument("--min-share", type=float, default=0.03)
    screen.add_argument("--output", type=Path, required=True)

    confirm = sub.add_parser("confirm", help="Simulate daily CE vs lookahead at one point.")
    confirm.add_argument("--beta", type=float, required=True)
    confirm.add_argument("--gamma", type=float, required=True)
    confirm.add_argument("--v", type=float, required=True)
    confirm.add_argument("--runs", type=int, default=500)
    confirm.add_argument("--behavior", choices=("v1", "v2"), default="v1")
    confirm.add_argument("--mc", action="store_true", help="Also run Monte Carlo policy iteration.")
    confirm.add_argument("--iterations", type=int, default=3)
    confirm.add_argument("--episodes", type=int, default=5000)
    confirm.add_argument("--min-visits", type=int, default=200)
    confirm.add_argument("--train-seed", type=int, default=2026)
    confirm.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    {"check": lambda: run_check(), "screen": lambda: run_screen(args), "confirm": lambda: run_confirm(args)}[args.mode]()


if __name__ == "__main__":
    main()
