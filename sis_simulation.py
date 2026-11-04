# a small SIS network simulation, one step at a time

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# The contact network
N = 200
TARGET_MEAN_DEGREE = 8
NETWORK_SEED = 2026
# Randomly split into 2 groups
GROUP_SEED = 2027
HORIZON = 84
# Create an initial infected state
# Each person will have a state: False: susceptible (S), True: infected (I)
INITIAL_INFECTED = 10 # starting with 10 people infected for every schedule
INFECTION_SEED = 2028
# full 84 days simulation
BETA = 0.04
GAMMA = 0.20
SIM_SEED = 2029

N_RUNS = 1000 

# 20 worlds x 50 runs x 5 schedules
N_WORLDS = 20
RUNS_PER_WORLD = 50


# Create a simple random network
def make_network(n: int, target_mean_degree: float, seed: int) -> nx.Graph:
    """Return an Erdős–Rényi graph with approximately the target mean degree."""
    # 1a: Compute edge probability p from E[degree] = (n - 1) * p.
    p = target_mean_degree/(n-1)
    # 1b: Create and return the graph with nx.erdos_renyi_graph(...).
    graph = nx.erdos_renyi_graph(n,p,seed=seed)
    return graph


def describe_network(graph: nx.Graph) -> None:
    """Print basic checks for the network you created."""
    # TODO 1c: Print the number of nodes and edges.
    print("Number of nodes: ",graph.number_of_nodes(),"; Number of edges: ", graph.number_of_edges())
    # TODO 1d: Compute and print the actual mean degree (=2*number of edges)
    actual_mean_degree = 2 * graph.number_of_edges() / graph.number_of_nodes()
    print("Actual mean degree: ",actual_mean_degree)


def split_groups(n: int, seed: int) -> np.ndarray:
    """Return an array of length n: 0 = group A, 1 = group B."""
    assert n % 2 == 0
    rng = np.random.default_rng(seed)
    # permutate the IDs from 0 to n-1 using rng.permutation(...)
    shuffled_id = rng.permutation(n)
    # create a group array with n elements
    groups = np.ones(n, dtype=int)
    # set all IDs to 1, then set the first half to 0
    for person_id in shuffled_id[:n//2]:
        groups[person_id] = 0 
    # return group
    return groups

# Attendance function: return a true/false array with length = n
def attendance(day: int, groups: np.ndarray,
               schedule: str, switch_days: int) -> np.ndarray:
    phase = (day // switch_days) % 2
    if schedule == "full":
        # return an array with all true
        return np.ones(len(groups), dtype=bool)
    if schedule == "on_off":
        # TODO: phase 0 -> all True; phase 1 -> all False
        return np.full(len(groups), phase == 0, dtype=bool)
    if schedule == "rotating":
        # TODO: phase 0 -> only group 0 attend;
        #       phase 1 -> only group 1 attend
        return groups == phase
    raise ValueError(f"Unknown schedule: {schedule}")


# Update 1-day SIS
# let beta = 0.04 = the probability tranmiss through an edge in 1 day. 
# let gamma = 0.20 = probability an infected person recover in 1 day.
def sis_step(graph, infected, present, beta, gamma, rng):
    next_infected = infected.copy()

    for person in graph.nodes:
        if infected[person]:
            # Infected person can recover, even when at home
            if rng.random() < gamma:
                next_infected[person] = False

        elif present[person]:
            # Person S can only be infected by people who attend
            k = sum(
                infected[neighbor] and present[neighbor]
                for neighbor in graph.neighbors(person)
            )
            infection_probability = 1 - (1 - beta) ** k

            if rng.random() < infection_probability:
                next_infected[person] = True

    return next_infected


def run_simulation(graph, groups, initial_infected,
                   schedule, switch_days, beta, gamma, horizon, seed, start_day = 0):
    rng = np.random.default_rng(seed)
    state = initial_infected.copy()
    counts = [int(np.sum(state))]  # day 0, before update

    for day in range(horizon):
        present = attendance(day + start_day, groups, schedule, switch_days)
        state = sis_step(graph, state, present, beta, gamma, rng)
        counts.append(int(np.sum(state)))

    return np.array(counts)


def main() -> None:
    graph = make_network(N, TARGET_MEAN_DEGREE, NETWORK_SEED)
    groups = split_groups(N, GROUP_SEED)

    rng = np.random.default_rng(INFECTION_SEED)
    infected = np.zeros(N, dtype=bool)
    initial_ids = rng.choice(N, size=INITIAL_INFECTED, replace=False)
    infected[initial_ids] = True

    assert np.sum(groups == 0) == N // 2
    assert np.sum(groups == 1) == N // 2
    assert np.sum(infected) == INITIAL_INFECTED
    
    
    scenarios = [
    ("full", 1),
    ("on_off", 1),
    ("on_off", 7),
    ("rotating", 1),
    ("rotating", 7),
    ]

    # print("\n Test full simulation")
    # results = {}

    # for schedule, switch_days in scenarios:
    #     counts = run_simulation(
    #         graph, groups, infected,
    #         schedule, switch_days,
    #         BETA, GAMMA, HORIZON, SIM_SEED
    #     )
    #     results[(schedule, switch_days)] = counts

    #     zero_days = np.flatnonzero(counts == 0)
    #     extinct_day = int(zero_days[0]) if len(zero_days) > 0 else None

    #     print(schedule, switch_days,
    #         "day 84:", counts[-1],
    #         "peak:", np.max(counts),
    #         "extinct day:", extinct_day)
        
        
    # # plotting
    # fig, ax = plt.subplots()

    # for (schedule, switch_days), counts in results.items():
    #     ax.plot(range(HORIZON + 1), counts,
    #             label=f"{schedule}, {switch_days} day")

    # ax.set_xlabel("Day")
    # ax.set_ylabel("Number infected")
    # ax.set_title("SIS: one stochastic run")
    # ax.legend()
    # fig.tight_layout()
    # fig.savefig("sis_single_run.png", dpi=160)
    # plt.close(fig)
    
    # print("\n Test 1000 runs for each schedule")
    # all_runs = {}
    
    # for scenario_index, (schedule, switch_days) in enumerate(scenarios):
    #     trajectories = []

    #     for rep in range(N_RUNS):
    #         seed = SIM_SEED + 1 + scenario_index * N_RUNS + rep
    #         start_day = rep % 14
    #         counts = run_simulation(
    #             graph, groups, infected,
    #             schedule, switch_days,
    #             BETA, GAMMA, HORIZON, seed, start_day
    #         )
    #         trajectories.append(counts)

    #     paths = np.stack(trajectories)
    #     all_runs[(schedule, switch_days)] = paths

    #     extinct_fraction = np.mean(paths[:, -1] == 0)
    #     mean_day_84 = np.mean(paths[:, -1])
    #     mean_over_days = np.mean(paths[:, 1:])

    #     print(
    #         schedule, switch_days,
    #         "extinct by day 84:", round(extinct_fraction, 3),
    #         "mean day 84:", round(mean_day_84, 2),
    #         "mean over days 1–84:", round(mean_over_days, 2)
    #     )
    # # Plot for 1000 runs each x 5 scenarios
    # fig, ax = plt.subplots()
    # days = np.arange(HORIZON + 1)

    # for (schedule, switch_days), paths in all_runs.items():
    #     mean = paths.mean(axis=0)
    #     se = paths.std(axis=0, ddof=1) / np.sqrt(N_RUNS)

    #     line, = ax.plot(days, mean, label=f"{schedule}, {switch_days} day")
    #     ax.fill_between(
    #         days,
    #         np.maximum(0, mean - 1.96 * se),
    #         mean + 1.96 * se,
    #         color=line.get_color(),
    #         alpha=0.15
    #     )

    # ax.set_xlabel("Day")
    # ax.set_ylabel("Mean number infected")
    # ax.set_title("SIS: mean across 1,000 runs")
    # ax.legend()
    # fig.tight_layout()
    # fig.savefig("sis_mean_1000_runs_startdate.png", dpi=160)
    # plt.close(fig)
    
    # for weekly, daily in [
    # (("on_off", 7), ("on_off", 1)),
    # (("rotating", 7), ("rotating", 1)),
    # ]:
    #     weekly_per_run = all_runs[weekly][:, 1:].mean(axis=1)
    #     daily_per_run = all_runs[daily][:, 1:].mean(axis=1)

    #     differences = weekly_per_run - daily_per_run
    #     estimate = differences.mean()
    #     margin = 1.96 * differences.std(ddof=1) / np.sqrt(N_RUNS)

    #     print(weekly[0], "weekly minus daily:",
    #         round(estimate, 3),
    #         "95% interval:",
    #         (round(estimate - margin, 3),
    #         round(estimate + margin, 3)))
    
    world_runs = {scenario: [] for scenario in scenarios}

    for world in range(N_WORLDS):
        graph_w = make_network(N, TARGET_MEAN_DEGREE, NETWORK_SEED + world)
        groups_w = split_groups(N, GROUP_SEED + world)

        initial_rng = np.random.default_rng(INFECTION_SEED + world)
        infected_w = np.zeros(N, dtype=bool)
        initial_ids_w = initial_rng.choice(
            N, size=INITIAL_INFECTED, replace=False
        )
        infected_w[initial_ids_w] = True

        for scenario_index, (schedule, switch_days) in enumerate(scenarios):
            trajectories = []

            for rep in range(RUNS_PER_WORLD):
                global_rep = world * RUNS_PER_WORLD + rep
                seed = SIM_SEED + 100_000 + global_rep * len(scenarios) + scenario_index
                start_day = global_rep % 14

                counts = run_simulation(
                    graph_w, groups_w, infected_w,
                    schedule, switch_days,
                    BETA, GAMMA, HORIZON, seed, start_day
                )
                trajectories.append(counts)

            world_runs[(schedule, switch_days)].append(np.stack(trajectories))

        print("Completed world", world + 1)

    for scenario in scenarios:
        cube = np.stack(world_runs[scenario])
        print(
            scenario,
            "shape:", cube.shape,
            "extinct by day 84:", round(np.mean(cube[:, :, -1] == 0), 3),
            "mean over days 1–84:", round(np.mean(cube[:, :, 1:]), 2),
        )

        
        
if __name__ == "__main__":
    main()
