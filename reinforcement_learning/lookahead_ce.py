"""Stage 3: lookahead CE (option B) on the real attendance model.

Daily CE solves, each day, the linear program
    maximize  expected group payoff today
    subject to  obedience (nobody gains by deviating from a private signal).
Lookahead CE keeps the same constraints and changes only the objective to
    expected group payoff today + expected value of tomorrow's state,
where the value V_{t+1}(k') of having k' infected people tomorrow comes from
backward induction on a belief model (method 1) or is learned by simulation
(method 2). Today's payoff is the expected REALIZED payoff (L_day per infected
person-day), so future infections are priced only through V. Daily CE can be
read as lookahead CE with a hand-made value (L_day / gamma per new infection)
that ignores onward transmission. Both recommenders use the same information
(day and prevalence) and face the same behavior rule.

Belief about who is infected. The recommender sees only prevalence pi, like
daily CE. The one-day game in game/ treats each person as infected with
probability pi, independently (that is where new_infection_probability comes
from). Lookahead CE uses the same belief to predict tomorrow, so it never uses
information daily CE does not have.

Run from the repository root (game/ must be on the path for its imports):
    PYTHONPATH=.:game .venv/bin/python reinforcement_learning/lookahead_ce.py
"""

from itertools import combinations

import networkx as nx
import numpy as np
from scipy.optimize import linprog

from game import new_infection_probability
from reinforcement_learning.tiny_mdp import returns_to_go
from multiday_game import (
    actions_from_private_recommendations,
    imitation_payoffs,
    initial_willingness,
    run_one_day,
    summarize_trajectory,
    update_willingness,
)
from network_game import (
    active_contacts,
    all_action_profiles,
    count_attending_neighbors,
    lp_arrays_with_contact_value,
)


def next_day_infection_probabilities(graph, profile, pi, beta, gamma):
    """Return each person's probability of being infected at the end of today."""
    # Two ways to be infected at the end of the day, under the belief that each
    # person is infected now with probability pi, independently:
    #   1. infected now and does not recover today:  pi * (1 - gamma)
    #   2. susceptible now, attends, and is infected by attending neighbors:
    #        (1 - pi) * new_infection_probability(k, pi, beta)
    #      where k is the number of attending neighbors. Each attending
    #      neighbor is infected with probability pi and transmits with
    #      probability beta, so the chance of escaping all k is (1 - pi*beta)^k.
    #      A person who stays home cannot be infected (same rule as sis_step).
    # The two cases cannot both happen, so their probabilities add.
    probabilities = np.zeros(graph.number_of_nodes())

    for person in graph.nodes:
        # Case 1: already infected and still infected tomorrow.
        stays_infected = pi * (1 - gamma)

        # Case 2: susceptible, attends, and is infected by attending neighbors.
        k = count_attending_neighbors(graph, profile, person)
        newly_infected = 0.0 if profile[person] == "H" else (1-pi) * new_infection_probability(k, pi, beta)

        # The two cases are disjoint, so their probabilities add.
        probabilities[person] = stays_infected + newly_infected

    return probabilities


def next_count_distribution(probabilities):
    """Return P(k' = j) for j = 0..N, the number infected at the end of today."""
    # Each person is infected tomorrow with their own probability p_i, and
    # under the independence belief these events are independent. The count
    # k' is then a sum of independent Bernoulli(p_i) variables with different
    # p_i (a "Poisson-binomial" distribution). V_{t+1} is indexed by k', so the
    # lookahead objective needs this whole distribution, not just its mean.
    #
    # Build it one person at a time. Before adding a person, distribution[j]
    # is the probability that j of the people seen so far are infected. Adding
    # a person with probability p:
    #   - they are not infected (probability 1 - p): the count stays j,
    #   - they are infected (probability p): the count moves from j to j + 1.
    # So the new distribution[j] = old[j] * (1 - p) + old[j - 1] * p.
    probabilities = np.asarray(probabilities, dtype=float)
    distribution = np.zeros(len(probabilities) + 1)
    distribution[0] = 1.0  # with nobody added yet, the count is 0 for sure

    for p in probabilities:
        updated = np.zeros_like(distribution)

        # Not infected: every count stays, weighted by 1 - p.
        updated += (1- p) * distribution

        # Infected: the mass at count j moves to j + 1, weighted by p.
        updated[1:] += p * distribution[:-1]

        distribution = updated

    return distribution


def expected_next_value(graph, profile, pi, beta, gamma, next_values):
    """Return E[V_{t+1}(k')] when today's attendance profile is `profile`."""
    # next_values[j] is V_{t+1}(j): the expected total payoff from tomorrow to
    # the end, starting tomorrow with j infected people. It has N + 1 entries.
    # This is the "looking ahead" term that lookahead CE adds to today's
    # payoff: a profile that spreads more infection shifts k' upward, and if
    # V decreases in k, that lowers the expected value of tomorrow.
    #
    # Steps: profile -> each person's infection probability tomorrow ->
    # distribution of the count k' -> average of V over that distribution.
    next_values = np.asarray(next_values, dtype=float)
    if len(next_values) != graph.number_of_nodes() + 1:
        raise ValueError("next_values needs one entry for each count 0..N.")

    # Profile -> each person's infection probability -> distribution of k'.
    next_day_infection_prob = next_day_infection_probabilities(graph, profile, pi, beta, gamma)
    distribution = next_count_distribution(next_day_infection_prob)

    # E[V(k')] = sum over j of P(k' = j) * V(j).
    return distribution @ next_values


def expected_realized_payoff(graph, profile, pi, beta, gamma, L_day, c, v):
    """Return the expected group payoff today, scored as the benchmark scores it."""
    # This is the "today" part of the lookahead objective (decision (i)). It
    # must match realized_daily_payoffs in game/multiday_game.py, which for
    # each person:
    #   - subtracts L_day if they are infected at the END of the day,
    #   - subtracts c if they stay home, or adds v per attending neighbor.
    # Each active edge therefore adds 2v to the group (v to each end).
    #
    # Why not the daily CE objective: that LP charges L_day / gamma per NEW
    # infection, which already counts the whole illness. Here today's cost
    # is only today's infected person-days; later days are left to V_{t+1},
    # so nothing is counted twice.
    #
    # The end-of-day infection state is exactly tomorrow's starting state, so
    # its probabilities come from next_day_infection_probabilities.
    infection_probabilities = next_day_infection_probabilities(graph, profile, pi, beta, gamma)

    # Expected infected person-days at the end of today, at L_day each.
    infection_term = -L_day * np.sum(infection_probabilities)

    # Home cost: c for each person who stays home.
    home_term = -c * profile.count("H")

    # 2v per active edge (v to each end).
    contact_term = 2*v*active_contacts(graph, profile)

    return infection_term + home_term + contact_term


def next_count_distributions(probabilities):
    """Batched next_count_distribution: the last axis holds the N people."""
    # Same one-person-at-a-time update as next_count_distribution, applied to
    # every leading index at once, so exact_count_transition can handle all
    # subsets and profiles in one numpy pass instead of a million Python calls.
    probabilities = np.asarray(probabilities, dtype=float)
    n_people = probabilities.shape[-1]
    distribution = np.zeros(probabilities.shape[:-1] + (n_people + 1,))
    distribution[..., 0] = 1.0
    for person in range(n_people):
        p = probabilities[..., person, None]
        updated = (1 - p) * distribution
        updated[..., 1:] += p * distribution[..., :-1]
        distribution = updated
    return distribution


def exact_count_transition(graph, beta, gamma):
    """Return transition[k, profile, k'] = P(k' infected tomorrow | exactly k now, profile)."""
    # Fix for the independence belief. That belief reads "k infected" as
    # "each person infected with prob k / N, independently", so it forgets
    # every day WHO is infected and redraws: from k = 1 with everyone home it
    # says P(k' = 0) = (1 - 0.1 * 0.8)^10 = 0.43, but the real chance is
    # gamma = 0.2 (one specific person must recover).
    #
    # Exact-count belief: exactly k people are infected; the recommender does
    # not know who, so every group S of k people is equally likely. For one S
    # and one profile, tomorrow's events are independent across people
    # (sis_step draws each person separately), with
    #   person in S:      still infected with prob 1 - gamma (home or not),
    #   person not in S:  infected with prob 1 - (1 - beta)^m if they attend,
    #                     where m = attending neighbors who are in S; 0 if home.
    # So k' given S is Poisson-binomial (next_count_distributions), and the
    # transition is its average over all C(N, k) groups S.
    #
    # The recommender still sees only (t, k), so this uses no information
    # daily CE lacks. It does not depend on the day, so it is computed once.
    # Shape: (N + 1, number of profiles, N + 1), profiles in the order of
    # all_action_profiles(graph).
    n_people = graph.number_of_nodes()
    profiles = all_action_profiles(graph)
    attend = np.array([[action == "A" for action in profile] for profile in profiles], dtype=float)  # (P, N)
    adjacency = nx.to_numpy_array(graph, nodelist=range(n_people))                                  # (N, N)
    transition = np.zeros((n_people + 1, len(profiles), n_people + 1))

    for k in range(n_people + 1):
        # One row per group S of size k: in_S[s, j] = 1 if person j is in S.
        in_S = np.array([[person in group for person in range(n_people)]
                         for group in combinations(range(n_people), k)], dtype=float)  # (M, N)
        in_S = in_S[:, None, :]        # (M, 1, N), broadcasts against profiles
        attends = attend[None, :, :]   # (1, P, N)

        # BLANK 1 (line below): replace `...` with m[s, p, i], the number of
        # person i's neighbors who are in S AND attend under profile p.
        # Step 1: (in_S * attends) is 1 for "infected and attending", shape (M, P, N).
        # Step 2: multiply by the adjacency matrix with @ to sum that over each
        #         person's neighbors (adjacency[j, i] = 1 if j and i are neighbors,
        #         and it is symmetric, so x @ adjacency sums x_j over neighbors j).
        # Example on the path 0 - 1 - 2, S = {1}, everyone attends:
        #   x = [0, 1, 0], x @ adjacency = [1, 0, 1] (both leaves see the center).
        infected_neighbors = (in_S * attend) @ adjacency

        # BLANK 2 (line below): replace `...` with each person's probability of
        # being infected tomorrow, shape (M, P, N), from the two cases above:
        #   in S:      1 - gamma
        #   not in S:  attends * (1 - (1 - beta) ** infected_neighbors)
        # Combine with in_S as a 0/1 switch: in_S * (case 1) + (1 - in_S) * (case 2).
        # Example (path, S = {1}, everyone attends, beta = 0.04, gamma = 0.2):
        #   [0.04, 0.8, 0.04].
        probabilities = in_S * (1 - gamma) + (1 - in_S) * attends * (1 - (1 - beta) ** infected_neighbors)

        # Distribution of k' for every (S, profile): shape (M, P, N + 1).
        distributions = next_count_distributions(probabilities)

        # BLANK 3 (line below): replace `...` with the average over the groups
        # S (axis 0), since every group of size k is equally likely.
        transition[k] = distributions.mean(axis=0)

    return transition


def solve_lookahead_ce(graph, pi, beta, L_day, gamma, c, v, next_values, *, next_counts=None):
    """Return (lottery over profiles, its objective value) for lookahead CE today."""
    # The linear program, with one probability x_p per attendance profile p:
    #     maximize    sum_p x_p * [ expected realized payoff today of p
    #                               + E[V_{t+1}(k') | p] ]
    #     subject to  daily CE's obedience constraints, x_p >= 0, sum_p x_p = 1.
    # The constraints are taken unchanged from game/: people still judge a
    # recommendation by their own one-day payoff, exactly as under daily CE.
    # Only the objective changes, from daily CE's one-day group cost to
    # today's realized payoff plus the value of tomorrow.
    #
    # linprog MINIMIZES, so pass the NEGATIVE of the values we want to maximize.
    profiles = all_action_profiles(graph)

    # Reuse daily CE's constraint arrays; its objective (first output) is not used.
    _, A_ub, b_ub, A_eq, b_eq = lp_arrays_with_contact_value(graph, pi, beta, L_day, gamma, c, v)

    if next_counts is None:
        # Independence belief (the original method 1): today's realized payoff
        # + value of tomorrow, one entry per LP column.
        profile_values = np.array([expected_realized_payoff(graph, p, pi, beta, gamma, L_day, c, v) + expected_next_value(graph, p, pi, beta, gamma, next_values) for p in profiles])
    else:
        # Exact-count belief: next_counts[p, j] = P(k' = j | profile p), the row
        # transition[k] of exact_count_transition. Both the infection cost of
        # today and the value of tomorrow come from this one distribution, so
        # the two parts of the objective use the same prediction.
        # Contact part, unchanged: 2v per active edge, c per person at home.
        contact_part = np.array([2 * v * active_contacts(graph, p) - c * p.count("H") for p in profiles])
        counts = np.arange(graph.number_of_nodes() + 1)

        # BLANK (line below): replace `...` with one value per profile, shape (P,):
        #   - L_day * E[k' | p]  +  contact_part[p]  +  E[V_{t+1}(k') | p].
        # Both expectations are a matrix-vector product with next_counts:
        #   E[k' | p] for every p is  next_counts @ counts,
        #   E[V(k') | p] for every p is  next_counts @ next_values.
        # Example: one profile with next_counts = [[0.2, 0.8]], L_day = 10,
        #   contact_part = [0], next_values = [5, -3]:
        #   -10 * 0.8 + 0 + (0.2 * 5 + 0.8 * -3) = -8 - 1.4 = -9.4.
        profile_values = -L_day * (next_counts @ counts) + contact_part + next_counts @ next_values

    # linprog minimizes, so negate to maximize.
    objective = -profile_values

    result = linprog(c=objective, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                     bounds=(0, None), method="highs")
    if not result.success:
        raise RuntimeError(f"Lookahead CE solver failed: {result.message}")

    # Remove tiny negative roundoff and renormalize, as daily CE does.
    probabilities = np.maximum(result.x, 0.0)
    probabilities /= probabilities.sum()
    return probabilities, float(probabilities @ profile_values)


def belief_backward_induction(graph, days, beta, L_day, gamma, c, v, *, transition=None):
    """Return values[t, k] and lotteries[t][k] by backward induction on the belief model."""
    # Method 1 for V: no simulation. Under the independence belief, the state
    # is just (day t, infected count k), with pi = k / N, and the next state's
    # distribution comes from next_count_distribution. So the Bellman equation
    #     V_t(k) = max over obedient lotteries of
    #              [ payoff today + E[V_{t+1}(k')] ]
    # is exactly the optimal value of solve_lookahead_ce at pi = k / N with
    # next_values = V_{t+1}. This is backward_induction from tiny_mdp.py with
    # "choose A or H" replaced by "solve the lookahead LP".
    #
    # values[days, k] = 0: after the last day there is nothing left to earn.
    # The belief ignores that real infections cluster on the network, so these
    # values can differ from what the simulator produces; method 2 (Monte
    # Carlo) measures that difference.
    n_people = graph.number_of_nodes()
    values = np.zeros((days + 1, n_people + 1))
    lotteries = [[None] * (n_people + 1) for _ in range(days)]

    for t in range(days - 1, -1, -1):
        for k in range(n_people + 1):
            pi = k / n_people

            # Bellman step: the LP solves the max over obedient lotteries.
            # transition=None keeps the independence belief; otherwise use the
            # exact-count belief's row for this k (it does not depend on t).
            next_counts = None if transition is None else transition[k]
            lottery, value = solve_lookahead_ce(graph, pi, beta, L_day, gamma, c, v ,values[t+1],
                                                next_counts=next_counts)

            values[t, k] = value 
            lotteries[t][k] = lottery

    return values, lotteries


def run_lookahead_trajectory(
    graph, initial_infected, lotteries, willingness, beta, gamma, L_day, c, v,
    recommendation_rng, decision_rng, sis_rng, imitation_rng=None, *,
    infection_draws_by_day=None, recovery_draws_by_day=None,
):
    """Play a lottery table lotteries[t][k] on the simulator; same outputs as run_ce_trajectory."""
    # This mirrors run_ce_trajectory in game/multiday_game.py line by line,
    # with one change: instead of solving daily CE from today's prevalence,
    # it looks up a precomputed lottery for (day, number infected). The
    # recommender still sees only the day and the infected count, never who
    # is infected.
    #
    # Everything else is the benchmark's code, so the comparison is fair:
    #   - one profile drawn from the lottery with recommendation_rng (same call
    #     as draw_ce_recommendations),
    #   - people respond with actions_from_private_recommendations, the exact
    #     rule daily CE faces (conditional gain from the public lottery, then
    #     the V1 or V2 willingness rule),
    #   - run_one_day for SIS and realized payoffs, with the paired SIS draws,
    #   - the same imitation update.
    # A sanity check below feeds it daily CE's own lotteries and requires the
    # result to match run_ce_trajectory exactly.
    n_people = graph.number_of_nodes()
    profiles = all_action_profiles(graph)
    days = len(lotteries)

    infected = initial_infected.copy()
    willingness = willingness.copy()
    infection_history = [infected.copy()]
    willingness_history = [willingness.copy()]
    payoff_history, recommendation_history, action_history = [], [], []

    for day in range(days):
        infection_draws = None if infection_draws_by_day is None else infection_draws_by_day[day]
        recovery_draws = None if recovery_draws_by_day is None else recovery_draws_by_day[day]

        # BLANK 1 (line below): replace `...` with the number of infected people
        # at the start of today, as a Python int. infected is a boolean array,
        # so its sum counts the True entries. This count is ALL the recommender
        # observes. Example: infected = [False, True, False] gives 1.
        k = int(infected.sum())

        pi = k / n_people

        # BLANK 2 (line below): replace `...` with today's lottery: the entry of
        # the table for this day and this infected count.
        lottery = lotteries[day][k]

        # Draw one profile and send each person their part privately.
        index = recommendation_rng.choice(len(profiles), p=lottery)
        recommendations = "".join(profiles[index])

        # People respond exactly as under daily CE. Argument order follows
        # game/: (..., pi, beta, L_day, gamma, c, v, rng).
        actions = actions_from_private_recommendations(
            graph, recommendations, lottery, willingness, pi, beta, L_day, gamma, c, v, decision_rng)

        # SIS and realized payoffs from the benchmark. Here the order is
        # (..., beta, gamma, L_day, c, v, rng), as in run_one_day's signature.
        infected, payoffs = run_one_day(
            graph, infected, actions, beta, gamma, L_day, c, v, sis_rng,
            infection_draws=infection_draws, recovery_draws=recovery_draws)

        infection_history.append(infected.copy())
        payoff_history.append(payoffs)
        recommendation_history.append(recommendations)
        action_history.append(actions)

        if imitation_rng is not None:
            willingness = update_willingness(
                graph, willingness, imitation_payoffs(payoffs, None), imitation_rng)
        willingness_history.append(willingness.copy())

    return (
        np.stack(infection_history),
        np.stack(payoff_history),
        recommendation_history,
        action_history,
        np.stack(willingness_history),
    )


def daily_ce_lottery_table(graph, days, beta, L_day, gamma, c, v):
    """Return daily CE's lottery for every (day, infected count), cleaned as game/ does."""
    # Daily CE depends only on prevalence, so its policy is the same table on
    # every day. Used to check run_lookahead_trajectory against the benchmark.
    from network_game import solve_best_correlated_equilibrium_with_contact_value

    n_people = graph.number_of_nodes()
    row = []
    for k in range(n_people + 1):
        result = solve_best_correlated_equilibrium_with_contact_value(graph, k / n_people, beta, L_day, gamma, c, v)
        probabilities = np.maximum(result.x, 0.0)
        row.append(probabilities / probabilities.sum())
    return [row] * days


def compare_tables_once(graph, initial_infected, tables, seed, beta, gamma, L_day, c, v, *, behavior="v1"):
    """Run every lottery table in `tables` on the same seed; return one summary per table."""
    # Paired comparison, built like compare_policies_once in game/: every
    # policy faces the same disease draws, the same starting willingness and
    # the same decision and imitation streams. Then a payoff difference
    # between two tables on one seed comes from the tables, not from luck.
    #
    # Streams: spawn(7) in the same order as compare_policies_once, so a
    # given seed means the same SIS draws, willingness, and so on as in the
    # benchmark (only the first four plus willingness are used here). The
    # sanity check below relies on this to match the benchmark's daily_ce row.
    if behavior not in ("v1", "v2"):
        raise ValueError(f"behavior must be 'v1' or 'v2', got {behavior!r}")

    (sis_seed, decision_seed, imitation_seed, recommendation_seed, _revision_seed,
     willingness_seed, _shuffle_seed) = np.random.SeedSequence(seed).spawn(7)
    rng = np.random.default_rng

    n_people = graph.number_of_nodes()
    days = len(next(iter(tables.values())))

    # Drawn ONCE, outside the policy loop: every table starts from this array.
    willingness = initial_willingness(n_people, behavior, rng(willingness_seed))

    # Paired SIS draws: one infection and one recovery uniform per day and person.
    sis_draw_rng = rng(sis_seed)
    shared_draws = dict(
        infection_draws_by_day=sis_draw_rng.random((days, n_people)),
        recovery_draws_by_day=sis_draw_rng.random((days, n_people)),
    )

    # V1 has no imitation, V2 does (same switch as the benchmark).
    use_imitation = behavior != "v1"

    results = {}
    for name, lotteries in tables.items():
        # BLANK 1 (line below): replace `...` with a FRESH generator for the
        # recommendation stream, built from recommendation_seed with rng(...).
        # Why fresh: a generator remembers how many numbers it has handed out.
        # If two tables shared one generator object, the second table would
        # start where the first one stopped, and the pairing would be lost.
        # Building a new one from the same seed restarts the stream.
        # Example: rng(s).random() == rng(s).random() is True for any seed s.
        recommendation_rng = rng(recommendation_seed)

        # BLANK 2 (line below): replace `...` with the imitation stream: a
        # fresh generator from imitation_seed when use_imitation is True,
        # otherwise None (run_lookahead_trajectory skips imitation on None).
        # One line, Python's `x if condition else y`.
        imitation_rng = rng(imitation_seed) if use_imitation else None

        states, payoffs, recommendations, actions, willingness_history = run_lookahead_trajectory(
            graph, initial_infected, lotteries, willingness, beta, gamma, L_day, c, v,
            recommendation_rng, rng(decision_seed), rng(sis_seed), imitation_rng, **shared_draws)

        results[name] = summarize_trajectory(
            graph, states, payoffs, actions, recommendations, willingness_history)
    return results


def compare_tables_replicates(graph, initial_infected, tables, n_replicates, root_seed,
                              beta, gamma, L_day, c, v, *, behavior="v1"):
    """Return one row per replicate and table, in the format of run_policy_replicates."""
    # Same seed derivation as run_policy_replicates, so rows can go straight
    # into paired_payoff_difference_ci from game/.
    rows = []
    for replicate, child in enumerate(np.random.SeedSequence(root_seed).spawn(n_replicates)):
        seed = int(child.generate_state(1, dtype=np.uint64)[0])
        results = compare_tables_once(graph, initial_infected, tables, seed,
                                      beta, gamma, L_day, c, v, behavior=behavior)
        for policy, summary in results.items():
            rows.append({"replicate": replicate, "policy": policy, **summary})
    return rows


def monte_carlo_values(graph, initial_infected, lotteries, n_episodes, seed,
                       beta, gamma, L_day, c, v, *, behavior="v1"):
    """Estimate V_t(k) for a fixed lottery table by averaging simulated returns-to-go."""
    # Method 2 for V, step 1: Monte Carlo POLICY EVALUATION. Same idea as the
    # per-(t, n) baselines in tiny_mdp.py: run the policy many times on the
    # real simulator and, every time the state (day t, infected count k) is
    # visited, record the return-to-go G_t = r_t + r_{t+1} + ... + r_{last}.
    # The average of those G_t is V_t(k) for THIS table.
    #
    # Why bother when belief_backward_induction already gives V? The belief
    # treats each person as infected independently with prob k / N. On the
    # network that is wrong: infections cluster, and on the path it matters
    # whether the one infected person is the center or a leaf. Monte Carlo
    # uses the real simulator, so the gap between the two tables measures how
    # wrong the belief is. It still uses only (t, k) as the state, so the
    # recommender keeps the information daily CE has.
    #
    # Definition matches belief_backward_induction: V_t(k) is the expected
    # payoff from the START of day t (today's payoff included) to the end.
    #
    # Output: values[t, k] (NaN where (t, k) was never visited) and
    # counts[t, k] (how many visits). Cells never visited cannot be learned,
    # the exploration effect seen in tiny_mdp.py; the caller decides what to
    # use there.
    #
    # Streams: one child seed per episode and spawn(7) in the benchmark order,
    # exactly as compare_tables_once, so episodes are independent and use
    # training seeds that differ from the evaluation root_seed.
    if behavior not in ("v1", "v2"):
        raise ValueError(f"behavior must be 'v1' or 'v2', got {behavior!r}")

    n_people = graph.number_of_nodes()
    days = len(lotteries)
    totals = np.zeros((days, n_people + 1))
    counts = np.zeros((days, n_people + 1), dtype=int)
    rng = np.random.default_rng

    for child in np.random.SeedSequence(seed).spawn(n_episodes):
        (sis_seed, decision_seed, imitation_seed, recommendation_seed, _revision_seed,
         willingness_seed, _shuffle_seed) = child.spawn(7)
        willingness = initial_willingness(n_people, behavior, rng(willingness_seed))
        imitation_rng = rng(imitation_seed) if behavior != "v1" else None

        states, payoffs, _, _, _ = run_lookahead_trajectory(
            graph, initial_infected, lotteries, willingness, beta, gamma, L_day, c, v,
            rng(recommendation_seed), rng(decision_seed), rng(sis_seed), imitation_rng)

        # payoffs has shape (days, n_people): one row per day, one column per
        # person. The reward of the recommender is the GROUP payoff per day.
        # BLANK 1 (line below): replace `...` with the daily group rewards,
        # shape (days,). Sum over people, i.e. over axis 1.
        # Example: payoffs = [[1, 2, 3], [4, 5, 6]] gives [6, 15].
        daily_rewards = payoffs.sum(axis=1)

        # Your returns_to_go from tiny_mdp.py: G_t for every day t, shape (days,).
        returns = returns_to_go(daily_rewards)

        # states has shape (days + 1, n_people): row t is who is infected at
        # the START of day t (row 0 = initial_infected, last row = after the
        # final day, which is not a decision state).
        for t in range(days):
            # BLANK 2 (two lines below): replace each `...`.
            #   k: the infected count at the start of day t, as a Python int
            #      (same as BLANK 1 of run_lookahead_trajectory, on row t).
            #   then add this episode's G_t to the running total of cell
            #   (t, k), and add 1 to its visit count.
            # Example: states[t] = [False, True, False], returns[t] = -20.0
            #   gives k = 1, totals[t, 1] += -20.0, counts[t, 1] += 1.
            k = int(states[t].sum())
            totals[t,k] += returns[t]
            counts[t,k] +=1
            

    # BLANK 3 (line below): replace `...` with the average return per cell,
    # NaN where counts is 0. np.where(condition, a, b) picks a where condition
    # is True, b elsewhere. Divide by np.maximum(counts, 1) so numpy never
    # divides by zero (those cells are replaced by NaN anyway).
    # Example: totals = [[-40, 0]], counts = [[2, 0]] gives [[-20, nan]].
    values = np.where(counts > 0, totals / np.maximum(counts, 1), np.nan)
    return values, counts


def monte_carlo_policy_iteration(graph, initial_infected, days, n_iterations, n_episodes, seed,
                                 beta, gamma, L_day, c, v, *, behavior="v1", min_visits=200,
                                 transition=None):
    """Alternate Monte Carlo evaluation and lookahead-CE improvement, starting from belief DP."""
    # Method 2 for V, step 2: POLICY ITERATION, the loop at the heart of most
    # RL methods:
    #   evaluate:  run the current table on the simulator, learn V_t(k)
    #              (monte_carlo_values);
    #   improve:   at every (t, k), re-solve the lookahead LP with the learned
    #              V_{t+1} (solve_lookahead_ce) to get a new table;
    #   repeat.
    # The start is method 1's answer (belief DP), so iteration 0 asks: "the
    # belief said this table is optimal; does the real simulator agree?"
    #
    # Two approximations, stated so they can be defended:
    #   1. Cells (t, k) visited fewer than min_visits times are too noisy, so
    #      they keep the belief-DP value (the exploration effect from
    #      tiny_mdp.py: what the policy never visits, it cannot learn).
    #   2. The LP still predicts tomorrow's count k' with the independence
    #      belief (next_count_distribution); only the VALUE of each k' comes
    #      from the simulator. So the recommender still uses only (t, k).
    #
    # Each iteration uses its own child seed, so evaluations are independent
    # and none of them uses the evaluation root_seed 123.
    #
    # Returns the final values (days + 1, N + 1), the final table, and a
    # history list with (values, counts, lotteries) per iteration.
    n_people = graph.number_of_nodes()
    # transition=None starts from (and falls back to) the independence belief;
    # passing exact_count_transition(...) uses the exact-count belief for the
    # start, the fallback values, and the prediction of k' in the LP.
    belief_values, lotteries = belief_backward_induction(graph, days, beta, L_day, gamma, c, v,
                                                         transition=transition)
    values = belief_values.copy()
    history = []

    for iteration_seed in np.random.SeedSequence(seed).spawn(n_iterations):
        seed_int = int(iteration_seed.generate_state(1, dtype=np.uint64)[0])

        # Evaluate the current table on the real simulator.
        mc_values, counts = monte_carlo_values(graph, initial_infected, lotteries, n_episodes, seed_int,
                                               beta, gamma, L_day, c, v, behavior=behavior)

        # BLANK 1 (line below): replace `...` with the learned value table for
        # days 0..days-1, shape (days, N + 1): the Monte Carlo value where the
        # cell was visited at least min_visits times, the belief-DP value
        # (belief_values[:days]) elsewhere. Same np.where pattern as BLANK 3
        # of monte_carlo_values.
        # Example: counts = [[500, 3]], mc_values = [[-20, -90]],
        #   belief_values[:days] = [[-25, -70]], min_visits = 200 -> [[-20, -70]].
        learned = np.where(counts >= min_visits, mc_values, belief_values[:days])

        # After the last day nothing is left: keep the row of zeros at the end.
        values = np.vstack([learned, np.zeros(n_people + 1)])

        # Improve: re-solve the lookahead LP at every (t, k).
        new_lotteries = [[None] * (n_people + 1) for _ in range(days)]
        for t in range(days):
            for k in range(n_people + 1):
                # BLANK 2 (line below): replace `...` with the value table the
                # LP should look ahead to from day t. Today's decision is
                # judged by the value of TOMORROW's state, so it is one row of
                # `values` (which row?). Same as in belief_backward_induction.
                next_values = values[t + 1]
                new_lotteries[t][k], _ = solve_lookahead_ce(
                    graph, k / n_people, beta, L_day, gamma, c, v, next_values,
                    next_counts=None if transition is None else transition[k])

        history.append((values.copy(), counts, lotteries))
        lotteries = new_lotteries

    return values, lotteries, history


if __name__ == "__main__":
    # Sanity checks on the 3-person path 0 - 1 - 2 (node 1 is the center).
    # Expected values are worked out by hand from the two-case formula with
    # beta = 0.04 and gamma = 0.2 (the benchmark values).
    path = nx.path_graph(3)
    beta, gamma = 0.04, 0.2

    # Nobody infected (pi = 0): nobody can be infected tomorrow.
    assert np.allclose(next_day_infection_probabilities(path, "AAA", 0.0, beta, gamma), 0.0)

    # Everyone home: only case 1 remains, pi * (1 - gamma) = 0.1 * 0.8 = 0.08.
    assert np.allclose(next_day_infection_probabilities(path, "HHH", 0.1, beta, gamma), 0.08)

    # Everyone attends, pi = 0.1, so pi * beta = 0.004.
    #   Center (k = 2): new = 1 - 0.996^2 = 0.007984;
    #                   0.08 + 0.9 * 0.007984 = 0.0871856.
    #   Leaves (k = 1): new = 0.004; 0.08 + 0.9 * 0.004 = 0.0836.
    assert np.allclose(next_day_infection_probabilities(path, "AAA", 0.1, beta, gamma),
                       [0.0836, 0.0871856, 0.0836])

    # Center home, leaves attend: each leaf has no attending neighbor (k = 0),
    # so nobody can be newly infected; everyone is 0.08.
    assert np.allclose(next_day_infection_probabilities(path, "AHA", 0.1, beta, gamma), 0.08)

    # gamma = 1: everyone infected now recovers, so only case 2 remains.
    # Leaves under "AAA": 0.9 * 0.004 = 0.0036.
    assert np.isclose(next_day_infection_probabilities(path, "AAA", 0.1, beta, 1.0)[0], 0.0036)

    # pi = 1: everyone is infected now; with gamma = 0.2 each stays infected
    # with probability 0.8, and there is nobody susceptible to infect.
    assert np.allclose(next_day_infection_probabilities(path, "AAA", 1.0, beta, gamma), 0.8)

    print("next_day_infection_probabilities: all sanity checks pass")

    # next_count_distribution. Expected values come from counting by hand or
    # from the binomial formula, which applies when every p is the same.
    from math import comb

    assert np.allclose(next_count_distribution([]), [1.0])
    assert np.allclose(next_count_distribution([0.3]), [0.7, 0.3])
    # Two fair coins: 0, 1, or 2 heads with probabilities 1/4, 1/2, 1/4.
    assert np.allclose(next_count_distribution([0.5, 0.5]), [0.25, 0.5, 0.25])
    # Certain outcomes: two people surely infected, one surely not.
    assert np.allclose(next_count_distribution([1.0, 0.0, 1.0]), [0, 0, 1, 0])
    # Equal probabilities: Binomial(3, 0.2), P(j) = C(3, j) 0.2^j 0.8^(3-j).
    assert np.allclose(next_count_distribution([0.2] * 3),
                       [comb(3, j) * 0.2 ** j * 0.8 ** (3 - j) for j in range(4)])
    # Different probabilities, using the "everyone attends" values above:
    # P(0) = product of (1 - p_i), P(3) = product of p_i, total 1, and the
    # mean equals the sum of the p_i.
    p = np.array([0.0836, 0.0871856, 0.0836])
    distribution = next_count_distribution(p)
    assert np.isclose(distribution[0], np.prod(1 - p)) and np.isclose(distribution[3], np.prod(p))
    assert np.isclose(distribution.sum(), 1.0)
    assert np.isclose(distribution @ np.arange(4), p.sum())

    print("next_count_distribution: all sanity checks pass")

    # expected_next_value. Expected values use only facts already checked:
    # the distribution sums to 1 and its mean is the sum of the probabilities.
    zero = np.zeros(4)
    assert np.isclose(expected_next_value(path, "AAA", 0.1, beta, gamma, zero), 0.0)

    # A constant V gives that constant back, because probabilities sum to 1.
    assert np.isclose(expected_next_value(path, "AAA", 0.1, beta, gamma, np.full(4, -7.0)), -7.0)

    # V(j) = j gives the expected number infected: for "AAA" at pi = 0.1 that
    # is 0.0836 + 0.0871856 + 0.0836 = 0.2543856.
    assert np.isclose(expected_next_value(path, "AAA", 0.1, beta, gamma, np.arange(4.0)), 0.2543856)

    # Everyone home: each person is infected tomorrow with probability 0.08,
    # so V(j) = -j gives -3 * 0.08 = -0.24.
    assert np.isclose(expected_next_value(path, "HHH", 0.1, beta, gamma, -np.arange(4.0)), -0.24)

    # If V falls as k' rises, a profile that spreads less infection must look
    # better: "AHA" (no contacts) beats "AAA" (two active edges).
    falling = -10.0 * np.arange(4.0)
    assert (expected_next_value(path, "AHA", 0.1, beta, gamma, falling)
            > expected_next_value(path, "AAA", 0.1, beta, gamma, falling))

    # Wrong length is a caller bug and must fail loudly.
    try:
        expected_next_value(path, "AAA", 0.1, beta, gamma, np.zeros(3))
        raise AssertionError("expected a ValueError for a length-3 value table")
    except ValueError:
        pass

    print("expected_next_value: all sanity checks pass")

    # expected_realized_payoff. Hand values on the path with pi = 0.1,
    # beta = 0.04, gamma = 0.2, L_day = 10, c = 0.05, v = 0.14, using the
    # infection probabilities checked above.
    L_day, c, v = 10.0, 0.05, 0.14
    # Everyone home: 3 * (-10 * 0.08) - 3 * 0.05 = -2.4 - 0.15 = -2.55.
    assert np.isclose(expected_realized_payoff(path, "HHH", 0.1, beta, gamma, L_day, c, v), -2.55)
    # Everyone attends: -10 * 0.2543856 + 2 edges * 2 * 0.14 = -2.543856 + 0.56.
    assert np.isclose(expected_realized_payoff(path, "AAA", 0.1, beta, gamma, L_day, c, v), -1.983856)
    # Leaves attend, center home: -10 * 0.24 - 0.05, no active edges.
    assert np.isclose(expected_realized_payoff(path, "AHA", 0.1, beta, gamma, L_day, c, v), -2.45)

    # Independent check against the benchmark code itself: start each run with
    # every person infected with probability pi (the independence belief),
    # play one day with run_one_day from game/, and average the realized group
    # payoff. Over 50000 runs the standard error is about 0.03, so 0.15 is
    # about five standard errors.
    from multiday_game import run_one_day
    rng = np.random.default_rng(2024)
    for profile in ("AAA", "HAH", "AAH"):
        totals = []
        for _ in range(50000):
            infected = rng.random(3) < 0.1
            _, payoffs = run_one_day(path, infected, profile, beta, gamma, L_day, c, v, rng)
            totals.append(payoffs.sum())
        formula = expected_realized_payoff(path, profile, 0.1, beta, gamma, L_day, c, v)
        assert abs(np.mean(totals) - formula) < 0.15, (profile, np.mean(totals), formula)

    print("expected_realized_payoff: all sanity checks pass")

    # solve_lookahead_ce. These checks use properties of the LP, not values
    # produced by the function itself.
    from network_game import solve_best_correlated_equilibrium_with_contact_value

    profiles = all_action_profiles(path)
    _, A_ub, _, _, _ = lp_arrays_with_contact_value(path, 0.1, beta, L_day, gamma, c, v)

    def lookahead_value(lottery, next_values):
        return sum(q * (expected_realized_payoff(path, p, 0.1, beta, gamma, L_day, c, v)
                        + expected_next_value(path, p, 0.1, beta, gamma, next_values))
                   for q, p in zip(lottery, profiles))

    falling = -40.0 * np.arange(4.0)  # each infected person tomorrow costs 40
    lottery, value = solve_lookahead_ce(path, 0.1, beta, L_day, gamma, c, v, falling)

    # A lottery: non-negative, sums to 1, and obedient (A_ub @ x <= 0 is the
    # obedience constraint as daily CE writes it).
    assert np.all(lottery >= 0) and np.isclose(lottery.sum(), 1.0)
    assert np.all(A_ub @ lottery <= 1e-9)

    # The returned value is the objective of the returned lottery.
    assert np.isclose(value, lookahead_value(lottery, falling))

    # Daily CE's lottery satisfies the same constraints, so it is feasible
    # here too; the lookahead optimum can only be at least as good under the
    # lookahead objective.
    daily = solve_best_correlated_equilibrium_with_contact_value(path, 0.1, beta, L_day, gamma, c, v)
    daily_lottery = np.maximum(daily.x, 0.0) / np.maximum(daily.x, 0.0).sum()
    assert value >= lookahead_value(daily_lottery, falling) - 1e-9

    # Adding a constant K to every V(k) adds exactly K to the optimal value,
    # because probabilities sum to 1 (the optimal lottery's value shifts by K).
    _, shifted_value = solve_lookahead_ce(path, 0.1, beta, L_day, gamma, c, v, falling + 5.0)
    assert np.isclose(shifted_value, value + 5.0)

    # Nobody infected (pi = 0): nobody can be infected tomorrow, so V adds the
    # same V(0) to every profile and the best lottery maximizes contacts:
    # everyone attends, value = 2 edges * 2v + V(0) = 0.56 + 3.0.
    lottery, value = solve_lookahead_ce(path, 0.0, beta, L_day, gamma, c, v, np.array([3.0, 0, 0, 0]))
    assert np.isclose(lottery[profiles.index(("A", "A", "A"))], 1.0) and np.isclose(value, 3.56)

    print("solve_lookahead_ce: all sanity checks pass")

    # belief_backward_induction. Hand values on the path with v = 0.14.
    values, lotteries = belief_backward_induction(path, 3, beta, L_day, gamma, c, v)

    # After the last day there is nothing left.
    assert np.allclose(values[3], 0.0)

    # k = 0: nobody is ever infected, so every day everyone attends and earns
    # 2 edges * 2v = 0.56. With d days left, V = 0.56 * d.
    assert np.allclose(values[:3, 0], [0.56 * 3, 0.56 * 2, 0.56 * 1])

    # k = 3 on the last day (pi = 1): nobody is susceptible, so attending is
    # free; each person stays infected with probability 0.8, so the expected
    # infection cost is -10 * 3 * 0.8 = -24, plus 0.56 from contacts.
    assert np.isclose(values[2, 3], -23.44)

    # The last day's row only looks one day ahead with V = 0 afterwards, so it
    # must equal solve_lookahead_ce with next_values = 0 (checked above).
    for k in range(4):
        assert np.isclose(values[2, k], solve_lookahead_ce(path, k / 3, beta, L_day, gamma, c, v, np.zeros(4))[1])

    # More infected people today can only make the future worse.
    for t in range(3):
        assert np.all(np.diff(values[t]) < 0), t

    # Every stored lottery is a probability vector.
    assert all(np.isclose(lotteries[t][k].sum(), 1.0) for t in range(3) for k in range(4))

    print("belief_backward_induction: all sanity checks pass")

    # run_lookahead_trajectory. The key check: given daily CE's own lotteries,
    # it must reproduce run_ce_trajectory from game/ exactly, on the same
    # seeds, for both behavior rules (V1: willingness 0, no imitation;
    # V2: random willingness with imitation).
    from multiday_game import run_ce_trajectory

    days = 14
    table = daily_ce_lottery_table(path, days, beta, L_day, gamma, c, v)
    start = np.array([False, True, False])  # the center is infected on day 0
    for label, start_willingness, imitate in (("V1", np.zeros(3), False),
                                               ("V2", np.random.default_rng(8).random(3), True)):
        for seed in range(5):
            draws_rng = np.random.default_rng(1000 + seed)
            shared = dict(infection_draws_by_day=draws_rng.random((days, 3)),
                          recovery_draws_by_day=draws_rng.random((days, 3)))
            def streams():
                return dict(recommendation_rng=np.random.default_rng(seed),
                            decision_rng=np.random.default_rng(seed + 100),
                            sis_rng=np.random.default_rng(seed + 200),
                            imitation_rng=np.random.default_rng(seed + 300) if imitate else None)
            ours = run_lookahead_trajectory(path, start, table, start_willingness, beta, gamma, L_day, c, v,
                                            **streams(), **shared)
            bench = run_ce_trajectory(path, start, days, start_willingness, beta, gamma, L_day, c, v,
                                      **streams(), **shared)
            assert np.array_equal(ours[0], bench[0]), (label, seed)   # infections
            assert np.allclose(ours[1], bench[1]), (label, seed)      # payoffs
            assert ours[2] == bench[2] and ours[3] == bench[3]        # recommendations, actions
            assert np.allclose(ours[4], bench[4]), (label, seed)      # willingness

    print("run_lookahead_trajectory: all sanity checks pass")


    # compare_tables_once / compare_tables_replicates.
    from multiday_game import compare_policies_once, paired_payoff_difference_ci

    uniform = [[np.full(len(profiles), 1 / len(profiles))] * 4] * days
    groups = np.array([0, 1, 0])  # group label per person; only the benchmark rotation uses it
    for behavior in ("v1", "v2"):
        for seed in (11, 12, 13):
            # (a) With daily CE's table, the "daily_ce" summary must equal the
            # benchmark's daily_ce row for the same seed: same streams, same code.
            ours = compare_tables_once(path, start, {"daily_ce": table}, seed,
                                       beta, gamma, L_day, c, v, behavior=behavior)["daily_ce"]
            bench = compare_policies_once(path, groups, start, days, seed, beta, gamma, L_day, c, v,
                                          behavior=behavior)["daily_ce"]
            assert ours == bench, (behavior, seed, ours, bench)

            # (b) Pairing: the same table entered twice under two names gives
            # identical summaries (each policy restarts every stream). Daily
            # CE's lotteries on the path put all mass on one profile, so the
            # draw would not reveal a shared stream; a uniform lottery over all
            # 8 profiles does (each draw then changes who is told A or H).
            twice = compare_tables_once(path, start, {"a": uniform, "b": uniform}, seed,
                                        beta, gamma, L_day, c, v, behavior=behavior)
            assert twice["a"] == twice["b"], (behavior, seed)

    # (c) Hence the paired difference of a table with itself is exactly 0 with
    # a zero-width interval.
    rows = compare_tables_replicates(path, start, {"a": uniform, "b": uniform}, 20, 5,
                                     beta, gamma, L_day, c, v, behavior="v2")
    assert paired_payoff_difference_ci(rows, "a", "b", np.random.default_rng(0)) == (0.0, 0.0, 0.0)

    print("compare_tables_once / compare_tables_replicates: all sanity checks pass")


    # monte_carlo_values. Expected values come from cases with a known answer.
    # (a) Nobody infected on day 0: nobody can ever be infected, every day
    # everyone attends (pi = 0) and earns 2 edges * 2v = 0.56. The return is
    # deterministic: V_t(0) = 0.56 * (14 - t), every episode visits (t, 0).
    nobody = np.zeros(3, dtype=bool)
    mc_values, mc_counts = monte_carlo_values(path, nobody, table, 50, 7, beta, gamma, L_day, c, v)
    assert np.allclose(mc_values[:, 0], 0.56 * (days - np.arange(days)))
    assert np.all(mc_counts[:, 0] == 50) and np.all(mc_counts[:, 1:] == 0)
    assert np.all(np.isnan(mc_values[:, 1:]))

    # (b) No transmission (beta = 0): new infections are impossible, each
    # infected person recovers independently with prob gamma, and the payoff
    # does not depend on WHO is infected. Then the independence belief is
    # exact, so Monte Carlo must agree with belief_backward_induction (checked
    # by hand above) on every well-visited cell, up to sampling noise.
    # Tolerance: one return lies in [-14 * 10 * 3, 14 * 0.56] (at most 3
    # people infected for 14 days), so its sd is at most half that width,
    # about 214; with >= 2000 visits, 5 standard errors is <= 24. Real noise
    # is far smaller (only the center's recovery is random), so 1.0 is used
    # and should pass with a wide margin.
    exact_values, exact_lotteries = belief_backward_induction(path, days, 0.0, L_day, gamma, c, v)
    mc_values, mc_counts = monte_carlo_values(path, start, exact_lotteries, 4000, 8, 0.0, gamma, L_day, c, v)
    well_visited = mc_counts >= 2000
    assert well_visited[0, 1] and well_visited.sum() >= days  # (0, 1) and many more
    assert np.allclose(mc_values[well_visited], exact_values[:days][well_visited], atol=1.0)

    print("monte_carlo_values: all sanity checks pass")


    # monte_carlo_policy_iteration.
    # (a) min_visits larger than n_episodes: no cell is ever trusted, so the
    # learned values are the belief values and re-solving reproduces the
    # belief-DP table exactly (method 1, verified above). v = 0.28 because
    # there the last days' lotteries are mixed and depend on V (see the
    # comparison above), so looking ahead to the wrong row changes the table.
    pi_values, pi_lotteries, pi_history = monte_carlo_policy_iteration(
        path, start, 3, 2, 30, 9, beta, gamma, L_day, c, 0.28, min_visits=31)
    belief3_values, belief3_lotteries = belief_backward_induction(path, 3, beta, L_day, gamma, c, 0.28)
    assert np.allclose(pi_values, belief3_values)
    assert all(np.allclose(pi_lotteries[t][k], belief3_lotteries[t][k]) for t in range(3) for k in range(4))
    assert len(pi_history) == 2

    # (b) No transmission (beta = 0): attending carries no risk and contacts
    # pay 2v > 0, while staying home costs c, so by hand the best lottery at
    # every (t, k) puts probability 1 on everyone attending, whatever V says
    # (V cannot differ across profiles when nobody can be infected).
    _, b0_lotteries, _ = monte_carlo_policy_iteration(
        path, start, days, 2, 300, 10, 0.0, gamma, L_day, c, v)
    everyone = profiles.index(("A", "A", "A"))
    assert all(np.isclose(b0_lotteries[t][k][everyone], 1.0) for t in range(days) for k in range(4))

    print("monte_carlo_policy_iteration: all sanity checks pass")


    # exact_count_transition. Expected values by hand on the path 0 - 1 - 2.
    T = exact_count_transition(path, beta, gamma)
    assert T.shape == (4, 8, 4) and np.allclose(T.sum(axis=2), 1.0)
    all_home = profiles.index(("H", "H", "H"))
    all_attend = profiles.index(("A", "A", "A"))

    # Nobody infected: nobody can be infected tomorrow.
    assert np.allclose(T[0, :, 0], 1.0)

    # One infected, everyone home: no transmission, so k' = 0 exactly when
    # that person recovers: P = gamma = 0.2 (the independence belief says 0.43
    # on 10 people; here on 3 it would say (1 - 0.8 / 3)^3 = 0.39).
    assert np.allclose(T[1, all_home], [0.2, 0.8, 0.0, 0.0])

    # One infected, only the center attends: a contact needs BOTH ends to
    # attend, so nobody can be newly infected (if S = {1}, the leaves are
    # home; if S is a leaf, that leaf is home). Same answer as everyone home.
    assert np.allclose(T[1, profiles.index(("H", "A", "H"))], [0.2, 0.8, 0.0, 0.0])

    # One infected, everyone attends. Average over S = {0}, {1}, {2}:
    #   S = {1} (center): leaves infected w.p. 0.04 each, center stays 0.8,
    #     P(k' = 0) = 0.2 * 0.96^2 = 0.18432, E[k'] = 0.8 + 0.08 = 0.88;
    #   S = {0} or {2} (a leaf): only the center is exposed (0.04),
    #     P(k' = 0) = 0.2 * 0.96 = 0.192, E[k'] = 0.84.
    #   Average: P(k' = 0) = (0.18432 + 2 * 0.192) / 3 = 0.18944,
    #            E[k'] = (0.88 + 2 * 0.84) / 3 = 0.853333.
    assert np.isclose(T[1, all_attend, 0], 0.18944)
    assert np.isclose(T[1, all_attend] @ np.arange(4), 0.88 / 3 + 2 * 0.84 / 3)

    # No transmission (beta = 0): k' ~ Binomial(k, 0.8) for every profile.
    from math import comb
    T0 = exact_count_transition(path, 0.0, gamma)
    for k in range(4):
        binomial = [comb(k, j) * 0.8 ** j * 0.2 ** (k - j) if j <= k else 0.0 for j in range(4)]
        assert np.allclose(T0[k], binomial), k

    # Everyone infected: nobody is susceptible, so k' ~ Binomial(3, 0.8) too.
    assert np.allclose(T[3], [comb(3, j) * 0.8 ** j * 0.2 ** (3 - j) for j in range(4)])

    print("exact_count_transition: all sanity checks pass")


    # Lookahead with the exact-count belief (next_counts / transition).
    # (a) Plumbing: feed the INDEPENDENCE belief's own next-count rows through
    # the new path; it must reproduce the original method 1 exactly, because
    # E[k'] = sum_i p_i is exactly the infection cost expected_realized_payoff uses.
    independence = np.array([[next_count_distribution(next_day_infection_probabilities(path, p, k / 3, beta, gamma))
                              for p in profiles] for k in range(4)])
    old_values, old_lotteries = belief_backward_induction(path, 3, beta, L_day, gamma, c, 0.28)
    new_values, new_lotteries = belief_backward_induction(path, 3, beta, L_day, gamma, c, 0.28, transition=independence)
    assert np.allclose(old_values, new_values)
    assert all(np.allclose(old_lotteries[t][k], new_lotteries[t][k]) for t in range(3) for k in range(4))

    # (b) Hand value, last day (V = 0 afterwards), everyone infected: nobody
    # is susceptible, so every profile has E[k'] = 3 * 0.8 = 2.4; attending is
    # free and earns contacts: -10 * 2.4 + 0.56 = -23.44 (v = 0.14), as before.
    exact = exact_count_transition(path, beta, gamma)
    exact_values, _ = belief_backward_induction(path, 1, beta, L_day, gamma, c, v, transition=exact)
    assert np.isclose(exact_values[0, 3], -23.44)

    # (c) Hand value, last day, one infected, v = 0, c = 0.05, exact-count
    # belief. The infected person stays infected w.p. 0.8 whatever happens,
    # so the cost is at least -8, and each person at home costs 0.05.
    #   Center home, leaves attend (A H A): no active edge (every edge touches
    #     the center), so no new risk: -8 - 0.05 = -8.05.
    #   Everyone attends: saves 0.05 but adds E[new infections] =
    #     0.853333 - 0.8 = 0.0533 (from the hand check above), i.e. -0.53.
    #   Center and one leaf attend: one active edge, new infection only when
    #     one end of it is the infected person: (0.04 + 0.04) / 3, i.e. -0.27.
    # So A H A is best, and it is obedient (leaves risk nothing by attending;
    # the center would face two attending leaves). Value -8.05.
    exact_values, _ = belief_backward_induction(path, 1, beta, L_day, gamma, c, 0.0, transition=exact)
    assert np.isclose(exact_values[0, 1], -8.05)

    print("lookahead with exact-count belief: all sanity checks pass")
