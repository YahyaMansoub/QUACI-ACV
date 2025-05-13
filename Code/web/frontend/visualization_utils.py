import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import numpy as np

def plot_pca_from_matrix(matrix: pd.DataFrame, title="PCA Visualization"):
    matrix = matrix.replace([np.inf, -np.inf], np.nan).dropna(axis=1)
    if matrix.shape[1] < 2:
        raise ValueError("Not enough valid columns after cleaning to perform PCA.")

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(matrix.values.T)

    pca = PCA(n_components=2)
    components = pca.fit_transform(scaled_data)

    fig, ax = plt.subplots(figsize=(8, 6))
    for i, name in enumerate(matrix.columns):
        ax.scatter(components[i, 0], components[i, 1], label=name)
        ax.text(components[i, 0], components[i, 1], name)

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title(title)
    ax.legend(loc="best")
    return fig

def plot_iqr_per_column(df: pd.DataFrame, title="IQR per Material"):
    iqr_values = df.quantile(0.75) - df.quantile(0.25)
    fig, ax = plt.subplots(figsize=(10, 5))
    iqr_values.plot(kind='bar', ax=ax)
    ax.set_title(title)
    ax.set_ylabel("IQR")
    ax.set_xlabel("Materials")
    plt.xticks(rotation=45, ha='right')
    return fig

def plot_material_distribution(df: pd.DataFrame, title="Material Distribution"):
    fig, ax = plt.subplots(figsize=(12, 6))
    df.sum(axis=0).sort_values().plot(kind='barh', ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Total Impact")
    return fig

def plot_parallel_coordinates(data: pd.DataFrame, class_column: str = None, title="Parallel Coordinates Plot"):
    use_color = class_column if class_column and pd.api.types.is_numeric_dtype(data[class_column]) else None
    fig = px.parallel_coordinates(data, color=use_color)
    fig.update_layout(title=title)
    return fig

def plot_ranking_probabilities_heatmap(result: dict, title="Ranking Probabilities Heatmap"):
    if not all(k in result for k in ['rows', 'cols', 'data']):
        raise ValueError("Result does not contain expected keys: 'rows', 'cols', 'data'.")

    rows = result['rows']
    cols = result['cols']
    data = result['data']

    heatmap_array = [[0 for _ in cols] for _ in rows]
    for r, c, v in data:
        heatmap_array[r][c] = v

    df = pd.DataFrame(heatmap_array, index=rows, columns=cols)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df, cmap='viridis', annot=True, fmt=".2f", ax=ax)
    ax.set_title(title)
    plt.tight_layout()
    return fig

def radar_chart_median_iqr(result: dict, title="Radar Chart (Median & IQR)"):
    from math import pi
    if not result or 'factors' not in result or 'values' not in result:
        raise ValueError("Invalid radar chart input structure.")

    labels = result['factors']
    categories = list(result['values'].keys())

    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))
    angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
    angles += angles[:1]

    for category in categories:
        medians = result['values'][category]['median'] + result['values'][category]['median'][:1]
        ax.plot(angles, medians, linewidth=1, linestyle='solid', label=str(category))
        ax.fill(angles, medians, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    return fig

def plot_discernibility_heatmap(result: dict, title="Discernibility Heatmap"):
    if not all(k in result for k in ['rows', 'cols', 'data']):
        raise ValueError("Result missing expected keys: 'rows', 'cols', 'data'.")

    rows = result['rows']
    cols = result['cols']
    data = result['data']

    heatmap_array = [[0 for _ in cols] for _ in rows]
    for r, c, v in data:
        heatmap_array[r][c] = v

    df = pd.DataFrame(heatmap_array, index=rows, columns=cols)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df, cmap="coolwarm", annot=True, fmt=".2f", ax=ax)
    ax.set_title(title)
    plt.tight_layout()
    return fig
