"""Stage 2 toy: a two-person, multi-day MDP small enough to solve by hand.

What the bandit lacked is that today's action changes tomorrow's state. Here
two people share one contact. Each day the recommender chooses a joint action:
"A" (both attend) or "H" (both stay home). It observes only n, the number of
infected people at the start of the day (0, 1, or 2), which plays the role of
prevalence in the real problem.

Model (a toy, chosen so the right answer is easy to derive by hand):
- Daily reward = 2v if both attend (one active edge) or -2c if both stay home,
  minus L_day for every person infected at the start of the day.
- If both attend and exactly one is infected (n = 1), the other becomes
  infected for the next day with probability beta.
- No recovery (gamma = 0), so n = 0 and n = 2 never change.

Why it is a useful test: attending always pays more TODAY (2v > -2c), so a
one-day-ahead recommender always says "A". But when n = 1, attending risks a
new infection that costs L_day on every remaining day. Looking ahead can say
"H". Backward induction gives the exact answer, so we can check whether
REINFORCE over whole episodes learns it.

Run from the repository root:
    PYTHONPATH=. .venv/bin/python reinforcement_learning/tiny_mdp.py
"""

import numpy as np

from reinforcement_learning.bandit_toy import grad_log_softmax, softmax_policy


# Toy parameters. They are not the calibrated model values; they are picked so
# the lookahead effect is large and easy to see: beta * L_day = 1.0 is much
# bigger than the one-day gain from attending, 2v + 2c = 0.3.
BETA = 0.1
V = 0.1
C = 0.05
L_DAY = 10.0


def tiny_step(n, action, rng, beta=BETA, v=V, c=C, L_day=L_DAY):
    """Return (reward today, infected count tomorrow) for state n and action."""
    if action not in ("A", "H"):
        raise ValueError(f"Unknown action {action!r}; expected 'A' or 'H'.")

    # Draw the infection uniform every day, whatever the state and action.
    # This keeps the random stream aligned across policies: day d always uses
    # the d-th draw, so two policies compared on the same seed face the same
    # luck (the same idea as the paired SIS draws in game/multiday_game.py).
    u = rng.random()

    # Contact benefit for one active edge (2v) or home cost for two people (2c).
    contact_or_home = 2 * v if action == "A" else -2 * c

    # Today's cost counts the people already infected at the start of the day.
    reward = contact_or_home - n * L_day

    # Infection can only spread when both attend and exactly one is infected.
    next_n = n

    # A uniform u falls below beta with probability beta.
    if action == "A" and n == 1 and u <= beta:
        next_n = 2

    return reward, next_n


ACTIONS = ("A", "H")


def backward_induction(days, beta=BETA, v=V, c=C, L_day=L_DAY):
    """Return exact values[t, n] and the optimal action policy[t][n] for every day and state."""
    # Why backward: on the last day there is no future, so the best action is
    # simply the one with the larger reward. Once the last day's values are
    # known, the day before can weigh today's reward against the expected
    # value of tomorrow, and so on back to day 0.
    #
    # values[t, n] is the best expected total reward from day t to the end,
    # starting with n infected. values[days, n] = 0: no days left, no reward.
    values = np.zeros((days + 1, 3))
    policy = [[None] * 3 for _ in range(days)]

    for t in range(days - 1, -1, -1):
        for n in range(3):
            q_values = {}
            for action in ACTIONS:
                # Today's reward is deterministic; reuse tiny_step's formula with
                # beta = 0 so it does not depend on the random draw.
                reward, _ = tiny_step(n, action, np.random.default_rng(0), 0.0, v, c, L_day)

                # The only random transition: n = 1 and both attend, so n becomes
                # 2 with probability beta. Otherwise n stays the same.
                p_infect = beta if (action == "A" and n == 1) else 0.0

                # Expected value of tomorrow: infection with p_infect, else unchanged.
                expected_next = p_infect * values[t+1, 2] + (1-p_infect) * values[t+1, n]

                # Q(n, action) = reward today + expected value of what follows.
                q_values[action] = reward + expected_next

            # Bellman: the value of a state is the best action's Q-value.
            values[t, n] = max(q_values.values())
            policy[t][n] = max(q_values, key=q_values.get)

    return values, policy


def run_episode(theta, start_n, policy_rng, env_rng, beta=BETA):
    """Play one episode with the softmax policy theta; return (states, actions, rewards)."""
    # theta has shape (days, 3, 2): one pair of logits for every day t and
    # every infected count n, over ACTIONS = ("A", "H"). So the policy is
    #     pi(action | t, n) = softmax(theta[t, n]).
    # This is the tabular version of the stage 4 recommender: it sees only the
    # day and the infected count, the same information daily CE uses.
    #
    # Two streams again: policy_rng picks actions, env_rng drives infections.
    # tiny_step uses exactly one env draw per day, so two policies run on the
    # same env seed face the same infection luck on every day.
    days = theta.shape[0]
    n = start_n
    states, actions, rewards = [], [], []

    for t in range(days):
        probabilities = softmax_policy(theta[t, n])

        # Draw an action index: 0 for "A", 1 for "H".
        a = policy_rng.choice(len(probabilities), p=probabilities)

        # Play the action (as a string) in the environment.
        reward, next_n = tiny_step(n, ACTIONS[a], env_rng, beta = beta, v = V, c = C, L_day = L_DAY)

        # Record what happened today, then move to tomorrow's state.
        states.append(n)
        actions.append(a)
        rewards.append(reward)
        n = next_n

    return states, actions, rewards


def returns_to_go(rewards):
    """Return G_t = r_t + r_{t+1} + ... + r_{last} for every day t."""
    # Credit assignment: which rewards should count when judging the action
    # taken on day t? Only today's and later ones. An action cannot change a
    # reward that was already paid before it, so including earlier rewards
    # would only add noise to the gradient, never signal.
    #
    # In the tiny MDP, staying home on day 0 costs a little today (-10.1 vs
    # -9.8) but protects day 1. G_0 adds day 1's reward to day 0's decision,
    # which is exactly what a one-day-ahead recommender ignores.
    #
    # Compute it backward in one pass: G_last = r_last, and each earlier day
    # adds its own reward to the running total from the day after.
    returns = np.zeros(len(rewards))
    running_total = 0.0

    for t in range(len(rewards) - 1, -1, -1):
        # Add day t's reward to G_{t+1}.
        running_total = running_total + rewards[t]
        returns[t] = running_total

    return returns


def reinforce_episode_update(theta, baselines, counts, states, actions, rewards, step_size):
    """Return (theta, baselines, counts) after one REINFORCE update from one episode."""
    # For every day t of the episode, with state n_t and action a_t:
    #     theta[t, n_t] += step_size * (G_t - b[t, n_t]) * grad log pi(a_t | t, n_t)
    # G_t is the return-to-go, so day 0's decision is judged by everything
    # that follows from it, not only by its own day.
    #
    # Baseline per (day, state): the average return-to-go seen so far in that
    # same (t, n). Returns here are always negative (infection costs dominate),
    # so without a baseline every action taken would be pushed down. With it,
    # an action is pushed up only when it did better than usual for that
    # (t, n). The baseline is read BEFORE it is updated with this episode, for
    # the same reason as in the bandit: it must not depend on today's action.
    #
    # Every gradient uses the theta that generated the episode, so all days are
    # updated against the same policy. Inputs are copied, never changed in place.
    returns = returns_to_go(rewards)
    new_theta = theta.copy()
    new_baselines = baselines.copy()
    new_counts = counts.copy()

    for t, (n, a, G) in enumerate(zip(states, actions, returns)):
        baseline = new_baselines[t, n]
        grad = grad_log_softmax(theta[t, n], a)

        # Policy-gradient step for (t, n), judged by the return-to-go.
        new_theta[t, n] += step_size * (G - baseline) * grad

        # Update the running average of returns for (t, n), after using it.
        new_counts[t, n] += 1

        # Incremental average: move toward G by 1/count of the gap.
        new_baselines[t, n] += (G-baseline) / new_counts[t,n]

    return new_theta, new_baselines, new_counts


def train_tiny(days, start_n, n_episodes, seed, step_size, use_baseline=True):
    """Train the tabular softmax policy with REINFORCE; return the final theta."""
    # Start from theta = 0 (each action has probability 1/2 in every (t, n))
    # and play n_episodes episodes from start_n, updating after each one.
    # The learner never sees beta, the reward formula, or backward_induction;
    # it only sees the states, actions, and rewards of the episodes it plays.
    #
    # Random streams: one for the policy's choices, one for the infections,
    # spawned from the same seed so a training run is reproducible.
    policy_seed, env_seed = np.random.SeedSequence(seed).spawn(2)
    policy_rng = np.random.default_rng(policy_seed)
    env_rng = np.random.default_rng(env_seed)

    theta = np.zeros((days, 3, 2))
    baselines = np.zeros((days, 3))
    counts = np.zeros((days, 3))

    for _ in range(n_episodes):
        # BLANK 1 (line below): replace `...` with one call to run_episode that
        # plays the CURRENT theta from start_n, using policy_rng and env_rng in
        # that order. It returns three lists: states, actions, rewards.
        states, actions, rewards = run_episode(theta, start_n, policy_rng, env_rng, beta = BETA)

        # BLANK 2 (line below): replace `...` with one call to
        # reinforce_episode_update, passing theta, baselines, counts, the three
        # lists from the episode, and step_size. It returns the new theta,
        # baselines, and counts, in that order.
        new_theta, new_baselines, counts = reinforce_episode_update(theta, baselines, counts, states, actions, rewards, step_size)

        theta = new_theta
        # Without a baseline, b stays 0 forever, so the update uses G itself.
        if use_baseline:
            baselines = new_baselines

    return theta


def forced_theta(days, choice):
    """Return logits that pick choice[t][n] ("A" or "H") with probability ~1."""
    # Helper for tests: a logit of +50 against 0 gives probability
    # 1 / (1 + e^-50), which is 1 to machine precision.
    theta = np.zeros((days, 3, 2))
    for t in range(days):
        for n in range(3):
            theta[t, n, ACTIONS.index(choice[t][n])] = 50.0
    return theta


if __name__ == "__main__":
    # Sanity checks. Expected values come from the model definition above,
    # with v = 0.1, c = 0.05, L_day = 10.
    rng = np.random.default_rng(0)

    # n = 0, attend: reward 2v = 0.2; nobody is infected, so nothing spreads.
    assert np.allclose(tiny_step(0, "A", rng), (0.2, 0))

    # n = 2, stay home: -2c - 2 * L_day = -0.1 - 20 = -20.1; stays at 2.
    assert np.allclose(tiny_step(2, "H", rng), (-20.1, 2))

    # n = 1, stay home: -0.1 - 10 = -10.1; no contact, so no spread.
    for _ in range(100):
        assert np.allclose(tiny_step(1, "H", rng), (-10.1, 1))

    # beta = 0 never infects; beta = 1 always infects (u < 1 always holds).
    assert tiny_step(1, "A", rng, beta=0.0)[1] == 1
    assert tiny_step(1, "A", rng, beta=1.0)[1] == 2

    # n = 1, attend: reward 0.2 - 10 = -9.8, and n becomes 2 with probability
    # beta = 0.1. Over 20000 draws one standard error is sqrt(0.1 * 0.9 / 20000),
    # about 0.002, so a tolerance of 0.01 is about five standard errors.
    rng = np.random.default_rng(1)
    outcomes = [tiny_step(1, "A", rng) for _ in range(20000)]
    assert all(np.isclose(reward, -9.8) for reward, _ in outcomes)
    assert abs(np.mean([next_n == 2 for _, next_n in outcomes]) - 0.1) < 0.01

    # Exactly one uniform is used per call, whatever the action: after one
    # call, the next draw equals the second draw of a fresh stream.
    for action in ("A", "H"):
        rng = np.random.default_rng(5)
        tiny_step(1, action, rng)
        assert rng.random() == np.random.default_rng(5).random(2)[1]

    print("tiny_step: all sanity checks pass")

    # backward_induction. Expected values worked out by hand in the module
    # docstring style: last day V(n) = 2v - n * L_day; day 0 compares
    # Q(A) - Q(H) = (2v + 2c) - beta * L_day = 0.3 - 1.0 at n = 1.
    values, policy = backward_induction(days=2)

    # Last day (t = 1): attend in every state; V = 0.2, -9.8, -19.8.
    assert policy[1] == ["A", "A", "A"]
    assert np.allclose(values[1], [0.2, -9.8, -19.8])

    # Day 0, n = 1: Q(H) = -10.1 + (-9.8) = -19.9;
    # Q(A) = -9.8 + 0.1 * (-19.8) + 0.9 * (-9.8) = -20.6. So H, value -19.9.
    # n = 0 and n = 2: actions do not change the state, so attend.
    assert policy[0] == ["A", "H", "A"]
    assert np.allclose(values[0], [0.4, -19.9, -39.6])

    # One day only: nothing to look ahead to, so always attend.
    assert backward_induction(days=1)[1][0] == ["A", "A", "A"]

    # Lower risk: beta = 0.02 gives beta * L_day = 0.2 < 0.3, so attending pays
    # even after looking ahead.
    assert backward_induction(days=2, beta=0.02)[1][0][1] == "A"

    # Three days, day 0, n = 1, using the day-0 values above as tomorrow:
    # Q(H) = -10.1 + (-19.9) = -30.0;
    # Q(A) = -9.8 + 0.1 * (-39.6) + 0.9 * (-19.9) = -31.67. So H.
    values, policy = backward_induction(days=3)
    assert policy[0][1] == "H" and np.isclose(values[0, 1], -30.0)

    print("backward_induction: all sanity checks pass")

    # run_episode. Expected values come from the hand-computed rewards of
    # tiny_step: A at n = 1 gives -9.8, H at n = 1 gives -10.1, A at n = 2
    # gives 0.2 - 20 = -19.8.
    optimal = forced_theta(2, [["A", "H", "A"], ["A", "A", "A"]])
    always_attend = forced_theta(2, [["A", "A", "A"], ["A", "A", "A"]])

    # Optimal policy from n = 1: H on day 0 (no spread possible), A on day 1.
    states, actions, rewards = run_episode(optimal, 1, np.random.default_rng(0), np.random.default_rng(1))
    assert states == [1, 1] and actions == [1, 0] and np.allclose(rewards, [-10.1, -9.8])

    # Always attend with beta = 1: the infection spreads on day 0 for sure.
    states, actions, rewards = run_episode(always_attend, 1, np.random.default_rng(0),
                                           np.random.default_rng(1), beta=1.0)
    assert states == [1, 2] and actions == [0, 0] and np.allclose(rewards, [-9.8, -19.8])

    # Average return of always attend from n = 1 should match the hand value
    # Q(A) = -20.6 from backward induction. The return is -29.6 with
    # probability 0.1 and -19.6 otherwise, so its standard deviation is
    # 10 * sqrt(0.1 * 0.9) = 3; over 20000 episodes one standard error is
    # 3 / sqrt(20000), about 0.02, and 0.1 is five standard errors.
    policy_rng, env_rng = np.random.default_rng(2), np.random.default_rng(3)
    returns = [sum(run_episode(always_attend, 1, policy_rng, env_rng)[2]) for _ in range(20000)]
    assert abs(np.mean(returns) - (-20.6)) < 0.1

    print("run_episode: all sanity checks pass")

    # returns_to_go. Expected values are sums written out by hand, and the
    # last check uses an independent formula (reversed cumulative sum).
    assert np.allclose(returns_to_go([1.0, 2.0, 3.0]), [6.0, 5.0, 3.0])
    assert np.allclose(returns_to_go([4.0]), [4.0])
    assert returns_to_go([]).shape == (0,)

    # The optimal tiny-MDP episode from n = 1: rewards -10.1 then -9.8, so
    # G_0 = -19.9 (the backward-induction value of day 0, n = 1) and G_1 = -9.8.
    assert np.allclose(returns_to_go([-10.1, -9.8]), [-19.9, -9.8])

    rewards = np.random.default_rng(0).normal(size=14)
    assert np.allclose(returns_to_go(rewards), np.cumsum(rewards[::-1])[::-1])

    print("returns_to_go: all sanity checks pass")

    # reinforce_episode_update. Hand values for one episode from n = 1 with
    # states [1, 1], actions [H, A] = [1, 0], rewards [-10.1, -9.8], so
    # G = [-19.9, -9.8]; theta = 0 so pi = [1/2, 1/2]; step_size 0.1; baselines 0.
    zeros = np.zeros((2, 3, 2))
    no_baseline, no_counts = np.zeros((2, 3)), np.zeros((2, 3))
    episode = ([1, 1], [1, 0], [-10.1, -9.8])

    theta, baselines, counts = reinforce_episode_update(zeros, no_baseline, no_counts, *episode, step_size=0.1)
    # Day 0, n = 1, action H: grad = [0 - 1/2, 1 - 1/2] = [-0.5, 0.5];
    # change = 0.1 * (-19.9 - 0) * [-0.5, 0.5] = [0.995, -0.995].
    assert np.allclose(theta[0, 1], [0.995, -0.995])
    # Day 1, n = 1, action A: grad = [0.5, -0.5];
    # change = 0.1 * (-9.8) * [0.5, -0.5] = [-0.49, 0.49].
    assert np.allclose(theta[1, 1], [-0.49, 0.49])
    # States the episode never visited keep their logits.
    assert np.allclose(theta[:, [0, 2]], 0.0)
    # First visit: the baseline becomes that visit's return, count 1.
    assert np.allclose(baselines[:, 1], [-19.9, -9.8]) and np.allclose(counts[:, 1], [1, 1])
    # Inputs were not modified in place.
    assert np.allclose(zeros, 0.0) and np.allclose(no_baseline, 0.0) and np.allclose(no_counts, 0.0)

    # Same episode again: now G - b = 0 on both days, so theta does not move
    # and the baselines stay put, while the counts reach 2.
    theta2, baselines2, counts2 = reinforce_episode_update(theta, baselines, counts, *episode, step_size=0.1)
    assert np.allclose(theta2, theta) and np.allclose(baselines2, baselines)
    assert np.allclose(counts2[:, 1], [2, 2])

    # step_size = 0: logits never move, but the baselines still learn.
    theta3, baselines3, _ = reinforce_episode_update(zeros, no_baseline, no_counts, *episode, step_size=0.0)
    assert np.allclose(theta3, 0.0) and np.allclose(baselines3[:, 1], [-19.9, -9.8])

    print("reinforce_episode_update: all sanity checks pass")

    # train_tiny. The target is the backward-induction policy, which was
    # checked by hand above: from n = 1, stay home on day 0 and attend after.
    # Only states the episodes keep reaching get learned. Once the policy
    # stays home on day 0, n stays 1, so n = 2 is almost never visited and its
    # logits barely move from 1/2. That is an exploration effect, not a bug, so
    # the check covers n = 1 on every day. The settings (step size 0.1, 2000
    # episodes) were tried on 20 seeds and learned the policy on all of them;
    # the 0.9 threshold is a loose check, not a computed value.
    for days in (2, 3):
        _, optimal_policy = backward_induction(days)
        theta = train_tiny(days, start_n=1, n_episodes=2000, seed=123, step_size=0.1)
        for t in range(days):
            best = ACTIONS.index(optimal_policy[t][1])
            assert softmax_policy(theta[t, 1])[best] > 0.9, (days, t)

    # The learned policy's average return should match the exact optimum
    # V_0(1) = -19.9 (2 days), which beats always attending (Q(A) = -20.6).
    theta = train_tiny(2, 1, 2000, seed=123, step_size=0.1)
    policy_rng, env_rng = np.random.default_rng(10), np.random.default_rng(11)
    learned = np.mean([sum(run_episode(theta, 1, policy_rng, env_rng)[2]) for _ in range(20000)])
    assert abs(learned - (-19.9)) < 0.1

    print("train_tiny: all sanity checks pass")
    print(f"  learned policy, 2 days from n = 1: mean return {learned:.2f} "
          f"(optimum -19.90, always attend -20.60)")

    # Demos (printed, not asserted): what breaks learning.
    def share_learning_home(**kwargs):
        days = kwargs.pop("days", 2)
        probs = [softmax_policy(train_tiny(days, 1, 2000, seed, **kwargs)[0, 1])[1] for seed in range(20)]
        return np.mean(probs), sum(p > 0.9 for p in probs)

    for label, kwargs in (
        ("step 0.1, baseline     ", dict(step_size=0.1)),
        ("step 0.1, no baseline  ", dict(step_size=0.1, use_baseline=False)),
        ("step 0.2, 3 days       ", dict(step_size=0.2, days=3)),
    ):
        mean_p, hits = share_learning_home(**kwargs)
        print(f"  {label}: mean P(H | day 0, n = 1) = {mean_p:.3f}, learned H in {hits}/20 seeds")
