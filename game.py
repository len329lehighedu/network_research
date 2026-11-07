from itertools import product
import numpy as np
from scipy.optimize import linprog

PLAYERS = (0, 1, 2)
ACTIONS = ("A", "H")


# Three players each choose A or H, giving 2^3 action profiles.
# This fixed order also indexes the eight lottery probabilities in the LP.
def all_action_profiles():
    """Return every possible combination of the three players' actions."""
    # use product(ACTIONS, repeat=...) then convert to list
    profiles = list(product(ACTIONS, repeat=len(PLAYERS)))
    return profiles

# On the complete three-person graph, k counts a player's attending peers.
# Each such peer is a possible workplace source of infection.
def count_other_attendees(profile, player):
    """Count attendees other than this player."""
    count = 0
    # loop through j in PLAYERS, skip if j == player,
    for j in PLAYERS:
        # count j that profile[j] == "A"
        if j != player and profile[j] == "A":
            count+=1
    return count

# Each attending peer is infectious and transmits with probability pi*beta.
# Independence gives q(k) = 1 - (1 - pi*beta)^k for a susceptible attendee.
def new_infection_probability(k, pi, beta):
    """Infection probability for an initially susceptible attendee."""
    return 1 - (1 - pi*beta)**k

# Infection status is unknown even to the player: initial infection costs L*pi.
# Home payoff is -L*pi-c; attendance adds -L*(1-pi)*q(k).
# This is a one-day game, so recovery does not enter the payoff.
def expected_payoff(profile, player, pi, beta, infection_cost, home_cost):
    """Expected one-day payoff for one player under one action profile."""
    k = count_other_attendees(profile, player)

    if profile[player] == "H":
        return -infection_cost * pi - home_cost  # -L*pi-c

    infection_probability = new_infection_probability(k, pi, beta)
    return -infection_cost*(pi + (1-pi)*infection_probability)  # -L*[pi + (1-pi)*infection_probability]

# A unilateral deviation changes one player's A/H choice and no other choice.
# Return a new tuple so the original action profile is unchanged.
def switch_action(profile, player):
    """Return a new profile with only this player's action switched."""
    changed = list(profile)
    if changed[player] == "H":
        changed[player] = "A"
    else:
        changed[player] = "H"
    return tuple(changed)

# Find nash equilibrium
# A pure Nash profile has no profitable unilateral action switch.
# The small tolerance treats numerical ties as indifference.
def is_nash_equilibrium(profile, pi, beta, infection_cost, home_cost):
    """Return True if no player benefits from switching alone."""
    for player in PLAYERS:
        current = expected_payoff(
            profile, player, pi, beta, infection_cost, home_cost
        )
        alternative_profile = switch_action(profile, player)
        alternative = expected_payoff(alternative_profile, player, pi, beta, infection_cost, home_cost)  # payoff of that player at alternative_profile

        if alternative > current + 1e-12:  # alternative greater than current?
            return False

    return True

# return a list of nash equilibria
# Apply the Nash condition to all eight profiles rather than assuming a form.
# At baseline parameters, the three two-attendee profiles pass.
def pure_nash_equilibria(pi, beta, infection_cost, home_cost):
    """Return all pure Nash equilibrium profiles."""
    equilibria = []
    for profile in all_action_profiles():
        # if profile is a Nash equilibrium, add to equilibria
        if (is_nash_equilibrium(profile, pi, beta, infection_cost, home_cost)):
            equilibria.append(profile)
    return equilibria

# compute total payoff
# Social welfare is the sum of the three players' expected one-day payoffs.
# The LP maximizes the lottery's expected value of this total.
def total_payoff(profile, pi, beta, infection_cost, home_cost):
    """Sum the three players' expected payoffs."""
    total = 0.0
    for player in PLAYERS:
        total += expected_payoff(profile, player, pi, beta, infection_cost, home_cost)
    return total

# compute obedience gain = payoff from current action - payoff when change action
# Obedience gain is payoff from following the assigned action minus deviating.
# Negative gain means the player prefers to switch at this profile.
def obedience_gain(profile, player, pi, beta, infection_cost, home_cost):
    """Payoff from obeying minus payoff from switching alone."""
    obey = expected_payoff(
        profile, player, pi, beta, infection_cost, home_cost
    )
    changed_profile = switch_action(profile, player)
    deviate = expected_payoff(changed_profile, player, pi, beta, infection_cost, home_cost)  # payoff of player at changed_profile
    return obey - deviate


# For player i recommended r, sum p(a)*gain_i(a) over profiles with a_i=r.
# The unnormalized sum has the same sign as the conditional gain if r occurs.
def recommendation_gain(
    probabilities, player, recommendation,
    pi, beta, infection_cost, home_cost
):
    """Weighted obedience gain for one player and recommendation."""
    total = 0.0
    profiles = all_action_profiles()

    for profile, probability in zip(profiles, probabilities):
        if profile[player] == recommendation:
            total += probability * obedience_gain(profile, player, pi, beta, infection_cost, home_cost)  # probability * obedience_gain()

    return total

# a function that check a random lottery: A valid lottery needs to have 8 probs, total = 1, and 
# A correlated equilibrium is a probability distribution over the eight profiles.
# Each of the three players has two nonnegative obedience sums, one per signal.
def is_correlated_equilibrium(
    probabilities, pi, beta, infection_cost, home_cost
):
    """Check probabilities and all six obedience constraints."""
    if len(probabilities) != len(all_action_profiles()):  # number of probs differ from number of profiles
        return False
    if any(p < -1e-12 for p in probabilities):  # a negative prob exist
        return False
    if abs(sum(probabilities) - 1.0) > 1e-12:  # total probs differ from 1
        return False

    for player in PLAYERS:
        for action in ACTIONS:
            gain = recommendation_gain(
                probabilities, player, action,
                pi, beta, infection_cost, home_cost
            )
            if gain < -1e-12:
                return False

    return True

# we want maximum total (probability x total payoff) for all profiles
# W[j] is the social welfare of profile j in all_action_profiles() order.
# The expected welfare of lottery x is the dot product W @ x.
def welfare_vector(pi, beta, infection_cost, home_cost):
    """Total payoff for each profile, in all_action_profiles() order."""
    values = []
    for profile in all_action_profiles():
        # TODO: tính total_payoff của profile rồi append vào values
        profile_total_payoff = total_payoff(profile, pi, beta, infection_cost, home_cost)
        values.append(profile_total_payoff)
    return values

# A set of obedience constraints. 
# For example, for player 0, the recommended action is "A": if a profile assigns "A" to player 0, 
# the `obedience_gain` value is applied; if a profile assigns "H" to player 0, the coefficient is 0.
# This row makes one obedience inequality linear in eight probabilities.
# Profiles assigning a different recommendation to this player get coefficient 0.
def obedience_row(
    player, recommendation, pi, beta, infection_cost, home_cost
):
    """One LP constraint row, ordered like all_action_profiles()."""
    row = []
    for profile in all_action_profiles():
        if profile[player] == recommendation:
            coefficient = obedience_gain(profile, player, pi, beta, infection_cost, home_cost)  # obedience_gain()
        else:
            coefficient = 0.0
        row.append(coefficient)
    return row

# get and label al obedience rows
# Three players times two possible recommendations yield six LP inequalities.
# labels identify the player and recommended action for each row.
def all_obedience_rows(pi, beta, infection_cost, home_cost):
    """Return labels and the six LP obedience rows."""
    labels = []
    rows = []

    for player in PLAYERS:
        for action in ACTIONS:
            labels.append((player, action))
            # add the corresponding obedience_row to rows
            rows.append(obedience_row(player, action, pi, beta, infection_cost, home_cost))

    return labels, rows

# objective = -W and A_ub = -R
# SciPy minimizes, so maximizing W @ x becomes minimizing -W @ x.
# Obedience R @ x >= 0 becomes -R @ x <= 0; equality enforces sum(x)=1.
# Nonnegative LP bounds make each x[j] a valid probability.
def lp_arrays(pi, beta, infection_cost, home_cost):
    """Build objective and constraints for scipy.optimize.linprog."""
    welfare = np.asarray(
        welfare_vector(pi, beta, infection_cost, home_cost), dtype=float
    )
    _, rows = all_obedience_rows(pi, beta, infection_cost, home_cost)

    objective = -welfare  # -welfare
    A_ub = -np.asarray(rows, dtype=float)  # A_ub = -R
    b_ub = np.zeros(len(rows))

    A_eq = np.ones((1, len(welfare)))
    b_eq = np.array([1.0])

    return objective, A_ub, b_ub, A_eq, b_eq


# Solve the eight-variable welfare-maximizing correlated-equilibrium LP.
# HiGHS returns result.x in profile order and result.fun = -optimal welfare.
def solve_best_correlated_equilibrium(
    pi, beta, infection_cost, home_cost
):
    """Find a correlated equilibrium with maximum total expected payoff."""
    objective, A_ub, b_ub, A_eq, b_eq = lp_arrays(
        pi, beta, infection_cost, home_cost
    )

    result = linprog(
        c=objective,  # objective
        A_ub=A_ub,    # A_ub
        b_ub=b_ub,    # b_ub
        A_eq=A_eq,    # A_eq
        b_eq=b_eq,    # b_eq
        bounds=(0, None),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(result.message)
    return result


# Players are exchangeable in this homogeneous complete-graph toy game.
# Sharing mass across profiles with equal attendance counts preserves CE and
# welfare while giving each player the same chance to attend.
def symmetrize_lottery(probabilities):
    """Share each attendance-count probability equally among matching profiles."""
    profiles = all_action_profiles()
    balanced = np.zeros(len(profiles))

    for attendees in range(len(PLAYERS) + 1):
        indices = [
            i for i, profile in enumerate(profiles)
            if profile.count("A") == attendees
        ]
        mass = sum(probabilities[i] for i in indices)   # sum probabilities[i] for i in indices
        for i in indices:
            balanced[i] = mass / len(indices)  # equally divide mass for the indices

    return balanced

# rotating c and pi
# Explore how Nash attendance changes when initial prevalence pi and home cost c vary.
# Two-attendee Nash profiles permit a fair one-day rotation lottery.
def print_rotation_sweep(beta, infection_cost):
    """Show equilibrium attendance as pi and home cost vary."""
    print("\nRotation sweep:")
    for pi in (0.1, 0.5, 0.9):
        for home_cost in (0.02, 0.05, 0.12):
            equilibria = pure_nash_equilibria(pi, beta, infection_cost, home_cost)  # pure_nash_equilibria(...)
            counts = sorted({
                profile.count("A") for profile in equilibria
            })
            rotation = 2 in counts  # does 2 in counts?
            print(
                f"pi={pi:.1f}, c={home_cost:.2f}: "
                f"attendees={counts}, rotation={rotation}"
            )

# calculating the range of c where rotation could happen, which pi fixed
# A two-attendee profile is Nash when its attendee accepts A against one peer
# and its person at home accepts H against two peers: d(1) <= c <= d(2).
# Here d(k) = L*(1-pi)*[1-(1-pi*beta)^k] is added infection cost.
def rotation_cost_interval(pi, beta, infection_cost):
    """Home-cost interval where two-attendee profiles are Nash equilibria."""
    lower = infection_cost * (1-pi) * new_infection_probability(1, pi, beta)  # infection_cost * (1-pi) * q(1)
    upper = infection_cost * (1-pi) * new_infection_probability(2, pi, beta)  # infection_cost * (1-pi) * q(2)
    return lower, upper

# Check the two-attendee Nash condition at pi=0,0.01,...,1.
# Printed points approximate the interval; they are not exact boundary roots.
def print_rotation_pi_grid(beta, infection_cost, home_cost):
    """Print pi values with rotation on a grid spaced by 0.01."""
    eligible = []

    for i in range(101):
        pi = i / 100
        low, high = rotation_cost_interval(pi, beta, infection_cost)
        if low <= home_cost <= high:  # home_cost within [low, high]?
            eligible.append(round(pi, 2))

    print(f"\nRotation pi grid at c={home_cost} (step 0.01):")
    print(eligible)

# Report the baseline game, optimal correlated lottery, and c/pi exploration.
# All displayed values use the same explicit parameter dictionary.
def main():
    params = dict(pi=0.1, beta=0.04, infection_cost=10, home_cost=0.05)
    print("Parameters:", params)
    profiles = all_action_profiles()
    print("All action profiles:")
    for profile in profiles:
        print(profile)

    nash_profiles = pure_nash_equilibria(**params)
    print("Pure Nash equilibria:", nash_profiles)

    result = solve_best_correlated_equilibrium(**params)  # giải LP với params
    balanced = symmetrize_lottery(result.x)  # cân bằng result.x

    fair_nash_welfare = sum(
    total_payoff(profile, **params) for profile in nash_profiles
    ) / len(nash_profiles)

    print("Fair Nash lottery total payoff:", round(fair_nash_welfare, 6))
    print("Optimal CE total payoff:", round(-result.fun, 6))
    print("CE welfare gain:", round(-result.fun - fair_nash_welfare, 6))
    print("Balanced lottery is CE:", is_correlated_equilibrium(balanced, **params))
    
    print("\nBalanced optimal CE probabilities:")
    for profile, probability in zip(profiles, balanced):
        if probability > 1e-8:
            print(profile, f"{probability:.6f}")
    
    print_rotation_sweep(params["beta"], params["infection_cost"])
    print_rotation_pi_grid(
    params["beta"], params["infection_cost"], params["home_cost"])

    low, high = rotation_cost_interval(
    params["pi"], params["beta"], params["infection_cost"]
    )
    print(f"Two-attendee Nash c interval: [{low:.6f}, {high:.6f}]")
    print("Current c supports rotation:", low <= params["home_cost"] <= high)
if __name__ == "__main__":
    main()
