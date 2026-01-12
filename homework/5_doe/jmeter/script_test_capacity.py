import pandas as pd

csv_path = "Test_results/Results/2400_CTT_Heavy_4.csv"

df = pd.read_csv(csv_path)

# 1) Response time medio (ms)
avg_response_ms = df["elapsed"].mean()

# 2) Latency media (ms)
avg_latency_ms = df["Latency"].mean()

# 3) Throughput (req/s)
start_ts = df["timeStamp"].min()
end_ts   = df["timeStamp"].max()

test_duration_sec = (end_ts - start_ts) / 1000.0  # da ms a secondi
num_samples = len(df)

throughput_rps = num_samples / test_duration_sec

print(f"Response time medio: {avg_response_ms:.2f} ms")
print(f"Latency media:       {avg_latency_ms:.2f} ms")
print(f"Throughput:          {throughput_rps:.2f} req/s")
