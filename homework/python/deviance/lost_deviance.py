import pandas as pd
import numpy as np


PCA_COLS = ["Principale1", "Principale2", "Principale3", "Principale4"]
UNUSED_COLS = ["AnonPages", "VmPTE", "Slab", "Colonna 25", "Cluster"]
# currently made 14 cluster

def variance_lost_after_pca(csv_path):
    """
    Returns:
        variance_lost, variance_retained
    """
    df = pd.read_csv(csv_path, sep=r"[;,]", engine="python")

    # Clean column names
    df.columns = df.columns.str.strip().str.replace("'", "")

    # Select numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns

    # Keep only valid ones
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
    
    # Variance
    var_original = df_norm.var(ddof=0).sum()
    var_pca = df[pca_cols].var(ddof=0).sum()

    variance_retained = var_pca / var_original
    variance_lost = 1 - variance_retained

    return variance_lost, variance_retained


def intracluster_variance(csv_path: str):
    """
    Calculates intra-cluster variance for each cluster in the dataset.
    
    Args:
        csv_path (str): Path to the CSV file
    
    Returns:
        dict: Mapping from cluster label to its variance value.
    """
    # Load dataset
    df = pd.read_csv(csv_path, sep=r"[;,]", engine="python")  # handles commas or semicolons
    
    # Ensure "CLUSTER" column exists
    if "Cluster" not in df.columns:
        raise ValueError("CSV must contain a 'CLUSTER' column.")
    
    # Get feature columns regarding clustering (all principal components)
    feature_cols = [col for col in df.columns if col in PCA_COLS]
    
    results = {"total": 0}
    for cluster, group in df.groupby("Cluster"):
        # Compute mean of the cluster
        mean_vector = group[feature_cols].mean().values
        # Compute squared distances to mean
        sq_dists = np.sum((group[feature_cols].values - mean_vector) ** 2, axis=1)
        # Variance = average squared distance
        variance = np.mean(sq_dists)
        results[cluster] = variance
        results["total"] += variance
    
    return results


if __name__ == "__main__":
    csv_file = "Q:\\Marcello\\University\\impianti\\impianti-di-elaborazione\\homework\\python\\deviance\\pca_clustering.csv"  
    
    pca_lost, pca_retained = variance_lost_after_pca(csv_file)

    print(f"Variance retained: {pca_retained*100:.2f}%")
    print(f"Variance lost: {pca_lost*100:.2f}%")
    
    
    variances = intracluster_variance(csv_file)
    print("Intra-cluster variances:")
    for cluster, var in variances.items():
        print(f"Cluster {cluster}: {var:.4f}")
        
    # Use the total value from the results dict
    total_dev_lost = pca_lost + (variances["total"]/100) * pca_retained
    print(f"Total deviance lost: {total_dev_lost}")
