import networkx as nx
import numpy as np
from network_sis.sis_experiment import sis_step, attendance
from contact_value_payoff import attendance_gain
from network_game import count_attending_neighbors, all_action_profiles, solve_best_correlated_equilibrium_with_contact_value, active_contacts


def make_two_community_graph():
    """Build two five-person communities connected by one bridge."""
    # Create two groups where everyone in each group knows one another.
    first = nx.complete_graph(5)
    second = nx.complete_graph(5)

    # Give the first group nodes 0–4 and the second group nodes 5–9.
    graph = nx.disjoint_union(first, second)

    # Connect the two groups with one edge.
    graph.add_edge(4, 5)

    # Store each person's group label at their node index.
    groups = np.array([0] * 5 + [1] * 5)

    return graph, groups

def advance_infection_one_day(graph, infected, actions, beta, gamma, rng, *, infection_draws=None, recovery_draws=None):
    """Advance the infection state using today's actual attendance."""
    # Mark each person as present if their action is A.
    present = np.array([action == "A" for action in actions], dtype=bool)

    # Use today's infection state and attendance to compute tomorrow's state.
    return sis_step(graph, infected, present, beta, gamma, rng, infection_draws=infection_draws, recovery_draws=recovery_draws)

def realized_daily_payoffs(graph, actions, next_infected, L_day, c, v):
    """Return each person's realized payoff for the day."""
    payoffs = np.zeros(graph.number_of_nodes(), dtype=float)

    for person in graph.nodes:
        # Charge the infection cost using the end-of-day state.
        if next_infected[person]:
            payoffs[person] -= L_day

        # Charge the home cost or add the value of actual contacts.
        if actions[person] == "H":
            payoffs[person] -= c
        else:
            contacts = sum(
                actions[neighbor] == "A"
                for neighbor in graph.neighbors(person)
            )
            payoffs[person] += v * contacts

    return payoffs

def run_one_day(graph, infected, actions, beta, gamma, L_day, c, v, rng, *, infection_draws=None, recovery_draws=None):
    """Run one day with given actions and return the next state and payoffs."""
    # Update infections using the actions taken today.
    next_infected = advance_infection_one_day(graph, infected, actions, beta, gamma, rng, infection_draws=infection_draws, recovery_draws=recovery_draws)

    # Compute payoffs using today's actions and the end-of-day infection state.
    payoffs = realized_daily_payoffs(graph, actions, next_infected, L_day, c, v)

    return next_infected, payoffs

def run_trajectory(graph, initial_infected, daily_actions, beta, gamma, L_day, c, v, rng):
    """Run a sequence of daily actions and return infection and payoff histories."""
    infected = initial_infected.copy()

    # Record the initial state before any actions are taken.
    infection_history = [infected.copy()]
    payoff_history = []

    for actions in daily_actions:
        # Carry the infection state from the end of one day into the next.
        infected, payoffs = run_one_day(graph, infected, actions, beta, gamma, L_day, c, v, rng)

        infection_history.append(infected.copy())
        payoff_history.append(payoffs)

    return np.stack(infection_history), np.stack(payoff_history)

def fixed_rotation_actions(groups, days, switch_days=1):
    """Return one attendance profile per day under fixed rotation."""
    daily_actions = []

    for day in range(days):
        # Get the attendance mask for the current day.
        present = attendance(day, groups, "rotating", switch_days)

        # Turn the mask into one A or H action per person.
        actions = "".join("A" if is_present else "H" for is_present in present)
        daily_actions.append(actions)

    return daily_actions

def deviation_gain(recommendation, k, pi, beta, L_day, gamma, c, v):
    """Return the expected payoff from switching minus following."""
    # Compute the expected payoff from attending minus staying home.
    gain = attendance_gain(k, pi, beta, L_day, gamma, c, v)

    # A deviation from H means attending.
    if recommendation == "H":
        return gain

    # A deviation from A means staying home.
    return -gain

def choose_actual_action(recommendation, gain, willingness, rng):
    """Choose an action given a recommendation and the gain from deviating."""
    # Follow when switching offers no meaningful improvement.
    if gain <= 1e-12:
        return recommendation

    # Follow with the given probability when switching is profitable.
    if rng.random() < willingness:
        return recommendation

    # Switch to the other action.
    return "A" if recommendation == "H" else "H"

def actions_from_fixed_recommendations(
    graph, recommendations, willingness, pi, beta, L_day, gamma, c, v, rng,
    forecast_profile=None,
):
    """Choose actual actions given a publicly announced rotation schedule."""
    # forecast_profile is the A/H profile people use to guess who will attend.
    # None keeps the legacy behavior: everyone believes the announced schedule.
    if forecast_profile is None:
        forecast_profile = recommendations

    actual_actions = []

    for person, recommendation in enumerate(recommendations):
        # Count neighbors expected to attend under the FORECAST profile.
        k = count_attending_neighbors(graph, forecast_profile, person)

        # Compute the expected gain from switching this person's action.
        gain = deviation_gain(recommendation, k, pi, beta, L_day, gamma, c, v)

        # Choose an action using this person's willingness to follow.
        action = choose_actual_action(recommendation, gain, willingness[person], rng)
        actual_actions.append(action)

    return "".join(actual_actions)

def run_fixed_rotation_day(
    graph, infected, recommendations, willingness, beta, gamma, L_day, c, v,
    decision_rng, sis_rng, *, infection_draws=None, recovery_draws=None,
    forecast_profile=None,
):
    """Run one rotation day and return actual actions, next state, and payoffs."""
    # Use start-of-day prevalence to evaluate the recommendation.
    pi = float(infected.mean())

    # Convert the announced schedule into actual attendance choices.
    actual_actions = actions_from_fixed_recommendations(graph, recommendations, willingness, pi, beta, L_day, gamma, c, v, decision_rng,
        forecast_profile=forecast_profile)

    # Use actual attendance for both infection updates and realized payoffs.
    next_infected, payoffs = run_one_day(graph, infected, actual_actions, beta, gamma, L_day, c, v, sis_rng, infection_draws=infection_draws,
        recovery_draws=recovery_draws)

    return actual_actions, next_infected, payoffs

def run_fixed_rotation_trajectory(
    graph, initial_infected, daily_recommendations, willingness,
    beta, gamma, L_day, c, v, decision_rng, sis_rng, imitation_rng=None, *, infection_draws_by_day=None, recovery_draws_by_day=None,
    belief="schedule", shuffle_rng=None,
):
    """Return infection, payoff, attendance, and willingness histories."""
    infected = initial_infected.copy()
    willingness = willingness.copy()
    infection_history = [infected.copy()]
    willingness_history = [willingness.copy()]
    payoff_history = []
    action_history = []

    for day, recommendations in enumerate(daily_recommendations):
        # Use today's willingness to choose today's actions.
        # Select the SIS draws for this day.
        infection_draws = (
            None if infection_draws_by_day is None else infection_draws_by_day[day]
        )
        recovery_draws = (
            None if recovery_draws_by_day is None else recovery_draws_by_day[day]
        )
        
        # Build the profile people use to count attending neighbors today.
        # action_history holds actual actions for days before `day` only.
        forecast_profile = rotation_forecast_profile(daily_recommendations, action_history, day, belief)

        actual_actions, infected, payoffs = run_fixed_rotation_day(graph, infected, recommendations, willingness, beta, gamma, 
        L_day, c, v, decision_rng, sis_rng, infection_draws=infection_draws, recovery_draws=recovery_draws,
        forecast_profile=forecast_profile)

        infection_history.append(infected.copy())
        payoff_history.append(payoffs)
        action_history.append(actual_actions)

        # Update willingness for the next day using today's payoffs.
        if imitation_rng is not None:
            willingness = update_willingness(
                graph, willingness, imitation_payoffs(payoffs, shuffle_rng), imitation_rng)

        willingness_history.append(willingness.copy())

    return (
        np.stack(infection_history),
        np.stack(payoff_history),
        action_history,
        np.stack(willingness_history),
    )

def initial_willingness(n_people, behavior, rng):
    """Return each person's starting willingness to follow a recommendation."""
    # Willingness is the probability of following a recommendation
    # when deviating would pay off. Values must lie in [0, 1].

    # Legacy: spread evenly from 0 to 1 by person index, as in Report 5.
    # It uses no randomness, so no RNG stream is consumed.
    if behavior == "legacy":
        return np.linspace(0, 1, n_people)

    # Version 1: nobody is willing to follow against their own interest.
    # Again no randomness is used.
    if behavior == "v1":
        return np.zeros(n_people)

    # Version 2: each person draws willingness independently from Uniform[0, 1),
    # using the per-replicate stream so other RNG streams stay untouched.
    # v2_shuffled starts from the same draw; only its imitation differs.
    if behavior in ("v2", "v2_shuffled"):
        return rng.random(n_people)

    # Any other value is a bug in the caller, so fail loudly.
    raise ValueError(
        f"Unknown behavior {behavior!r}; expected 'legacy', 'v1', 'v2', or 'v2_shuffled'."
    )


def rotation_forecast_profile(daily_recommendations, action_history, day, belief):
    """Return the A/H profile a person uses to count attending neighbors today."""
    # daily_recommendations[d] is the announced schedule for day d (a string of A/H).
    # action_history[d] is the profile of ACTUAL actions on day d, and only days
    # before `day` are filled in, so we never peek at today or the future.

    # Schedule belief: everyone assumes the announced schedule will be followed.
    if belief == "schedule":
        return daily_recommendations[day]

    # Last-same-phase belief: use what neighbors actually did the most recent
    # time the schedule looked the same as today's.
    if belief == "last_same_phase":
        # Walk backward from yesterday to day 0 and stop at the first day d
        # whose schedule equals today's schedule.
        for d in range(day - 1, -1, -1):
            if daily_recommendations[d] == daily_recommendations[day]:
                return action_history[d]

        # No earlier day had the same schedule, so fall back to the schedule itself.
        return daily_recommendations[day]

    raise ValueError(
        f"Unknown belief {belief!r}; expected 'schedule' or 'last_same_phase'."
    )


def shuffle_payoffs(payoffs, rng):
    """Return a random permutation of today's payoffs, leaving the input unchanged."""
    # Neutral imitation baseline (v2_shuffled): keep the same payoff values and
    # ties, but break the link between a person's behavior and the payoff
    # they are compared on.
    # permutation returns a copy, so the real payoffs stay intact.
    return rng.permutation(payoffs)


def imitation_payoffs(payoffs, shuffle_rng):
    """Return the payoffs people compare when imitating neighbors."""
    # shuffle_rng is None except under v2_shuffled. Imitation then compares
    # shuffled payoffs; outcomes and group payoff always keep the real ones.
    return payoffs if shuffle_rng is None else shuffle_payoffs(payoffs, shuffle_rng)


def update_willingness(graph, willingness, payoffs, rng):
    """Return tomorrow's willingness after one round of peer imitation."""
    next_willingness = willingness.copy()

    for person in graph.nodes:
        neighbors = list(graph.neighbors(person))
        if not neighbors:
            continue

        # Sample one neighbor uniformly from the contact network.
        neighbor = rng.choice(neighbors)

        # Copy the neighbor's starting willingness if they earned more today.
        if payoffs[neighbor] > payoffs[person]:
            next_willingness[person] = willingness[neighbor]

    return next_willingness

def conditional_deviation_gain(
    graph, probabilities, person, recommendation, pi, beta, L_day, gamma, c, v
):
    """Return the expected gain from switching given a private recommendation."""
    signal_probability = 0.0
    weighted_gain = 0.0

    for profile, probability in zip(
        all_action_profiles(graph), probabilities, strict=True
    ):
        # Keep profiles consistent with what this person was told.
        if profile[person] != recommendation or probability == 0.0:
            continue

        k = count_attending_neighbors(graph, profile, person)
        gain = deviation_gain(recommendation, k, pi, beta, L_day, gamma, c, v)
        signal_probability += probability
        weighted_gain += probability * gain

    if signal_probability == 0.0:
        raise ValueError("This recommendation has zero probability.")

    # Normalize by the probability of receiving this recommendation.
    return weighted_gain / signal_probability

def draw_ce_recommendations(graph, pi, beta, L_day, gamma, c, v, rng):
    """Solve today's CE and draw one recommendation profile."""
    # Solve the one-day game using today's prevalence.
    result = solve_best_correlated_equilibrium_with_contact_value(graph, pi, beta, L_day, gamma, c, v)
    if not result.success:
        raise RuntimeError(f"CE solver failed: {result.message}")

    # Remove any tiny negative roundoff and normalize the probabilities.
    probabilities = np.maximum(result.x, 0.0)
    probabilities /= probabilities.sum()

    # Draw a profile index using the CE lottery.
    profiles = all_action_profiles(graph)
    index = rng.choice(len(profiles), p=probabilities)
    recommendations = "".join(profiles[index])

    return recommendations, probabilities

def actions_from_private_recommendations(
    graph, recommendations, probabilities, willingness,
    pi, beta, L_day, gamma, c, v, rng,
):
    """Choose actual actions using each person's private recommendation."""
    actual_actions = []

    for person, recommendation in enumerate(recommendations):
        # Evaluate switching using only this person's signal and the lottery.
        gain = conditional_deviation_gain(graph, probabilities, person, recommendation, pi, beta, L_day, gamma, c, v)

        # Apply this person's willingness to follow when switching pays more.
        action = choose_actual_action(recommendation, gain, willingness[person], rng)
        actual_actions.append(action)

    return "".join(actual_actions)

def run_ce_day(
    graph, infected, willingness, beta, gamma, L_day, c, v,
    recommendation_rng, decision_rng, sis_rng, *, infection_draws=None, recovery_draws=None,
):
    """Run one day with private CE recommendations."""
    pi = float(infected.mean())

    # Solve today's CE and draw a joint recommendation profile.
    recommendations, probabilities = draw_ce_recommendations(graph, pi, beta, L_day, gamma, c, v, recommendation_rng)

    # Let each person decide using their private recommendation.
    actual_actions = actions_from_private_recommendations(graph, recommendations, probabilities, willingness, pi, beta, L_day, gamma, c, v, decision_rng)

    # Update infections and compute payoffs using actual attendance.
    next_infected, payoffs = run_one_day(graph, infected, actual_actions, beta, gamma, L_day, c, v, sis_rng, infection_draws=infection_draws,
        recovery_draws=recovery_draws)

    return recommendations, actual_actions, next_infected, payoffs

def run_ce_trajectory(
    graph, initial_infected, days, willingness, beta, gamma, L_day, c, v,
    recommendation_rng, decision_rng, sis_rng, imitation_rng=None, *, infection_draws_by_day=None, recovery_draws_by_day=None,
    shuffle_rng=None,
):
    """Return infection, payoff, recommendation, action, and willingness histories."""
    infected = initial_infected.copy()
    willingness = willingness.copy()
    infection_history = [infected.copy()]
    willingness_history = [willingness.copy()]
    payoff_history = []
    recommendation_history = []
    action_history = []

    for day in range(days):
        # Select the SIS draws for this day.
        infection_draws = (
            None if infection_draws_by_day is None else infection_draws_by_day[day]
        )
        recovery_draws = (
            None if recovery_draws_by_day is None else recovery_draws_by_day[day]
        )
        
        # Solve today's CE using the state carried forward from yesterday.
        recommendations, actions, infected, payoffs = run_ce_day(graph, infected, willingness, beta, gamma, 
        L_day, c, v, recommendation_rng, decision_rng, sis_rng, infection_draws=infection_draws, recovery_draws=recovery_draws)

        infection_history.append(infected.copy())
        payoff_history.append(payoffs)
        recommendation_history.append(recommendations)
        action_history.append(actions)

        # Update willingness for the next day using today's realized payoffs.
        if imitation_rng is not None:
            willingness = update_willingness(
                graph, willingness, imitation_payoffs(payoffs, shuffle_rng), imitation_rng)
        willingness_history.append(willingness.copy())

    return (
        np.stack(infection_history),
        np.stack(payoff_history),
        recommendation_history,
        action_history,
        np.stack(willingness_history),
    )
    
def actions_without_recommendations(
    graph, previous_actions, pi, beta, L_day, gamma, c, v, *, update_prob=1.0, revision_rng=None,
):
    """Choose today's actions using yesterday's attendance as a forecast."""
    
    if not 0.0 <= update_prob <= 1.0:
        raise ValueError("update_prob must be between 0 and 1.")
    if update_prob == 0.0:
        return "".join(previous_actions)
    if update_prob < 1.0 and revision_rng is None:
        raise ValueError("Partial updating requires a revision RNG.")
    
    actions = []
    tolerance = 1e-12

    for person, previous_action in enumerate(previous_actions):
        
        # Keep yesterday's action when this person does not revise.
        if update_prob < 1 and revision_rng.random() >= update_prob:
            actions.append(previous_action)
            continue
        # Count neighbors who attended yesterday.
        k = count_attending_neighbors(graph, previous_actions, person)

        # Compare attending with staying home at today's prevalence.
        gain = attendance_gain(k, pi, beta, L_day, gamma, c, v)

        if gain > tolerance:
            actions.append("A")
        elif gain < -tolerance:
            actions.append("H")
        else:
            actions.append(previous_action)

    return "".join(actions)


def run_no_recommendation_trajectory(
    graph, initial_infected, initial_actions, days, beta, gamma, L_day, c, v,
    sis_rng, *, infection_draws_by_day=None, recovery_draws_by_day=None, update_prob=1.0, revision_rng=None,
):
    """Return infection, payoff, and attendance histories without recommendations."""
    infected = initial_infected.copy()
    previous_actions = initial_actions
    infection_history = [infected.copy()]
    payoff_history = []
    action_history = []

    for day in range(days):
        # Use today's prevalence and yesterday's actions to choose attendance.
        pi = float(infected.mean())
        actions = actions_without_recommendations(graph, previous_actions, pi, beta, L_day, gamma, c, v, update_prob=update_prob, revision_rng=revision_rng)
        
        # Select the SIS draws for this day.
        infection_draws = (
            None if infection_draws_by_day is None else infection_draws_by_day[day]
        )
        recovery_draws = (
            None if recovery_draws_by_day is None else recovery_draws_by_day[day]
        )

        # Advance SIS and compute payoffs using today's actual actions.
        infected, payoffs = run_one_day(graph, infected, actions, beta, gamma, L_day, c, v, sis_rng, infection_draws=infection_draws,
            recovery_draws=recovery_draws,)

        infection_history.append(infected.copy())
        payoff_history.append(payoffs)
        action_history.append(actions)

        # Use today's actions as tomorrow's attendance forecast.
        previous_actions = actions

    return np.stack(infection_history), np.stack(payoff_history), action_history

def summarize_trajectory(graph, states, payoffs, actions, recommendations=None, willingness_history=None):
    """Summarize outcomes from one simulation run."""
    # Count infections at the end of each simulated day, excluding day zero.
    infected_person_days = states[1:].sum()

    # Count actual attendance and active edges across all days.
    attendance_person_days = sum(profile.count("A") for profile in actions)
    active_edge_days = sum(active_contacts(graph, profile) for profile in actions)

    follow_rate = None
    if recommendations is not None:
        # Count matches between recommended and actual actions.
        matches = sum(
            actual == recommended
            for daily_actions, daily_recommendations in zip(
                actions, recommendations, strict=True
            )
            for actual, recommended in zip(
                daily_actions, daily_recommendations, strict=True
            )
        )
        follow_rate = matches / (len(actions) * graph.number_of_nodes())

    # Average willingness on days 0, 7, and the last day (day 14 in the benchmark);
    # None when the policy has no willingness. Row d of willingness_history is the
    # willingness used on day d, and the last row is after the final update.
    willingness_d0 = willingness_d7 = final_mean_willingness = None
    if willingness_history is not None:
        willingness_d0 = float(willingness_history[0].mean())
        willingness_d7 = float(willingness_history[7].mean())
        final_mean_willingness = float(willingness_history[-1].mean())

    return {
        "infected_person_days": int(infected_person_days),
        "attendance_person_days": attendance_person_days,
        "active_edge_days": active_edge_days,
        "group_payoff": float(payoffs.sum()),
        "follow_rate": follow_rate,
        "willingness_d0": willingness_d0,
        "willingness_d7": willingness_d7,
        "final_mean_willingness": final_mean_willingness,
    }
    
    
def compare_policies_once(
    graph, groups, initial_infected, days, seed,
    beta, gamma, L_day, c, v, *, update_prob=1.0,
    behavior="legacy", rotation_belief="schedule",
):
    """Run all three attendance policies from the same initial conditions."""
    params = dict(beta=beta, gamma=gamma, L_day=L_day, c=c, v=v)

    # Give disease, decisions, imitation, recommendations, revisions, starting
    # willingness, and payoff shuffling separate RNG streams. spawn keys children
    # by index, so the first six streams stay identical to the old spawn(6) and
    # earlier results reproduce.
    (sis_seed, decision_seed, imitation_seed, recommendation_seed, revision_seed,
     willingness_seed, shuffle_seed) = np.random.SeedSequence(seed).spawn(7)
    rng = np.random.default_rng

    # Build the starting willingness inside, so every replicate gets its own draw.
    # Rotation and CE both start from this same array.
    willingness = initial_willingness(graph.number_of_nodes(), behavior, rng(willingness_seed))

    # Version 1 has no peer imitation; legacy and v2 do.
    use_imitation = behavior != "v1"

    # Only v2_shuffled permutes payoffs before imitation.
    use_shuffle = behavior == "v2_shuffled"
    
    # Generate one infection draw and one recovery draw per day and person.
    sis_draw_rng = rng(sis_seed)
    draw_shape = (days, graph.number_of_nodes())
    shared_draws = dict(
        infection_draws_by_day=sis_draw_rng.random(draw_shape),
        recovery_draws_by_day=sis_draw_rng.random(draw_shape),
    )
    
    results = {}

    states, payoffs, actions = run_no_recommendation_trajectory(
        graph, initial_infected, "A" * graph.number_of_nodes(), days,
        **params, sis_rng=rng(sis_seed), **shared_draws, update_prob=update_prob, revision_rng=rng(revision_seed)
    )
    results["no_recommendation"] = summarize_trajectory(graph, states, payoffs, actions)

    fixed_recommendations = fixed_rotation_actions(groups, days)
    states, payoffs, actions, willingness_history = run_fixed_rotation_trajectory(
        graph, initial_infected, fixed_recommendations, willingness, **params,
        decision_rng=rng(decision_seed), sis_rng=rng(sis_seed),
        imitation_rng=rng(imitation_seed) if use_imitation else None,
        belief=rotation_belief, shuffle_rng=rng(shuffle_seed) if use_shuffle else None,
        **shared_draws
    )
    results["fixed_rotation"] = summarize_trajectory(
        graph, states, payoffs, actions, fixed_recommendations, willingness_history)

    states, payoffs, ce_recommendations, actions, willingness_history = run_ce_trajectory(
        graph, initial_infected, days, willingness, **params,
        recommendation_rng=rng(recommendation_seed),
        decision_rng=rng(decision_seed), sis_rng=rng(sis_seed),
        imitation_rng=rng(imitation_seed) if use_imitation else None,
        shuffle_rng=rng(shuffle_seed) if use_shuffle else None, **shared_draws
    )
    results["daily_ce"] = summarize_trajectory(
        graph, states, payoffs, actions, ce_recommendations, willingness_history)

    return results


def run_policy_replicates(
    graph, groups, initial_infected, days, n_replicates,
    root_seed, beta, gamma, L_day, c, v, *, update_prob=1.0,
    behavior="legacy", rotation_belief="schedule",
):
    """Return one result row per replicate and policy."""
    params = dict(beta=beta, gamma=gamma, L_day=L_day, c=c, v=v, update_prob=update_prob,
                  behavior=behavior, rotation_belief=rotation_belief)
    rows = []

    # Give each replicate a separate seed derived from the root seed.
    replicate_seeds = np.random.SeedSequence(root_seed).spawn(n_replicates)

    for replicate, child_seed in enumerate(replicate_seeds):
        seed = int(child_seed.generate_state(1, dtype=np.uint64)[0])

        # Run all three policies from the same initial conditions.
        results = compare_policies_once(graph, groups, initial_infected, days, seed, **params)

        for policy, summary in results.items():
            rows.append({
                "replicate": replicate,
                "policy": policy,
                **summary,
            })

    return rows


def summarize_policy_replicates(rows):
    """Return mean outcomes and replicate counts by policy."""
    rows_by_policy = {}
    for row in rows:
        rows_by_policy.setdefault(row["policy"], []).append(row)

    metrics = (
        "infected_person_days",
        "attendance_person_days",
        "active_edge_days",
        "group_payoff",
        "follow_rate",
        "willingness_d0",
        "willingness_d7",
        "final_mean_willingness",
    )
    summaries = {}

    for policy, policy_rows in rows_by_policy.items():
        summary = {"n_replicates": len(policy_rows)}

        for metric in metrics:
            # Collect available values for this policy and metric.
            values = [
                policy_row[metric]
                for policy_row in policy_rows
                if policy_row[metric] is not None
            ]
            summary[metric] = float(np.mean(values)) if values else None

        summaries[policy] = summary

    return summaries


def paired_payoff_difference_ci(rows, policy_a, policy_b, rng, draws=2000):
    """Return the mean payoff difference A minus B and its 95% bootstrap interval."""
    # Match payoff values by replicate ID.
    payoffs_a = {
        row["replicate"]: row["group_payoff"]
        for row in rows if row["policy"] == policy_a
    }
    payoffs_b = {
        row["replicate"]: row["group_payoff"]
        for row in rows if row["policy"] == policy_b
    }

    if payoffs_a.keys() != payoffs_b.keys() or len(payoffs_a) < 2:
        raise ValueError("Both policies must have the same two or more replicates.")

    differences = np.array([
        payoffs_a[replicate] - payoffs_b[replicate]
        for replicate in sorted(payoffs_a)
    ])
    n = len(differences)

    # Resample paired differences and compute one mean per bootstrap draw.
    indices = rng.integers(0, n, size=(draws, n))
    bootstrap_means = differences[indices].mean(axis=1)

    lower, upper = np.quantile(bootstrap_means, (0.025, 0.975))
    return float(differences.mean()), float(lower), float(upper)