"""Stage 1 toy: a K-armed bandit solved with REINFORCE.

A bandit is the one-day, no-state version of the recommender problem. Each
action k pays a random reward with an unknown mean mu_k, and the goal is to
learn a policy that puts most probability on the best action.

The policy is a softmax over K logits theta. This is the same kind of object
as the daily CE lottery: a probability vector over actions. In stage 4 the
actions will be the 1024 attendance profiles of the 10-person network.

Run from the repository root:
    PYTHONPATH=. .venv/bin/python reinforcement_learning/bandit_toy.py
"""

import numpy as np


def softmax_policy(theta):
    """Return action probabilities pi(k) = exp(theta_k) / sum_j exp(theta_j)."""
    theta = np.asarray(theta, dtype=float)

    # Why subtract the maximum first: exp(1000) overflows to inf, and inf/inf
    # is nan. Softmax does not change when the same constant is added to every
    # logit (the constant cancels between numerator and denominator), so
    # shifting by max(theta) keeps the answer exact while every exponent is
    # at most exp(0) = 1.

    shifted = theta - theta.max()

    # Unnormalized weights; every value now lies in (0, 1].
    weights = np.exp(shifted)

    # Normalize so the probabilities sum to 1.
    return weights / np.sum(weights)


def grad_log_softmax(theta, k):
    """Return the gradient of log pi(k) with respect to every logit theta_j."""
    # Why this is the core of REINFORCE: the policy-gradient estimate for one
    # sampled action k with reward R is R * grad log pi(k). So this vector says
    # how to move every logit to make action k more likely.
    #
    # Derivation: log pi(k) = theta_k - log(sum_j exp(theta_j)). The first term
    # depends only on theta_k, so its derivative is 1 when j = k and 0 otherwise.
    # The second term's derivative with respect to theta_j is
    # exp(theta_j) / sum_i exp(theta_i) = pi(j). Together:
    #     d log pi(k) / d theta_j = 1[j = k] - pi(j).
    probabilities = softmax_policy(theta)

    # One-hot vector for the sampled action: the 1[j = k] term.
    indicator = np.zeros_like(probabilities)

    # 1[j = k] equals 1 at the sampled action and 0 everywhere else.
    indicator[k] = 1.0

    # Apply 1[j = k] - pi(j) to every j at once: vector minus vector.
    return indicator - probabilities


def pull_arm(means, k, rng, noise_sd=1.0):
    """Return one noisy reward from arm k: its mean plus Gaussian noise."""
    # Why a noisy toy environment: the 14-day group payoff in the real problem
    # is noisy because SIS infections are random. A bandit with known means
    # mimics that noise while still letting us check the answer: the learner
    # should end up on the arm with the largest mean.
    #
    # The rng is passed in, never created here, so each experiment controls its
    # own random stream (same rule as SeedSequence(...).spawn in game/).

    noise = rng.normal(0, noise_sd)

    # Reward = the arm's mean + noise.
    return means[k] + noise


def reinforce_step(theta, means, action_rng, reward_rng, step_size, baseline=0.0, noise_sd=1.0):
    """Run one REINFORCE update and return (new theta, sampled arm, reward)."""
    # One step of learning:
    #   1. sample an arm k from the current policy pi_theta,
    #   2. pull it and observe a noisy reward R,
    #   3. move theta along (R - b) * grad log pi(k).
    # If R beats the baseline b, arm k becomes more likely; if R falls short,
    # it becomes less likely. Averaged over k ~ pi, (R - b) * grad log pi(k)
    # equals the true gradient of the expected reward, because the b term
    # averages to 0 (the score-function identity checked above).
    #
    # Two separate streams: choosing the arm and drawing the reward are
    # different sources of randomness, so they never share a generator.
    theta = np.asarray(theta, dtype=float)
    probabilities = softmax_policy(theta)

    # Draw one arm index 0..K-1 with the policy's probabilities.
    k = action_rng.choice(len(probabilities), p=probabilities)

    reward = pull_arm(means, k, reward_rng, noise_sd)

    # Policy-gradient update: theta + alpha * (R - b) * grad log pi(k).
    new_theta = theta + step_size*(reward - baseline) * grad_log_softmax(theta, k)

    return new_theta, k, reward


def train_bandit(means, n_steps, seed, step_size, noise_sd=1.0, use_baseline=True):
    """Run REINFORCE for n_steps from theta = 0; return (theta, rewards, baselines)."""
    # theta starts at 0, so the first policy is uniform: no arm is favored
    # before any reward is seen.
    #
    # Baseline: the average of the rewards seen BEFORE this step. It must not
    # include the current reward, otherwise b would depend on the sampled arm
    # and the gradient estimate would no longer be unbiased. It starts at 0
    # because no reward has been seen yet.
    #
    # Random streams: one for choosing arms, one for rewards, both spawned
    # from the same seed so a run is reproducible.
    action_seed, reward_seed = np.random.SeedSequence(seed).spawn(2)
    action_rng = np.random.default_rng(action_seed)
    reward_rng = np.random.default_rng(reward_seed)

    theta = np.zeros(len(means))
    running_mean = 0.0
    rewards, baselines = [], []

    for step in range(n_steps):
        # Without a baseline, b = 0 for every step.
        baseline = running_mean if use_baseline else 0.0
        theta, _, reward = reinforce_step(
            theta, means, action_rng, reward_rng, step_size, baseline, noise_sd)

        rewards.append(reward)
        baselines.append(baseline)

        # BLANK (line below): replace `...` with the running average after
        # adding this reward, updated incrementally (no need to store and
        # re-sum the list). Hint: after n rewards, the new average moves from
        # the old one toward the new reward by 1/n of the gap.
        running_mean += (reward - running_mean) / (step + 1)

    return theta, np.array(rewards), np.array(baselines)


if __name__ == "__main__":
    # Sanity checks. Each expected value is worked out by hand, not by
    # running softmax_policy.

    # Equal logits give equal probabilities: e^0 / (e^0 + e^0) = 1/2.
    assert np.allclose(softmax_policy([0.0, 0.0]), [0.5, 0.5])

    # theta = [0, ln 3]: weights are e^0 = 1 and e^(ln 3) = 3, total 4,
    # so the probabilities are 1/4 and 3/4.
    assert np.allclose(softmax_policy([0.0, np.log(3.0)]), [0.25, 0.75])

    # Shift invariance: adding 5 to every logit multiplies every weight by
    # e^5, which cancels in the ratio.
    theta = np.array([0.3, -1.2, 2.0])
    assert np.allclose(softmax_policy(theta + 5.0), softmax_policy(theta))

    # Overflow: theta = [1000, 0]. The second weight is e^(-1000) relative to
    # the first, which is 0 in floating point, so the answer is [1, 0], not nan.
    probabilities = softmax_policy([1000.0, 0.0])
    assert np.all(np.isfinite(probabilities))
    assert np.allclose(probabilities, [1.0, 0.0])

    # A probability vector: non-negative and summing to 1.
    probabilities = softmax_policy(np.random.default_rng(0).normal(size=1024))
    assert np.all(probabilities >= 0.0) and np.isclose(probabilities.sum(), 1.0)

    print("softmax_policy: all sanity checks pass")

    # grad_log_softmax. Hand values use 1[j = k] - pi(j) with the pi values
    # from the softmax checks above.

    # theta = [0, 0], pi = [1/2, 1/2], k = 0: [1 - 1/2, 0 - 1/2].
    assert np.allclose(grad_log_softmax([0.0, 0.0], 0), [0.5, -0.5])

    # theta = [0, ln 3], pi = [1/4, 3/4], k = 1: [0 - 1/4, 1 - 3/4].
    assert np.allclose(grad_log_softmax([0.0, np.log(3.0)], 1), [-0.25, 0.25])

    # The entries always sum to 0: sum_j 1[j = k] = 1 and sum_j pi(j) = 1.
    theta = np.array([0.3, -1.2, 2.0])
    for k in range(3):
        assert np.isclose(grad_log_softmax(theta, k).sum(), 0.0)

    # Finite differences on log pi(k), using the already verified softmax_policy:
    # (log pi_k(theta + h e_j) - log pi_k(theta - h e_j)) / (2h) approximates
    # the j-th entry of the gradient.
    h = 1e-6
    for k in range(3):
        numeric = []
        for j in range(3):
            step = np.zeros(3)
            step[j] = h
            numeric.append(
                (np.log(softmax_policy(theta + step)[k])
                 - np.log(softmax_policy(theta - step)[k])) / (2 * h)
            )
        assert np.allclose(grad_log_softmax(theta, k), numeric, atol=1e-6)

    # Score-function identity: averaging grad log pi(k) over k ~ pi gives 0,
    # because sum_k pi(k) (e_k - pi) = pi - pi. This is why subtracting a
    # baseline b from the reward does not bias the gradient: E[b * grad] = 0.
    pi = softmax_policy(theta)
    expected = sum(pi[k] * grad_log_softmax(theta, k) for k in range(3))
    assert np.allclose(expected, 0.0)

    print("grad_log_softmax: all sanity checks pass")

    # pull_arm. Expected values come from the definition reward = mean + noise.
    means = np.array([0.0, 1.0, 0.5])

    # No noise: the reward is exactly the arm's mean.
    for k in range(3):
        assert pull_arm(means, k, np.random.default_rng(0), noise_sd=0.0) == means[k]

    # Same seed, same reward: the function uses only the stream it is given.
    assert pull_arm(means, 2, np.random.default_rng(7)) == pull_arm(means, 2, np.random.default_rng(7))

    # Many pulls of arm 1 with noise_sd = 1: the sample mean should be within
    # about 3 standard errors of 1. One standard error is 1 / sqrt(20000), about
    # 0.007, so the tolerance is 0.03. The sample standard deviation should be
    # close to 1 by the same reasoning.
    rng = np.random.default_rng(1)
    draws = np.array([pull_arm(means, 1, rng) for _ in range(20000)])
    assert abs(draws.mean() - 1.0) < 0.03
    assert abs(draws.std() - 1.0) < 0.03

    print("pull_arm: all sanity checks pass")

    # reinforce_step. Expected logits are worked out by hand from
    # theta + alpha * (R - b) * (e_k - pi), given the arm k the step returns.

    # step_size = 0: nothing moves, whatever arm is drawn.
    new_theta, _, _ = reinforce_step([0.3, -0.2], [0.0, 1.0], np.random.default_rng(0),
                                     np.random.default_rng(1), step_size=0.0)
    assert np.allclose(new_theta, [0.3, -0.2])

    # theta = [0, 0] so pi = [1/2, 1/2]; no noise so R = mean of the drawn arm;
    # alpha = 0.1, b = 0. Arm 1 (mean 1): R = 1, grad = [-1/2, 1/2], so
    # theta becomes [-0.05, +0.05]. Arm 0 (mean 0): R = 0, so theta stays [0, 0].
    for seed in range(10):
        new_theta, k, reward = reinforce_step([0.0, 0.0], [0.0, 1.0], np.random.default_rng(seed),
                                              np.random.default_rng(99), step_size=0.1, noise_sd=0.0)
        expected = [-0.05, 0.05] if k == 1 else [0.0, 0.0]
        assert reward == float(k) and np.allclose(new_theta, expected)

    # Reward equal to the baseline: R - b = 0, so theta does not move.
    new_theta, _, _ = reinforce_step([0.4, 0.1], [2.0, 2.0], np.random.default_rng(3),
                                     np.random.default_rng(4), step_size=0.5, baseline=2.0, noise_sd=0.0)
    assert np.allclose(new_theta, [0.4, 0.1])

    # Arm frequencies follow pi: with theta = [0, ln 3] arm 1 should be drawn
    # about 3/4 of the time. Over 4000 steps with step_size 0 (theta fixed),
    # one standard error is sqrt(0.75 * 0.25 / 4000), about 0.007, so 0.03 is
    # about four standard errors.
    action_rng, reward_rng = np.random.default_rng(5), np.random.default_rng(6)
    arms = [reinforce_step([0.0, np.log(3.0)], [0.0, 1.0], action_rng, reward_rng, step_size=0.0)[1]
            for _ in range(4000)]
    assert abs(np.mean(arms) - 0.75) < 0.03

    print("reinforce_step: all sanity checks pass")

    # train_bandit.
    means = np.array([0.0, 1.0, 0.5])
    theta, rewards, baselines = train_bandit(means, n_steps=2000, seed=123, step_size=0.1)

    # The baseline at step t is the plain average of rewards 0..t-1, computed
    # here directly with np.mean (independent of the incremental update).
    assert baselines[0] == 0.0
    for t in (1, 2, 10, 500, 1999):
        assert np.isclose(baselines[t], rewards[:t].mean())

    # Learning: arm 1 has the largest mean, so after 2000 steps the policy
    # should put most of its probability there (theory: the gradient points
    # toward the best arm). The 0.9 threshold is a loose check, not a computed value.
    final_policy = softmax_policy(theta)
    assert np.argmax(final_policy) == 1 and final_policy[1] > 0.9

    print("train_bandit: all sanity checks pass")
    print(f"  final policy = {np.round(final_policy, 3)} (best arm is 1)")

    # Why the baseline matters: add 10 to every mean. The best arm is still
    # arm 1, but without a baseline every reward is about +10, so every drawn
    # arm gets pushed up and the signal is buried. Compare across seeds.
    shifted = means + 10.0
    for use_baseline in (True, False):
        final = [softmax_policy(train_bandit(shifted, 2000, seed, 0.01, use_baseline=use_baseline)[0])[1]
                 for seed in range(20)]
        label = "with baseline   " if use_baseline else "without baseline"
        print(f"  means + 10, {label}: mean pi(best arm) over 20 seeds = {np.mean(final):.3f}")
