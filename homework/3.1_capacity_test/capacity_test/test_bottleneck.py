import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from common import plot_metrics

def process_csv(file_path):
    df = pd.read_csv(file_path,  sep="\\s+", skiprows=1)

    averages = df.mean().to_dict()

    # Add filename as column
    averages["file"] = os.path.basename(file_path)

    return averages


def process_summary(summary_file="summary_results.csv"):
    df = pd.read_csv(summary_file)

    # Extract prefix before "_<number>.csv"
    df["group"] = df["file"].str.extract(r"_(\d+)_")[0]

    # Group by prefix and average values
    grouped = (
        df.groupby("group")[df.columns.difference(["file", "group"])]
        .mean()
        .reset_index()
    )

    # Save the grouped summary
    output_file = os.path.splitext(summary_file)[0] + "_grouped.csv"
    grouped.to_csv(output_file, index=False)

    print(f"✅ Grouped summary written to: {output_file}")
    return grouped


def plot_grouped_summary(grouped_df, output_prefix="summary_plot_vmstat"):
    plot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot/vmstat")
    
    # Extract numeric prefix from group name for sorting (e.g., "150_CTT" -> 150)
    grouped_df["prefix"] = grouped_df["group"].str.extract(r"^(\d+)")
    grouped_df["prefix"] = pd.to_numeric(grouped_df["prefix"], errors="coerce")
    # Sort by prefix
    grouped_df = grouped_df.sort_values("prefix")
    

    # --- Plot CPU parameters ---
    metrics = ["us", "sy", "id", "wa", "st", "gu"]
    plot_metrics(grouped_df, metrics, plot_dir, f"{output_prefix}_avg_cpu", "CTT", "Avg", "CPU group", True)
    
    # --- Plot IO parameters ---
    metrics = ["bi", "bo"]
    plot_metrics(grouped_df, metrics, plot_dir, f"{output_prefix}_avg_io", "CTT", "Avg", "IO group", True)
    
    # --- Plot MEMORY parameters ---
    metrics = ["swpd", "free", "buff", "cache"]
    plot_metrics(grouped_df, metrics, plot_dir, f"{output_prefix}_avg_memory", "CTT", "Avg", "MEMORY group", True)
    
    # --- Plot PROCS parameters ---
    metrics = ["r", "b"]
    plot_metrics(grouped_df, metrics, plot_dir, f"{output_prefix}_avg_procs", "CTT", "Avg", "PROCS group", True)

    # --- Plot SWAP parameters ---
    metrics = ["si", "so"]
    plot_metrics(grouped_df, metrics, plot_dir, f"{output_prefix}_avg_swap", "CTT", "Avg", "SWAP group", True)
    
    # --- Plot SYSTEM parameters ---
    metrics = ["in", "cs"]
    plot_metrics(grouped_df, metrics, plot_dir, f"{output_prefix}_avg_system", "CTT", "Avg", "SYSTEM group", True)


if __name__ == "__main__":
    # Get absolute path to the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vmstat = os.path.join(script_dir, "vmstat")

    csv_files = glob.glob(os.path.join(vmstat, "*.csv"))

    results = []
    for file in csv_files:
        metrics = process_csv(file)
        results.append(metrics)

    # Save results into a summary CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv("homework/capacity_test/summary_results_vmstat.csv", index=False)

    print("Summary written to summary_results.csv")

    to_plot = process_summary(os.path.join(script_dir, "summary_results_vmstat.csv"))

    plot_grouped_summary(to_plot)
