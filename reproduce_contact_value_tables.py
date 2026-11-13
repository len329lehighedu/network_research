"""Print the README contact-value tables from saved experiment data."""

import argparse
import csv
from itertools import product
from pathlib import Path


def print_table(headers, rows):
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        print("| " + " | ".join(map(str, row)) + " |")
    print()


def print_community_tables(directory):
    import numpy as np

    from network_sis.community_obedience import bootstrap_pair_obedience

    beta_codes = (40, 50, 60, 70, 80, 85, 90, 100, 110, 120)
    comparisons = tuple(product((1, 7), ("random", "even")))
    metrics = ("home", "home_k_positive", "attend", "home_k_zero")
    shares = {group: {metric: [] for metric in metrics} for group in ("Whole", "Random or Even")}
    break_even_rows = []
    interval_rows = []

    def interval(point, draws, scale=1):
        lo, hi = np.quantile(draws, (0.025, 0.975)) * scale
        if scale == 100:
            return f"{point * scale:.1f}% [{lo:.1f}, {hi:.1f}]"
        return f"{point:.3f} [{lo:.3f}, {hi:.3f}]"

    for code in beta_codes:
        path = directory / f"beta{code:04d}_20w50r.npz"
        row = [f"{code / 1000:.3f}"]
        with np.load(path, allow_pickle=False) as data:
            for switch, alternative in comparisons:
                fit = bootstrap_pair_obedience(data, alternative, switch, L_day=10, c=0.05)
                row.append(f"{fit['v_point']:.4f}")
                for split, group in (("whole", "Whole"), (alternative, "Random or Even")):
                    for metric in metrics:
                        shares[group][metric].append(fit["point_shares"][split][metric])

                if code == 85:
                    def share_interval(split, metric):
                        return interval(fit["point_shares"][split][metric], fit["share_draws"][split][metric], 100)

                    interval_rows.append((
                        "Daily" if switch == 1 else "Weekly", alternative.title(),
                        interval(fit["v_point"], fit["v_draws"]),
                        share_interval("whole", "home_k_positive"),
                        share_interval(alternative, "home_k_positive"),
                        share_interval("whole", "attend"),
                    ))
        break_even_rows.append(row)

    print_table(("β", "Daily: Whole vs. Random", "Daily: Whole vs. Even",
                 "Weekly: Whole vs. Random", "Weekly: Whole vs. Even"), break_even_rows)

    def percent_range(values):
        low, high = f"{min(values):.1%}", f"{max(values):.1%}"
        return low if low == high else f"{low.removesuffix('%')}–{high}"

    print_table(("Split", "Home → attend", "Home → attend, k > 0", "Attend → home", "Home with k = 0"),
                [(group, *(percent_range(values[m]) for m in metrics)) for group, values in shares.items()])
    print_table(("Switching", "Alternative", "v* [95% CI]", "Whole: home → attend, k > 0",
                 "Alternative: home → attend, k > 0", "Whole: attend → home"), interval_rows)


def print_atlas_tables(path):
    from network_game import (
        connected_atlas_graphs,
        expected_payoff_with_contact_value,
        pure_nash_equilibria_with_contact_value,
    )

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    tol = 1e-8

    def counts(group):
        return (
            sum(float(row["ce_gain_vs_pure"]) > tol for row in group if row["ce_gain_vs_pure"]),
            sum(float(row["ce_gain_vs_independent_found"]) > tol for row in group if row["ce_gain_vs_independent_found"]),
            sum(abs(float(row["best_ce"]) - float(row["social_minimum"])) <= tol for row in group),
        )

    pairs = sorted({(float(row["pi"]), float(row["c"])) for row in rows})
    summary = []
    for pi, c in pairs:
        group = [row for row in rows if (float(row["pi"]), float(row["c"])) == (pi, c)]
        summary.append((f"{pi:.2f}", f"{c:.2f}", *(f"{count}/{len(group)}" for count in counts(group))))
    summary.append(("Total", "", *(f"{count}/{len(rows)}" for count in counts(rows))))
    print_table(("π", "c", "CE improves on best pure Nash", "CE improves on lowest-cost independent Nash found",
                 "CE reaches social minimum"), summary)

    by_equilibria = []
    for c in (0.05, 0.12):
        for unique in (True, False):
            group = [row for row in rows if float(row["pi"]) == 0.1 and float(row["c"]) == c
                     and (int(row["pure_nash_count"]) == 1) == unique]
            by_equilibria.append(("0.10", f"{c:.2f}", "One" if unique else "Multiple",
                                   f"{counts(group)[0]}/{len(group)}"))
    print_table(("π", "c", "Pure equilibria per network", "CE improves on best pure Nash"), by_equilibria)

    example = next(row for row in rows if int(row["atlas_id"]) == 42
                   and float(row["pi"]) == 0.1 and float(row["c"]) == 0.05)
    params = {key: float(example[key]) for key in ("pi", "beta", "L_day", "gamma", "c", "v")}
    graph = dict(connected_atlas_graphs(5))[42]
    profile, = pure_nash_equilibria_with_contact_value(graph, **params)
    pure_max = max(-expected_payoff_with_contact_value(graph, profile, i, **params)
                   - params["L_day"] * params["pi"] for i in graph.nodes)
    print_table(("Atlas 42 outcome", "Expected group cost", "Highest expected individual cost"), (
        (f"Unique pure Nash (`{''.join(profile)}`)", f"{float(example['best_pure_nash']):.6f}", f"{pure_max:.6f}"),
        ("Lowest-cost independent Nash found", f"{float(example['lowest_independent_nash_found']):.6f}", "—"),
        ("Optimal CE, averaged over graph symmetries", f"{float(example['best_ce']):.6f}",
         f"{float(example['highest_individual_ce_cost']):.6f}"),
        ("Social minimum", f"{float(example['social_minimum']):.6f}", "—"),
    ))
    pure = float(example["best_pure_nash"])
    minimum = float(example["social_minimum"])
    reduction = pure - float(example["best_ce"])
    print_table(("CE comparison with best pure Nash", "Value"), (
        ("Group cost reduction above baseline", f"{reduction:.6f}"),
        ("Group cost reduction relative to best pure Nash", f"{reduction / pure:.1%}"),
        ("Share of the gap to the social minimum closed", f"{reduction / (pure - minimum):.1%}"),
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--community-dir", type=Path)
    inputs.add_argument("--atlas-csv", type=Path)
    args = parser.parse_args()
    if args.community_dir is not None:
        print_community_tables(args.community_dir)
    else:
        print_atlas_tables(args.atlas_csv)


if __name__ == "__main__":
    main()
