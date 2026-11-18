"""Structural features of the connected 4–6 person graph atlas networks."""

import csv
from collections import defaultdict
from itertools import combinations

import networkx as nx
import numpy as np


def triangle_count(graph):
    """Return the number of distinct three-person triangles in a graph."""
    # NetworkX returns the number of triangles touching each individual node.
    node_counts = nx.triangles(graph)

    # Each triangle touches three nodes, so the sum counts it three times.
    return sum(node_counts.values()) // 3


def maximum_degree(graph):
    """Return the largest number of neighbors held by one person."""
    # Degree counts the edges incident to each node in this simple graph.
    degrees = dict(graph.degree())

    # The atlas graphs are nonempty, so a maximum degree always exists.
    return max(degrees.values())


def maximum_independent_set_size(graph):
    """Return the exact size of the largest set with no internal edges."""
    nodes = list(graph.nodes())

    # Try larger candidate sets first; the first valid size is the maximum.
    # At most six nodes are used here, so exhaustive search is small.
    for size in range(len(nodes), -1, -1):
        for chosen in combinations(nodes, size):
            # A candidate is valid only when none of its node pairs has an edge.
            independent = all(
                not graph.has_edge(u, v)
                for u, v in combinations(chosen, 2)
            )
            if independent:
                return size


def load_feature_records(csv_path, pi=0.1, c=0.05):
    """Join saved game outcomes to exact structural features by atlas ID."""
    atlas = nx.graph_atlas_g()
    records = []

    # The CSV has one row per network and parameter pair.
    with open(csv_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if float(row["pi"]) != pi or float(row["c"]) != c:
                continue

            atlas_id = int(row["atlas_id"])
            graph = atlas[atlas_id]
            assert graph.number_of_nodes() == int(row["n"])
            assert graph.number_of_edges() == int(row["edges"])

            best_pure_cost = float(row["best_pure_nash"])
            best_ce_cost = float(row["best_ce"])

            # A lower CE cost yields a positive gain over the pure benchmark.
            ce_gain = best_pure_cost - best_ce_cost

            records.append({
                "atlas_id": atlas_id,
                "n": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
                "pure_nash_count": int(row["pure_nash_count"]),
                "triangles": triangle_count(graph),
                "max_degree": maximum_degree(graph),
                "independent_set_size": maximum_independent_set_size(graph),
                "ce_gain": ce_gain,
            })

    return records


def summarize_by_feature(records, feature):
    """Summarize CE gains for each observed value of one network feature."""
    groups = defaultdict(list)
    for record in records:
        groups[record[feature]].append(record)

    summary = []
    for value, group in sorted(groups.items()):
        gains = [record["ce_gain"] for record in group]

        # Ignore differences that are only floating-point rounding error.
        improved = sum(gain > 1e-9 for gain in gains)

        summary.append({
            "value": value,
            "networks": len(group),
            "improved": improved,
            "improvement_rate": improved / len(group),
            "mean_gain": sum(max(0.0, gain) for gain in gains) / len(group),
        })

    return summary


def ols_hc1(design, outcome):
    """Least-squares coefficients and HC1 (heteroskedasticity-robust) standard errors.

    design: (n, p) array, one row per network, first column all ones (intercept).
    outcome: (n,) array, e.g. the CE gain of each network.
    Returns (coefficients, standard_errors), both shape (p,).
    """
    design = np.asarray(design, dtype=float)
    outcome = np.asarray(outcome, dtype=float)
    n, p = design.shape

    # Coefficients solve the normal equations X'X b = X'y. lstsq solves the
    # least-squares problem directly, which is more stable than inverting X'X.
    coefficients = np.linalg.lstsq(design, outcome, rcond=None)[0]

    # Residuals: what the fitted line leaves unexplained for each network.
    residuals = outcome - design @ coefficients

    # Sandwich estimator. "Bread" (X'X)^-1 is the usual OLS part; "meat"
    # X' diag(e^2) X lets each network have its own residual variance. Many
    # networks have CE gain exactly 0, so equal variances would be a poor guess.
    bread = np.linalg.inv(design.T @ design)
    meat = (design * residuals[:, None] ** 2).T @ design

    # HC1 rescales HC0 by n / (n - p), the same small-sample correction as the
    # usual s^2 = SSR / (n - p). It matters here: about 139 networks, ~5 columns.
    covariance = n / (n - p) * bread @ meat @ bread

    return coefficients, np.sqrt(np.diag(covariance))


def regression_design(records, features, size_levels=(5, 6)):
    """Design matrix: intercept, the listed features, and network-size dummies.

    Network size enters as dummies (fixed effects) rather than a straight line,
    so the alpha coefficient compares networks of the same size without assuming
    the CE gain changes linearly from 4 to 5 to 6 people. The smallest size (4)
    is the baseline, so it has no dummy; a dummy for every size plus the
    intercept would make the columns linearly dependent.
    Returns (design, column_names), design shape (len(records), 1 + len(features) + len(size_levels)).
    """
    column_names = ["intercept", *features, *(f"n={size}" for size in size_levels)]
    rows = []
    for record in records:
        feature_values = [float(record[name]) for name in features]
        size_dummies = [float(record["n"] == size) for size in size_levels]
        rows.append([1.0, *feature_values, *size_dummies])
    return np.array(rows), column_names


def ce_gain_regression(records, features, size_levels=(5, 6), tolerance=1e-9):
    """Regress the CE gain on network features with size fixed effects (HC1 SEs).

    Outcome: best pure Nash group cost minus best CE group cost, as in Report 5.
    Gains at or below `tolerance` are LP rounding noise (some are -1e-15), so
    they count as exactly 0, the same rule Report 5 uses to count a gain.
    Returns (column_names, coefficients, standard_errors).
    """
    gains = np.array([record["ce_gain"] for record in records])
    # outcome = ...  gains above `tolerance`, else 0.0
    outcome = np.where(gains > tolerance, gains, 0.0)

    # build X for these records
    design, column_names = regression_design(records, features, size_levels)
    # fit
    coefficients, standard_errors = ols_hc1(design, outcome)

    return column_names, coefficients, standard_errors


def print_ce_gain_regression(csv_path="game/atlas_contact_value_4_6.csv", pi=0.1, home_costs=(0.05, 0.12),
                             features=("independent_set_size", "edges")):
    """Print the Report 6 supplement table: CE gain on alpha, edges and size dummies.

    Only pi = 0.1 is used: at pi = 0.5 no atlas network has a CE gain, so the
    outcome is identically 0 there. The interval is coefficient +/- 1.96 SE
    (normal approximation, the statsmodels default for robust covariances).
    """
    print("| c | Term | Coefficient | HC1 SE | 95% CI | Networks | CE improves |")
    print("|---|---|---:|---:|---|---:|---:|")
    for c in home_costs:
        records = load_feature_records(csv_path, pi=pi, c=c)
        names, coefficients, standard_errors = ce_gain_regression(records, features)
        improved = sum(record["ce_gain"] > 1e-9 for record in records)
        for name, b, se in zip(names, coefficients, standard_errors):
            # 95% CI
            lower, upper = b - 1.96 * se, b + 1.96 * se
            print(f"| {c:.2f} | {name} | {b:+.6f} | {se:.6f} | [{lower:+.6f}, {upper:+.6f}] | "
                  f"{len(records)} | {improved} |")


if __name__ == "__main__":
    # (a) Exact linear outcome: y = 1 + 2*x1 + 0.5*x2 with no noise.
    # The fit must return (1, 2, 0.5) and every residual is 0, so the SEs are 0.
    x1 = np.array([1, 2, 2, 3, 4, 4, 5], dtype=float)
    x2 = np.array([3, 1, 4, 1, 5, 9, 2], dtype=float)
    X = np.column_stack([np.ones_like(x1), x1, x2])
    b, se = ols_hc1(X, 1 + 2 * x1 + 0.5 * x2)
    assert np.allclose(b, [1, 2, 0.5]) and np.allclose(se, 0, atol=1e-8), (b, se)

    # (b) Hand-worked simple regression: x = 0..3, y = (1, 3, 2, 5).
    # xbar = 1.5, ybar = 2.75, Sxx = 5, Sxy = 5.5 -> slope 1.1, intercept 1.1.
    # Residuals (-0.1, 0.8, -1.3, 0.6). HC0 slope variance
    #   = sum (x - xbar)^2 e^2 / Sxx^2 = 1.415 / 25 = 0.0566;
    # HC1 multiplies by n / (n - p) = 4 / 2, so the slope SE = sqrt(0.1132) = 0.33645.
    X = np.column_stack([np.ones(4), np.arange(4.0)])
    b, se = ols_hc1(X, [1, 3, 2, 5])
    assert np.allclose(b, [1.1, 1.1]) and np.isclose(se[1], 0.336452, atol=1e-6), (b, se)

    print("ols_hc1: all sanity checks pass")

    # regression_design on two hand-made records: a 4-person network (baseline,
    # both dummies 0) and a 6-person one (only the n=6 dummy is 1).
    toy = [{"n": 4, "independent_set_size": 2, "edges": 3},
           {"n": 6, "independent_set_size": 3, "edges": 7}]
    X, names = regression_design(toy, ("independent_set_size", "edges"))
    assert names == ["intercept", "independent_set_size", "edges", "n=5", "n=6"], names
    assert np.array_equal(X, [[1, 2, 3, 0, 0], [1, 3, 7, 0, 1]]), X

    # On the saved atlas slice: there are 6, 21 and 112 connected graphs with
    # 4, 5 and 6 nodes (a known count), so 139 rows and dummy sums 21 and 112.
    records = load_feature_records("game/atlas_contact_value_4_6.csv", pi=0.1, c=0.05)
    X, _ = regression_design(records, ("independent_set_size", "edges"))
    assert X.shape == (139, 5) and np.array_equal(X[:, 3:].sum(axis=0), [21, 112]), X[:, 3:].sum(axis=0)

    print("regression_design: all sanity checks pass")

    # ce_gain_regression without features reduces to group means, so the
    # expected values come from the Report 5 tables (c = 0.05, 6 decimals):
    # (a) intercept only = pooled mean gain. Weighting the "Pure Nash count"
    #     table's mean gains by its network counts gives 0.009900.
    _, b, _ = ce_gain_regression(records, (), size_levels=())
    assert np.isclose(b[0], 0.009900, atol=2e-6), b
    # (b) size dummies only: intercept = mean gain of the 6 four-person networks,
    #     dummies = size mean minus that. From the "Edges, by network size" table:
    #     n=4 mean 0.006277, n=5 mean 0.008928, n=6 mean 0.010277.
    _, b, _ = ce_gain_regression(records, ())
    assert np.allclose(b, [0.006277, 0.008928 - 0.006277, 0.010277 - 0.006277], atol=2e-6), b

    print("ce_gain_regression: all sanity checks pass")

    # Cross-check the full regression against an independent implementation:
    # statsmodels OLS with HC1 covariance must give the same coefficients and SEs.
    import statsmodels.api as sm
    for c in (0.05, 0.12):
        records = load_feature_records("game/atlas_contact_value_4_6.csv", pi=0.1, c=c)
        _, b, se = ce_gain_regression(records, ("independent_set_size", "edges"))
        X, _ = regression_design(records, ("independent_set_size", "edges"))
        y = np.array([r["ce_gain"] if r["ce_gain"] > 1e-9 else 0.0 for r in records])
        fit = sm.OLS(y, X).fit(cov_type="HC1")
        assert np.allclose(b, fit.params) and np.allclose(se, fit.bse), (b, fit.params, se, fit.bse)
    print("ce_gain_regression matches statsmodels HC1")

    print_ce_gain_regression()
