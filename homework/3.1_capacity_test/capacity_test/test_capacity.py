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
    
    power = throughput / (avg_response_time / 1000)

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
    
    # Calculate knee capacity (max power)
    # Knee Capacity = massimo valore della metrica di Power
    max_power_index = grouped_df["power"].idxmax()
    knee_capacity = grouped_df.loc[max_power_index, "prefix"]
    max_power_value = grouped_df.loc[max_power_index, "power"]
    knee_throughput = grouped_df.loc[max_power_index, "throughput"]
    knee_response_time = grouped_df.loc[max_power_index, "avg_response_time_ms"]
    
    # Calculate usable capacity
    # Capacità Utilizzabile = punto dopo il quale la power comincia drasticamente a decrescere
    # Cerchiamo il punto dopo la knee capacity dove la power è ancora accettabile
    # (almeno 10% del valore massimo)
    points_after_knee = grouped_df[grouped_df["prefix"] > knee_capacity].copy()
    
    if len(points_after_knee) > 0:
        # Trova il punto dove la power scende sotto il 10% del massimo
        threshold = max_power_value * 0.10
        below_threshold = points_after_knee[points_after_knee["power"] < threshold]
        
        if len(below_threshold) > 0:
            # Prendi il punto appena prima che scenda sotto la soglia
            usable_idx = below_threshold.index[0]
            # Trova l'indice precedente nel dataframe originale
            original_indices = grouped_df.index.tolist()
            pos = original_indices.index(usable_idx)
            if pos > 0:
                usable_idx = original_indices[pos - 1]
        else:
            # Se tutti i punti dopo knee sono sopra la soglia, prendi l'ultimo
            usable_idx = points_after_knee.index[-1]
        
        usable_capacity_actual = grouped_df.loc[usable_idx, "prefix"]
        usable_throughput = grouped_df.loc[usable_idx, "throughput"]
        usable_response_time = grouped_df.loc[usable_idx, "avg_response_time_ms"]
        usable_power = grouped_df.loc[usable_idx, "power"]
    else:
        # Se non ci sono punti dopo knee, usa knee stesso
        usable_capacity_actual = knee_capacity
        usable_throughput = knee_throughput
        usable_response_time = knee_response_time
        usable_power = max_power_value
    
    print("\n" + "="*60)
    print("CAPACITY ANALYSIS RESULTS")
    print("="*60)
    print(f"\nKnee Capacity (Maximum Power):")
    print(f"  - Definizione: Massimo valore della metrica di Power")
    print(f"  - CTT: {knee_capacity:.0f}")
    print(f"  - Power: {max_power_value:.4f}")
    print(f"  - Throughput: {knee_throughput:.2f} req/s")
    print(f"  - Avg Response Time: {knee_response_time:.2f} ms")
    print(f"\nCapacità Utilizzabile:")
    print(f"  - Definizione: Punto dopo il quale la power")
    print(f"    comincia drasticamente a decrescere")
    print(f"  - CTT: {usable_capacity_actual:.0f}")
    print(f"  - Power: {usable_power:.4f}")
    print(f"  - Throughput: {usable_throughput:.2f} req/s")
    print(f"  - Avg Response Time: {usable_response_time:.2f} ms")
    print("="*60 + "\n")

    # --- Plot Average Response Time ---
    plot_metrics(grouped_df, "avg_response_time_ms", plot_dir, f"{output_prefix}_avg_response_time", "CTT", "Avg [ms]", "Response Time", axvline_x=knee_capacity, axvline_x2=usable_capacity_actual)

    # --- Plot Throughput ---
    plot_metrics(grouped_df, "throughput", plot_dir, f"{output_prefix}_throughput", "CTT", "Avg [req/s]", "Throughput", axvline_x=knee_capacity, axvline_x2=usable_capacity_actual)

    # --- Plot Power ---
    plot_metrics(grouped_df, "power", plot_dir, f"{output_prefix}_power", "CTT", "Avg [req/s²]", "Power", axvline_x=knee_capacity, axvline_x2=usable_capacity_actual)

    print(f"✅ Line plots saved in {plot_dir}/")
    
    return knee_capacity, usable_capacity_actual


if __name__ == "__main__":
    # Get absolute path to the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    jmeter_dir = os.path.join(script_dir, "jmeter")
    
    csv_files = glob.glob(os.path.join(jmeter_dir, "*.csv"))
    print(f"Found {len(csv_files)} CSV files in jmeter directory")

    results = []
    for file in csv_files:
        metrics = process_csv(file)
        results.append(metrics)

    # Save results into a summary CSV in the script directory
    summary_path = os.path.join(script_dir, "summary_results.csv")
    results_df = pd.DataFrame(results)
    results_df.to_csv(summary_path, index=False)

    print(f"✅ Summary written to {summary_path}")
    
    # Process summary and group by CTT values (averaging the 3 repetitions)
    to_plot = process_summary(summary_path)
    
    # Plot and calculate capacities
    knee_capacity, usable_capacity = plot_grouped_summary(to_plot)
