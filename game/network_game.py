"""Small contact networks for the one-day attendance game."""

import argparse
from itertools import product
from game import new_infection_probability, switch_action
from scipy.optimize import linprog, least_squares
from networkx.algorithms.isomorphism import GraphMatcher
import networkx as nx
import numpy as np
from contact_value_payoff import attendance_gain
import csv 


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

def expected_payoff_with_contact_value(
    graph, profile, player, pi, beta, L_day, gamma, c, v
):
    """Compute a player's expected payoff under the contact-value model."""
    home_payoff = -L_day * pi - c 

    if profile[player] == "H":
        return home_payoff

    k = count_attending_neighbors(graph, profile, player) 
    gain = attendance_gain(k, pi, beta, L_day, gamma, c, v) 
    return home_payoff + gain

def obedience_gain_with_contact_value(
    graph, profile, player, pi, beta, L_day, gamma, c, v
):
    """Return the payoff from following the profile minus the payoff from switching."""
    # Compute the player's payoff under the current profile.
    current_payoff = expected_payoff_with_contact_value(graph, profile, player, pi, beta, L_day, gamma, c, v)

    # Flip only this player's action using switch_action.
    switched_profile = switch_action(profile, player)

    # Recompute the same player's payoff under the switched profile.
    switched_payoff = expected_payoff_with_contact_value(graph, switched_profile, player, pi, beta, L_day, gamma, c, v)

    return current_payoff - switched_payoff

def is_nash_equilibrium_with_contact_value(
    graph, profile, pi, beta, L_day, gamma, c, v
):
    """Check whether anyone can gain by switching their action alone."""
    for player in graph.nodes:
        # Compare this player's current payoff with their payoff after switching.
        gain = obedience_gain_with_contact_value(graph, profile, player, pi, beta, L_day, gamma, c, v)

        # Allow a small tolerance for floating-point rounding.
        if gain < -1e-12:
            return False

    return True

def pure_nash_equilibria_with_contact_value(
    graph, pi, beta, L_day, gamma, c, v
):
    """Return all pure Nash equilibria under the contact-value model."""
    equilibria = []

    # Keep only profiles in which no player gains by switching alone.
    for profile in all_action_profiles(graph):
        if is_nash_equilibrium_with_contact_value(graph, profile, pi, beta, L_day, gamma, c, v):
            equilibria.append(profile)

    return equilibria

def extra_cost_with_contact_value(
    graph, profile, pi, beta, L_day, gamma, c, v
):
    """Return the group's expected cost above its common infection baseline."""
    total_payoff = 0.0

    # Add each player's expected payoff under this profile.
    for player in graph.nodes:
        total_payoff += expected_payoff_with_contact_value(graph, profile, player, pi, beta, L_day, gamma, c, v)

    # Compute the group's expected cost from infections already present.
    baseline = graph.number_of_nodes() * L_day * pi

    # Convert payoff to cost and subtract the common baseline.
    return -total_payoff - baseline

def social_optimum_with_contact_value(graph, pi, beta, L_day, gamma, c, v):
    """Return the minimum group cost and all profiles that attain it."""
    profiles = all_action_profiles(graph)
    costs = []

    # Compute the group cost of each profile in the same order.
    for profile in profiles:
        cost = extra_cost_with_contact_value(graph, profile, pi, beta, L_day, gamma, c, v)
        costs.append(cost)

    minimum = min(costs)
    best_profiles = []

    # Keep every profile whose cost matches the minimum within rounding tolerance.
    for profile, cost in zip(profiles, costs):
        if abs(cost - minimum) < 1e-12:
            best_profiles.append(profile)

    return minimum, best_profiles

def best_pure_nash_cost_with_contact_value(graph, pi, beta, L_day, gamma, c, v):
    """Return the lowest group cost among pure Nash equilibria."""
    # Find all pure Nash profiles for these parameters.
    equilibria = pure_nash_equilibria_with_contact_value(graph, pi, beta, L_day, gamma, c, v)
    costs = []

    # Compute the group cost of each equilibrium profile.
    for profile in equilibria:
        costs.append(extra_cost_with_contact_value(graph, profile, pi, beta, L_day, gamma, c, v))

    return min(costs, default=None)

def obedience_row_with_contact_value(
    graph, player, recommendation, pi, beta, L_day, gamma, c, v
):
    """Return one obedience coefficient per action profile."""
    row = []

    for profile in all_action_profiles(graph):
        # Only profiles that give this player the specified recommendation contribute.
        if profile[player] == recommendation:
            coefficient = obedience_gain_with_contact_value(graph, profile, player, pi, beta, L_day, gamma, c, v)
        else:
            coefficient = 0.0

        row.append(coefficient)

    return row

def all_obedience_rows_with_contact_value(graph, pi, beta, L_day, gamma, c, v):
    """Return the labels and coefficients for all obedience constraints."""
    labels = []
    rows = []

    # Create one row for each player and each possible recommendation.
    for player in graph.nodes:
        for recommendation in ACTIONS:
            labels.append((player, recommendation))
            rows.append(obedience_row_with_contact_value(graph, player, recommendation, pi, beta, L_day, gamma, c, v))

    return labels, rows

def cost_vector_with_contact_value(graph, pi, beta, L_day, gamma, c, v):
    """Return the group cost of each profile in LP column order."""
    costs = []

    # Use the same profile order as the obedience matrix.
    for profile in all_action_profiles(graph):
        cost = extra_cost_with_contact_value(graph, profile, pi, beta, L_day, gamma, c, v)
        costs.append(cost)

    return np.asarray(costs, dtype=float)

def lp_arrays_with_contact_value(graph, pi, beta, L_day, gamma, c, v):
    """Build the objective and constraints for the contact-value CE."""
    # Use group costs directly because linprog minimizes the objective.
    objective = cost_vector_with_contact_value(graph, pi, beta, L_day, gamma, c, v)
    _, rows = all_obedience_rows_with_contact_value(
        graph, pi, beta, L_day, gamma, c, v
    )

    # Express the obedience constraints in less-than-or-equal form.
    A_ub = -np.asarray(rows, dtype=float)
    b_ub = np.zeros(len(rows))

    # Require the probabilities to sum to one.
    A_eq = np.ones((1, len(objective)))
    b_eq = np.array([1.0])

    return objective, A_ub, b_ub, A_eq, b_eq

def solve_best_correlated_equilibrium_with_contact_value(
    graph, pi, beta, L_day, gamma, c, v
):
    """Find a correlated equilibrium that minimizes expected group cost."""
    objective, A_ub, b_ub, A_eq, b_eq = lp_arrays_with_contact_value(graph, pi, beta, L_day, gamma, c, v)

    # Require every profile probability to be nonnegative.
    return linprog(
        c=objective,
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=(0, None),
        method="highs",
    )
    
def cost_summary_with_contact_value(graph, pi, beta, L_day, gamma, c, v):
    """Return the best pure Nash, best CE, and social minimum costs."""
    params = dict(pi=pi, beta=beta, L_day=L_day, gamma=gamma, c=c, v=v)

    nash_profiles = pure_nash_equilibria_with_contact_value(graph, **params)

    # get minimum extra_cost in nash_profiles
    nash_costs = [
        extra_cost_with_contact_value(graph, profile, **params)
        for profile in nash_profiles
    ]

    # Find the lowest cost among pure Nash equilibria.
    best_pure_nash = min(nash_costs)

    # Solve the CE linear program and check that it succeeded.
    result = solve_best_correlated_equilibrium_with_contact_value(graph,**params)
    if not result.success:
        raise RuntimeError(f"CE solver failed: {result.message}")

    # Read the minimum cost and discard the profiles that attain it.
    minimum, _ = social_optimum_with_contact_value(graph, **params)

    return best_pure_nash, float(result.fun), minimum

def individual_costs_with_contact_value(
    graph, probabilities, pi, beta, L_day, gamma, c, v
):
    """Return each player's expected cost above baseline, in node order."""
    profiles = all_action_profiles(graph)
    costs = np.zeros(graph.number_of_nodes(), dtype=float)

    for profile, probability in zip(profiles, probabilities, strict=True):
        for player in graph.nodes:
            # Compute this player's payoff under the current profile.
            payoff = expected_payoff_with_contact_value(graph, profile, player, pi, beta, L_day, gamma, c, v)

            # Convert payoff to extra cost and weight it by profile probability.
            costs[player] += (-payoff - L_day*pi) * probability

    return costs

def independent_profile_probabilities(graph, attendance_probs):
    """Return profile probabilities when players choose independently."""
    probabilities = []

    for profile in all_action_profiles(graph):
        probability = 1.0

        # Multiply by each player's probability of taking their assigned action.
        for player, action in enumerate(profile):
            p_attend = attendance_probs[player]
            if action == "A":
                probability *= p_attend
            else:
                probability *= 1 - p_attend

        probabilities.append(probability)

    return np.asarray(probabilities, dtype=float)

def independent_attendance_gain_with_contact_value(
    graph, attendance_probs, player, pi, beta, L_day, gamma, c, v
):
    """Return the expected gain from attending against independent choices."""
    # Fix this player's action at A while leaving everyone else's choices as given.
    forced_attendance = list(attendance_probs)
    forced_attendance[player] = 1.0
    probabilities = independent_profile_probabilities(graph, forced_attendance)

    expected_gain = 0.0
    for profile, probability in zip(
        all_action_profiles(graph), probabilities, strict=True
    ):
        if probability == 0.0:
            continue

        # For this profile, obedience gain is the payoff from A minus H.
        gain = obedience_gain_with_contact_value(graph, profile, player, pi, beta, L_day, gamma, c, v)
        expected_gain += probability * gain

    return expected_gain

def is_independent_nash_with_contact_value(
    graph, attendance_probs, pi, beta, L_day, gamma, c, v, tol=1e-9
):
    """Check whether each player assigns probability only to best responses."""
    for player in graph.nodes:
        prob = attendance_probs[player]
        gain = independent_attendance_gain_with_contact_value(
            graph, attendance_probs, player, pi, beta, L_day, gamma, c, v
        )

        # Reject positive attendance probability when staying home pays more.
        if prob > 0 and gain < -tol:
            return False

        # Reject positive home probability when attending pays more.
        if prob < 1 and gain > tol:
            return False

    return True

def independent_nash_cost_with_contact_value(
    graph, attendance_probs, pi, beta, L_day, gamma, c, v
):
    """Return the expected group cost of a given independent Nash equilibrium."""
    params = dict(pi=pi, beta=beta, L_day=L_day, gamma=gamma, c=c, v=v)

    # Check that each player's strategy is a best response.
    if not is_independent_nash_with_contact_value(graph, attendance_probs, pi, beta, L_day, gamma, c, v):
        raise ValueError("Attendance probabilities do not form a Nash equilibrium.")

    # Convert independent attendance choices into a lottery over profiles.
    probabilities = independent_profile_probabilities(graph, attendance_probs)

    # Sum the expected costs of all players.
    costs = individual_costs_with_contact_value(graph, probabilities, pi, beta, L_day, gamma, c, v)
    return float(costs.sum())

def find_independent_nash_for_pattern(graph, pattern, pi, beta, L_day, gamma, c, v):
    """Find a Nash candidate for a pattern of fixed and mixed actions."""
    params = dict(pi=pi, beta=beta, L_day=L_day, gamma=gamma, c=c, v=v)
    mixing_players = [i for i, value in enumerate(pattern) if value is None]

    if not mixing_players:
        if is_independent_nash_with_contact_value(graph, pattern, **params):
            return list(pattern)
        return None

    def build_attendance(mixed_probs):
        # Insert the trial probabilities into the mixed positions.
        attendance = list(pattern)
        for player, probability in zip(mixing_players, mixed_probs, strict=True):
            attendance[player] = float(probability)
        return attendance

    def residuals(mixed_probs):
        # Each mixing player must be indifferent between A and H.
        attendance = build_attendance(mixed_probs)
        return [
            independent_attendance_gain_with_contact_value(graph, attendance, player, **params)
            for player in mixing_players
        ]

    result = least_squares(
        residuals, [0.5] * len(mixing_players), bounds=(0.0, 1.0), gtol=1e-13
    )
    candidate = build_attendance(result.x)

    # Check that the proposed mixing probabilities are inside the interval.
    if not result.success or any(not 1e-8 < q < 1 - 1e-8 for q in result.x):
        return None

    # Check best responses for all players, including those with fixed actions.
    if is_independent_nash_with_contact_value(graph, candidate, **params):
        return candidate

    return None

def find_independent_nash_candidates(graph, pi, beta, L_day, gamma, c, v):
    """Return verified Nash candidates found across all strategy patterns."""
    params = dict(pi=pi, beta=beta, L_day=L_day, gamma=gamma, c=c, v=v)
    candidates = []

    # Enumerate every combination of fixed and mixed strategies.
    for pattern in product((0.0, 1.0, None), repeat=graph.number_of_nodes()):
        candidate = find_independent_nash_for_pattern(graph, pattern, **params)

        # Keep candidates that passed the best-response checks.
        if candidate is not None:
            candidates.append(candidate)

    return candidates

def lowest_cost_independent_nash_found(graph, pi, beta, L_day, gamma, c, v):
    """Return the lowest cost found and its attendance probabilities."""
    params = dict(pi=pi, beta=beta, L_day=L_day, gamma=gamma, c=c, v=v)
    candidates = find_independent_nash_candidates(graph, **params)
    best_cost = None
    best_candidate = None

    # Evaluate each verified equilibrium and keep the cheapest one found.
    for candidate in candidates:
        cost = independent_nash_cost_with_contact_value(graph, candidate, **params)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_candidate = candidate

    return best_cost, best_candidate

def contact_value_result_row(graph, pi, beta, L_day, gamma, c, v):
    """Return the group cost benchmarks and the highest individual CE cost."""
    params = dict(pi=pi, beta=beta, L_day=L_day, gamma=gamma, c=c, v=v)

    # Compute the two Nash benchmarks and the unconstrained minimum.
    pure_cost = best_pure_nash_cost_with_contact_value(graph, **params)
    independent_cost, _ = lowest_cost_independent_nash_found(graph, **params)
    social_minimum, _ = social_optimum_with_contact_value(graph, **params)

    # Solve the CE once and reuse its lottery to compute individual costs.
    result = solve_best_correlated_equilibrium_with_contact_value(graph, **params)
    if not result.success:
        raise RuntimeError(f"CE solver failed: {result.message}")

    balanced = symmetrize_lottery(graph, result.x)
    individual_costs = individual_costs_with_contact_value(graph, balanced, **params)

    return {
        "best_pure_nash": pure_cost,
        "lowest_independent_nash_found": independent_cost,
        "best_ce": float(result.fun),
        "social_minimum": social_minimum,
        "highest_individual_ce_cost": float(max(individual_costs)),
    }
    
    
def connected_atlas_graphs(n):
    """Return (atlas_id, graph) pairs for connected graphs with n nodes."""
    graphs = []

    # Keep the original atlas ID so each graph can be identified later.
    for atlas_id, graph in enumerate(nx.graph_atlas_g()):
        if graph.number_of_nodes() != n:
            continue

        # Check connectivity only after filtering by size.
        if nx.is_connected(graph):
            graphs.append((atlas_id, graph))

    return graphs

def atlas_results_for_size(n, pi, beta, L_day, gamma, c, v):
    """Return one result row per connected atlas graph with n nodes."""
    params = dict(pi=pi, beta=beta, L_day=L_day, gamma=gamma, c=c, v=v)
    results = []

    for atlas_id, graph in connected_atlas_graphs(n):
        # Count the pure Nash equilibria and compute the cost benchmarks.
        pure_equilibria = pure_nash_equilibria_with_contact_value(graph, **params)
        costs = contact_value_result_row(graph, **params)

        results.append({
            "atlas_id": atlas_id,
            "n": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "pure_nash_count": len(pure_equilibria),
            **costs,
        })

    return results

def atlas_parameter_grid(sizes, pi_values, c_values, beta, L_day, gamma, v):
    """Return one row per graph and parameter combination."""
    results = []

    # Evaluate every combination of graph size, prevalence, and home cost.
    for n, pi, c in product(sizes, pi_values, c_values):
        rows = atlas_results_for_size(n, pi, beta, L_day, gamma, c, v)

        # Store the parameter values alongside each graph result.
        for row in rows:
            # Measure the cost reduction relative to each Nash benchmark.
            ce_cost = row["best_ce"]
            ce_gain_vs_pure = row["best_pure_nash"] - ce_cost
            independent_cost = row["lowest_independent_nash_found"]
            ce_gain_vs_independent = (
                None if independent_cost is None else independent_cost - ce_cost
            )

            results.append({
                "pi": pi,
                "c": c,
                **row,
                "ce_gain_vs_pure": ce_gain_vs_pure,
                "ce_gain_vs_independent_found": ce_gain_vs_independent,
                "beta": beta,
                "L_day": L_day,
                "gamma": gamma,
                "v": v,
            })

    return results

def write_atlas_results_csv(rows, path):
    """Write atlas results to a CSV file."""
    if not rows:
        raise ValueError("No atlas results to write.")

    # Use the keys from the first row as column names.
    fieldnames = list(rows[0])

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        # Write all result rows in the same column order.
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary", action="store_true",
        help="print the network-game cost, attendance, and contact table",
    )
    
    parser.add_argument(
    "--atlas-output", metavar="CSV",
    help="write the contact-value atlas results to this CSV file",
    )
    parser.add_argument(
        "--sizes", nargs="+", type=int, choices=(4, 5, 6), default=[4],
        help="graph sizes for the atlas grid (default: 4)",
    )
    
    args = parser.parse_args()
    if args.summary:
        print_network_summary()
        return
    
    if args.atlas_output:
        # Run the same parameter grid for each requested graph size.
        rows = atlas_parameter_grid(
            sizes=args.sizes,
            pi_values=(0.1, 0.5),
            c_values=(0.05, 0.12),
            beta=0.04,
            L_day=10,
            gamma=0.2,
            v=0.14,
        )

        # Save the results and report the number of rows written.
        write_atlas_results_csv(rows, args.atlas_output)
        print(f"Saved {len(rows)} rows to {args.atlas_output}")
        return

    for name, graph in example_networks().items():
        print(
            f"{name}: nodes={graph.number_of_nodes()}, "
            f"edges={graph.number_of_edges()}, "
            f"profiles={len(all_action_profiles(graph))}"
        )


if __name__ == "__main__":
    main()
