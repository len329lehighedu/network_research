"""Compare attendance schedules in a stochastic SIS contact network.

Run ``python sis_simulation.py --sanity`` for model checks, then run
``python sis_simulation.py`` for the default 20-world experiment.
"""

import argparse
from pathlib import Path

import matplotlib
import networkx as nx
import numpy as np

matplotlib.use("Agg")  # Save figures without requiring a desktop plot window.
import matplotlib.pyplot as plt


# 1. Experiment settings. All random seeds and model assumptions are here.
N = 200
TARGET_MEAN_DEGREE = 8
INITIAL_INFECTED = 10
HORIZON = 84  # days; 6 complete 14-day schedule cycles
BETA = 0.04  # infection probability per active infected-susceptible edge per day
GAMMA = 0.20  # recovery probability per infected person per day

NETWORK_SEED = 2026
GROUP_SEED = 2027
INFECTION_SEED = 2028
SIM_SEED = 2029

DEFAULT_WORLDS = 20
DEFAULT_RUNS_PER_WORLD = 50
SANITY_RUNS = 1000
SCENARIOS = [
    ("full", 1),
    ("on_off", 1),
    ("on_off", 7),
    ("rotating", 1),
    ("rotating", 7),
]


# 2. Construct one random contact network, its two groups, and initial cases.
def make_network(n: int, target_mean_degree: float, seed: int) -> nx.Graph:
    """Create an Erdős-Rényi graph with expected degree target_mean_degree."""
    edge_probability = target_mean_degree / (n - 1)
    return nx.erdos_renyi_graph(n, edge_probability, seed=seed)


def split_groups(n: int, seed: int) -> np.ndarray:
    """Assign exactly half of the people to group 0 and half to group 1."""
    if n % 2 != 0:
        raise ValueError("The population size must be even")

    rng = np.random.default_rng(seed)
    shuffled_ids = rng.permutation(n)
    groups = np.ones(n, dtype=int)
    for person_id in shuffled_ids[: n // 2]:
        groups[person_id] = 0
    return groups


def make_initial_state(n: int, number_infected: int, seed: int) -> np.ndarray:
    """Return a Boolean state array: False = S and True = I."""
    rng = np.random.default_rng(seed)
    infected = np.zeros(n, dtype=bool)
    initial_ids = rng.choice(n, size=number_infected, replace=False)
    infected[initial_ids] = True
    return infected


# 3. Determine attendance and update all SIS states simultaneously each day.
def attendance(
    day: int, groups: np.ndarray, schedule: str, switch_days: int
) -> np.ndarray:
    """Return a Boolean array showing who attends on this calendar day."""
    phase = (day // switch_days) % 2
    if schedule == "full":
        return np.ones(len(groups), dtype=bool)
    if schedule == "on_off":
        return np.full(len(groups), phase == 0, dtype=bool)
    if schedule == "rotating":
        return groups == phase
    raise ValueError(f"Unknown schedule: {schedule}")


def sis_step(
    graph: nx.Graph,
    infected: np.ndarray,
    present: np.ndarray,
    beta: float,
    gamma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Advance one day, reading only start-of-day states for transmission."""
    next_infected = infected.copy()

    for person in graph.nodes:
        if infected[person]:
            # Infected people can recover even when they stay home.
            if rng.random() < gamma:
                next_infected[person] = False
        elif present[person]:
            # A susceptible person can be infected by attending infected neighbors.
            infectious_neighbors = sum(
                infected[neighbor] and present[neighbor]
                for neighbor in graph.neighbors(person)
            )
            infection_probability = 1 - (1 - beta) ** infectious_neighbors
            if rng.random() < infection_probability:
                next_infected[person] = True

    return next_infected


# 4. Run one trajectory for a specified schedule and starting calendar phase.
def run_simulation(
    graph: nx.Graph,
    groups: np.ndarray,
    initial_infected: np.ndarray,
    schedule: str,
    switch_days: int,
    beta: float,
    gamma: float,
    horizon: int,
    seed: int,
    start_day: int = 0,
) -> np.ndarray:
    """Return infected counts for day 0 through day horizon, including fadeout."""
    rng = np.random.default_rng(seed)
    state = initial_infected.copy()
    counts = [int(np.sum(state))]

    for day in range(horizon):
        present = attendance(day + start_day, groups, schedule, switch_days)
        state = sis_step(graph, state, present, beta, gamma, rng)
        counts.append(int(np.sum(state)))

    return np.array(counts)


# 5. Repeat across independent random networks, group splits, and initial cases.
def run_world_experiment(
    number_worlds: int, runs_per_world: int
) -> dict[tuple[str, int], np.ndarray]:
    """Return one (world, run, day) array for each attendance schedule."""
    world_runs = {scenario: [] for scenario in SCENARIOS}

    for world in range(number_worlds):
        graph = make_network(N, TARGET_MEAN_DEGREE, NETWORK_SEED + world)
        groups = split_groups(N, GROUP_SEED + world)
        initial_infected = make_initial_state(
            N, INITIAL_INFECTED, INFECTION_SEED + world
        )

        for scenario_index, (schedule, switch_days) in enumerate(SCENARIOS):
            trajectories = []
            for rep in range(runs_per_world):
                global_rep = world * runs_per_world + rep
                seed = SIM_SEED + 100_000 + global_rep * len(SCENARIOS) + scenario_index
                start_day = global_rep % 14
                counts = run_simulation(
                    graph,
                    groups,
                    initial_infected,
                    schedule,
                    switch_days,
                    BETA,
                    GAMMA,
                    HORIZON,
                    seed,
                    start_day,
                )
                trajectories.append(counts)

            world_runs[(schedule, switch_days)].append(np.stack(trajectories))

        print(f"Completed world {world + 1}/{number_worlds}")

    return {
        scenario: np.stack(world_runs[scenario]) for scenario in SCENARIOS
    }


# 6. Report outcomes and visualize average prevalence across worlds.
def print_results(world_runs: dict[tuple[str, int], np.ndarray]) -> None:
    """Print day-84 fadeout and mean prevalence, including extinct runs."""
    print(f"Horizon: {HORIZON} days; {N} people; beta={BETA}; gamma={GAMMA}")
    for scenario in SCENARIOS:
        paths = world_runs[scenario]
        extinction_fraction = np.mean(paths[:, :, -1] == 0)
        mean_day_84 = np.mean(paths[:, :, -1])
        mean_over_days = np.mean(paths[:, :, 1:])
        print(
            f"{scenario}: shape={paths.shape}, "
            f"extinct by day 84={extinction_fraction:.3f}, "
            f"mean day 84={mean_day_84:.2f}, "
            f"mean days 1-84={mean_over_days:.2f}"
        )


def plot_results(
    world_runs: dict[tuple[str, int], np.ndarray], output_path: Path
) -> None:
    """Plot the mean and a 95% Monte Carlo interval across world means."""
    colors = {
        ("full", 1): "tab:blue",
        ("on_off", 1): "tab:orange",
        ("on_off", 7): "tab:green",
        ("rotating", 1): "tab:red",
        ("rotating", 7): "tab:purple",
    }
    days = np.arange(HORIZON + 1)
    figure, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

    for scenario in SCENARIOS:
        # Average runs within each world before estimating across-world uncertainty.
        world_means = world_runs[scenario].mean(axis=1)
        mean = world_means.mean(axis=0)
        if len(world_means) > 1:
            se = world_means.std(axis=0, ddof=1) / np.sqrt(len(world_means))
        else:
            se = np.zeros_like(mean)

        label = f"{scenario[0]}, {scenario[1]} day"
        for axis in axes if scenario[0] != "full" else axes[:1]:
            axis.plot(days, mean, label=label, color=colors[scenario])
            axis.fill_between(
                days,
                np.maximum(0, mean - 1.96 * se),
                mean + 1.96 * se,
                color=colors[scenario],
                alpha=0.15,
            )

    axes[0].set_title("All attendance schedules")
    axes[1].set_title("50% attendance schedules")
    for axis in axes:
        axis.set_ylabel("Mean number infected")
        axis.legend(fontsize=8)
    axes[1].set_xlabel("Day")
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    print(f"Saved plot: {output_path}")


# 7. Run focused checks for attendance, reinfection, and low/high transmission.
def run_sanity_checks() -> None:
    """Print full-attendance sensitivity and verify two exact model behaviors."""
    graph = make_network(N, TARGET_MEAN_DEGREE, NETWORK_SEED)
    groups = split_groups(N, GROUP_SEED)
    initial_infected = make_initial_state(N, INITIAL_INFECTED, INFECTION_SEED)

    # Every 14-day phase must give exactly 50% attendance for hybrid schedules.
    for start_day in range(14):
        for schedule, switch_days in SCENARIOS:
            person_days = sum(
                np.sum(attendance(day + start_day, groups, schedule, switch_days))
                for day in range(HORIZON)
            )
            expected = N * HORIZON if schedule == "full" else N * HORIZON // 2
            assert person_days == expected
    print("Attendance check passed for all 14 starting phases")

    # With certain infection and recovery, the infection swaps between two people.
    tiny_graph = nx.path_graph(2)
    tiny_present = np.array([True, True])
    state = np.array([True, False])
    rng = np.random.default_rng(0)
    state = sis_step(tiny_graph, state, tiny_present, 1.0, 1.0, rng)
    assert np.array_equal(state, [False, True])
    state = sis_step(tiny_graph, state, tiny_present, 1.0, 1.0, rng)
    assert np.array_equal(state, [True, False])
    print("Reinfection check passed")

    # Full attendance should fade out rapidly with low beta and persist with high beta.
    for beta in (0.001, 0.08):
        paths = np.stack(
            [
                run_simulation(
                    graph,
                    groups,
                    initial_infected,
                    "full",
                    1,
                    beta,
                    GAMMA,
                    HORIZON,
                    SIM_SEED + 10_000 + rep,
                )
                for rep in range(SANITY_RUNS)
            ]
        )
        print(
            f"beta={beta}: extinct by day 28={np.mean(paths[:, 28] == 0):.3f}, "
            f"extinct by day 84={np.mean(paths[:, 84] == 0):.3f}, "
            f"mean infected on day 84={np.mean(paths[:, 84]):.3f}"
        )


# 8. Command-line entry point. Default settings reproduce the reported experiment.
def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sanity", action="store_true", help="run model checks")
    parser.add_argument("--worlds", type=int, default=DEFAULT_WORLDS)
    parser.add_argument("--runs-per-world", type=int, default=DEFAULT_RUNS_PER_WORLD)
    args = parser.parse_args()

    if args.sanity:
        run_sanity_checks()
        return
    if args.worlds < 1 or args.runs_per_world < 1:
        parser.error("--worlds and --runs-per-world must be positive")

    world_runs = run_world_experiment(args.worlds, args.runs_per_world)
    print_results(world_runs)
    plot_results(world_runs, Path("sis_mean_multiworld.png"))


if __name__ == "__main__":
    main()
