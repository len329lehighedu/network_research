"""Plot the sampled deviation shares recorded in Report 5."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
REPORT = HERE.parent / "reports/report5-deviation-curves-and-multiday-game.md"


def read_sampled_curves():
    """Read the four comparison tables without duplicating their numbers."""
    curves = {}
    current = None
    for line in REPORT.read_text(encoding="utf-8").splitlines():
        if line.startswith("### Daily switching: whole versus "):
            current = ("Daily", line.split("whole versus ", 1)[1].split(" ", 1)[0])
            curves[current] = {}
        elif line.startswith("### Weekly switching: whole versus "):
            current = ("Weekly", line.split("whole versus ", 1)[1].split(" ", 1)[0])
            curves[current] = {}
        elif line.startswith(("## ", "### ")):
            current = None
        elif current is not None and line.startswith("| "):
            fields = [field.strip() for field in line.strip("|").split("|")]
            if fields[0] in ("Whole", "Random", "Even"):
                split = fields[0]
                curves[current].setdefault(split, []).append(
                    (float(fields[1]), float(fields[4]), float(fields[5]))
                )
    return curves


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args()
    curves = read_sampled_curves()
    expected = {("Daily", "random"), ("Daily", "even"),
                ("Weekly", "random"), ("Weekly", "even")}
    assert set(curves) == expected
    assert all(len(points) == 5 for pair in curves.values() for points in pair.values())

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.5), sharex=True, sharey=True)
    colors = {"Whole": "#1763a6", "Random": "#d47b1f", "Even": "#d47b1f"}
    for row, schedule in enumerate(("Daily", "Weekly")):
        for col, comparison in enumerate(("random", "even")):
            ax = axes[row, col]
            for split in ("Whole", comparison.title()):
                points = curves[(schedule, comparison)][split]
                x, home, attend = zip(*points)
                legend_name = "Whole" if split == "Whole" else "Comparison"
                ax.plot(x, home, "o-", color=colors[split], linewidth=2,
                        markersize=4, label=f"{legend_name}: home, k>0")
                ax.plot(x, attend, "s--", color=colors[split], linewidth=2,
                        markersize=4, label=f"{legend_name}: attending")
            ax.set_title(f"{schedule}: whole versus {comparison}")
            ax.set_xlim(-0.03, 1.03)
            ax.set_ylim(-0.03, 1.03)
            ax.set_xticks((0, 0.25, 0.5, 0.75, 1))
            ax.set_yticks((0, 0.25, 0.5, 0.75, 1))
            ax.grid(alpha=0.2)
            if row == 1:
                ax.set_xlabel("Contact value / pair-specific break-even value")
            if col == 0:
                ax.set_ylabel("Share with profitable deviation")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 0.96))
    fig.suptitle("Deviation shares as contact value rises (β = 0.085)", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf"):
        fig.savefig(args.output_dir / f"obedience_v_curves.{suffix}", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
