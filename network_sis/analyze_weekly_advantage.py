"""Analyze daily versus weekly switching from saved community SIS paths.

Example:
    .venv/bin/python network_sis/analyze_weekly_advantage.py \
        network_sis/beta0085_20w50r.npz

This script reads an existing NPZ file. It does not simulate new epidemics.
"""

import argparse
from pathlib import Path

import numpy as np

from network_communities import (
    SPLITTERS,
    build_community_world,
    load_community_data,
    paired_world_mean_ci,
)
from sis_experiment import attendance


def survivor_statistics_by_world_day(paths):
    """Return survival probability and infection count among survivors.

    Both outputs have shape (world, day), covering days 1 through 84.
    A run survives on a day if its infection count is greater than zero.
    The conditional mean is NaN when no run survives in that world on that day.
    """
    if paths.ndim != 3 or paths.shape[1] == 0 or paths.shape[2] < 2:
        raise ValueError("Expected a nonempty (world, run, day) array")

    # Day 0 contains the shared initial cases. We study the subsequent days.
    counts = paths[:, :, 1:]
    alive = counts > 0

    # Average and count over runs (axis 1), keeping worlds and days separate.
    survival_fraction = alive.mean(axis=1)
    number_alive = alive.sum(axis=1)

    # Infected counts in extinct runs are zero, so summing all runs gives
    # the numerator for the mean among runs that still have infection.
    # NaN records that the conditional mean is undefined with zero survivors.
    conditional_mean = np.divide(
        counts.sum(axis=1),
        number_alive,
        out=np.full(number_alive.shape, np.nan, dtype=float),
        where=number_alive > 0,
    )
    return survival_fraction, conditional_mean


def weekly_comparisons(paths):
    """Compare weekly with daily switching, pairing the same worlds.

    Positive infected_difference means weekly has fewer infections.
    Positive extinction_difference means weekly fades out more often.
    """
    comparisons = {}
    for split_name in SPLITTERS:
        for policy in ("rotating", "control"):
            daily = paths[(split_name, policy, 1)]
            weekly = paths[(split_name, policy, 7)]
            if daily.shape != weekly.shape:
                raise ValueError("Daily and weekly arrays must have the same shape")

            # Each world contributes one mean over its runs and days 1–84.
            # Bootstrap after subtracting within worlds, preserving pairing.
            daily_infected = daily[:, :, 1:].mean(axis=(1, 2))
            weekly_infected = weekly[:, :, 1:].mean(axis=(1, 2))
            infected_difference, infected_ci = paired_world_mean_ci(
                daily_infected, weekly_infected
            )

            # At day 84, zero infected means the run has faded out.
            daily_extinct = (daily[:, :, -1] == 0).mean(axis=1)
            weekly_extinct = (weekly[:, :, -1] == 0).mean(axis=1)
            extinction_difference, extinction_ci = paired_world_mean_ci(
                weekly_extinct, daily_extinct
            )

            daily_survival, daily_conditional = survivor_statistics_by_world_day(
                daily
            )
            weekly_survival, weekly_conditional = survivor_statistics_by_world_day(
                weekly
            )

            # At day 84, conditioning is defined only if each schedule has at
            # least one surviving run in the world. Record how many worlds qualify.
            valid = np.isfinite(daily_conditional[:, -1]) & np.isfinite(
                weekly_conditional[:, -1]
            )
            conditional_difference = None
            conditional_ci = None
            if valid.sum() >= 2:
                conditional_difference, conditional_ci = paired_world_mean_ci(
                    daily_conditional[valid, -1],
                    weekly_conditional[valid, -1],
                )

            # A clean 84-day conditional comparison requires survivors in
            # both schedules on every day of the same world. In particular,
            # worlds extinct before day 84 cannot contribute a full path.
            complete = np.isfinite(daily_conditional).all(axis=1) & np.isfinite(
                weekly_conditional
            ).all(axis=1)
            conditional_path_difference = None
            conditional_path_ci = None
            if complete.sum() >= 2:
                conditional_path_difference, conditional_path_ci = (
                    paired_world_mean_ci(
                        daily_conditional[complete].mean(axis=1),
                        weekly_conditional[complete].mean(axis=1),
                    )
                )

            comparisons[(split_name, policy)] = {
                "infected_difference": infected_difference,
                "infected_ci": infected_ci,
                "extinction_difference": extinction_difference,
                "extinction_ci": extinction_ci,
                "conditional_difference": conditional_difference,
                "conditional_ci": conditional_ci,
                "conditional_worlds": int(valid.sum()),
                "conditional_path_difference": conditional_path_difference,
                "conditional_path_ci": conditional_path_ci,
                "complete_path_worlds": int(complete.sum()),
                "total_worlds": int(len(valid)),
                "daily_survivors_day84": int((daily[:, :, -1] > 0).sum()),
                "weekly_survivors_day84": int((weekly[:, :, -1] > 0).sum()),
                "daily_conditional_day84": float(
                    daily[:, :, -1].sum() / max((daily[:, :, -1] > 0).sum(), 1)
                ),
                "weekly_conditional_day84": float(
                    weekly[:, :, -1].sum() / max((weekly[:, :, -1] > 0).sum(), 1)
                ),
            }

            # Check the exact identity E[I] = P(alive) E[I | alive]
            # for every world and day. With zero survivors, both sides are zero.
            for data, survival, conditional in (
                (daily, daily_survival, daily_conditional),
                (weekly, weekly_survival, weekly_conditional),
            ):
                np.testing.assert_allclose(
                    data[:, :, 1:].mean(axis=1),
                    survival * np.nan_to_num(conditional, nan=0.0),
                )

    return comparisons


def print_weekly_comparisons(comparisons):
    """Print compact Markdown tables and explain undefined conditional means."""
    print("\nWeekly advantage across all runs (95% bootstrap CI over paired worlds):")
    print(
        "| split | policy | daily − weekly: mean infected, days 1–84 "
        "| weekly − daily: extinction by day 84 |"
    )
    print("|---|---|---:|---:|")
    for (split_name, policy), row in comparisons.items():
        inf_low, inf_high = row["infected_ci"]
        ext_low, ext_high = row["extinction_ci"]
        print(
            f"| {split_name} | {policy} | "
            f"{row['infected_difference']:+.2f} [{inf_low:+.2f}, {inf_high:+.2f}] | "
            f"{row['extinction_difference']:+.3f} "
            f"[{ext_low:+.3f}, {ext_high:+.3f}] |"
        )

    print("\nAmong runs still infected on day 84:")
    print(
        "| split | policy | daily: survivors; mean infected "
        "| weekly: survivors; mean infected | paired worlds | "
        "daily − weekly: conditional mean [95% world CI] |"
    )
    print("|---|---|---:|---:|---:|---:|")
    for (split_name, policy), row in comparisons.items():
        if row["conditional_ci"] is None:
            difference_text = "undefined"
        else:
            low, high = row["conditional_ci"]
            difference_text = (
                f"{row['conditional_difference']:+.2f} "
                f"[{low:+.2f}, {high:+.2f}]"
            )
        print(
            f"| {split_name} | {policy} | "
            f"{row['daily_survivors_day84']}; "
            f"{row['daily_conditional_day84']:.2f} | "
            f"{row['weekly_survivors_day84']}; "
            f"{row['weekly_conditional_day84']:.2f} | "
            f"{row['conditional_worlds']}/{row['total_worlds']} | "
            f"{difference_text} |"
        )
    print(
        "Conditional comparisons use only worlds with survivors under both "
        "schedules. The pooled conditional means use all surviving runs."
    )

    print("\nMean infected among surviving runs on each day, averaged over days 1–84:")
    print(
        "| split | policy | complete paired worlds | "
        "daily − weekly [95% world CI] |"
    )
    print("|---|---|---:|---:|")
    for (split_name, policy), row in comparisons.items():
        if row["conditional_path_ci"] is None:
            difference_text = "undefined"
        else:
            low, high = row["conditional_path_ci"]
            difference_text = (
                f"{row['conditional_path_difference']:+.2f} "
                f"[{low:+.2f}, {high:+.2f}]"
            )
        print(
            f"| {split_name} | {policy} | "
            f"{row['complete_path_worlds']}/{row['total_worlds']} | "
            f"{difference_text} |"
        )


def deterministic_sis_step(probabilities, edge_u, edge_v, present, beta, gamma):
    """Advance one day using a deterministic, node-level SIS approximation.

    Each entry is the probability that a person is infected at the start of
    the day. We approximate neighbors' infection states as independent.
    Consequently, this is a mean-field model, not the exact expectation of
    the finite stochastic SIS process.
    """
    if not 0 <= beta <= 1 or not 0 <= gamma <= 1:
        raise ValueError("beta and gamma must be probabilities")

    # An edge can transmit only if both endpoints are present today.
    active = present[edge_u] & present[edge_v]
    u = edge_u[active]
    v = edge_v[active]

    # For susceptible person i, the probability of avoiding every neighbor
    # is product_j (1 - beta * p_j). Logs turn that product into a sum.
    log_no_infection = np.zeros(len(probabilities), dtype=float)
    with np.errstate(divide="ignore"):
        np.add.at(log_no_infection, u, np.log1p(-beta * probabilities[v]))
        np.add.at(log_no_infection, v, np.log1p(-beta * probabilities[u]))
    infection_probability = -np.expm1(log_no_infection)

    # An infected person remains infected with probability 1-gamma. A person
    # susceptible at the start of the day can acquire infection from neighbors.
    # These cases are disjoint because the SIS update is simultaneous.
    return (
        probabilities * (1 - gamma)
        + (1 - probabilities) * infection_probability
    )


def deterministic_trajectory(
    graph, groups, initial, schedule, switch_days, beta, gamma, horizon,
    start_day,
):
    """Return expected infected counts under the node-level approximation."""
    edge_array = np.asarray(list(graph.edges()), dtype=int).reshape(-1, 2)
    edge_u, edge_v = edge_array[:, 0], edge_array[:, 1]

    # Initial infected status is known within each constructed world.
    probabilities = initial.astype(float).copy()
    counts = np.empty(horizon + 1, dtype=float)
    counts[0] = probabilities.sum()

    for day in range(horizon):
        present = attendance(day + start_day, groups, schedule, switch_days)
        probabilities = deterministic_sis_step(
            probabilities, edge_u, edge_v, present, beta, gamma
        )
        counts[day + 1] = probabilities.sum()

    return counts


def deterministic_weekly_comparisons(number_worlds, beta, gamma, horizon, phases):
    """Rebuild saved worlds and compare daily/weekly without epidemic draws.

    The saved simulation varied the starting calendar day. We average this
    deterministic model over the chosen start phases before comparing worlds.
    Each world contributes one paired daily-minus-weekly difference.
    """
    if number_worlds < 2 or not 1 <= phases <= 14:
        raise ValueError("Use at least two worlds and between 1 and 14 phases")

    differences = {
        (split_name, policy): []
        for split_name in SPLITTERS
        for policy in ("rotating", "control")
    }
    worlds = np.random.SeedSequence(2026).spawn(number_worlds)

    for world_index, world_sequence in enumerate(worlds):
        graph, _, initial, groups, controls, _ = build_community_world(
            world_sequence
        )
        for split_name in SPLITTERS:
            for policy in ("rotating", "control"):
                active_graph = graph if policy == "rotating" else controls[split_name]
                schedule = "rotating" if policy == "rotating" else "on_off"

                # Apply the same phases to daily and weekly. This removes
                # starting phase as an explanation for their difference.
                daily_means = []
                weekly_means = []
                for start_day in range(phases):
                    daily = deterministic_trajectory(
                        active_graph, groups[split_name], initial, schedule,
                        1, beta, gamma, horizon, start_day,
                    )
                    weekly = deterministic_trajectory(
                        active_graph, groups[split_name], initial, schedule,
                        7, beta, gamma, horizon, start_day,
                    )
                    daily_means.append(daily[1:].mean())
                    weekly_means.append(weekly[1:].mean())

                differences[(split_name, policy)].append(
                    np.mean(daily_means) - np.mean(weekly_means)
                )
        print(f"Completed deterministic world {world_index + 1}/{number_worlds}",
              flush=True)

    return {
        key: paired_world_mean_ci(np.asarray(values), np.zeros(len(values)))
        for key, values in differences.items()
    }


def print_deterministic_comparisons(comparisons, phases):
    print(
        f"\nDeterministic node-level approximation, averaged over {phases} "
        "start phase(s):"
    )
    print("| split | policy | daily − weekly: mean infected, days 1–84 [95% world CI] |")
    print("|---|---|---:|")
    for (split_name, policy), (mean, (low, high)) in comparisons.items():
        print(
            f"| {split_name} | {policy} | "
            f"{mean:+.2f} [{low:+.2f}, {high:+.2f}] |"
        )


def linearized_sis_step(mass, edge_u, edge_v, present, beta, gamma):
    """Advance a rare-infection perturbation by (1-gamma)I + beta A_today.

    This is the disease-free linearization of the deterministic SIS update.
    Values can grow beyond one and are therefore infection *mass*, not valid
    individual infection probabilities once an outbreak becomes large.
    """
    active = present[edge_u] & present[edge_v]
    u = edge_u[active]
    v = edge_v[active]

    infected_neighbor_mass = np.zeros(len(mass), dtype=float)
    np.add.at(infected_neighbor_mass, u, mass[v])
    np.add.at(infected_neighbor_mass, v, mass[u])
    return (1 - gamma) * mass + beta * infected_neighbor_mass


def linearized_trajectory(
    graph, groups, initial, schedule, switch_days, beta, gamma, horizon,
    start_day,
):
    """Return the total linearized infection mass on days 0 through horizon."""
    edge_array = np.asarray(list(graph.edges()), dtype=int).reshape(-1, 2)
    edge_u, edge_v = edge_array[:, 0], edge_array[:, 1]
    mass = initial.astype(float).copy()
    totals = np.empty(horizon + 1, dtype=float)
    totals[0] = mass.sum()

    for day in range(horizon):
        present = attendance(day + start_day, groups, schedule, switch_days)
        mass = linearized_sis_step(
            mass, edge_u, edge_v, present, beta, gamma
        )
        totals[day + 1] = mass.sum()

    return totals


def linearized_weekly_comparisons(number_worlds, beta, gamma, horizon, phases):
    """Compare switching in the linearized model on the same saved worlds.

    We first average each schedule over start phases within a world, then
    calculate that world's percentage reduction from daily to weekly.
    Worlds, rather than individual phases, are resampled for the 95% CI.
    """
    if number_worlds < 2 or not 1 <= phases <= 14:
        raise ValueError("Use at least two worlds and between 1 and 14 phases")
    if horizon % 14:
        raise ValueError("Cycle-end comparison requires a multiple of 14 days")

    reductions = {
        (split_name, policy): []
        for split_name in SPLITTERS
        for policy in ("rotating", "control")
    }
    maximum_cycle_gap = 0.0
    worlds = np.random.SeedSequence(2026).spawn(number_worlds)

    for world_index, world_sequence in enumerate(worlds):
        graph, _, initial, groups, controls, _ = build_community_world(
            world_sequence
        )
        for split_name in SPLITTERS:
            for policy in ("rotating", "control"):
                active_graph = graph if policy == "rotating" else controls[split_name]
                schedule = "rotating" if policy == "rotating" else "on_off"
                daily_means = []
                weekly_means = []

                for start_day in range(phases):
                    daily = linearized_trajectory(
                        active_graph, groups[split_name], initial, schedule,
                        1, beta, gamma, horizon, start_day,
                    )
                    weekly = linearized_trajectory(
                        active_graph, groups[split_name], initial, schedule,
                        7, beta, gamma, horizon, start_day,
                    )

                    # In this model, daily and weekly operators commute over
                    # a complete 14-day cycle. Their cycle-end masses should
                    # match even if their intermediate daily paths differ.
                    cycle_gap = np.max(
                        np.abs(daily[14::14] - weekly[14::14])
                        / np.maximum(1.0, np.abs(daily[14::14]))
                    )
                    maximum_cycle_gap = max(maximum_cycle_gap, cycle_gap)
                    np.testing.assert_allclose(
                        daily[14::14], weekly[14::14], rtol=1e-10, atol=1e-10
                    )
                    daily_means.append(daily[1:].mean())
                    weekly_means.append(weekly[1:].mean())

                daily_mean = float(np.mean(daily_means))
                weekly_mean = float(np.mean(weekly_means))
                reductions[(split_name, policy)].append(
                    100 * (daily_mean - weekly_mean) / daily_mean
                )
        print(f"Completed linearized world {world_index + 1}/{number_worlds}",
              flush=True)

    return (
        {key: paired_world_mean_ci(values, np.zeros(len(values)))
         for key, values in reductions.items()},
        maximum_cycle_gap,
    )


def print_linearized_comparisons(comparisons, maximum_cycle_gap, phases):
    print(
        f"\nRare-infection linearization, averaged over {phases} "
        "start phase(s):"
    )
    print("| split | policy | daily − weekly, % of daily mass [95% world CI] |")
    print("|---|---|---:|")
    for (split_name, policy), (mean, (low, high)) in comparisons.items():
        print(
            f"| {split_name} | {policy} | "
            f"{mean:+.2f}% [{low:+.2f}%, {high:+.2f}%] |"
        )
    print(
        "Largest relative daily/weekly difference at a 14-day cycle end: "
        f"{maximum_cycle_gap:.2e}"
    )
    print(
        "Linearized mass can exceed the population; percentages compare "
        "the two linear paths and are not infection prevalence."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path, help="saved community NPZ file")
    parser.add_argument(
        "--deterministic", action="store_true",
        help="also rebuild worlds and run the deterministic SIS approximation",
    )
    parser.add_argument(
        "--linearized", action="store_true",
        help="also compare daily/weekly paths near the disease-free state",
    )
    parser.add_argument(
        "--phases", type=int, default=14,
        help="number of start phases for the deterministic approximation (1–14)",
    )
    args = parser.parse_args()

    paths, _, metadata = load_community_data(args.data)
    print(
        f"Loaded {args.data}: beta={metadata['beta']}, "
        f"{metadata['number_worlds']} worlds, "
        f"{metadata['runs_per_world']} runs/world, "
        f"{metadata['horizon']} days"
    )
    print_weekly_comparisons(weekly_comparisons(paths))
    if args.deterministic:
        deterministic = deterministic_weekly_comparisons(
            metadata["number_worlds"], metadata["beta"], metadata["gamma"],
            metadata["horizon"], args.phases,
        )
        print_deterministic_comparisons(deterministic, args.phases)
    if args.linearized:
        linearized, maximum_cycle_gap = linearized_weekly_comparisons(
            metadata["number_worlds"], metadata["beta"], metadata["gamma"],
            metadata["horizon"], args.phases,
        )
        print_linearized_comparisons(
            linearized, maximum_cycle_gap, args.phases
        )


if __name__ == "__main__":
    main()
