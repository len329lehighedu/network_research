"""Small contact networks for the one-day attendance game."""

from itertools import product

import networkx as nx


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


def main():
    for name, graph in example_networks().items():
        print(
            f"{name}: nodes={graph.number_of_nodes()}, "
            f"edges={graph.number_of_edges()}, "
            f"profiles={len(all_action_profiles(graph))}"
        )


if __name__ == "__main__":
    main()
