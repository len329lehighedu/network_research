"""Structural features of the connected 4–6 person graph atlas networks."""

import csv
from collections import defaultdict
from itertools import combinations

import networkx as nx


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
