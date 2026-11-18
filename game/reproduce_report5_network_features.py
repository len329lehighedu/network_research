"""Regenerate the network feature and bowtie sections of Report 5."""

import argparse
import csv
import math
from pathlib import Path

import networkx as nx

from contact_value_payoff import attendance_gain
from network_game import (
    all_action_profiles,
    count_attending_neighbors,
    extra_cost_with_contact_value,
    obedience_gain_with_contact_value,
    pure_nash_equilibria_with_contact_value,
    social_optimum_with_contact_value,
    solve_best_correlated_equilibrium_with_contact_value,
    symmetrize_lottery,
)
from network_sis.atlas_network_features import (
    load_feature_records,
    summarize_by_feature,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "game/atlas_contact_value_4_6.csv"
GAIN_TOLERANCE = 1e-9
BOWTIE_PARAMS = dict(pi=0.1, beta=0.04, L_day=10, gamma=0.2, c=0.05, v=0.14)


def gain_count(records):
    """Count networks whose CE improvement exceeds numerical noise."""
    return sum(record["ce_gain"] > GAIN_TOLERANCE for record in records)


def add_feature_table(lines, records, feature, label, by_size=False):
    """Append the same pooled or size-stratified tables used in the analysis."""
    if by_size:
        lines.extend([
            f"### {label}, by network size",
            "",
            f"| People | {label} | Networks | CE improves | Share | Mean CE gain |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for n in (4, 5, 6):
            subset = [record for record in records if record["n"] == n]
            for row in summarize_by_feature(subset, feature):
                lines.append(
                    f'| {n} | {row["value"]} | {row["networks"]} | '
                    f'{row["improved"]} | {row["improvement_rate"]:.3f} | '
                    f'{row["mean_gain"]:.6f} |'
                )
    else:
        lines.extend([
            f"### {label}, all 139 networks",
            "",
            f"| {label} | Networks | CE improves | Share | Mean CE gain |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ])
        for row in summarize_by_feature(records, feature):
            lines.append(
                f'| {row["value"]} | {row["networks"]} | '
                f'{row["improved"]} | {row["improvement_rate"]:.3f} | '
                f'{row["mean_gain"]:.6f} |'
            )
    lines.append("")


def add_cross_tabs(lines, records):
    """Append alpha by equilibrium multiplicity and within-edge comparisons."""
    lines.extend([
        "## Largest independent set within equilibrium groups",
        "",
        "| People | Pure Nash | α group | Networks | CE improves | Share |",
        "| ---: | --- | --- | ---: | ---: | ---: |",
    ])
    for n in (5, 6):
        for multiple in (False, True):
            for small_alpha in (True, False):
                group = [
                    record for record in records
                    if record["n"] == n
                    and (record["pure_nash_count"] > 1) == multiple
                    and (record["independent_set_size"] <= 2) == small_alpha
                ]
                improves = gain_count(group)
                share = f"{improves / len(group):.3f}" if group else "—"
                pure_label = "Multiple" if multiple else "One"
                alpha_label = "≤2" if small_alpha else "≥3"
                lines.append(
                    f"| {n} | {pure_label} | {alpha_label} | {len(group)} | "
                    f"{improves} | {share} |"
                )
    lines.extend([
        "",
        "## Largest independent set at the same edge count",
        "",
        "Six-person networks with multiple pure Nash equilibria; only edge counts "
        "where both α groups occur are shown.",
        "",
        "| Edges | α ≤ 2: CE gains / networks | α ≥ 3: CE gains / networks |",
        "| ---: | ---: | ---: |",
    ])
    subset = [record for record in records if record["n"] == 6 and record["pure_nash_count"] > 1]
    assert len(subset) == 91
    overlap_small = []
    overlap_large = []
    for edges in sorted({record["edges"] for record in subset}):
        small = [
            record for record in subset
            if record["edges"] == edges and record["independent_set_size"] <= 2
        ]
        large = [
            record for record in subset
            if record["edges"] == edges and record["independent_set_size"] >= 3
        ]
        if small and large:
            lines.append(
                f"| {edges} | {gain_count(small)}/{len(small)} | "
                f"{gain_count(large)}/{len(large)} |"
            )
            overlap_small.extend(small)
            overlap_large.extend(large)
    assert (gain_count(overlap_small), len(overlap_small)) == (26, 31)
    assert (gain_count(overlap_large), len(overlap_large)) == (15, 45)
    lines.extend([
        f"| **Total in shared edge strata** | **{gain_count(overlap_small)}/{len(overlap_small)}** | "
        f"**{gain_count(overlap_large)}/{len(overlap_large)}** |",
        "",
    ])


def bowtie_details():
    """Recompute the bowtie's pure Nash, social minimum, and symmetric CE."""
    graph = nx.graph_atlas_g()[42]
    profiles = all_action_profiles(graph)
    pure = pure_nash_equilibria_with_contact_value(graph, **BOWTIE_PARAMS)
    minimum, minimum_profiles = social_optimum_with_contact_value(graph, **BOWTIE_PARAMS)
    result = solve_best_correlated_equilibrium_with_contact_value(graph, **BOWTIE_PARAMS)
    assert result.success and len(pure) == 1
    assert math.isclose(minimum, 0.15, abs_tol=1e-9)
    assert math.isclose(result.fun, 0.191455241742459, abs_tol=1e-9)
    lottery = symmetrize_lottery(graph, result.x)
    assert math.isclose(sum(lottery), 1.0, abs_tol=1e-9)
    expected_cost = sum(
        probability * extra_cost_with_contact_value(graph, profile, **BOWTIE_PARAMS)
        for profile, probability in zip(profiles, lottery)
    )
    assert math.isclose(expected_cost, result.fun, abs_tol=1e-9)
    return graph, profiles, pure[0], minimum, minimum_profiles, result.fun, lottery


def add_bowtie(lines, records):
    """Append the unique-equilibrium exceptions and the bowtie hand calculation."""
    exceptions = [
        record for record in records
        if record["pure_nash_count"] == 1 and record["ce_gain"] > GAIN_TOLERANCE
    ]
    assert len(exceptions) == 4
    lines.extend([
        "## Four CE gains with a unique pure Nash",
        "",
        "| Atlas ID | People | Edges | Triangles | Maximum degree | α | CE gain |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for record in exceptions:
        lines.append(
            f'| {record["atlas_id"]} | {record["n"]} | {record["edges"]} | '
            f'{record["triangles"]} | {record["max_degree"]} | '
            f'{record["independent_set_size"]} | {record["ce_gain"]:.6f} |'
        )

    graph, profiles, pure, minimum, minimum_profiles, ce_cost, lottery = bowtie_details()
    pure_cost = extra_cost_with_contact_value(graph, pure, **BOWTIE_PARAMS)
    assert "".join(pure) == "AAAAH" and math.isclose(pure_cost, 0.21, abs_tol=1e-9)
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    lines.extend([
        "",
        "## Bowtie (atlas 42) by hand",
        "",
        f"Edges: `{edges}`. The two triangles share node 4.",
        "",
        f"The unique pure Nash is `{''.join(pure)}` with group cost **{pure_cost:.6f}** "
        "above the common infection baseline.",
        "",
        "| Person | Pure action | Attending neighbors k | Gain from attending |",
        "| ---: | :---: | ---: | ---: |",
    ])
    for person in graph.nodes:
        k = count_attending_neighbors(graph, pure, person)
        gain = attendance_gain(k, **BOWTIE_PARAMS)
        lines.append(f"| {person} | {pure[person]} | {k} | {gain:+.6f} |")
    lines.extend([
        "",
        "Each attending outer node has one active contact: infection cost 0.18 "
        "minus contact benefit 0.14. Node 4 stays home and pays c = 0.05. "
        "Hence `4(0.18 − 0.14) + 0.05 = 0.210000`.",
        "",
        f"The social minimum is **{minimum:.6f}**, attained by "
        f"`{', '.join(''.join(profile) for profile in minimum_profiles)}`. "
        "Each has two nonadjacent attendees, zero active contacts, and three "
        "people home, so group cost is `3c = 0.15`.",
        "",
    ])
    sample = minimum_profiles[0]
    lines.extend([
        f"In `{''.join(sample)}`, the home-assigned people have these "
        "unilateral gains from attending:",
        "",
        "| Home person | Attending neighbors k | Gain from attending |",
        "| ---: | ---: | ---: |",
    ])
    for person in graph.nodes:
        if sample[person] == "H":
            k = count_attending_neighbors(graph, sample, person)
            gain = attendance_gain(k, **BOWTIE_PARAMS)
            lines.append(f"| {person} | {k} | {gain:+.6f} |")
    lines.extend([
        "",
        "The two outer home-assigned people want to deviate, so the social "
        "minimum profiles are not pure Nash equilibria.",
        "",
        f"The best correlated equilibrium has expected group cost **{ce_cost:.6f}** "
        f"and improves on the unique pure Nash by **{pure_cost - ce_cost:.6f}** "
        f"({100 * (pure_cost - ce_cost) / pure_cost:.1f}%). "
        "The lottery below averages the LP solution over graph automorphisms.",
        "",
        "| Profile | Probability | Group cost |",
        "| :--- | ---: | ---: |",
    ])
    support = []
    for profile, probability in zip(profiles, lottery):
        if probability > 1e-8:
            cost = extra_cost_with_contact_value(graph, profile, **BOWTIE_PARAMS)
            support.append((profile, probability, cost))
            lines.append(f"| `{''.join(profile)}` | {probability:.6f} | {cost:.6f} |")
    assert len(support) == 9

    def category_mass(target_cost):
        return sum(
            probability for _, probability, cost in support
            if math.isclose(cost, target_cost, abs_tol=1e-8)
        )

    lines.extend([
        "",
        "| Profile category | Total probability | Cost per profile |",
        "| :--- | ---: | ---: |",
        f"| Four social-minimum profiles | {category_mass(0.15):.6f} | 0.150000 |",
        f"| Four profiles with center and two outer nodes attending | "
        f"{category_mass(0.25928):.6f} | 0.259280 |",
        f"| Center alone (`HHHHA`) | {category_mass(0.20):.6f} | 0.200000 |",
        "",
        "Category totals use unrounded probabilities, so they may differ "
        "slightly from sums of the displayed profile rows.",
        "",
        "| Person | Recommendation | Probability of recommendation | "
        "Conditional gain from obeying |",
        "| ---: | :---: | ---: | ---: |",
    ])
    for person in (0, 4):
        for action in ("A", "H"):
            mass = sum(
                probability for profile, probability in zip(profiles, lottery)
                if profile[person] == action
            )
            weighted_gain = sum(
                probability * obedience_gain_with_contact_value(
                    graph, profile, person, **BOWTIE_PARAMS
                )
                for profile, probability in zip(profiles, lottery)
                if profile[person] == action
            )
            conditional_gain = weighted_gain / mass
            assert conditional_gain >= -1e-9
            if abs(conditional_gain) < 5e-9:
                conditional_gain = 0.0
            lines.append(
                f"| {person} | {action} | {mass:.6f} | {conditional_gain:+.8f} |"
            )
    lines.extend([
        "",
        "The outer-node `H` and center-node `A` obedience constraints bind. "
        "The costly profiles make staying home more attractive to an outer "
        "node who receives `H`; the center-alone profile offsets the center's "
        "temptation to stay home when it receives `A`. These conditional "
        "incentives let the CE place positive probability on social-minimum "
        "profiles that are not pure Nash equilibria.",
        "",
    ])


def add_c012(lines, records, csv_path):
    """Append the c = 0.12 feature checks and the three no-gain exceptions."""
    assert len(records) == 139 and gain_count(records) == 32
    unique = [record for record in records if record["pure_nash_count"] == 1]
    multiple = [record for record in records if record["pure_nash_count"] > 1]
    assert (len(unique), gain_count(unique)) == (104, 0)
    assert (len(multiple), gain_count(multiple)) == (35, 32)
    lines.extend([
        "## Feature checks at c = 0.12",
        "",
        "The same 139 networks and game parameters are used, changing only "
        "the cost of staying home from 0.05 to 0.12.",
        "",
    ])
    add_feature_table(lines, records, "pure_nash_count", "Pure Nash count")

    lines.extend([
        "### Largest independent set among networks with multiple pure Nash",
        "",
        "No four-person network has multiple pure Nash at this c.",
        "",
        "| People | α | Networks | CE improves | Share | Mean CE gain |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for n in (5, 6):
        subset = [record for record in multiple if record["n"] == n]
        for row in summarize_by_feature(subset, "independent_set_size"):
            lines.append(
                f'| {n} | {row["value"]} | {row["networks"]} | '
                f'{row["improved"]} | {row["improvement_rate"]:.3f} | '
                f'{row["mean_gain"]:.6f} |'
            )
    lines.append("")

    six_multiple = [record for record in multiple if record["n"] == 6]
    assert len(six_multiple) == 31 and gain_count(six_multiple) == 28
    for feature, label in (
        ("edges", "Edges"),
        ("triangles", "Triangles"),
        ("max_degree", "Maximum degree"),
    ):
        lines.extend([
            f"### {label} among six-person networks with multiple pure Nash",
            "",
            f"| {label} | Networks | CE improves | Share | Mean CE gain |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ])
        for row in summarize_by_feature(six_multiple, feature):
            lines.append(
                f'| {row["value"]} | {row["networks"]} | '
                f'{row["improved"]} | {row["improvement_rate"]:.3f} | '
                f'{row["mean_gain"]:.6f} |'
            )
        lines.append("")

    exceptions = [
        record for record in multiple if record["ce_gain"] <= GAIN_TOLERANCE
    ]
    assert {record["atlas_id"] for record in exceptions} == {186, 194, 198}
    with open(csv_path, newline="", encoding="utf-8") as handle:
        source_rows = {
            int(row["atlas_id"]): row for row in csv.DictReader(handle)
            if float(row["pi"]) == 0.1 and float(row["c"]) == 0.12
            and int(row["atlas_id"]) in {186, 194, 198}
        }
    lines.extend([
        "### Multiple-equilibrium networks with no CE gain",
        "",
        "| Atlas ID | Pure Nash | Edges | Triangles | Maximum degree | α | "
        "Best pure | Best CE | Social minimum | Pure-to-minimum gap |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for record in exceptions:
        row = source_rows[record["atlas_id"]]
        pure = float(row["best_pure_nash"])
        ce = float(row["best_ce"])
        minimum = float(row["social_minimum"])
        assert math.isclose(pure, ce, abs_tol=1e-9) and pure > minimum
        lines.append(
            f'| {record["atlas_id"]} | {record["pure_nash_count"]} | '
            f'{record["edges"]} | {record["triangles"]} | '
            f'{record["max_degree"]} | {record["independent_set_size"]} | '
            f'{pure:.6f} | {ce:.6f} | {minimum:.6f} | '
            f'{pure - minimum:.6f} |'
        )
    lines.extend([
        "",
        "All three retain a positive gap to the social minimum. The CE "
        "constraints prevent an improvement at these parameters.",
        "",
        "### Matched networks at 10–11 edges and maximum degree 4",
        "",
        "These six-person networks all have multiple pure Nash.",
        "",
        "| Atlas ID | Pure Nash | Edges | Triangles | α | CE gain |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    matched = [
        record for record in six_multiple
        if record["edges"] in (10, 11) and record["max_degree"] == 4
    ]
    assert len(matched) == 10
    for record in sorted(matched, key=lambda row: (row["edges"], row["atlas_id"])):
        lines.append(
            f'| {record["atlas_id"]} | {record["pure_nash_count"]} | '
            f'{record["edges"]} | {record["triangles"]} | '
            f'{record["independent_set_size"]} | {record["ce_gain"]:.6f} |'
        )
    lines.extend([
        "",
        "At c = 0.12, equilibrium multiplicity is the strongest descriptive "
        "separator: 0/104 unique-equilibrium networks improve, versus 32/35 "
        "with multiple equilibria. Within those 35 networks, α does not "
        "separate outcomes as it did at c = 0.05: among six-person networks, "
        "14/16 with α = 2 and 12/13 with α = 3 improve. Edge count and triangle "
        "count are not monotone; all three failures have maximum degree 4, "
        "but 21/24 networks with that degree still improve. The matched table "
        "contains both outcomes at the same network size, edge count, and "
        "maximum degree; no individual feature shown is a sufficient rule.",
        "",
    ])


def render_report(records, records_c012, csv_path):
    """Build the full report with tables and narrowly supported findings."""
    assert len(records) == 139
    assert len({record["atlas_id"] for record in records}) == 139
    assert gain_count(records) == 65
    assert {n: sum(record["n"] == n for record in records) for n in (4, 5, 6)} == {
        4: 6, 5: 21, 6: 112
    }

    lines = [
        "# Network features and recommendation gains (Report 5)",
        "",
        "Data: the 139 connected graph-atlas networks with 4–6 people, from "
        f"`{csv_path.name}` at π = 0.1 and c = 0.05 or 0.12. "
        "The one-day game uses β = 0.04, L_day = 10, γ = 0.2, and contact value "
        "v = 0.14. CE gain is best-pure-Nash group cost minus best-CE group "
        "cost; a gain greater than 1e-9 counts as an improvement. Mean CE "
        "gain averages over every network in a row, including zero gains.",
        "",
        "The graph atlas is an enumeration of network structures, not a "
        "random sample. Shares below are descriptive; no causal or sampling "
        "inference is claimed.",
        "",
        "## Feature tables at c = 0.05",
        "",
    ]
    add_feature_table(lines, records, "pure_nash_count", "Pure Nash count")
    add_feature_table(lines, records, "edges", "Edges")
    add_feature_table(lines, records, "edges", "Edges", by_size=True)
    add_feature_table(lines, records, "triangles", "Triangles", by_size=True)
    add_feature_table(lines, records, "max_degree", "Maximum degree", by_size=True)
    add_feature_table(
        lines, records, "independent_set_size", "Largest independent set α", by_size=True
    )
    add_cross_tabs(lines, records)
    add_bowtie(lines, records)
    add_c012(lines, records_c012, csv_path)

    lines.extend([
        "## Findings and limits",
        "",
        "The next six findings concern c = 0.05; the c = 0.12 comparisons "
        "are reported above.",
        "",
        "- CE improves on best pure Nash in **65/139** networks. The gain occurs "
        "in **4/29** networks with one pure Nash and **61/110** with multiple "
        "pure Nash equilibria; multiplicity is associated with gain but is not "
        "necessary.",
        "- Edge count alone is not monotone within network size. For six-person "
        "networks, 8/14 with 10 edges improve, while 2/5 with 12 edges improve. "
        "Sparse extreme edge-count cells are unstable as descriptive rates.",
        "- Among six-person networks, 5/19 with no triangles improve versus "
        "49/93 with at least one triangle. The share does not rise steadily with "
        "triangle count; triangles also covary with density.",
        "- Maximum degree shows little separation among six-person networks: "
        "14/27 at degree 3, 24/49 at degree 4, and 15/34 at degree 5.",
        "- The largest-independent-set size gives the clearest descriptive "
        "separation. Among six-person networks with multiple pure Nash "
        "equilibria, CE improves in **28/35** with α ≤ 2 versus **23/56** with "
        "α ≥ 3. Restricting to edge counts 7–12 where both groups occur gives "
        "**26/31** versus **15/45**. This does not isolate α from every other "
        "network feature.",
        "- Bowtie shows why one pure Nash does not rule out a CE gain: private "
        "recommendations can make a lottery over non-Nash profiles obedient "
        "after conditioning on the recommendation.",
        "",
        "## Complete feature data at π = 0.10",
        "",
        "| c | Atlas ID | People | Edges | Pure Nash count | Triangles | Maximum degree | Largest independent set | CE gain |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for cost, case_records in ((0.05, records), (0.12, records_c012)):
        for record in case_records:
            lines.append(
                f"| {cost:.2f} | {record['atlas_id']} | {record['n']} | "
                f"{record['edges']} | {record['pure_nash_count']} | "
                f"{record['triangles']} | {record['max_degree']} | "
                f"{record['independent_set_size']} | {max(0.0, record['ce_gain']):.6f} |"
            )
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--output", type=Path, help="Write to a file instead of stdout.")
    args = parser.parse_args()
    records = load_feature_records(args.csv, pi=0.1, c=0.05)
    records_c012 = load_feature_records(args.csv, pi=0.1, c=0.12)
    report = render_report(records, records_c012, args.csv)
    if args.output is None:
        print(report, end="")
        return
    args.output.write_text(report, encoding="utf-8")
    print(
        f"Wrote {args.output} ({len(records)} networks per c; "
        f"{gain_count(records)} gains at c=0.05, "
        f"{gain_count(records_c012)} at c=0.12)"
    )


if __name__ == "__main__":
    main()
