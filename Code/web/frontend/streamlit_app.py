# frontend/streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import seaborn as sns

from visualization_utils import (
    plot_pca_from_matrix,
    plot_iqr_per_column,
    plot_material_distribution,
    plot_parallel_coordinates,
    plot_ranking_probabilities_heatmap,
    radar_chart_median_iqr,
    plot_discernibility_heatmap
)

st.set_page_config(page_title="ACV Analysis", layout="wide")
API_BASE_URL = "http://localhost:5000/api"

def upload_csv(file):
    files = {'file': (file.name, file, 'text/csv')}
    try:
        res = requests.post(f"{API_BASE_URL}/upload", files=files)
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        st.error(f"❌ Upload failed: {e}")
        return None

def fetch_analysis_result(endpoint):
    try:
        res = requests.get(f"{API_BASE_URL}/upload/results/{endpoint}")
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        st.error(f"❌ Failed to fetch {endpoint} data: {e}")
        return None

def plot_heatmap(matrix_data, title):
    if not matrix_data or not all(k in matrix_data for k in ['rows', 'cols', 'data']):
        st.warning(f"⚠️ No heatmap data found for {title}")
        return
    rows = matrix_data['rows']
    cols = matrix_data['cols']
    data = matrix_data['data']
    heatmap_array = [[0] * len(cols) for _ in range(len(rows))]
    for r, c, v in data:
        if r < len(rows) and c < len(cols):
            heatmap_array[r][c] = v
    df = pd.DataFrame(heatmap_array, index=rows, columns=cols)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df, cmap="viridis", annot=False, ax=ax)
    ax.set_title(title)
    st.pyplot(fig)

def plot_boxplot(box_data, title):
    if not box_data or 'boxData' not in box_data or 'axis' not in box_data:
        st.warning(f"No boxplot data found for {title}")
        return
    df = pd.DataFrame(box_data['boxData'], index=box_data['axis'])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df.T, ax=ax)
    ax.set_title(title)
    st.pyplot(fig)

def main():
    st.title("🏗️ Life Cycle Assessment Dashboard (ACV)")

    uploaded_file = st.file_uploader("📁 Upload a CSV file", type=["csv"])
    df = None

    if uploaded_file:
        result = upload_csv(uploaded_file)
        if result:
            st.success(result.get('message', '✅ File uploaded successfully.'))

        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        numeric_df = df.select_dtypes(include=['float64', 'int64'])

        st.subheader("📊 Choose analyses to run")
        options = st.multiselect(
            "Available Analyses",
            ['uncertainty', 'smd', 'drd', 'heijungs', 'discernability', 'ranking'],
            default=['uncertainty', 'smd', 'drd']
        )

        for option in options:
            st.markdown(f"### 🔍 {option.capitalize()} Analysis")
            data = fetch_analysis_result(option)
            if not data:
                st.warning(f"No result returned for {option}.")
                continue

            if option == 'ranking':
                plot_ranking_probabilities_heatmap(data)  # requires preprocessed input

            elif option == 'discernability':
                plot_discernibility_heatmap(data)

            elif option in ['smd', 'drd']:
                if option in data:
                    plot_heatmap(data[option], f"{option.capitalize()} Heatmap")
                else:
                    st.warning(f"⚠️ No structured heatmap data in '{option}' result.")
            else:
                st.json(data)

        st.divider()
        st.subheader("🧪 Additional Visualizations")

        if st.button("PCA Projection"):
            try:
                fig = plot_pca_from_matrix(numeric_df)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Failed to plot PCA: {e}")

        if st.button("IQR per Material"):
            try:
                fig = plot_iqr_per_column(numeric_df)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Failed to plot IQR: {e}")

        if st.button("Material Distribution"):
            try:
                fig = plot_material_distribution(numeric_df)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Failed to plot material distribution: {e}")

        if st.button("Parallel Coordinates Plot"):
            try:
                parallel_df = numeric_df.copy()
                if df.shape[1] > 0:
                    parallel_df.insert(0, "Impact", df.iloc[:, 0])
                fig = plot_parallel_coordinates(parallel_df)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to plot parallel coordinates: {e}")

        if st.button("Radar Chart (Median & IQR)"):
            try:
                fig = radar_chart_median_iqr(numeric_df)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Failed to plot radar chart: {e}")

if __name__ == "__main__":
    main()
