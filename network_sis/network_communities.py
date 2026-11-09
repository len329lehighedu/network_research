# Build a network with communities, for example 8 communities of 25 people with most edges inside them. 
# Compare three ways to form the two Rotating groups: keep each community together, split people at random, 
# and split each community evenly between the groups. 
# For each split, add an On-Off control with the same number of active contact days, made by removing edges at random.
import networkx as nx
import numpy as np
import argparse
from pathlib import Path
from sis_experiment import (
    make_initial_state,
    INITIAL_INFECTED,
    run_simulation,
    count_active_contact_days,
    HORIZON,
    GAMMA,
    early_growth_threshold,
)


N_COMMUNITIES = 8
COMMUNITY_SIZE = 25
N = N_COMMUNITIES * COMMUNITY_SIZE
P_IN = 0.25
P_OUT = 2 / 175

def make_community_network(seed: int):
    """Return a graph and each person's community ID."""
    rng = np.random.default_rng(seed)
    graph = nx.Graph()
    graph.add_nodes_from(range(N))

    # Person 0–24 in community 0, 25–49 in community 1, ...
    community_ids = np.repeat(
        np.arange(N_COMMUNITIES), COMMUNITY_SIZE
    )

    # Loop through each pair (u,v) with u < v
    for u in range(N):
        for v in range(u+1, N):
            # use P_IN if community_ids[u] == community_ids[v],
            # else use P_OUT.
            if community_ids[u] == community_ids[v]:
                edge_probability = P_IN
            else:
                edge_probability = P_OUT

            # TODO: rng.random() < edge probabiltiy -> graph.add_edge(u, v).
            if rng.random() < edge_probability:
                graph.add_edge(u,v)

    return graph, community_ids


# keep each community together
def split_whole_communities(community_ids, seed: int):
    """Keep each community together in one of two 100-person groups."""
    rng = np.random.default_rng(seed)
    groups = np.ones(len(community_ids), dtype=int)

    # Randomly choose four entire communities for group 0.
    chosen_communities = rng.permutation(N_COMMUNITIES)[:4]

    for community in chosen_communities:
        # Select every person in this community and assign them to group 0.
        groups[community_ids == community] = 0

    return groups

# split people at random
def split_people_randomly(community_ids, seed: int):
    """Randomly assign half of all people to each group."""
    rng = np.random.default_rng(seed)
    number_people = len(community_ids)
    groups = np.ones(number_people, dtype=int)

    # Select half of the person IDs for group 0.
    selected_people = rng.permutation(number_people)[:number_people // 2]
    groups[selected_people] = 0

    return groups

# split each community evenly between the groups
def split_each_community_evenly(community_ids, seed: int):
    """Split each community 12/13 while keeping both groups at 100 people."""
    rng = np.random.default_rng(seed)
    groups = np.ones(len(community_ids), dtype=int)

    # Randomly choose four communities that give 13 members to group 0.
    extra_group_zero = set(rng.permutation(N_COMMUNITIES)[:4])

    for community in range(N_COMMUNITIES):
        # Find the person IDs belonging to this community.
        member_ids = np.flatnonzero(community_ids == community)

        # The other four communities give 12 members to group 0.
        number_group_zero = 13 if community in extra_group_zero else 12

        # Randomly select this community's members for group 0.
        selected_people = rng.permutation(member_ids)[:number_group_zero]
        groups[selected_people] = 0

    return groups

def count_within_group_edges(graph, groups):
    """Count edges connecting two people in the same rotation group."""
    total = 0

    for u, v in graph.edges():
        # A within-group edge can be active when its group attends.
        if groups[u] == groups[v]:
            total += 1

    return total

def make_contact_matched_control_graph(graph, groups, seed: int):
    """Randomly retain enough edges to match Rotating's active contact days."""
    rng = np.random.default_rng(seed)
    edges = list(graph.edges())

    # Each retained On-Off edge and each within-group Rotating edge
    # is active on 42 of the 84 days.
    number_to_keep = count_within_group_edges(graph, groups)
    selected_indices = rng.permutation(len(edges))[:number_to_keep]

    control = nx.Graph()
    control.add_nodes_from(graph.nodes())

    # Preserve every person, including those with no retained edges.
    for index in selected_indices:
        u, v = edges[index]
        control.add_edge(u, v)

    return control

SPLITTERS = {
    "whole": split_whole_communities,
    "random": split_people_randomly,
    "even": split_each_community_evenly,
}

COMMUNITY_SCENARIOS = [
    (split_name, policy, switch_days)
    for split_name in SPLITTERS
    for policy in ("rotating", "control")
    for switch_days in (1, 7)
]

def build_community_world(world_sequence: np.random.SeedSequence):
    """Build one network, three group splits, and their matched controls."""
    streams = world_sequence.spawn(9)

    # Use separate streams for the graph and initial infections.
    graph_seed = int(streams[0].generate_state(1)[0])
    infection_seed = int(streams[1].generate_state(1)[0])

    graph, community_ids = make_community_network(graph_seed)
    initial = make_initial_state(N, INITIAL_INFECTED, infection_seed)

    groups = {}
    controls = {}

    for index, (name, splitter) in enumerate(SPLITTERS.items()):
        # Streams 2–4 belong to the three group splits.
        split_seed = int(streams[index+2].generate_state(1)[0])

        # Streams 5–7 belong to their three matched controls.
        control_seed = int(streams[index+5].generate_state(1)[0])

        groups[name] = splitter(community_ids, split_seed)
        controls[name] = make_contact_matched_control_graph(
            graph, groups[name], control_seed
        )

    # Stream 8 is reserved for epidemic runs on this world.
    simulation_sequence = streams[8]
    return graph, community_ids, initial, groups, controls, simulation_sequence


def run_one_community_world(
    world_sequence: np.random.SeedSequence,
    runs_per_world: int,
    beta: float,
    world_index: int = 0,
):
    """Run every community scenario on one shared network and initial state."""
    graph, _, initial, groups, controls, simulation_sequence = (
        build_community_world(world_sequence)
    )

    # Allocate a separate epidemic stream to every scenario and run.
    run_sequences = simulation_sequence.spawn(len(COMMUNITY_SCENARIOS) * runs_per_world)

    paths = {}
    contact_days = {}

    for scenario_index, scenario in enumerate(COMMUNITY_SCENARIOS):
        split_name, policy, switch_days = scenario

        # Rotating uses the original graph; the control uses its sampled graph.
        active_graph = graph if policy == "rotating" else controls[split_name]
        schedule = "rotating" if policy == "rotating" else "on_off"

        contact_days[scenario] = count_active_contact_days(
            active_graph, groups[split_name], schedule,
            switch_days, HORIZON,
        )

        trajectories = []
        for rep in range(runs_per_world):
            # Keep the phase aligned across policies for the same run number.
            start_day = (world_index * runs_per_world + rep) % 14
            seed = run_sequences[scenario_index * runs_per_world + rep]

            counts = run_simulation(
                active_graph, groups[split_name], initial,
                schedule, switch_days, beta, GAMMA, HORIZON,
                seed, start_day,
            )
            trajectories.append(counts)

        paths[scenario] = np.stack(trajectories)

    return paths, contact_days

def run_community_experiment(
    number_worlds: int,
    runs_per_world: int,
    beta: float,
    verbose: bool = False
):
    """Collect epidemic paths and contact days across independent worlds."""
    world_sequences = np.random.SeedSequence(2026).spawn(number_worlds)

    all_paths = {scenario: [] for scenario in COMMUNITY_SCENARIOS}
    all_contacts = {scenario: [] for scenario in COMMUNITY_SCENARIOS}

    for world_index, world_sequence in enumerate(world_sequences):
        paths, contact_days = run_one_community_world(
            world_sequence, runs_per_world, beta, world_index
        )

        # Keep each world's runs together for later world-level intervals.
        for scenario in COMMUNITY_SCENARIOS:
            all_paths[scenario].append(paths[scenario])
            all_contacts[scenario].append(contact_days[scenario])
            
        if verbose:
            print(f"Completed world {world_index + 1}/{number_worlds}", flush=True)

    # Stack worlds without mixing them with the run axis.
    stacked_paths = {
        scenario: np.stack(all_paths[scenario])
        for scenario in COMMUNITY_SCENARIOS
    }
    stacked_contacts = {
        scenario: np.asarray(all_contacts[scenario])
        for scenario in COMMUNITY_SCENARIOS
    }

    return stacked_paths, stacked_contacts

def summarize_scenario(paths, contact_days):
    """Return prevalence, fadeout, and contact days for each world."""
    # Exclude day 0, then average over runs and days within each world.
    prevalence_by_world = paths[:,:,1:].mean(axis=(1,2))

    # A run has faded out by day 84 when its final count is zero.
    extinction_by_world = np.mean(paths[:, :, -1] == 0, axis=1)

    return {
        "prevalence_by_world": prevalence_by_world,
        "extinction_by_world": extinction_by_world,
        "contact_days_by_world": np.asarray(contact_days),
    }
    
def bootstrap_world_mean_ci(values, draws: int = 10_000):
    """Return a mean and 95% bootstrap interval across worlds."""
    values = np.asarray(values, dtype=float)
    number_worlds = len(values)
    rng = np.random.default_rng(np.random.SeedSequence(4040))

    # Each row is one resample of complete worlds.
    indices = rng.integers(
        0, number_worlds, size=(draws, number_worlds)
    )

    bootstrap_means = values[indices].mean(axis=1)
    lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])

    return float(values.mean()), (float(lower), float(upper))


def paired_world_mean_ci(first_by_world, second_by_world):
    """Bootstrap the mean of first minus second, pairing the same worlds."""
    first = np.asarray(first_by_world, dtype=float)
    second = np.asarray(second_by_world, dtype=float)

    if first.shape != second.shape:
        raise ValueError("Both scenarios must contain the same worlds")

    # Subtract within each world before resampling worlds.
    differences = first - second

    return bootstrap_world_mean_ci(differences)


def summarize_community_results(paths, contacts):
    """Summarize all scenarios using worlds as the uncertainty unit."""
    results = {}

    for scenario in COMMUNITY_SCENARIOS:
        world = summarize_scenario(paths[scenario], contacts[scenario])

        # Bootstrap one infection-count summary per world.
        mean_infected, infected_ci = bootstrap_world_mean_ci(
            world["prevalence_by_world"]
        )

        # Bootstrap one fadeout fraction per world.
        extinction_fraction, extinction_ci = bootstrap_world_mean_ci(
            world["extinction_by_world"]
        )

        results[scenario] = {
            "mean_infected": mean_infected,
            "infected_ci": infected_ci,
            "extinction_fraction": extinction_fraction,
            "extinction_ci": extinction_ci,
            "mean_contact_days": float(
                world["contact_days_by_world"].mean()
            ),
        }

    return results

# 3 classification types × daily/weekly. Within each world:
# Control − Rotating for the average number of cases: a positive value indicates that the Rotating scenario has fewer cases.
# Rotating − Control for the rate of outbreak termination: a positive value indicates that the Rotating scenario terminates outbreaks more frequently.
def summarize_matched_comparisons(paths, contacts):
    """Compare each Rotating schedule with its contact-matched control."""
    comparisons = {}

    for split_name in SPLITTERS:
        for switch_days in (1, 7):
            rotating_key = (split_name, "rotating", switch_days)
            control_key = (split_name, "control", switch_days)

            rotating = summarize_scenario(
                paths[rotating_key], contacts[rotating_key]
            )
            control = summarize_scenario(
                paths[control_key], contacts[control_key]
            )

            # Contact matching must hold separately in every world.
            if not np.array_equal(
                rotating["contact_days_by_world"],
                control["contact_days_by_world"],
            ):
                raise ValueError("Active contact days are not matched")

            infected_difference, infected_ci = paired_world_mean_ci(
            control["prevalence_by_world"], rotating["prevalence_by_world"],
            )
            extinction_difference, extinction_ci = paired_world_mean_ci(
            rotating["extinction_by_world"], control["extinction_by_world"],
            )

            comparisons[(split_name, switch_days)] = {
                "control_minus_rotating_infected": infected_difference,
                "infected_ci": infected_ci,
                "rotating_minus_control_extinction": extinction_difference,
                "extinction_ci": extinction_ci,
            }

    return comparisons

def print_community_scenario_table(results):
    """Print scenario outcomes with 95% world bootstrap intervals."""
    print(
        "| split | policy | switch days | "
        "mean infected, days 1–84 [95% world CI] | "
        "extinct by day 84 [95% world CI] | "
        "mean active contact days |"
    )
    print("|---|---|---:|---:|---:|---:|")

    for split_name, policy, switch_days in COMMUNITY_SCENARIOS:
        row = results[(split_name, policy, switch_days)]
        infected_low, infected_high = row["infected_ci"]
        extinct_low, extinct_high = row["extinction_ci"]

        print(
            f"| {split_name} | {policy} | {switch_days} | "
            f"{row['mean_infected']:.2f} "
            f"[{infected_low:.2f}, {infected_high:.2f}] | "
            f"{row['extinction_fraction']:.3f} "
            f"[{extinct_low:.3f}, {extinct_high:.3f}] | "
            f"{row['mean_contact_days']:.1f} |"
        )
        
def print_community_comparison_table(comparisons):
    """Print paired differences with worlds as the bootstrap unit."""
    print(
        "| split | switch days | "
        "control − rotating: mean infected [95% world CI] | "
        "rotating − control: extinction [95% world CI] |"
    )
    print("|---|---:|---:|---:|")

    for split_name in SPLITTERS:
        for switch_days in (1, 7):
            row = comparisons[(split_name, switch_days)]
            infected_low, infected_high = row["infected_ci"]
            extinct_low, extinct_high = row["extinction_ci"]

            print(
                f"| {split_name} | {switch_days} | "
                f"{row['control_minus_rotating_infected']:.2f} "
                f"[{infected_low:.2f}, {infected_high:.2f}] | "
                f"{row['rotating_minus_control_extinction']:.3f} "
                f"[{extinct_low:.3f}, {extinct_high:.3f}] |"
            )

def community_thresholds_one_world(world_sequence: np.random.SeedSequence):
    """Compute early-growth thresholds for the three matched comparisons."""
    graph, _, _, groups, controls, _ = build_community_world(world_sequence)
    thresholds = {}

    for split_name in SPLITTERS:
        # Cross-group edges are inactive under Rotating.
        thresholds[(split_name, "rotating")] = early_growth_threshold(
            graph, groups[split_name], "rotating", GAMMA
        )

        # The control follows On-Off on its sampled graph.
        thresholds[(split_name, "control")] = early_growth_threshold(
            controls[split_name], groups[split_name], "on_off", GAMMA
        )

    return thresholds

def run_community_threshold_experiment(number_worlds: int):
    """Return one early-growth threshold per world and policy."""
    thresholds = {
        (split_name, policy): []
        for split_name in SPLITTERS
        for policy in ("rotating", "control")
    }

    # Recreate the same seeded worlds used by the epidemic experiment.
    world_sequences = np.random.SeedSequence(2026).spawn(number_worlds)

    for world_sequence in world_sequences:
        world_thresholds = community_thresholds_one_world(world_sequence)

        # Preserve the world axis for confidence intervals.
        for key in thresholds:
            thresholds[key].append(world_thresholds[key])

    return {
        key: np.asarray(values)
        for key, values in thresholds.items()
    }
            
def print_community_threshold_table(thresholds):
    """Report thresholds and paired gaps with 95% world bootstrap intervals."""
    print("| split | policy | mean beta threshold [95% world CI] |")
    print("|---|---|---:|")

    for split_name in SPLITTERS:
        for policy in ("rotating", "control"):
            mean, (low, high) = bootstrap_world_mean_ci(
                thresholds[(split_name, policy)]
            )
            print(
                f"| {split_name} | {policy} | "
                f"{mean:.4f} [{low:.4f}, {high:.4f}] |"
            )

    print("\nMatched threshold gaps (control minus Rotating):")
    print("| split | mean gap [95% world CI] |")
    print("|---|---:|")

    for split_name in SPLITTERS:
        mean, (low, high) = paired_world_mean_ci(
            thresholds[(split_name, "control")],
            thresholds[(split_name, "rotating")],
        )
        print(
            f"| {split_name} | "
            f"{mean:+.4f} [{low:+.4f}, {high:+.4f}] |"
        )

def save_community_data(output_path, paths, contacts, beta: float):
    """Save all trajectories, contact counts, and run settings to an NPZ file."""
    output_path = Path(output_path)
    if output_path.suffix != ".npz":
        raise ValueError("Output path must end in .npz")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    example = paths[COMMUNITY_SCENARIOS[0]]
    payload = {
        "format_version": np.array(1),
        "beta": np.array(beta),
        "gamma": np.array(GAMMA),
        "horizon": np.array(HORIZON),
        "number_people": np.array(N),
        "number_worlds": np.array(example.shape[0]),
        "runs_per_world": np.array(example.shape[1]),
    }

    for scenario in COMMUNITY_SCENARIOS:
        split_name, policy, switch_days = scenario
        label = f"{split_name}_{policy}_{switch_days}"

        # Store the full world/run/day cube and the matching world contact counts.
        payload[f"paths_{label}"] = paths[scenario]
        payload[f"contacts_{label}"] = contacts[scenario]

    np.savez_compressed(output_path, **payload)
    return output_path


def load_community_data(input_path):
    """Load saved trajectories and reject incomplete or incompatible files."""
    metadata_keys = (
        "format_version", "beta", "gamma", "horizon", "number_people",
        "number_worlds", "runs_per_world",
    )
    paths = {}
    contacts = {}

    with np.load(input_path, allow_pickle=False) as archive:
        missing_metadata = set(metadata_keys) - set(archive.files)
        if missing_metadata:
            raise ValueError(f"Missing metadata: {sorted(missing_metadata)}")
        metadata = {key: archive[key].item() for key in metadata_keys}

        if metadata["format_version"] != 1:
            raise ValueError("Unsupported community data format")
        if metadata["horizon"] != HORIZON or metadata["number_people"] != N:
            raise ValueError("Saved population or horizon differs from this model")
        if not np.isclose(metadata["gamma"], GAMMA):
            raise ValueError("Saved recovery probability differs from this model")

        expected_path_shape = (
            metadata["number_worlds"], metadata["runs_per_world"], HORIZON + 1,
        )
        expected_contact_shape = (metadata["number_worlds"],)
        for scenario in COMMUNITY_SCENARIOS:
            split_name, policy, switch_days = scenario
            label = f"{split_name}_{policy}_{switch_days}"
            path_key = f"paths_{label}"
            contact_key = f"contacts_{label}"
            if path_key not in archive or contact_key not in archive:
                raise ValueError(f"Missing saved scenario: {scenario}")

            path_array = archive[path_key]
            contact_array = archive[contact_key]
            if path_array.shape != expected_path_shape:
                raise ValueError(f"Wrong trajectory shape for {scenario}")
            if contact_array.shape != expected_contact_shape:
                raise ValueError(f"Wrong contact shape for {scenario}")
            paths[scenario] = path_array.copy()
            contacts[scenario] = contact_array.copy()

    return paths, contacts, metadata

def main():
    """Run and report the community-network comparison."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--worlds", type=int, default=20)
    parser.add_argument("--runs-per-world", type=int, default=50)
    parser.add_argument("--beta", type=float, default=0.07)
    parser.add_argument(
        "--save-data", type=Path, default=None,
        help="save all epidemic paths and contact counts as an NPZ file",
    )
    args = parser.parse_args()

    if args.worlds < 2 or args.runs_per_world < 1:
        parser.error("Use at least 2 worlds and 1 run per world")
    if not 0 <= args.beta <= 1:
        parser.error("--beta must be between 0 and 1")

    paths, contacts = run_community_experiment(
        args.worlds, args.runs_per_world, args.beta, verbose=True
    )
    if args.save_data is not None:
        saved_path = save_community_data(
            args.save_data, paths, contacts, args.beta
        )
        print(f"Saved data: {saved_path}")
    results = summarize_community_results(paths, contacts)
    comparisons = summarize_matched_comparisons(paths, contacts)

    print(
        f"\nHorizon: {HORIZON} days; beta={args.beta}; "
        f"worlds={args.worlds}; runs/world={args.runs_per_world}"
    )
    print("\nScenario outcomes:")
    print_community_scenario_table(results)
    print("\nContact-matched paired comparisons:")
    print_community_comparison_table(comparisons)


if __name__ == "__main__":
    main()
