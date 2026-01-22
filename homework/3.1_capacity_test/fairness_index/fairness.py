import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

def process_csv(file_path):
    df = pd.read_csv(file_path)

    total_ok = df[df['responseMessage'] == "OK"].shape[0]
    total_nok = df[df['responseMessage'] != "OK"].shape[0]
    
    df = df[df["responseMessage"] == "OK"]

    duration = (df['timeStamp'].max() - df['timeStamp'].min()) / 1000

    avg_response_time = df['elapsed'].mean()    
    
    throughput = total_ok / duration
    
    return {
        "file": os.path.basename(file_path),
        "response_time_ms": avg_response_time,
        "throughput": throughput,
        "total_ok": total_ok,
        "total_nok": total_nok
    }


def process_summary_avg(summary_file):
    df = pd.read_csv(summary_file)

    # get CTT value for grouping
    df["group"] = df["file"].str.replace(r"_\d+\.csv$", "", regex=True)
    df["nominal_troughput"] = pd.to_numeric(df["group"], errors='coerce') / 60

    grouped = df.groupby("group").agg({
        "throughput": "mean",
        "nominal_troughput": "mean"
    }).reset_index()

    output_file = os.path.splitext(summary_file)[0] + "_grouped.csv"
    grouped.to_csv(output_file, index=False)

    return grouped


def compute_fairness_index(avg_grouped_csv, output_file):
    df = pd.read_csv(avg_grouped_csv)

    # normalized throughput
    normalized_throughput = df["throughput"] / df["nominal_troughput"]

    # fairness index
    numerator = (normalized_throughput.sum()) ** 2
    denominator = normalized_throughput.shape[0] * (normalized_throughput ** 2).sum()
    fairness = numerator / denominator

    print(f"Throughput: {df['throughput'].values} \nFair troughput: {df['nominal_troughput'].values} \nNormalized throughput: {normalized_throughput.values} \nFairness Index: {fairness:.4f}")
    
    # Save fairness index to file
    result_df = pd.DataFrame({
        "throughput": df["throughput"].values,
        "nominal_throughput": df["nominal_troughput"].values,
        "normalized_throughput": normalized_throughput.values
    })
    result_df.loc[len(result_df)] = ["", "", ""]
    result_df.loc[len(result_df)] = ["Fairness Index", fairness, ""]
    result_df.to_csv(output_file, index=False)
    print(f"\nFairness index saved to: {output_file}")
    
    return fairness


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    summary_dir = os.path.join(script_dir, "summary")
    
    csv_files = glob.glob(os.path.join(summary_dir, "*.csv"))

    results = []
    for file in csv_files:
        metrics = process_csv(file)
        results.append(metrics)

    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(script_dir, "avg.csv"), index=False)
    
    process_summary_avg(os.path.join(script_dir, "avg.csv"))
    
    fairness_output = os.path.join(script_dir, "fairness_index_result.csv")
    compute_fairness_index(os.path.join(script_dir, "avg_grouped.csv"), fairness_output)
    
