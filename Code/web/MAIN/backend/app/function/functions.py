
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_discernibility_heatmap(
    matrices: List[np.ndarray],
    labels: List[str],
    factor_names: List[str],
    heatmap_theme: str = "viridis",
    annot_fontsize: int = 10,
    label_fontsize: int = 12,
    title_fontsize: int = 14,
    cell_padding: float = 0.1,
    colorbar_shrink: float = 0.8,
):
    """
    Plots a heatmap of discernibility analysis for multiple alternatives and factors.

    Parameters:
    matrices (List[np.ndarray]): List of matrices for each alternative (shape: n_samples x n_factors).
    labels (List[str]): List of labels for each alternative.
    factor_names (List[str]): List of names for each factor (e.g., water, carbon, material).
    heatmap_theme (str): Color palette for the heatmap. Default is "YlGnBu".
    annot_fontsize (int): Font size for annotations inside the heatmap cells. Default is 10.
    label_fontsize (int): Font size for axis labels. Default is 12.
    title_fontsize (int): Font size for the title. Default is 14.
    cell_padding (float): Padding between heatmap cells. Default is 0.1.
    colorbar_shrink (float): Shrink factor for the colorbar. Default is 0.8.
    """
    n_alternatives = len(matrices)
    n_factors = matrices[0].shape[1]

    # Initialize a matrix to store discernibility probabilities
    heatmap_data = np.zeros(
        (n_alternatives * (n_alternatives - 1) // 2, n_factors))

    # Fill the heatmap data
    row_labels = []
    idx = 0

    for i in range(n_alternatives):
        for j in range(i + 1, n_alternatives):
            row_labels.append(f"{labels[i]} > {labels[j]}")
            heatmap_data[idx, :] = Discernibility_Analysis(
                matrices[i], matrices[j])
            idx += 1

    # Dynamically adjust figure size based on heatmap dimensions
    # Adjust width based on number of factors
    fig_width = max(10, n_factors * 1.5)
    # Adjust height based on number of comparisons
    fig_height = max(6, len(row_labels) * 0.5)
    plt.figure(figsize=(fig_width, fig_height))

    # Plot the heatmap
    ax = sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".2f",
        cmap=heatmap_theme,
        xticklabels=factor_names,
        yticklabels=row_labels,
        annot_kws={"size": annot_fontsize},  # Customize annotation font size
        linewidths=cell_padding,  # Add padding between cells
        cbar_kws={"shrink": colorbar_shrink},  # Adjust colorbar size
    )

    # Customize axis labels and title
    plt.xlabel("Factors", fontsize=label_fontsize)
    plt.ylabel("Alternative Comparisons", fontsize=label_fontsize)
    plt.title("Discernibility Analysis Heatmap",
              fontsize=title_fontsize, pad=20)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha="right", fontsize=label_fontsize)
    plt.yticks(fontsize=label_fontsize)

    # Adjust layout to prevent overlapping
    plt.tight_layout()

    # Show the plot
    plt.show()