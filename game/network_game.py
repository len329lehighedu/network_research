"""Small contact networks for the one-day attendance game."""

import argparse
from itertools import product
from game import new_infection_probability, switch_action
from scipy.optimize import linprog
from networkx.algorithms.isomorphism import GraphMatcher
import networkx as nx
import numpy as np


ACTIONS = ("A", "H")


def example_networks():
    """Return example graphs with four, five, and six people."""
    triangle_with_leaf = nx.Graph()
    triangle_with_leaf.add_edges_from(
        [(0, 1), (1, 2), (2, 0), (2, 3)]
    )

    return {
        "path_4": nx.path_graph(4),
        "star_5": nx.star_graph(4),
        "triangle_with_leaf_4": triangle_with_leaf,
        "path_6": nx.path_graph(6),
    }


def all_action_profiles(graph):
    """List A/H choices in node order 0, 1, ..., n-1."""
    number_of_people = graph.number_of_nodes()
    if set(graph.nodes) != set(range(number_of_people)):
        raise ValueError("Graph nodes must be numbered 0, 1, ..., n-1")
    return list(product(ACTIONS, repeat=number_of_people))


def count_attending_neighbors(graph, profile, player):
    """Count this player's graph neighbors who attend."""
    count = 0
    # TODO: duyệt graph.neighbors(player), đếm neighbor có profile[neighbor] == "A"
    for neighbor in graph.neighbors(player):
        if profile[neighbor] == "A":
            count = count + 1
    return count

def expected_payoff(graph, profile, player, pi, beta, infection_cost, home_cost):
    """Expected one-day payoff using this player's graph neighbors."""
    if profile[player] == "H":
        # payoff when at home U(H)
        return -infection_cost*pi - home_cost

    k = count_attending_neighbors(graph, profile, player)
    infection_probability = new_infection_probability(k, pi, beta)

    # payoff when attend
    return -infection_cost*(pi + (1-pi)*infection_probability)

def is_nash_equilibrium(
    graph, profile, pi, beta, infection_cost, home_cost
):
    """True if no player benefits from switching action alone."""
    for player in graph.nodes:
        current = expected_payoff(
            graph, profile, player, pi, beta, infection_cost, home_cost
        )
        changed = switch_action(profile, player)

        # calculate payoff of player in changed
        alternative = expected_payoff(graph, changed, player, pi, beta, infection_cost, home_cost)

        # If alternative > current + 1e-12 (player switch alone)
        if alternative > current + 1e-12:
            return False

    return True

def pure_nash_equilibria(graph, pi, beta, infection_cost, home_cost):
    """Return all pure Nash profiles on this graph."""
    equilibria = []

    for profile in all_action_profiles(graph):
        # if profile is Nash equilibria -> add to list
        if (is_nash_equilibrium(graph, profile, pi, beta, infection_cost, home_cost)):
            equilibria.append(profile)

    return equilibria

def total_payoff(graph, profile, pi, beta, infection_cost, home_cost):
    """Sum expected payoffs across all players on this graph."""
    total = 0.0

    for player in graph.nodes:
        # add expected_payoff of player to total
        total += expected_payoff(graph, profile, player, pi, beta, infection_cost, home_cost)

    return total

def extra_cost(graph, profile, pi, beta, infection_cost, home_cost):
    """Group cost above the baseline n*L*pi."""
    baseline = graph.number_of_nodes() * infection_cost * pi
    # convert total_payoff to cost, then baseline
    return -total_payoff(graph, profile, pi, beta, infection_cost, home_cost) - baseline

def social_optimum(graph, pi, beta, infection_cost, home_cost):
    """Return the lowest extra cost and all profiles attaining it."""
    profiles = all_action_profiles(graph)
    costs = [
        extra_cost(graph, profile, pi, beta, infection_cost, home_cost)
        for profile in profiles
    ]

    minimum = min(costs)
    # get profile that has cost close to minimum
    best_profiles = [
    profile
    for profile, cost in zip(profiles, costs)
    if abs(cost - minimum) < 1e-12
    ]

    return minimum, best_profiles

def obedience_gain(graph, profile, player, pi, beta, infection_cost, home_cost):
    """Payoff from obeying minus payoff from switching alone."""
    obey = expected_payoff(
        graph, profile, player, pi, beta, infection_cost, home_cost
    )
    changed = switch_action(profile, player)

    # payoff of each player in changed
    deviate = expected_payoff(graph, changed, player, pi, beta, infection_cost, home_cost)

    return obey - deviate


def obedience_row(
    graph, player, recommendation, pi, beta, infection_cost, home_cost
):
    """One obedience-constraint coefficient per action profile."""
    row = []

    for profile in all_action_profiles(graph):
        if profile[player] == recommendation:
            # coefficient = obedience_gain(...) on this graph
            coefficient = obedience_gain(graph, profile, player, pi, beta, infection_cost, home_cost)
        else:
            coefficient = 0.0

        row.append(coefficient)

    return row

def all_obedience_rows(graph, pi, beta, infection_cost, home_cost):
    """Return (player, recommendation) labels and all LP rows."""
    labels = []
    rows = []

    for player in graph.nodes:
        for action in ACTIONS:
            labels.append((player, action))
            # add the corresponding obedience_row to rows
            rows.append(obedience_row(graph, player, action, pi, beta, infection_cost, home_cost))

    return labels, rows

def welfare_vector(graph, pi, beta, infection_cost, home_cost):
    """Total payoff of each profile, in LP column order."""
    values = []

    for profile in all_action_profiles(graph):
        # append all total_payoff of profile to values
        values.append(total_payoff(graph, profile, pi, beta, infection_cost, home_cost))

    return values

def lp_arrays(graph, pi, beta, infection_cost, home_cost):
    """Build the objective and constraints for the network CE LP."""
    welfare = np.asarray(
        welfare_vector(graph, pi, beta, infection_cost, home_cost),
        dtype=float,
    )
    _, rows = all_obedience_rows(
        graph, pi, beta, infection_cost, home_cost
    )

    objective = -welfare          # -welfare

    # Obedience: R @ x >= 0; SciPy needs A_ub @ x <= b_ub.
    A_ub = -np.asarray(rows, dtype=float)
    b_ub = np.zeros(len(rows))

    # total probabilities of all profile = 1
    A_eq = np.ones((1, len(welfare)))
    b_eq = np.array([1.0])

    return objective, A_ub, b_ub, A_eq, b_eq

def solve_best_correlated_equilibrium(
    graph, pi, beta, infection_cost, home_cost
):
    """Find the highest-welfare CE on this graph."""
    objective, A_ub, b_ub, A_eq, b_eq = lp_arrays(
        graph, pi, beta, infection_cost, home_cost
    )

    result = linprog(
        c=objective,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=(0, None),
        method="highs",
    )

    if not result.success:
        raise RuntimeError(result.message)

    return result


def is_correlated_equilibrium(
    graph, probabilities, pi, beta, infection_cost, home_cost
):
    """Check probability rules and every network obedience constraint."""
    if len(probabilities) != len(all_action_profiles(graph)):
        return False
    if any(value < -1e-9 for value in probabilities):
        return False
    if abs(sum(probabilities) - 1.0) > 1e-9:
        return False

    _, rows = all_obedience_rows(
        graph, pi, beta, infection_cost, home_cost
    )

    for row in rows:
        # total probability * obedience gain for this row
        weighted_gain = np.dot(row, probabilities)

        if weighted_gain < -1e-9:
            return False

    return True


def cost_summary(graph, pi, beta, infection_cost, home_cost):
    """Compare best pure Nash, best CE, and social minimum."""
    params = dict(
        pi=pi, beta=beta,
        infection_cost=infection_cost, home_cost=home_cost,
    )

    nash_profiles = pure_nash_equilibria(graph, **params)

    # get minimum extra_cost in nash_profiles
    nash_costs = [
        extra_cost(graph, profile, **params)
        for profile in nash_profiles
    ]
    best_pure_nash = min(nash_costs)

    result = solve_best_correlated_equilibrium(graph, **params)
    baseline = graph.number_of_nodes() * infection_cost * pi

    # result.fun is total cost including baseline
    best_ce = result.fun - baseline

    minimum, _ = social_optimum(graph, **params)

    return best_pure_nash, best_ce, minimum


def attendance_probabilities(graph, probabilities):
    """Probability each player attends under a lottery over profiles."""
    profiles = all_action_profiles(graph)
    chances = []

    for player in graph.nodes:
        # sum probability of the profile that profile[player] == "A"
        chance = sum(
            probability
            for profile, probability in zip(profiles, probabilities)
            if profile[player] == "A"
        )
        chances.append(chance)

    return chances

def relabel_profile(profile, mapping):
    """Move each old node's action to its mapped node."""
    changed = [None] * len(profile)

    for old_node, new_node in mapping.items():
        # assign action of old_node to new_node
        changed[new_node] = profile[old_node]

    return tuple(changed)


def relabel_lottery(graph, probabilities, mapping):
    """Move lottery probability mass under a graph node mapping."""
    profiles = all_action_profiles(graph)
    position = {profile: i for i, profile in enumerate(profiles)}
    moved = np.zeros(len(profiles))

    for profile, probability in zip(profiles, probabilities):
        changed_profile = relabel_profile(profile, mapping)

        # add probability to changed_profile in moved
        moved[position[changed_profile]] += probability

    return moved


def symmetrize_lottery(graph, probabilities):
    """Average a lottery over the graph's node symmetries."""
    mappings = list(GraphMatcher(graph, graph).isomorphisms_iter())
    balanced = np.zeros(len(all_action_profiles(graph)))

    for mapping in mappings:
        # add lottery
        balanced += relabel_lottery(graph, probabilities, mapping)

    return balanced / len(mappings)

def active_contacts(graph, profile):
    """Count edges whose two endpoints both attend."""
    total = 0

    for u, v in graph.edges:
        # if both profile[u] and profile[v] is "A", increment
        if profile[u] == "A" and profile[v] == "A":
            total+=1

    return total

def expected_active_contacts(graph, probabilities):
    """Expected number of active edges under a lottery."""
    profiles = all_action_profiles(graph)

    # TODO: với mỗi (profile, probability), nhân probability
    # với active_contacts(graph, profile), rồi cộng tất cả
    return sum(
            probability * active_contacts(graph, profile)
            for profile, probability in zip(profiles, probabilities)
        )


def print_network_summary():
    """Print reproducible cost and contact summaries for the example graphs."""
    params = dict(pi=0.1, beta=0.04, infection_cost=10, home_cost=0.05)
    print("One-day network game; parameters:", params)
    print("Costs are group totals above n*L*pi; contact counts are per day.")
    print(
        "| Graph | n | edges | Best pure Nash | Best CE | Social minimum | "
        "CE gap closed | CE cost/person | CE active edges |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    attendance_rows = []
    for name, graph in example_networks().items():
        nash_cost, ce_cost, minimum_cost = cost_summary(graph, **params)
        raw = solve_best_correlated_equilibrium(graph, **params).x
        balanced = symmetrize_lottery(graph, raw)
        if not is_correlated_equilibrium(graph, balanced, **params):
            raise RuntimeError(f"Symmetrized lottery is not a CE: {name}")

        gap = nash_cost - minimum_cost
        gap_text = (
            "—" if abs(gap) < 1e-10
            else f"{(nash_cost - ce_cost) / gap:.1%}"
        )
        contacts = expected_active_contacts(graph, balanced)
        print(
            f"| {name} | {graph.number_of_nodes()} | {graph.number_of_edges()} | "
            f"{nash_cost:.6f} | {ce_cost:.6f} | {minimum_cost:.6f} | "
            f"{gap_text} | {ce_cost / graph.number_of_nodes():.6f} | "
            f"{contacts:.6f} |"
        )
        attendance = attendance_probabilities(graph, balanced)
        attendance_rows.append(
            f"{name}: " + ", ".join(f"{float(value):.6f}" for value in attendance)
        )

    print("\nAttendance probabilities by node in one symmetry-balanced optimal CE:")
    for row in attendance_rows:
        print(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary", action="store_true",
        help="print the network-game cost, attendance, and contact table",
    )
    args = parser.parse_args()
    if args.summary:
        print_network_summary()
        return

    for name, graph in example_networks().items():
        print(
            f"{name}: nodes={graph.number_of_nodes()}, "
            f"edges={graph.number_of_edges()}, "
            f"profiles={len(all_action_profiles(graph))}"
        )


if __name__ == "__main__":
    main()
