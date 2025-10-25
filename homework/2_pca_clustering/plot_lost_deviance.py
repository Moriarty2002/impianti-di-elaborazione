"""Plot total_deviance_lost heatmap from results_summary.csv

Creates a heatmap with PCA on the x-axis, Cluster on the y-axis and
color representing the `total_dev_lost` value. Saves image to
./plots/total_deviance_lost_heatmap.png by default.

Usage:
	python plot_lost_deviance.py          # reads results_summary.csv in same folder and saves plot
	python plot_lost_deviance.py --show   # also shows the plot window
	python plot_lost_deviance.py --csv /path/to/results_summary.csv --out out.png
"""

from pathlib import Path
import argparse
import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(csv_path: Path) -> pd.DataFrame:
	df = pd.read_csv(csv_path)
	# Ensure expected columns exist
	expected = {"PCA", "Cluster", "total_dev_lost"}
	if not expected.issubset(set(df.columns)):
		raise ValueError(f"CSV must contain columns: {expected}. Found: {list(df.columns)}")
	# Convert to numeric if needed
	df["PCA"] = pd.to_numeric(df["PCA"], errors="coerce")
	df["Cluster"] = pd.to_numeric(df["Cluster"], errors="coerce")
	df["total_dev_lost"] = pd.to_numeric(df["total_dev_lost"], errors="coerce")
	return df.dropna(subset=["PCA", "Cluster", "total_dev_lost"])  # drop rows we can't plot


def make_heatmap(df: pd.DataFrame, out_path: Path, show: bool = False, cluster_order: str = "decreasing") -> None:
	# Pivot so rows=Cluster, cols=PCA
	pivot = df.pivot(index="Cluster", columns="PCA", values="total_dev_lost")

	# Sort rows and columns numerically. Respect cluster_order: if 'decreasing', show larger
	# cluster numbers at the top (inverse order).
	ascending = True if cluster_order == "increasing" else False
	pivot = pivot.sort_index(ascending=ascending)
	pivot = pivot.reindex(sorted(pivot.columns), axis=1)

	# Create plot
	plt.figure(figsize=(max(6, pivot.shape[1]*1.2), max(4, pivot.shape[0]*0.4)))
	cmap = sns.color_palette("rocket_r", as_cmap=True)
	ax = sns.heatmap(pivot, annot=True, fmt=".3f", cmap=cmap, cbar_kws={"label": "total_dev_lost"})
	ax.set_xlabel("PCA components")
	ax.set_ylabel("Cluster")
	ax.set_title("Total Deviance Lost (by PCA vs Cluster)")

	out_path.parent.mkdir(parents=True, exist_ok=True)
	plt.tight_layout()
	plt.savefig(out_path, dpi=200)
	print(f"Saved heatmap to: {out_path}")
	if show:
		plt.show()
	plt.close()


def make_lineplot(df: pd.DataFrame, out_path: Path, show: bool = False, cluster_order: str = "decreasing", column_order: str = "increasing") -> None:
	"""Plot lines of total_dev_lost vs PCA for each Cluster.

	X axis: PCA components
	Y axis: total_dev_lost
	One line per Cluster
	"""
	# Aggregate and pivot so index=Cluster (x axis), columns=PCA (one line per PCA)
	grp = df.groupby(["Cluster", "PCA"])["total_dev_lost"].mean().reset_index()
	pivot = grp.pivot(index="Cluster", columns="PCA", values="total_dev_lost")

	# Sort Cluster values ascending (we will invert x-axis later to match example)
	pivot = pivot.sort_index(ascending=True)

	# Determine PCA/column plotting order. The `column_order` controls whether
	# PCA columns (the different lines) are plotted in increasing or decreasing order.
	cols = sorted(pivot.columns) if column_order == "increasing" else sorted(pivot.columns, reverse=True)

	fig, ax = plt.subplots(figsize=(10, 6))
	palette = sns.color_palette("tab10", n_colors=len(cols))

	for i, col in enumerate(cols):
		# convert to numpy arrays to avoid type issues with some pandas ExtensionArrays
		y = pivot[col].to_numpy()
		x = pivot.index.to_numpy()
		ax.plot(x, y, marker="o", markersize=8, linewidth=2, label=f"{int(col)} PCA", color=palette[i])

		# Annotate each point with a small colored box (semi-transparent)
		for xi, yi in zip(x, y):
			if pd.isna(yi):
				continue
			ax.text(xi, yi + 0.01 * max(0.1, max(pivot.max().max(), abs(yi))), f"{yi:.2f}",
					fontsize=9, ha="center", va="bottom",
					bbox=dict(boxstyle='round,pad=0.2', facecolor=palette[i], alpha=0.25, edgecolor='none'))

	ax.set_xlabel("# Cluster")
	ax.set_ylabel("Deviance Loss")
	ax.set_title("Deviance Loss PCA + Clustering")
	ax.grid(alpha=0.35)
	ax.legend(title=None, loc="upper left")

	# Respect cluster_order: if 'decreasing', invert x-axis so cluster values decrease left->right.
	if cluster_order == "decreasing":
		ax.invert_xaxis()

	out_path.parent.mkdir(parents=True, exist_ok=True)
	plt.tight_layout()
	plt.savefig(out_path, dpi=200, bbox_inches="tight")
	print(f"Saved line plot to: {out_path}")
	if show:
		plt.show()
	plt.close()


def main(argv=None):
	parser = argparse.ArgumentParser(description="Plot total_deviance_lost heatmap from results_summary.csv")
	parser.add_argument("--csv", help="Path to results_summary.csv (default: same folder)", default=None)
	parser.add_argument("--out", help="Output image path or prefix. If not provided, files are saved to ./plots/", default=None)
	parser.add_argument("--plot", choices=["heatmap", "line", "both"], default="both",
						help="Which plot to generate (default: both)")
	parser.add_argument("--cluster-order", choices=["increasing", "decreasing"], default="decreasing",
						help="Order of clusters along the x-axis (increasing left->right or decreasing left->right). Default: decreasing.")
	parser.add_argument("--column-order", choices=["increasing", "decreasing"], default="decreasing",
						help="Order of PCA columns (lines) plotted: increasing or decreasing. Default: decreasing.")
	parser.add_argument("--show", help="Also show the plot window", action="store_true")
	args = parser.parse_args(argv)

	# Determine default paths relative to this script
	base = Path(__file__).resolve().parent
	csv_path = Path(args.csv) if args.csv else base / "results_summary.csv"
	out_path = Path(args.out) if args.out else base / "plots"

	if not csv_path.exists():
		print(f"CSV file not found: {csv_path}")
		sys.exit(2)

	df = load_data(csv_path)
	if df.empty:
		print("No valid rows to plot after parsing. Exiting.")
		sys.exit(3)

	# Generate requested plots
	plot_choice = args.plot
	# Prepare variables for output paths
	hp = None
	lp = None
	# If out_path is a file path (has suffix), use it directly for the single plot
	if plot_choice in ("heatmap", "both"):
		if out_path.is_dir():
			hp = out_path / "total_deviance_lost_heatmap.png"
		else:
			# if user provided a file name, append suffix to avoid overwriting
			hp = out_path.with_suffix(out_path.suffix or ".png") if out_path.suffix else out_path
		if hp is not None:
			make_heatmap(df, hp, show=args.show, cluster_order=args.cluster_order)

	if plot_choice in ("line", "both"):
		if out_path.is_dir():
			lp = out_path / "total_deviance_lost_lines.png"
		else:
			lp = out_path.with_suffix(out_path.suffix or ".png") if out_path.suffix else out_path
		if lp is not None:
			make_lineplot(df, lp, show=args.show, cluster_order=args.cluster_order, column_order=args.column_order)


if __name__ == "__main__":
	main()

