"""Compare attendance schedules in a stochastic SIS contact network.

Run ``python network_sis/sis_experiment.py --sanity`` for model checks, then run
``python network_sis/sis_experiment.py`` for the default 20-world experiment.
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
# Eleven values for the professor's requested transmission sweep.
BETA_GRID = [round(0.02 + 0.01 * i, 2) for i in range(11)]
GAMMA = 0.20  # recovery probability per infected person per day

NETWORK_SEED = 2026
GROUP_SEED = 2027
INFECTION_SEED = 2028
SIM_SEED = 2029

DEFAULT_WORLDS = 20
DEFAULT_RUNS_PER_WORLD = 50
DEFAULT_SINGLE_WORLD_RUNS = 1000
SANITY_RUNS = 1000
SCENARIOS = [
    ("full", 1),
    ("on_off", 1),
    ("on_off", 7),
    ("rotating", 1),
    ("rotating", 7),
]
# Figures 1-3 keep the five original scenarios; world experiments add controls.
# These controls keep On-Off attendance while using a graph with half its edges.
CONTROL_SCENARIOS = [
    ("on_off_half", 1),
    ("on_off_half", 7),
]
WORLD_SCENARIOS = SCENARIOS + CONTROL_SCENARIOS


# 2. Construct one random contact network, its two groups, and initial cases.
def make_network(n: int, target_mean_degree: float, seed: int) -> nx.Graph:
    """Create an Erdős-Rényi graph with expected degree target_mean_degree."""
    edge_probability = target_mean_degree / (n - 1)
    return nx.erdos_renyi_graph(n, edge_probability, seed=seed)


def make_half_edge_graph(graph: nx.Graph, seed: int) -> nx.Graph:
    """Keep a random half of the edges while preserving every node."""
    # Sample the edge set once per world; daily and weekly controls share it.
    # Edge-day totals become comparable with Rotating, but the retained
    # network topology is still different from Rotating's within-group edges.
    rng = np.random.default_rng(seed)
    edges = list(graph.edges())
    # An odd edge count cannot be halved exactly, so retain floor(E / 2).
    kept_indices = rng.choice(
        len(edges), size=len(edges) // 2, replace=False
    )

    reduced = nx.Graph()
    # Isolated people must remain in the graph so they can still recover.
    reduced.add_nodes_from(graph.nodes)

    # for each index in kept_indices
    # we get the corresponding edges and add them to reduced.
    for i in kept_indices:
        u, v = edges[i]
        reduced.add_edge(u, v)

    return reduced


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
    # The same phase formula handles one-day and seven-day switching.
    phase = (day // switch_days) % 2
    if schedule == "full":
        return np.ones(len(groups), dtype=bool)
    # on_off_half means schedule on-off with graph only keeps half the number of edges
    if schedule in ("on_off", "on_off_half"):
        return np.full(len(groups), phase == 0, dtype=bool)
    if schedule == "rotating":
        return groups == phase
    raise ValueError(f"Unknown schedule: {schedule}")

#


def count_active_contact_days(
    graph: nx.Graph,
    groups: np.ndarray,
    schedule: str,
    switch_days: int,
    horizon: int,
    start_day: int = 0,
) -> int:
    # One active contact day is one graph edge with both endpoints present.
    # This counts contact opportunities, not transmission events or person-days.
    total = 0

    for day in range(horizon):
        # The starting phase matters within a partial cycle; 84 days contains
        # six complete 14-day cycles, so its total is phase independent.
        present = attendance(day + start_day, groups, schedule, switch_days)
        # Loop through each edge (u,v) in the graph
        for u, v in graph.edges():
            # If present[u] = present[v] = true -> add 1 to total
            if present[u] and present[v]:
                total += 1
    return total


def early_growth_matrix(
    graph: nx.Graph,
    groups: np.ndarray,
    schedule: str,
    switch_days: int,
    beta: float,
    gamma: float,
    day: int,
) -> np.ndarray:
    # Near zero prevalence, new infections are linear in infected neighbors:
    # p_(t+1) ≈ [(1-gamma)I + beta*A_t] p_t.
    present = attendance(day, groups, schedule, switch_days)
    # IDs index the state vector, so adjacency rows must use the same order.
    adjacency = nx.to_numpy_array(
        graph, nodelist=range(len(groups)), dtype=float
    )
    # 1: keep edge (u,v) when present[u] and present[v]
    active_adjacency = adjacency * np.outer(present, present)
    # 2: M_t = (1-gamma)I + beta*A_t
    return (1-gamma)*np.eye(len(groups)) + beta*active_adjacency


def cycle_growth_matrix(
    graph: nx.Graph,
    groups: np.ndarray,
    schedule: str,
    switch_days: int,
    beta: float,
    gamma: float,
    cycle_days: int = 14,
) -> np.ndarray:
    # Start with the identity: before day 0, the state has not changed.
    product = np.eye(len(groups))

    for day in range(cycle_days):
        daily_matrix = early_growth_matrix(
            graph, groups, schedule, switch_days,
            beta, gamma, day,
        )
        # After day d, product = M_d @ ... @ M_1 @ M_0.
        # multiply the new daily matrix to the left of the product
        product = daily_matrix @ product

    return product


def cycle_growth_factor(
    graph: nx.Graph,
    groups: np.ndarray,
    schedule: str,
    switch_days: int,
    beta: float,
    gamma: float,
    cycle_days: int = 14,
) -> float:
    # The spectral radius measures growth of a rare-infection perturbation
    # across the full cycle; it does not equal finite-run extinction risk.
    product = cycle_growth_matrix(
        graph, groups, schedule, switch_days,
        beta, gamma, cycle_days,
    )

    # get all eigenvalues of the product matrix
    eigenvalues = np.linalg.eigvals(product)
    # return the maximum absolute value
    return float(np.max(np.abs(eigenvalues)))


def largest_adjacency_eigenvalue(
    graph: nx.Graph, nodes
) -> float:
    # Passing only group IDs extracts that group's induced adjacency matrix;
    # edges to people outside the supplied group are omitted.
    adjacency = nx.to_numpy_array(
        graph, nodelist=list(nodes), dtype=float
    )

    # For an undirected graph the matrix is symmetric; eigvalsh returns
    # real eigenvalues in ascending order, so [-1] is lambda_max.
    # get all the eigenvalues
    eigenvalues = np.linalg.eigvalsh(adjacency)

    # return the largest eigenvalue
    return float(eigenvalues[-1])

# Early growth for Full Attendance


def early_growth_threshold(
    graph: nx.Graph,
    groups: np.ndarray,
    schedule: str,
    gamma: float,
) -> float:
    # Full attendance: g_14 = (1-gamma + beta*lambda_max)^14.
    # Setting g_14 = 1 gives beta_c = gamma / lambda_max.
    if schedule == "full":
        largest = largest_adjacency_eigenvalue(graph, graph.nodes)
        if largest == 0:
            return float("inf")  # no edges to get
        return gamma / largest
    # On-Off has seven on days and seven off days per 14-day cycle. Its
    # matrices commute, so daily and weekly have the same early-growth root.
    # For on_off_half, graph is the already-thinned graph from this world.
    if schedule in ("on_off", "on_off_half"):
        largest = largest_adjacency_eigenvalue(graph, graph.nodes)
        if largest == 0:
            return float("inf")

        survival = 1 - gamma
        # Solve [survival*(survival + beta*lambda_max)]^7 = 1.
        return (1 / survival - survival) / largest
    # Rotating removes every cross-group workplace edge. Each group has seven
    # on and seven off days, and the faster-growing group sets the threshold.
    if schedule == "rotating":
        # for the rotating schedule, the two groups never interact with eachh other
        # we find the largest eigenvalue of each group, then use the larger one
        group_0_nodes = np.flatnonzero(groups == 0)
        group_1_nodes = np.flatnonzero(groups == 1)

        largest_0 = largest_adjacency_eigenvalue(graph, group_0_nodes)
        largest_1 = largest_adjacency_eigenvalue(graph, group_1_nodes)
        largest = max(largest_0, largest_1)

        if largest == 0:
            return float("inf")

        survival = 1 - gamma
        # The root has the same form as On-Off, using the larger group lambda.
        return (1 / survival - survival) / largest

    raise NotImplementedError(schedule)


def run_threshold_experiment(number_worlds: int) -> dict:
    # Retain one deterministic threshold per world and scenario. No epidemic
    # trajectories are simulated here; only graph eigenvalues are needed.
    thresholds = {scenario: [] for scenario in WORLD_SCENARIOS}

    # Recreate exactly the graph and group streams used by the beta sweep.
    root_sequence = np.random.SeedSequence(2026)
    world_sequences = root_sequence.spawn(number_worlds)

    for world in range(number_worlds):
        (
            network_sequence,
            group_sequence,
            _infection_sequence,
            _simulation_sequence,
            edge_sequence,
        ) = world_sequences[world].spawn(5)

        # The infection and simulation children occupy their original slots;
        # skipping them without changing spawn order preserves the same world.
        network_seed = int(network_sequence.generate_state(1)[0])
        group_seed = int(group_sequence.generate_state(1)[0])
        edge_seed = int(edge_sequence.generate_state(1)[0])

        graph = make_network(N, TARGET_MEAN_DEGREE, network_seed)
        groups = split_groups(N, group_seed)
        half_graph = make_half_edge_graph(graph, edge_seed)

        # Switching frequency does not change the linearized 14-day threshold,
        # so compute four unique graph/schedule combinations per world.
        # Compute and save threshold
        threshold_by_schedule = {
            "full": early_growth_threshold(graph, groups, "full", GAMMA),
            "on_off": early_growth_threshold(graph, groups, "on_off", GAMMA),
            "rotating": early_growth_threshold(graph, groups, "rotating", GAMMA),
            "on_off_half": early_growth_threshold(
                half_graph, groups, "on_off_half", GAMMA
            ),
        }

        # Copy each value into its daily and weekly scenario rows.
        for schedule, switch_days in WORLD_SCENARIOS:
            thresholds[(schedule, switch_days)].append(
                threshold_by_schedule[schedule]
            )

    return {
        scenario: np.array(thresholds[scenario])
        for scenario in WORLD_SCENARIOS
    }


def print_threshold_table(thresholds: dict) -> None:
    # Resample whole worlds: graph and group variation is the uncertainty unit.
    number_worlds = len(thresholds[WORLD_SCENARIOS[0]])
    rng = np.random.default_rng(
        np.random.SeedSequence(2026, spawn_key=(6, 0))
    )
    bootstrap_indices = rng.integers(
        0, number_worlds, size=(10_000, number_worlds)
    )

    print("| schedule | mean beta threshold | 95% world CI |")
    print("|---|---:|---:|")

    for scenario in WORLD_SCENARIOS:
        values = thresholds[scenario]  # one threshold for each world
        # The reported threshold is the mean of world-specific beta_c values.
        mean_threshold = values.mean()

        # Use the same resampled world indices for every scenario row.
        # Get worlds and compute mean for each
        bootstrap_means = values[bootstrap_indices].mean(axis=1)
        # 95% CI
        lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])

        print(
            f"| {scenario[0]}, {scenario[1]} day | "
            f"{mean_threshold:.4f} | [{lower:.4f}, {upper:.4f}] |"
        )

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
    seed: int | np.random.SeedSequence,
    start_day: int = 0,
) -> np.ndarray:
    """Return infected counts for day 0 through day horizon, including fadeout."""
    # default_rng accepts either an integer or a spawned SeedSequence; a new
    # child per run gives that trajectory its own transmission/recovery draws.
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
    number_worlds: int, runs_per_world: int, beta: float, verbose: bool = True
) -> tuple[dict[tuple[str, int], np.ndarray],
           dict[tuple[str, int], np.ndarray]]:
    """Return epidemic paths and active contact days for each schedule."""
    # Each key will contain one trajectory array and one contact count per world.
    world_runs = {scenario: [] for scenario in WORLD_SCENARIOS}
    contact_days = {scenario: [] for scenario in WORLD_SCENARIOS}
    # Change seeds supply mechanism
    root_sequence = np.random.SeedSequence(2026)
    world_sequences = root_sequence.spawn(number_worlds)

    for world in range(number_worlds):
        # Give the network, group split, initial cases, epidemic draws, and
        # edge-thinning control separate children of this world's seed.
        network_sequence, group_sequence, infection_sequence, simulation_sequence, edge_sequence = (
            world_sequences[world].spawn(5)
        )
        network_seed = int(network_sequence.generate_state(1)[0])
        group_seed = int(group_sequence.generate_state(1)[0])
        infection_seed = int(infection_sequence.generate_state(1)[0])
        simulation_sequences = simulation_sequence.spawn(
            len(WORLD_SCENARIOS) * runs_per_world)
        edge_seed = int(edge_sequence.generate_state(1)[0])

        graph = make_network(N, TARGET_MEAN_DEGREE, network_seed)
        half_graph = make_half_edge_graph(graph, edge_seed)
        groups = split_groups(N, group_seed)
        initial_infected = make_initial_state(
            N, INITIAL_INFECTED, infection_seed
        )

        for scenario_index, (schedule, switch_days) in enumerate(WORLD_SCENARIOS):
            # All schedules share the original world; only the half-edge
            # controls transmit on the permanently thinned graph.
            active_graph = half_graph if schedule == "on_off_half" else graph
            # Count edge-days once per world/schedule, not once per epidemic run.
            contacts = count_active_contact_days(
                active_graph, groups, schedule, switch_days, HORIZON
            )
            contact_days[(schedule, switch_days)].append(contacts)
            trajectories = []
            for rep in range(runs_per_world):
                global_rep = world * runs_per_world + rep
                # Independent children within a world avoid accidental reuse
                # across schedules; the same indexing is reused across betas.
                seed = simulation_sequences[scenario_index *
                                            runs_per_world + rep]
                # Vary phase relative to the introduced infections across runs.
                start_day = global_rep % 14
                counts = run_simulation(
                    active_graph,
                    groups,
                    initial_infected,
                    schedule,
                    switch_days,
                    beta,
                    GAMMA,
                    HORIZON,
                    seed,
                    start_day,
                )
                trajectories.append(counts)

            world_runs[(schedule, switch_days)].append(np.stack(trajectories))

        if verbose:
            print(f"Completed world {world + 1}/{number_worlds}")

    # A path array has axes (world, run, day); contacts have axis (world,).
    paths = {
        scenario: np.stack(world_runs[scenario]) for scenario in WORLD_SCENARIOS
    }
    contacts = {
        scenario: np.array(contact_days[scenario]) for scenario in WORLD_SCENARIOS
    }
    return paths, contacts

# run beta sweep from 0.02 to 0.12


def run_beta_sweep(number_worlds: int, runs_per_world: int) -> dict:
    # Each call rebuilds the same seeded worlds and epidemic streams. Only
    # beta changes, making cross-beta comparisons paired by construction.
    summary = {}

    for beta in BETA_GRID:
        world_runs, _ = run_world_experiment(
            number_worlds, runs_per_world, beta, verbose=False
        )

        for scenario in WORLD_SCENARIOS:
            paths = world_runs[scenario]

            # Keep one summary per world rather than every trajectory from
            # every beta; this also preserves worlds as the bootstrap units.
            # 1: mean infected through days 1–84, one for each world
            prevalence_by_world = paths[:, :, 1:].mean(axis=(1, 2))

            # 2 extinction by day 84, one for each world
            extinction_by_world = np.mean(paths[:, :, -1] == 0, axis=1)

            summary[(beta, scenario)] = {
                "prevalence_by_world": prevalence_by_world,
                "extinction_by_world": extinction_by_world,
            }

        print(f"Completed beta={beta:.2f}")

    return summary

# print beta sweep function


def print_beta_sweep(summary: dict) -> None:
    # Print Markdown so the 11 beta values and seven scenarios can be copied
    # directly into the report without transcribing numbers by hand.
    print(
        "| beta | schedule | mean infected, days 1–84 [95% world CI] | extinct by day 84 [95% world CI] |")
    print("|---:|---|---:|---:|")

    # 95% CI for mean prevalence in the sweep table
    number_worlds = len(
        summary[(BETA_GRID[0], WORLD_SCENARIOS[0])]["prevalence_by_world"])
    rng = np.random.default_rng(np.random.SeedSequence(2026, spawn_key=(5, 0)))
    # A single index matrix keeps world resampling aligned across all rows.
    bootstrap_indices = rng.integers(
        0, number_worlds, size=(10_000, number_worlds))

    for beta in BETA_GRID:
        for scenario in WORLD_SCENARIOS:
            row = summary[(beta, scenario)]

            # Mean prevalence includes zeros after extinction and excludes day 0.
            # mean, bootstrap, and 95% CIs
            mean_prevalence = np.mean(row["prevalence_by_world"])
            prevalence_by_world = row["prevalence_by_world"]
            bootstrap_means = prevalence_by_world[bootstrap_indices].mean(
                axis=1)
            lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])

            # A world's extinction value is its fraction of runs at zero on
            # day 84; bootstrap those world fractions, not individual runs.
            # mean, bootstrap, and 95% CIs
            extinction_fraction = np.mean(row["extinction_by_world"])
            extinction_by_world = row["extinction_by_world"]
            bootstrap_extinction = extinction_by_world[bootstrap_indices].mean(
                axis=1)
            ext_lower, ext_upper = np.quantile(
                bootstrap_extinction, [0.025, 0.975]
            )

            label = f"{scenario[0]}, {scenario[1]} day"
            print(
                f"| {beta:.2f} | {label} | "
                f"{mean_prevalence:.2f} [{lower:.2f}, {upper:.2f}] | {extinction_fraction:.3f} [{ext_lower:.3f}, {ext_upper:.3f}] |"
            )

# Plot the beta sweep
def plot_beta_sweep(summary: dict, output_path: Path) -> None:
    # Three scales reveal the overall trend, all 50% schedules, and the
    # focused Rotating versus half-edge On-Off comparison.
    figure, axes = plt.subplots(3, 1, figsize=(9, 11), sharex=True)

    for scenario in WORLD_SCENARIOS:
        # Every point is the mean of the world-level prevalence summaries.
        mean_by_beta = [
            summary[(beta, scenario)]["prevalence_by_world"].mean()
            for beta in BETA_GRID
        ]
        label = f"{scenario[0]}, {scenario[1]} day"

        # Reuse the first panel's color for a schedule in the other panels.
        line, = axes[0].plot(BETA_GRID, mean_by_beta, marker="o", label=label)
        if scenario[0] != "full":
            axes[1].plot(
                BETA_GRID, mean_by_beta, marker="o",
                color=line.get_color(), label=label,
            )
        if scenario[0] in ("rotating", "on_off_half"):
            axes[2].plot(
                BETA_GRID, mean_by_beta, marker="o",
                color=line.get_color(), label=label,
            )

    axes[0].set_title("All attendance schedules")
    axes[1].set_title("50% attendance schedules")
    axes[2].set_title("Rotating vs On-Off with half the edges")
    for axis in axes:
        axis.set_ylabel("Mean infected, days 1–84")
        axis.legend(fontsize=8)
    axes[2].set_xlabel("Transmission probability β")

    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    print(f"Saved sweep plot: {output_path}")


def make_figure_world() -> tuple[nx.Graph, np.ndarray, np.ndarray, np.random.SeedSequence]:
    """Build one shared world for Figures 1-3 with independent random streams."""
    # Keep the network, group split, and initial infections fixed across the
    # three historical figures so only run count and phase treatment change.
    root = np.random.SeedSequence(2026, spawn_key=(1,))
    network_sequence, group_sequence, infection_sequence, simulation_sequence = (
        root.spawn(4)
    )
    graph = make_network(N, TARGET_MEAN_DEGREE, int(
        network_sequence.generate_state(1)[0]))
    groups = split_groups(N, int(group_sequence.generate_state(1)[0]))
    initial_infected = make_initial_state(
        N, INITIAL_INFECTED, int(infection_sequence.generate_state(1)[0])
    )
    return graph, groups, initial_infected, simulation_sequence


def run_figure_experiment(
    runs: int, varied_phase: bool
) -> dict[tuple[str, int], np.ndarray]:
    """Run each schedule on one world, at phase zero or across 14 phases."""
    graph, groups, initial_infected, simulation_sequence = make_figure_world()
    # The single run is the first fixed-phase path. The varied-phase figure
    # uses another simulation child on the same fixed network and cases.
    # Use a separate child for each figure mode, then each schedule and run.
    mode_sequence = simulation_sequence.spawn(3)[2 if varied_phase else 1]
    run_sequences = mode_sequence.spawn(len(SCENARIOS) * runs)
    results = {}
    for scenario_index, (schedule, switch_days) in enumerate(SCENARIOS):
        trajectories = []
        for rep in range(runs):
            seed = run_sequences[scenario_index * runs + rep]
            # The fixed version aligns every outbreak with phase zero; the
            # varied version spreads introduction across all 14 phases.
            start_day = rep % 14 if varied_phase else 0
            trajectories.append(
                run_simulation(
                    graph, groups, initial_infected, schedule, switch_days,
                    BETA, GAMMA, HORIZON, seed, start_day,
                )
            )
        results[(schedule, switch_days)] = np.stack(trajectories)
    return results


def print_figure_results(
    results: dict[tuple[str, int], np.ndarray], varied_phase: bool
) -> None:
    """Report prevalence and extinction for a single fixed network."""
    # These figures condition on one world, unlike the 20-world experiment.
    phase_label = "varied start phase" if varied_phase else "fixed start phase"
    print(f"One-world experiment: {phase_label}; horizon={HORIZON} days")
    for scenario in SCENARIOS:
        paths = results[scenario]
        print(
            f"{scenario}: runs={len(paths)}, "
            f"extinct by day {HORIZON}={np.mean(paths[:, -1] == 0):.3f}, "
            f"mean day {HORIZON}={paths[:, -1].mean():.2f}, "
            f"mean days 1-{HORIZON}={paths[:, 1:].mean():.2f}"
        )


def print_figure_weekly_daily_intervals(
    results: dict[tuple[str, int], np.ndarray]
) -> None:
    """Print paired run-level 95% intervals conditional on the fixed world."""
    for schedule in ("on_off", "rotating"):
        # Collapse each 84-day path to one prevalence summary per run.
        weekly = results[(schedule, 7)][:, 1:].mean(axis=1)
        daily = results[(schedule, 1)][:, 1:].mean(axis=1)
        # Subtract matching run positions before estimating uncertainty.
        differences = weekly - daily
        estimate = differences.mean()
        if len(differences) > 1:
            # This normal-approximation interval describes run variation on
            # the fixed world; it is not the multiworld bootstrap interval.
            margin = 1.96 * differences.std(ddof=1) / np.sqrt(len(differences))
            interval = f"[{estimate - margin:.3f}, {estimate + margin:.3f}]"
        else:
            interval = "unavailable with one run"
        print(
            f"{schedule} weekly minus daily: {estimate:.3f}; 95% run-level interval: {interval}")


def plot_figure_experiment(
    results: dict[tuple[str, int], np.ndarray], output_path: Path
) -> None:
    """Plot one trajectory or the mean and run-level interval on one world."""
    figure, axis = plt.subplots()
    days = np.arange(HORIZON + 1)
    # A single trajectory has no sampling interval; multi-run means do.
    single_run = len(next(iter(results.values()))) == 1
    for scenario in SCENARIOS:
        paths = results[scenario]
        mean = paths.mean(axis=0)
        line, = axis.plot(
            days, mean, label=f"{scenario[0]}, {scenario[1]} day")
        if not single_run:
            # The band reflects Monte Carlo uncertainty across runs on this
            # one fixed graph, not variation across random networks.
            se = paths.std(axis=0, ddof=1) / np.sqrt(len(paths))
            axis.fill_between(
                days, np.maximum(0, mean - 1.96 * se), mean + 1.96 * se,
                color=line.get_color(), alpha=0.15,
            )
    axis.set_xlabel("Day")
    axis.set_ylabel(
        "Number infected" if single_run else "Mean number infected")
    axis.set_title(
        "SIS: one stochastic run" if single_run else f"SIS: mean across {len(paths):,} runs"
    )
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    print(f"Saved plot: {output_path}")


# 6. Report outcomes and visualize average prevalence across worlds.
def print_results(
    world_runs: dict[tuple[str, int], np.ndarray],
    contact_days: dict[tuple[str, int], np.ndarray],
    beta: float
) -> None:
    """Print day-84 fadeout and mean prevalence, including extinct runs."""
    print(f"Horizon: {HORIZON} days; {N} people; beta={beta}; gamma={GAMMA}")

    # The same resampled world indices are used for every schedule's CI.
    # bootstrap: let's say we have 20 worlds, we choose 20 worlds multiple times.
    # each time calculate the mean of the 20 values chose, then calculate 95% CI
    number_worlds = len(world_runs[WORLD_SCENARIOS[0]])
    bootstrap_rng = np.random.default_rng(
        np.random.SeedSequence(2026, spawn_key=(2,))
    )
    bootstrap_indices = bootstrap_rng.integers(
        0, number_worlds, size=(10_000, number_worlds)
    )
    for scenario in WORLD_SCENARIOS:
        paths = world_runs[scenario]
        # Average runs and days inside each world before resampling worlds.
        mean_by_world = paths[:, :, 1:].mean(axis=(1, 2))
        bootstrap_means = mean_by_world[bootstrap_indices].mean(axis=1)
        lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])
        # Contact days count active graph edges over all 84 days; they are not
        # person-days or infection events.
        mean_active_contacts = np.mean(contact_days[scenario])
        extinction_fraction = np.mean(paths[:, :, -1] == 0)
        mean_day_84 = np.mean(paths[:, :, -1])
        mean_over_days = np.mean(paths[:, :, 1:])
        print(
            f"{scenario}: shape={paths.shape}, "
            f"extinct by day 84={extinction_fraction:.3f}, "
            f"mean day 84={mean_day_84:.2f}, "
            f"mean days 1-84={mean_over_days:.2f}, "
            f"95% world CI=[{lower:.2f}, {upper:.2f}], "
            f"mean active contact days={mean_active_contacts:.1f}"
        )


def print_world_comparisons(
    world_runs: dict[tuple[str, int], np.ndarray]
) -> None:
    """Print paired 95% bootstrap intervals using worlds as the units."""
    # The control comparisons test how much of Rotating's advantage remains
    # when On-Off is assigned roughly the same number of active edge-days.
    comparisons = [
        (("on_off", 7), ("on_off", 1)),
        (("rotating", 7), ("rotating", 1)),
        (("on_off", 1), ("rotating", 1)),
        (("on_off", 7), ("rotating", 7)),
        (("on_off_half", 1), ("rotating", 1)),
        (("on_off_half", 7), ("rotating", 7)),
    ]
    number_worlds = len(world_runs[WORLD_SCENARIOS[0]])
    if number_worlds < 2:
        print("At least two worlds are needed for comparison intervals")
        return

    bootstrap_rng = np.random.default_rng(3030)
    bootstrap_indices = bootstrap_rng.integers(
        0, number_worlds, size=(10_000, number_worlds)
    )
    print("Mean prevalence differences (first minus second), 95% world bootstrap CI")
    for first, second in comparisons:
        # Pair the same world under both policies before bootstrap resampling.
        first_by_world = world_runs[first][:, :, 1:].mean(axis=(1, 2))
        second_by_world = world_runs[second][:, :, 1:].mean(axis=(1, 2))
        differences = first_by_world - second_by_world
        bootstrap_means = differences[bootstrap_indices].mean(axis=1)
        lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])
        print(
            f"{first} - {second}: {differences.mean():.3f} "
            f"[{lower:.3f}, {upper:.3f}]"
        )


def plot_results(
    world_runs: dict[tuple[str, int], np.ndarray], output_path: Path
) -> None:
    """Plot the mean and a 95% Monte Carlo interval across world means."""
    # The lower panel removes Full attendance so six 50% schedules are visible.
    colors = {
        ("full", 1): "tab:blue",
        ("on_off", 1): "tab:orange",
        ("on_off", 7): "tab:green",
        ("on_off_half", 1): "tab:brown",
        ("on_off_half", 7): "tab:pink",
        ("rotating", 1): "tab:red",
        ("rotating", 7): "tab:purple",
    }
    days = np.arange(HORIZON + 1)
    figure, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

    for scenario in WORLD_SCENARIOS:
        # Take means within worlds first: multiple epidemic runs from one
        # graph are not independent graph samples.
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
    # Select one reproducible report mode; the default runs the 20-world
    # comparison, while --sweep and --thresholds have dedicated branches.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sanity", action="store_true",
                        help="run model checks")
    parser.add_argument(
        "--figure", choices=("single", "fixed-phase", "varied-phase", "multiworld"),
        default="multiworld", help="which reported figure to reproduce",
    )
    parser.add_argument("--figure-runs", type=int,
                        default=DEFAULT_SINGLE_WORLD_RUNS)
    parser.add_argument("--worlds", type=int, default=DEFAULT_WORLDS)
    parser.add_argument("--runs-per-world", type=int,
                        default=DEFAULT_RUNS_PER_WORLD)
    parser.add_argument(
        "--plot-path", type=Path, default=None,
        help="override the default PNG filename for the selected figure",
    )
    parser.add_argument("--beta", type=float, default=BETA,
                        help="transmission probability for the multiworld experiment",)
    parser.add_argument(
        "--sweep", action="store_true",
        help="run all beta values in BETA_GRID",
    )
    parser.add_argument(
        "--thresholds", action="store_true",
        help="compute 14-day early-growth thresholds across worlds",
    )

    args = parser.parse_args()

    # Reject combinations whose beta or figure options would be ignored.
    if args.thresholds and (
        args.sweep or args.sanity
        or args.figure != "multiworld" or args.beta != BETA
    ):
        parser.error("--thresholds runs alone; use --worlds to choose world count")

    if args.sweep and (
        args.sanity or args.figure != "multiworld" or args.beta != BETA
    ):
        parser.error(
            "--sweep uses BETA_GRID; do not combine it with "
            "--sanity, another --figure, or a single --beta"
        )
    if not 0 <= args.beta <= 1:
        parser.error("--beta must be between 0 and 1")
    if args.figure != "multiworld" and args.beta != BETA:
        parser.error(
            "--beta currently applies only to the multiworld experiment")

    if args.sanity:
        run_sanity_checks()
        return
    if args.worlds < 1 or args.runs_per_world < 1 or args.figure_runs < 1:
        parser.error(
            "--worlds, --runs-per-world and --figure-runs must be positive")

    if args.thresholds:
        # Thresholds use graph eigenvalues only, so this mode is inexpensive.
        thresholds = run_threshold_experiment(args.worlds)
        print_threshold_table(thresholds)
        return
    if args.sweep:
        # Reuse the same number of worlds in the epidemic and threshold tables.
        summary = run_beta_sweep(args.worlds, args.runs_per_world)
        print_beta_sweep(summary)
        thresholds = run_threshold_experiment(args.worlds)
        print_threshold_table(thresholds)
        plot_beta_sweep(summary, args.plot_path or Path("graphs/reproduced_sis_beta_sweep.png"))
        return

    if args.figure != "multiworld":
        # Figures 1-3 retain the five original schedules on one fixed world.
        varied_phase = args.figure == "varied-phase"
        runs = 1 if args.figure == "single" else args.figure_runs
        default_names = {
            "single": "graphs/reproduced_sis_single_run.png",
            "fixed-phase": "graphs/reproduced_sis_mean_1000_runs.png",
            "varied-phase": "graphs/reproduced_sis_mean_1000_runs_startdate.png",
        }
        results = run_figure_experiment(runs, varied_phase)
        print_figure_results(results, varied_phase)
        if runs > 1:
            print_figure_weekly_daily_intervals(results)
        plot_figure_experiment(
            results, args.plot_path or Path(default_names[args.figure]))
        return

    world_runs, contact_days = run_world_experiment(
        args.worlds, args.runs_per_world, args.beta, verbose=False)
    # Print the seven-schedule table and paired comparisons before saving plot.
    print_results(world_runs, contact_days, args.beta)
    print_world_comparisons(world_runs)
    plot_results(world_runs, args.plot_path or Path("graphs/reproduced_sis_mean_multiworld.png"))


if __name__ == "__main__":
    main()
