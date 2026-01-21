import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

def plot_metrics(grouped_df, metrics, plot_dir, output_file_name, xLabel: str, yLabel: str, title: str, legend: bool = False, axvline_x = None, axvline_x2 = None):
    plt.figure(figsize=(8, 5))
    # Plot each metric as a line
    for col in [metrics]:
        plt.plot(grouped_df["prefix"], grouped_df[col], marker="o", linestyle="-", label=col)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.grid(True, linestyle="--", alpha=0.6)
    if legend:
        plt.legend(title="metric")
    if axvline_x:
        plt.axvline(
            x=axvline_x,
            color='green',
            linestyle='--',
            linewidth=0.9,
            label='Knee Capacity'
        )
    if axvline_x2:
        plt.axvline(
            x=axvline_x2,
            color='blue',
            linestyle='--',
            linewidth=0.9,
            label='Usable Capacity'
        )
    if axvline_x or axvline_x2:
        plt.legend()
    plt.xticks(grouped_df["prefix"])
    plt.tight_layout()
    plt.savefig(f"{plot_dir}/{output_file_name}.png")
    plt.close()