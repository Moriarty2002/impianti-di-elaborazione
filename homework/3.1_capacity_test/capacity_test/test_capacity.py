import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from common import plot_metrics

def process_csv(file_path):
    # Read CSV file
    df = pd.read_csv(file_path)

    # Total requests correctly served
    total_ok = df[df['responseMessage'] == "OK"].shape[0]
    total_nok = df[df['responseMessage'] != "OK"].shape[0]
    
    df = df[df["responseMessage"] == "OK"]

    duration = (df['timeStamp'].max() - df['timeStamp'].min()) / 1000

    avg_response_time = df['elapsed'].mean()    
    
    throughput = total_ok / duration
    
    power = throughput / avg_response_time

    return {
        "file": os.path.basename(file_path),
        "total_ok": total_ok,
        "total_nok": total_nok,
        "duration_sec": duration,
        "avg_response_time_ms": avg_response_time,
        "throughput": throughput,
        "power": power
    }


def process_summary(summary_file="summary_results.csv"):
    # Read the summary file
    df = pd.read_csv(summary_file)

    # Add throughput column
    df["throughput"] = df["total_ok"] / df["duration_sec"]

    # Extract prefix before "_<number>.csv"
    df["group"] = df["file"].str.replace(r"_\d+\.csv$", "", regex=True)

    # Group by prefix and average values
    grouped = df.groupby("group").agg({
        "avg_response_time_ms": "mean",
        "throughput": "mean",
        "power": "mean"
    }).reset_index()

    # Save the grouped summary
    output_file = os.path.splitext(summary_file)[0] + "_grouped.csv"
    grouped.to_csv(output_file, index=False)

    print(f"✅ Grouped summary written to: {output_file}")
    return grouped


def plot_grouped_summary(grouped_df, output_prefix="summary_plot"):
    plot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot")
    
    # Extract numeric prefix from group name for sorting (e.g., "150_CTT" -> 150)
    grouped_df["prefix"] = grouped_df["group"].str.extract(r"^(\d+)")
    grouped_df["prefix"] = pd.to_numeric(grouped_df["prefix"], errors="coerce")

    # Sort by prefix
    grouped_df = grouped_df.sort_values("prefix")
    
    # Get x for knee capacity
    max_power_index = grouped_df["power"].idxmax()
    x_for_max_power = grouped_df.loc[max_power_index, "prefix"]

    # --- Plot Average Response Time ---
    plot_metrics(grouped_df, "avg_response_time_ms", plot_dir, f"{output_prefix}_avg_response_time", "CTT", "Avg [ms]", "Response Time", axvline_x=x_for_max_power)

    # --- Plot Throughput ---
    plot_metrics(grouped_df, "throughput", plot_dir, f"{output_prefix}_throughput", "CTT", "Avg", "Throughput", axvline_x=x_for_max_power)

    # --- Plot Power ---
    plot_metrics(grouped_df, "power", plot_dir, f"{output_prefix}_power", "CTT", "Avg", "Power", axvline_x=x_for_max_power)

    print(f"✅ Line plots saved as {output_prefix}_avg_response_time.png and {output_prefix}_throughput.png")


if __name__ == "__main__":
    # Get absolute path to the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    jmeter_dir = os.path.join(script_dir, "jmeter")
    
    csv_files = glob.glob(os.path.join(jmeter_dir, "*.csv"))
    # print(csv_files)

    results = []
    for file in csv_files:
        metrics = process_csv(file)
        results.append(metrics)

    # Save results into a summary CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv("homework/capacity_test/summary_results.csv", index=False)

    print("Summary written to summary_results.csv")
    
    to_plot = process_summary(os.path.join(script_dir, "summary_results.csv"))
    
    plot_grouped_summary(to_plot)
