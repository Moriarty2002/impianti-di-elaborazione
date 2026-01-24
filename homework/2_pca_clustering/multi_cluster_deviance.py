import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Columns to exclude from feature analysis
UNUSED_COLS = ["swpd", "si", "so", "st", "time"]


def intracluster_deviance(df, cluster_col, feature_cols):
    """
    Calculates intra-cluster deviance (sum of squared distances to the cluster mean)
    for each cluster in the dataset. Features are Z-score normalized before calculation.

    Args:
        df (DataFrame): The dataset
        cluster_col (str): Name of the cluster column
        feature_cols (list): List of feature column names to use

    Returns:
        dict: Mapping from cluster label to its deviance (SST) value. The key
              "total" contains the sum of all cluster deviances.
    """
    # Filter valid cluster assignments
    df_filtered = df[df[cluster_col].notna() & (df[cluster_col].astype(str).str.strip() != '')]
    
    if df_filtered.empty:
        raise ValueError(f"No rows with a valid '{cluster_col}' found after filtering.")

    # Z-score normalization on features (CRITICAL for scale consistency)
    df_norm = df_filtered[feature_cols].apply(lambda x: (x - x.mean()) / x.std(ddof=0))
    
    # Create a copy with normalized features for grouping
    df_work = df_filtered.copy()
    df_work[feature_cols] = df_norm

    results = {"total": 0}
    for cluster, group in df_work.groupby(cluster_col):
        # Compute mean vector of the cluster (on normalized features)
        mean_vector = group[feature_cols].mean().values
        # Compute squared distances to mean for each row
        sq_dists = np.sum((group[feature_cols].values - mean_vector) ** 2, axis=1)
        # Deviance (SST) for the cluster = sum of squared distances
        deviance_cluster = np.sum(sq_dists)
        results[str(cluster)] = deviance_cluster
        results["total"] += deviance_cluster

    return results


def calculate_total_deviance(df, feature_cols):
    """
    Calculate total deviance (SST) of features.
    
    Args:
        df (DataFrame): The dataset
        feature_cols (list): List of feature column names to use
        
    Returns:
        float: Total deviance
    """
    # Z-score normalization on features
    df_norm = df[feature_cols].apply(lambda x: (x - x.mean()) / x.std(ddof=0))
    
    # Deviance = total sum of squared deviations (SST) across rows and features
    total_deviance = ((df_norm - df_norm.mean()) ** 2).sum().sum()
    
    return total_deviance


def process_multi_cluster_csv(csv_path):
    """
    Process a CSV file with multiple cluster columns and calculate deviance lost
    for each clusterization.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        DataFrame: Results for each cluster type with deviance metrics
    """
    # Load dataset with comma as decimal separator
    df = pd.read_csv(csv_path, sep=',', quotechar='"', decimal=',', skipinitialspace=True, engine='c')
    
    # Clean column names
    df.columns = df.columns.str.strip().str.replace("'", "")
    
    # Identify cluster columns (columns starting with 'Cluster_')
    cluster_cols = [col for col in df.columns if col.startswith('Cluster_')]
    
    if not cluster_cols:
        raise ValueError("No cluster columns found. Expected columns starting with 'Cluster_'")
    
    print(f"Found cluster columns: {cluster_cols}")
    
    # Select numeric feature columns (excluding cluster and unused columns)
    numeric_cols = df.select_dtypes(include=["number"]).columns
    feature_cols = [col for col in numeric_cols 
                   if col not in cluster_cols and col not in UNUSED_COLS]
    
    if not feature_cols:
        raise ValueError("No feature columns found for analysis.")
    
    print(f"Using feature columns: {feature_cols}")
    
    # Calculate total deviance of original features (without clustering)
    total_deviance = calculate_total_deviance(df, feature_cols)
    print(f"Total deviance (no clustering): {total_deviance:.6f}")
    
    # Process each cluster column
    results = []
    
    for cluster_col in cluster_cols:
        # Extract cluster count from column name (e.g., 'Cluster_33' -> 33)
        cluster_count = int(cluster_col.split('_')[-1])
        error_msg = ""
        
        try:
            # Calculate intra-cluster deviance
            deviances = intracluster_deviance(df, cluster_col, feature_cols)
            intra_total = deviances.get("total", 0)
            
            # Normalized intra-cluster deviance (same as original script)
            normalized_intra = intra_total / total_deviance if total_deviance > 0 else 0
            
            # For no PCA: pca_lost = 0, pca_retained = 1
            # Following original formula: total_dev_lost = pca_lost + normalized_intra * pca_retained
            pca_lost = 0.0
            pca_retained = 1.0
            
            # deviance_retained in original script context refers to PCA retention
            deviance_retained = pca_retained
            deviance_lost = pca_lost
            
            # Total deviance lost following original formula
            total_dev_lost = pca_lost + normalized_intra * pca_retained
            
            # Store results in same format as original script
            results.append({
                'PCA': 0,  # No PCA applied
                'Cluster': cluster_count,
                'deviance_retained': deviance_retained,
                'deviance_lost': deviance_lost,
                'intra_cluster_total': intra_total,
                'total_dev_lost': total_dev_lost,
                'error': error_msg
            })
            
            print(f"Processed: {cluster_col} -> retained={deviance_retained:.6f}, lost={deviance_lost:.6f}, intra_total={intra_total}, total_dev_lost={total_dev_lost:.6f}")
            
        except Exception as e:
            error_msg = f"Error: {e}"
            print(f"Error processing {cluster_col}: {e}")
            results.append({
                'PCA': 0,
                'Cluster': cluster_count,
                'deviance_retained': float('nan'),
                'deviance_lost': float('nan'),
                'intra_cluster_total': float('nan'),
                'total_dev_lost': float('nan'),
                'error': error_msg
            })
    
    return pd.DataFrame(results)


def plot_deviance_results(results_df, output_path):
    """
    Create plots showing deviance lost and retained for each cluster type.
    
    Args:
        results_df (DataFrame): Results dataframe
        output_path (str): Path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Sort by number of clusters
    results_df = results_df.sort_values('Cluster')
    
    # Plot 1: Deviance Lost vs Number of Clusters
    ax1.plot(results_df['Cluster'], results_df['deviance_lost'], 
             marker='o', linewidth=2, markersize=8, color='#e74c3c')
    ax1.set_xlabel('Number of Clusters', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Deviance Lost', fontsize=12, fontweight='bold')
    ax1.set_title('Deviance Lost vs Number of Clusters', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(results_df['Cluster'])
    
    # Add value labels
    for x, y in zip(results_df['Cluster'], results_df['deviance_lost']):
        ax1.annotate(f'{y:.4f}', (x, y), textcoords="offset points", 
                    xytext=(0, 10), ha='center', fontsize=9)
    
    # Plot 2: Deviance Retained vs Number of Clusters
    ax2.plot(results_df['Cluster'], results_df['deviance_retained'], 
             marker='s', linewidth=2, markersize=8, color='#3498db')
    ax2.set_xlabel('Number of Clusters', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Deviance Retained', fontsize=12, fontweight='bold')
    ax2.set_title('Deviance Retained vs Number of Clusters', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(results_df['Cluster'])
    
    # Add value labels
    for x, y in zip(results_df['Cluster'], results_df['deviance_retained']):
        ax2.annotate(f'{y:.4f}', (x, y), textcoords="offset points", 
                    xytext=(0, 10), ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_path}")
    plt.close()
    
    # Create combined plot showing both metrics
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = results_df['Cluster']
    width = 0.35
    x_pos = np.arange(len(x))
    
    bars1 = ax.bar(x_pos - width/2, results_df['deviance_lost'], width, 
                   label='Deviance Lost', color='#e74c3c', alpha=0.8)
    bars2 = ax.bar(x_pos + width/2, results_df['deviance_retained'], width, 
                   label='Deviance Retained', color='#3498db', alpha=0.8)
    
    ax.set_xlabel('Number of Clusters', fontsize=12, fontweight='bold')
    ax.set_ylabel('Deviance', fontsize=12, fontweight='bold')
    ax.set_title('Deviance Lost vs Retained by Cluster Count', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.4f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    combined_path = output_path.replace('.png', '_combined.png')
    plt.savefig(combined_path, dpi=300, bbox_inches='tight')
    print(f"Combined plot saved to: {combined_path}")
    plt.close()


if __name__ == "__main__":
    # Get absolute path to the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Input CSV file
    csv_file = os.path.join(script_dir, "csv", "no_pca_only_clustering.csv")
    
    # Output files
    results_file = os.path.join(script_dir, "multi_cluster_results.csv")
    plot_file = os.path.join(script_dir, "plots", "multi_cluster_deviance.png")
    
    # Ensure plots directory exists
    os.makedirs(os.path.dirname(plot_file), exist_ok=True)
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at '{csv_file}'")
    else:
        print(f"Processing: {os.path.basename(csv_file)}\n")
        
        # Process the CSV and calculate deviance metrics
        results_df = process_multi_cluster_csv(csv_file)
        
        # Save results to CSV
        results_df.to_csv(results_file, index=False, float_format='%.6f')
        print(f"\nAppended results to: {results_file}")
        
        # Create plots
        print("\nGenerating plots...")
        plot_deviance_results(results_df, plot_file)
        
        print("\nProcessing complete!")
