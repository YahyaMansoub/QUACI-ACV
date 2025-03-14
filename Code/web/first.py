import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Environmental Indicators and Random Matrix Generator"

# Define environmental indicators
environmental_indicators = [
    "Air Quality Index (AQI)", "Carbon Dioxide (CO2) Emissions", "Methane (CH4) Emissions",
    "Nitrous Oxide (N2O) Emissions", "Particulate Matter (PM2.5 and PM10)", "Ozone (O3) Concentration",
    "Water Quality Index (WQI)", "Biodiversity Index", "Deforestation Rate", "Soil Erosion Rate",
    "Waste Generation Rate", "Recycling Rate", "Energy Consumption", "Renewable Energy Usage",
    "Water Consumption", "Land Use Change"
]

# Function to generate random matrices


def generate_matrix(rows, columns, distributions=None, global_mean_std=None):
    if global_mean_std:
        mean, std = global_mean_std
        return np.random.normal(loc=mean, scale=std, size=(rows, columns))
    if distributions is None or len(distributions) != columns:
        raise ValueError(
            "Number of distributions must match the number of columns or provide a global mean and std.")
    matrix = np.zeros((rows, columns))
    for col in range(columns):
        mean, std = distributions[col]
        matrix[:, col] = np.random.normal(loc=mean, scale=std, size=rows)
    return matrix


# Layout of the Dash app
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Environmental Indicators and Random Matrix Generator"),
            className="mb-4")),  # Fixed: Added closing parenthesis

    # Input components
    dbc.Row([
        dbc.Col([
            html.Label("Select Environmental Indicators"),
            dcc.Dropdown(
                id="indicator-dropdown",
                options=[{"label": ind, "value": ind}
                         for ind in environmental_indicators],
                multi=True,
                value=[environmental_indicators[0]]
            ),
            html.Label("Number of Rows"),
            dcc.Input(id="rows-input", type="number", value=5, min=1),
            html.Label("Number of Columns"),
            dcc.Input(id="columns-input", type="number", value=3, min=1),
            html.Label("Global Mean"),
            dcc.Input(id="mean-input", type="number", value=0),
            html.Label("Global Standard Deviation"),
            dcc.Input(id="std-input", type="number", value=1),
            dbc.Button("Generate Matrix", id="generate-button",
                       color="primary", className="mt-2")
        ], width=4),

        # Output components
        dbc.Col([
            html.H4("Generated Matrix"),
            html.Div(id="matrix-output"),
            html.H4("Matrix Heatmap"),
            dcc.Graph(id="matrix-heatmap")
        ], width=8)
    ])
])

# Callback to generate matrix and heatmap


@app.callback(
    [Output("matrix-output", "children"),
     Output("matrix-heatmap", "figure")],
    [Input("generate-button", "n_clicks")],
    [State("indicator-dropdown", "value"),
     State("rows-input", "value"),
     State("columns-input", "value"),
     State("mean-input", "value"),
     State("std-input", "value")]
)
def update_matrix(n_clicks, indicators, rows, columns, mean, std):
    if n_clicks is None:
        return "", {}

    # Generate random matrix
    matrix = generate_matrix(rows, columns, global_mean_std=(mean, std))

    # Convert matrix to DataFrame for display
    df = pd.DataFrame(matrix, columns=indicators if indicators else [
                      f"Column {i+1}" for i in range(columns)])

    # Create heatmap
    heatmap = go.Figure(data=go.Heatmap(z=matrix, x=df.columns, y=[
                        f"Row {i+1}" for i in range(rows)]))
    heatmap.update_layout(title="Matrix Heatmap",
                          xaxis_title="Columns", yaxis_title="Rows")

    return df.to_string(), heatmap


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
