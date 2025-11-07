import os
import pandas as pd
import numpy as np


PCA_COLS = ["Principale1", "Principale2", "Principale3", "Principale4", "Principale5"]
UNUSED_COLS = ["responseCode", "responseMessage", "threadName", "dataType", "success", "failureMessage", "URL", "timeStamp", "label", "Cluster"]

def deviance_lost_after_pca(csv_path):
    """
    Returns:
        deviance_lost, deviance_retained
    """
    # Try to read CSV using comma as field separator and comma as decimal
    # inside quoted numeric fields (European format). Use skipinitialspace
    # to tolerate a space after delimiters.
    df = pd.read_csv(csv_path, sep=',', quotechar='"', decimal=',', skipinitialspace=True, engine='c')

    # If a Cluster column exists, drop rows without a cluster (NaN or empty string)
    if 'Cluster' in df.columns:
        df = df[df['Cluster'].notna() & (df['Cluster'].astype(str).str.strip() != '')]
        if df.empty:
            raise ValueError("No rows with a valid 'Cluster' found after filtering.")

    # Clean column names (strip whitespace and remove stray apostrophes)
    df.columns = df.columns.str.strip().str.replace("'", "")

    # Ensure PCA columns are numeric; some imports may still produce strings
    # (if quoting/decimal detection failed). Coerce explicitly as a fallback.
    for col in PCA_COLS:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            # Remove surrounding quotes, convert decimal comma to dot and coerce
            s = df[col].astype(str).str.strip().str.replace('"', '').str.replace("'", "")
            s = s.str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(s, errors='coerce')

    # Select numeric columns after coercion
    numeric_cols = df.select_dtypes(include=["number"]).columns

    # Keep only valid PCA numeric ones
    pca_cols = [col for col in PCA_COLS if col in numeric_cols]
    print("PCA", pca_cols)
    
    original_cols = [col for col in numeric_cols if col not in pca_cols and col not in UNUSED_COLS]
    print("NORMAL", original_cols)
    
    if not pca_cols:
        raise ValueError("No PCA columns detected. Check PCA_COLS list vs actual CSV columns.")
    if not original_cols:
        raise ValueError("No original columns detected. Check UNUSED_COLS list vs actual CSV columns.")

    # --- Z-SCORE normalization on original features to correctly compare with principal components ---
    df_norm = df[original_cols].apply(lambda x: (x - x.mean()) / x.std(ddof=0))

    # Deviance = total sum of squared deviations (SST) across rows and features.
    # Compute explicitly as sum((x - mean(x))**2) for clarity and to avoid
    # relying on variance * n. This matches the definition of deviance (SST).
    dev_original = ((df_norm - df_norm.mean()) ** 2).sum().sum()

    # For PCA components, compute SST from their means (not normalized here).
    dev_pca = ((df[pca_cols] - df[pca_cols].mean()) ** 2).sum().sum()

    if dev_original == 0:
        raise ValueError("Original features have zero total deviance after normalization; cannot compute deviance ratio.")

    deviance_retained = dev_pca / dev_original
    deviance_lost = 1 - deviance_retained

    return deviance_lost, deviance_retained


def intracluster_deviance(csv_path: str):
    """
    Calculates intra-cluster deviance (sum of squared distances to the cluster mean)
    for each cluster in the dataset. This returns per-cluster SST (sum of squared
    deviations) and a `total` entry containing the sum across all clusters.

    Args:
        csv_path (str): Path to the CSV file

    Returns:
        dict: Mapping from cluster label to its deviance (SST) value. The key
              "total" contains the sum of all cluster deviances.
    """

    # Load dataset. Expect comma-separated fields and comma decimal inside
    # quoted numeric fields. Use skipinitialspace to tolerate spaces after commas.
    df = pd.read_csv(csv_path, sep=',', quotechar='"', decimal=',', skipinitialspace=True, engine='c')

    # Ensure "Cluster" column exists
    if "Cluster" not in df.columns:
        raise ValueError("CSV must contain a 'Cluster' column.")

    # Drop rows without a cluster (NaN or empty string)
    df = df[df['Cluster'].notna() & (df['Cluster'].astype(str).str.strip() != '')]
    if df.empty:
        raise ValueError("No rows with a valid 'Cluster' found after filtering.")

    # Get feature columns regarding clustering (all principal components)
    feature_cols = [col for col in df.columns if col in PCA_COLS]
    if not feature_cols:
        raise ValueError(f"No PCA feature columns found in CSV. Expected one of: {PCA_COLS}")

    results = {"total": 0}
    for cluster, group in df.groupby("Cluster"):
        # Compute mean vector of the cluster
        mean_vector = group[feature_cols].mean().values
        # Compute squared distances to mean for each row
        sq_dists = np.sum((group[feature_cols].values - mean_vector) ** 2, axis=1)
        # Deviance (SST) for the cluster = sum of squared distances
        deviance_cluster = np.sum(sq_dists)
        results[str(cluster)] = deviance_cluster
        results["total"] += deviance_cluster

    return results


if __name__ == "__main__":
    # Get absolute path to the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Folder with CSVs to process (one or many). If the folder does not exist
    # the script will fallback to processing a single `hl_pca_clustering.csv` in the same dir.
    csv_folder = os.path.join(script_dir, "csv")
    fallback_csv = os.path.join(script_dir, "hl_pca_clustering.csv")

    # Output summary file (appended rows for each processed CSV file)
    results_file = os.path.join(script_dir, "results_summary.csv")

    # Columns: filename, deviance_retained, deviance_lost, intra_cluster_total, total_dev_lost, error
    processed_any = False

    if os.path.isdir(csv_folder):
        csv_files = [os.path.join(csv_folder, f) for f in sorted(os.listdir(csv_folder)) if f.lower().endswith('.csv')]
    else:
        csv_files = []

    # Fallback to single test.csv if no files found
    if not csv_files and os.path.exists(fallback_csv):
        csv_files = [fallback_csv]

    if not csv_files:
        print(f"No CSV files found in '{csv_folder}' and no fallback '{fallback_csv}' present. Nothing to do.")
    else:
        for csv_file in csv_files:
            processed_any = True
            error_msg = ""
            try:
                pca_lost, pca_retained = deviance_lost_after_pca(csv_file)
            except Exception as e:
                pca_lost = float('nan')
                pca_retained = float('nan')
                error_msg = f"deviance_lost_after_pca error: {e}"

            try:
                deviances = intracluster_deviance(csv_file)
                intra_total = deviances.get("total", 0)
            except Exception as e:
                intra_total = float('nan')
                error_msg = (error_msg + "; " if error_msg else "") + f"intracluster_deviance error: {e}"

            # Compute total PCA deviance to normalize intracluster total (matching previous logic)
            total_pca_deviance = 0
            try:
                df_main = pd.read_csv(csv_file, sep=',', quotechar='"', decimal=',', skipinitialspace=True, engine='c')
                # If a Cluster column exists, drop rows without a cluster
                if 'Cluster' in df_main.columns:
                    df_main = df_main[df_main['Cluster'].notna() & (df_main['Cluster'].astype(str).str.strip() != '')]
                    if df_main.empty:
                        # No valid rows left; treat as an error for downstream steps
                        raise ValueError("No rows with a valid 'Cluster' found after filtering in main read.")
                pca_feature_cols = [c for c in PCA_COLS if c in df_main.columns]
                if pca_feature_cols:
                    total_pca_deviance = ((df_main[pca_feature_cols] - df_main[pca_feature_cols].mean()) ** 2).sum().sum()
            except Exception as e:
                total_pca_deviance = 0
                error_msg = (error_msg + "; " if error_msg else "") + f"read_main error: {e}"

            normalized_intra = (intra_total / total_pca_deviance) if (total_pca_deviance and not np.isnan(intra_total)) else 0

            total_dev_lost = float('nan')
            try:
                if not np.isnan(pca_lost) and not np.isnan(pca_retained):
                    total_dev_lost = pca_lost + normalized_intra * pca_retained
            except Exception:
                total_dev_lost = float('nan')

            # Parse PCA and Cluster counts from filename like '6_componenti_13_cluster.csv'
            base = os.path.basename(csv_file)


            # Prepare row and append to results CSV. Include original filename to make debugging easier.
            row = {
                'filename': base,
                'deviance_retained': pca_retained,
                'deviance_lost': pca_lost,
                'intra_cluster_total': intra_total,
                'total_dev_lost': total_dev_lost,
                'error': error_msg
            }

            # Write/appended the row
            df_row = pd.DataFrame([row])
            header = not os.path.exists(results_file)
            df_row.to_csv(results_file, mode='a', header=header, index=False, float_format='%.6f')

            print(f"Processed: {os.path.basename(csv_file)} -> retained={pca_retained:.6f}, lost={pca_lost:.6f}, intra_total={intra_total}, total_dev_lost={total_dev_lost:.6f}")

        if processed_any:
            print(f"Appended results to: {results_file}")
