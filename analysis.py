import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def compute_smd(a1, a2):
    """
    Compute Standardized Mean Difference (SMD) for each indicator.
    
    Parameters:
    -----------
    a1: np.array (n_simulations, k_indicators)
        First alternative matrix
    a2: np.array (n_simulations, k_indicators)
        Second alternative matrix
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with SMD values and standard errors
    """
    mean_diff = np.mean(a1 - a2, axis=0)
    std_diff = np.std(a1 - a2, axis=0, ddof=1)
    smd = mean_diff / std_diff  # Cohen's d for each indicator
    std_error = std_diff / np.sqrt(a1.shape[0])  # Standard error for error bars

    smd_df = pd.DataFrame(
        {'SMD': smd, 'StdError': std_error},
        index=[f'Indicator {i+1}' for i in range(a1.shape[1])]
    )
    return smd_df

def compute_drd(a1, a2):
    """
    Compute Distribution of Relative Differences (DRD) for each indicator.
    
    Parameters:
    -----------
    a1: np.array (n_simulations, k_indicators)
        First alternative matrix
    a2: np.array (n_simulations, k_indicators)
        Second alternative matrix
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with DRD values
    """
    drd = (a1 - a2) / np.maximum(a1, a2)  # Element-wise operation
    drd_df = pd.DataFrame(drd, columns=[f'Indicator {i+1}' for i in range(a1.shape[1])])
    return drd_df

def plot_smd(smd_df):
    """
    Plot the Standardized Mean Difference (SMD) values using a horizontal bar chart with confidence intervals.
    
    Parameters:
    -----------
    smd_df: pd.DataFrame
        DataFrame containing SMD values and standard errors.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Sort by absolute SMD values for better visualization
    smd_df = smd_df.reindex(smd_df['SMD'].abs().sort_values(ascending=True).index)

    # Define bar colors based on significance
    colors = ['red' if abs(x) > 0.5 else 'grey' for x in smd_df['SMD']]  

    # Plot horizontal bar chart
    ax.barh(smd_df.index, smd_df['SMD'], xerr=smd_df['StdError'], color=colors, capsize=5, alpha=0.75)

    # Add reference line at 0
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1.5, label='Reference Line (0)')

    # Labels and title
    ax.set_xlabel('Standardized Mean Difference (SMD)', fontsize=12)
    ax.set_ylabel('Indicators', fontsize=12)
    ax.set_title('SMD Comparison with Confidence Intervals', fontsize=14)
    ax.legend(fontsize=10)

    plt.show()

def plot_drd(drd_df, indifference_zone=0.1):
    """
    Improved DRD boxplot function.
    
    Parameters:
    -----------
    drd_df: pd.DataFrame
        DataFrame containing DRD values for each indicator.
    indifference_zone: float, optional (default=0.1)
        The size of the indifference zone around 0.
    """
    plt.figure(figsize=(12, 6))

    # Boxplot with thinner lines
    boxprops = dict(linestyle='-', linewidth=1, color='black')
    whiskerprops = dict(linestyle='-', linewidth=1, color='black')
    capprops = dict(linewidth=1)
    medianprops = dict(color="green", linewidth=2)

    drd_df.boxplot(grid=False, boxprops=boxprops, whiskerprops=whiskerprops, 
                  capprops=capprops, medianprops=medianprops)

    # Add shaded reference region (indifference zone)
    plt.axhline(y=0, color='orange', linestyle='--', linewidth=1.5, label='Reference Line (0)')
    plt.fill_between(
        x=[0, drd_df.shape[1] + 1], 
        y1=-indifference_zone, 
        y2=indifference_zone, 
        color='orange', 
        alpha=0.3, 
        label=f'Indifference Zone (±{indifference_zone})'
    )

    # Labels and title
    plt.ylabel('DRD Value')
    plt.xlabel('Indicators')
    plt.title('Distribution of Relative Differences (DRD)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()