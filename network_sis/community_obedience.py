import numpy as np
from game.contact_value_payoff import attendance_gain
from network_sis.sis_experiment import attendance
from network_sis.network_communities import build_community_world
from game.contact_value_payoff import attendance_gain, extra_infection_cost

def attending_contact_counts(graph, present):
    """For each person, count neighbors who are attending today."""
    counts = np.zeros(graph.number_of_nodes(), dtype=int)

    # for each person in graph.nodes,
    # count neighbor that present[neighbor] == True
    # save into counts[person]
    for person in graph.nodes:
        for neighbor in graph.neighbors(person):
            if present[neighbor]:
                counts[person] += 1

    return counts

def deviation_flags(present, counts, pi, beta, L_day, gamma, c, v):
    """Return gains, home-day deviations, and attend-day deviations."""
    gains = np.array([
        attendance_gain(int(k), pi, beta, L_day, gamma, c, v)
        for k in counts
    ])

    home_deviates = (~present) & (gains > 1e-12)
    attend_deviates = present & (gains < -1e-12)
    return gains, home_deviates, attend_deviates

def prevalence_at_start(path, day, number_people):
    """Fraction infected before the update on this day."""
    if not 0 <= day < len(path) - 1:
        raise ValueError("day must be between 0 and horizon - 1")
    return float(path[day]) / number_people

def evaluate_one_day(
    graph, groups, path, day, start_day, switch_days,
    beta, L_day, gamma, c, v,
):
    pi = prevalence_at_start(path, day, graph.number_of_nodes())
    present = attendance(day + start_day, groups, "rotating", switch_days)
    counts = attending_contact_counts(graph, present)
    gains, home, attend = deviation_flags(
        present, counts, pi, beta, L_day, gamma, c, v
    )
    return pi, present, counts, gains, home, attend

def summarize_one_run(
    graph, groups, path, start_day, switch_days,
    beta, L_day, gamma, c, v,
):
    """Count deviation opportunities and choices across one trajectory."""
    summary = {
        "home_slots": 0,
        "home_deviations": 0,
        "attend_slots": 0,
        "attend_deviations": 0,
        "alive_home_slots": 0,
        "alive_home_deviations": 0,
        "alive_attend_slots": 0,
        "alive_attend_deviations": 0,
    }

    # The path includes day H, but decisions occur only on days 0 through H-1.
    for day in range(len(path) - 1):
        # call evaluate_one_day() with this day and unpack its output.
        pi, present, _, _, home, attend = evaluate_one_day(graph, groups, path, day, start_day, switch_days, beta, L_day, gamma, c, v)

        # Count each scheduled person-day and each profitable deviation.
        daily = {
            "home_slots": int(np.count_nonzero(~present)),
            "home_deviations": int(np.count_nonzero(home)),
            "attend_slots": int(np.count_nonzero(present)),
            "attend_deviations": int(np.count_nonzero(attend)),
        }
        for key, value in daily.items():
            summary[key] += value

        # include this day only if infection exists at its start.
        if pi > 0:
            for key, value in daily.items():
                summary["alive_" + key] += value

    return summary

def summarize_saved_run(data, world_index, rep, split_name, switch_days,
                        L_day, c, v):
    """Evaluate obedience for one saved rotating-schedule run."""
    number_worlds = int(data["number_worlds"])
    runs_per_world = int(data["runs_per_world"])

    # Rebuild the exact network and group assignments used for this world.
    # The experiment created all worlds from SeedSequence(2026).
    # select the seed sequence at world_index.
    world_sequence = np.random.SeedSequence(2026).spawn(number_worlds)[world_index]
    graph, _, _, groups, _, _ = build_community_world(world_sequence)

    # Select this split's saved infection path for one world and one run.
    # Saved keys have the form "paths_whole_rotating_1".
    # read the path for split_name, switch_days, world_index, and rep.
    path_key = f"paths_{split_name}_rotating_{switch_days}"
    path = data[path_key][world_index, rep]

    # The original simulation varied the schedule's starting phase by run.
    start_day = (world_index * runs_per_world + rep) % 14

    return summarize_one_run(
        graph, groups[split_name], path, start_day, switch_days,
        beta=float(data["beta"]),
        L_day=L_day,
        gamma=float(data["gamma"]),
        c=c,
        v=v,
    )
    
    
def summarize_saved_world(data, world_index, split_name, switch_days,
                          L_day, c, v):
    """Add obedience counts across every saved run in one world."""
    number_worlds = int(data["number_worlds"])
    runs_per_world = int(data["runs_per_world"])

    # Recreate this world's graph and group assignments once.
    world_sequence = np.random.SeedSequence(2026).spawn(number_worlds)[world_index]
    graph, _, _, groups, _, _ = build_community_world(world_sequence)

    # This array has shape: runs_per_world × (horizon + 1).
    path_key = f"paths_{split_name}_rotating_{switch_days}"
    world_paths = data[path_key][world_index]

    totals = None
    for rep, path in enumerate(world_paths):
        # Match the starting phase used when this run was simulated.
        start_day = (world_index * runs_per_world + rep) % 14

        # call summarize_one_run() for this path and store its dictionary.
        run_counts = summarize_one_run(
            graph, groups[split_name], path, start_day, switch_days,
            beta=float(data["beta"]),
            L_day=L_day,
            gamma=float(data["gamma"]),
            c=c,
            v=v,
        )

        # Use the first run to establish the dictionary keys.
        if totals is None:
            totals = {key: 0 for key in run_counts}
        for key, count in run_counts.items():
            totals[key] += count

    return totals

def summarize_all_worlds(data, split_name, switch_days, L_day, c, v):
    """Add deviation counts across every saved world and run."""
    totals = None

    for world_index in range(int(data["number_worlds"])):
        # TODO: summarize this world using summarize_saved_world().
        world_counts = summarize_saved_world(data, world_index, split_name, switch_days, L_day, c, v)

        # Add counts before computing shares, so every person-day
        # contributes once to the experiment-wide result.
        if totals is None:
            totals = {key: 0 for key in world_counts}
        for key, count in world_counts.items():
            totals[key] += count

    return totals


def contact_value_thresholds(counts, pi, beta, L_day, gamma, c):
    """Return each person's contact-value threshold when k is positive."""
    thresholds = np.full(len(counts), np.nan)

    for person, k in enumerate(counts):
        # With no attending neighbors, v cannot change this person's gain.
        if k == 0:
            continue

        # Solve c + k*v - d(k) = 0 for v.
        # TODO: calculate this person's threshold using extra_infection_cost().
        thresholds[person] = (extra_infection_cost(k, pi, beta, L_day, gamma)-c)/k

    return thresholds

def collect_run_thresholds(graph, groups, path, start_day, switch_days,
                           beta, L_day, gamma, c):
    """Collect contact-value thresholds across one saved trajectory."""
    home_thresholds = []
    attend_thresholds = []
    home_zero_contacts = 0
    attend_zero_contacts = 0

    for day in range(len(path) - 1):
        # Use prevalence at the start of the decision day.
        pi = prevalence_at_start(path, day, graph.number_of_nodes())
        present = attendance(day + start_day, groups, "rotating", switch_days)
        counts = attending_contact_counts(graph, present)

        # TODO: calculate everyone's threshold from counts and today's pi.
        thresholds = contact_value_thresholds(counts, pi, beta, L_day, gamma, c)

        # A zero-contact person has no threshold in v.
        home_zero_contacts += int(np.count_nonzero((~present) & (counts == 0)))
        attend_zero_contacts += int(np.count_nonzero(present & (counts == 0)))

        # Keep thresholds for people with at least one attending neighbor.
        home_thresholds.extend(thresholds[(~present) & (counts > 0)])
        attend_thresholds.extend(thresholds[present & (counts > 0)])

    return (
        np.asarray(home_thresholds),
        np.asarray(attend_thresholds),
        home_zero_contacts,
        attend_zero_contacts,
    )
    
    
def collect_saved_world_thresholds(data, world_index, split_name, switch_days,
                                   L_day, c):
    """Collect thresholds from every saved run in one world."""
    number_worlds = int(data["number_worlds"])
    runs_per_world = int(data["runs_per_world"])

    # Rebuild the graph and groups once for this world.
    world_sequence = np.random.SeedSequence(2026).spawn(number_worlds)[world_index]
    graph, _, _, groups, _, _ = build_community_world(world_sequence)

    path_key = f"paths_{split_name}_rotating_{switch_days}"
    world_paths = data[path_key][world_index]

    all_home = []
    all_attend = []
    home_zero_total = 0
    attend_zero_total = 0

    for rep, path in enumerate(world_paths):
        start_day = (world_index * runs_per_world + rep) % 14

        # TODO: call collect_run_thresholds() for this path.
        home, attend, home_zero, attend_zero = collect_run_thresholds(
            graph, groups[split_name], path, start_day, switch_days,
            beta=float(data["beta"]),
            L_day=L_day,
            gamma=float(data["gamma"]),
            c=c,
        )

        all_home.append(home)
        all_attend.append(attend)
        home_zero_total += home_zero
        attend_zero_total += attend_zero

    return (
        np.concatenate(all_home),
        np.concatenate(all_attend),
        home_zero_total,
        attend_zero_total,
    )
    

def collect_all_world_thresholds(data, split_name, switch_days, L_day, c):
    """Collect contact-value thresholds across every saved world."""
    all_home = []
    all_attend = []
    home_zero_total = 0
    attend_zero_total = 0

    for world_index in range(int(data["number_worlds"])):
        # TODO: collect this world's thresholds and zero-contact counts.
        home, attend, home_zero, attend_zero = collect_saved_world_thresholds(data, world_index, split_name, switch_days, L_day, c)

        # Keep the arrays separate until every world has been processed.
        all_home.append(home)
        all_attend.append(attend)
        home_zero_total += home_zero
        attend_zero_total += attend_zero

    return (
        np.concatenate(all_home),
        np.concatenate(all_attend),
        home_zero_total,
        attend_zero_total,
    )
    

def welfare_break_even_v(data, split_a, split_b, switch_days, L_day):
    """Find v where two rotating splits have equal expected welfare."""
    label_a = f"{split_a}_rotating_{switch_days}"
    label_b = f"{split_b}_rotating_{switch_days}"

    paths_a = data[f"paths_{label_a}"]
    paths_b = data[f"paths_{label_b}"]
    contacts_a = data[f"contacts_{label_a}"]
    contacts_b = data[f"contacts_{label_b}"]

    # Count infected person-days at the end of each modeled day.
    # Exclude path day 0, matching the existing days 1–84 results table.
    # TODO 1: calculate A's mean infected person-days minus B's.
    extra_infected_days = paths_a[:, :, 1:].sum(axis=2).mean() - paths_b[:, :, 1:].sum(axis=2).mean()

    # Each contact array stores 84-day edge-days, one value per world.
    # TODO 2: calculate A's mean edge-days minus B's.
    extra_contact_days = contacts_a.mean() - contacts_b.mean()

    if extra_contact_days <= 0:
        raise ValueError("split_a must provide more active contact days")

    # Each active edge benefits two people, so its welfare value is 2*v.
    # Both rotating splits schedule 100 people home each day; c cancels.
    return L_day * extra_infected_days / (2 * extra_contact_days)


def world_welfare_differences(data, split_a, split_b, switch_days):
    """Return paired infection and contact differences for each world."""
    label_a = f"{split_a}_rotating_{switch_days}"
    label_b = f"{split_b}_rotating_{switch_days}"

    paths_a = data[f"paths_{label_a}"]
    paths_b = data[f"paths_{label_b}"]
    contacts_a = data[f"contacts_{label_a}"]
    contacts_b = data[f"contacts_{label_b}"]

    # Sum infected people over days 1–84 within each run.
    # Then average the 50 runs within each world; keep 20 world values.
    # TODO 1: compute A minus B infected person-days for every world.
    extra_infected_by_world = (paths_a[:, :, 1:].sum(axis=2).mean(axis=1) - paths_b[:, :, 1:].sum(axis=2).mean(axis=1))

    # Contact arrays already contain one 84-day edge-day total per world.
    # TODO 2: compute A minus B edge-days for every world.
    extra_contacts_by_world = contacts_a - contacts_b

    return extra_infected_by_world, extra_contacts_by_world

def deviation_counts_from_thresholds(thresholds, v):
    """Count predicted deviations at a chosen contact value."""
    home, attend, home_zero, attend_zero = thresholds

    # Home slots with k=0 always prefer attending because c>0.
    # For k>0, home deviation requires v to exceed the threshold.
    # TODO 1: count home deviations among slots with k>0.
    home_positive_deviations = np.count_nonzero(v > home)

    # An attending person prefers home when v is below their threshold.
    # Attending slots with k=0 do not deviate because c>0.
    # TODO 2: count attending deviations.
    attend_deviations = np.count_nonzero(v < attend)

    return {
        "home_slots": len(home) + home_zero,
        "home_deviations": home_zero + home_positive_deviations,
        "home_positive_slots": len(home),
        "home_positive_deviations": home_positive_deviations,
        "home_zero_slots": home_zero,
        "attend_slots": len(attend) + attend_zero,
        "attend_deviations": attend_deviations,
    }
    
def deviation_counts_from_sorted_thresholds(home_sorted, attend_sorted, v):
    """Count strict deviations using sorted threshold arrays."""
    # TODO 1: count home thresholds strictly below v.
    home_positive_deviations = np.searchsorted(home_sorted, v, side="left")

    # TODO 2: count attend thresholds strictly above v.
    attend_deviations = len(attend_sorted) - np.searchsorted(attend_sorted, v, side="right")

    return home_positive_deviations, attend_deviations


def prepare_sorted_world_thresholds(data, split_name, switch_days, L_day, c):
    """Cache sorted thresholds separately for each independent world."""
    prepared = []

    for world_index in range(int(data["number_worlds"])):
        # TODO: collect this world's four threshold outputs.
        home, attend, home_zero, attend_zero = collect_saved_world_thresholds(data, world_index, split_name, switch_days, L_day, c)

        prepared.append((
            np.sort(home),
            np.sort(attend),
            home_zero,
            attend_zero,
        ))

    return prepared


def pooled_deviation_shares(prepared, world_indices, v):
    """Pool deviation counts over a selected sample of worlds."""
    home_slots = 0
    home_positive_slots = 0
    home_zero_slots = 0
    home_positive_deviations = 0
    attend_slots = 0
    attend_deviations = 0

    for world_index in world_indices:
        home, attend, home_zero, attend_zero = prepared[world_index]

        # TODO: count both kinds of deviation using the sorted arrays.
        home_dev, attend_dev = deviation_counts_from_sorted_thresholds(home, attend, v)

        home_slots += len(home) + home_zero
        home_positive_slots += len(home)
        home_zero_slots += home_zero
        home_positive_deviations += home_dev
        attend_slots += len(attend) + attend_zero
        attend_deviations += attend_dev

    return {
        "home": (
            home_zero_slots + home_positive_deviations
        ) / home_slots,
        "home_k_positive": (
            home_positive_deviations / home_positive_slots
        ),
        "home_k_zero": home_zero_slots / home_slots,
        "attend": attend_deviations / attend_slots,
    }
    
    
def bootstrap_pair_obedience(
    data, comparison, switch_days, L_day, c,
    draws=1000, seed=417,
):
    """Resample worlds and recompute welfare and obedience together."""
    extra_infected, extra_contacts = world_welfare_differences(
        data, "whole", comparison, switch_days,
    )
    number_worlds = len(extra_infected)
    split_names = ("whole", comparison)
    metrics = ("home", "home_k_positive", "home_k_zero", "attend")

    # Cache graph-dependent thresholds once per split and world.
    prepared = {
        split_name: prepare_sorted_world_thresholds(
            data, split_name, switch_days, L_day, c,
        )
        for split_name in split_names
    }

    # Compute point estimates from the original 20 worlds.
    v_point = (
        L_day * extra_infected.mean()
        / (2 * extra_contacts.mean())
    )
    point_shares = {
        split_name: pooled_deviation_shares(
            prepared[split_name], range(number_worlds), v_point,
        )
        for split_name in split_names
    }

    # Store one v and one set of shares per bootstrap draw.
    v_draws = np.empty(draws)
    share_draws = {
        split_name: {
            metric: np.empty(draws) for metric in metrics
        }
        for split_name in split_names
    }

    rng = np.random.default_rng(seed)
    for draw in range(draws):
        world_indices = rng.integers(
            0, number_worlds, size=number_worlds,
        )

        # TODO 1: recompute v* using only the sampled worlds.
        v_draw = L_day * extra_infected[world_indices].mean() / (2 * extra_contacts[world_indices].mean())
        v_draws[draw] = v_draw

        for split_name in split_names:
            # TODO 2: pool this split's sampled worlds at v_draw.
            shares = pooled_deviation_shares(prepared[split_name], world_indices, v_draw)
            for metric in metrics:
                share_draws[split_name][metric][draw] = shares[metric]

    return {
        "v_point": v_point,
        "point_shares": point_shares,
        "v_draws": v_draws,
        "share_draws": share_draws,
    }