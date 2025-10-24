import os
import pandas as pd
import numpy as np


PCA_COLS = ["Principale1", "Principale2", "Principale3", "Principale4", "Principale5", "Principale6"]
UNUSED_COLS = ["swpd", "si", "so", "st", "Cluster", "time"]
# currently made 14 cluster

def deviance_lost_after_pca(csv_path):
    """
    Returns:
        deviance_lost, deviance_retained
    """
    # Try to read CSV using comma as field separator and comma as decimal
    # inside quoted numeric fields (European format). Use skipinitialspace
    # to tolerate a space after delimiters.
    df = pd.read_csv(csv_path, sep=',', quotechar='"', decimal=',', skipinitialspace=True, engine='c')

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
    csv_file = os.path.join(script_dir, "test.csv")

    # Compute deviance lost/retained from PCA
    pca_lost, pca_retained = deviance_lost_after_pca(csv_file)

    print(f"Deviance retained: {pca_retained*100:.2f}%")
    print(f"Deviance lost: {pca_lost*100:.2f}%")

    deviances = intracluster_deviance(csv_file)
    print("Intra-cluster deviances:")
    for cluster, dev in deviances.items(): #print only 'total' column
        if cluster == "total":
            print(f"Cluster {cluster}: {dev:.4f}")

    # Compute total PCA deviance (SST) to normalize intra-cluster total so units match.
    df_main = pd.read_csv(csv_file, sep=',', quotechar='"', decimal=',', skipinitialspace=True, engine='c')
    pca_feature_cols = [c for c in PCA_COLS if c in df_main.columns]
    total_pca_deviance = 0
    if pca_feature_cols:
        total_pca_deviance = ((df_main[pca_feature_cols] - df_main[pca_feature_cols].mean()) ** 2).sum().sum()

    intra_total = deviances.get("total", 0)
    normalized_intra = (intra_total / total_pca_deviance) if total_pca_deviance > 0 else 0

    total_dev_lost = pca_lost + normalized_intra * pca_retained
    print(f"Total deviance lost: {total_dev_lost:.4f}")
