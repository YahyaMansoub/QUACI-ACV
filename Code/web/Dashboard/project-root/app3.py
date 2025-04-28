import dash
from dash import dcc, html, Input, Output, State, callback, no_update, ALL
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.colors import hex_to_rgb
import base64
import io
import itertools
from typing import List, Tuple, Dict

# Predefined environmental factors (50 examples)
ENVIRONMENTAL_FACTORS = [
    "Carbon Footprint", "Water Usage Efficiency", "Renewable Energy Ratio",
    "Waste Recycling Rate", "Air Quality Index", "Biodiversity Impact",
    "Soil Contamination Level", "Noise Pollution Index", "Energy Consumption Intensity",
    "Material Circularity", "Toxic Emissions", "Land Use Efficiency",
    "Sustainable Sourcing Score", "Environmental Compliance Index",
    "Greenhouse Gas Intensity", "Water Pollution Index", "Ecosystem Services Impact",
    "Environmental Remediation Costs", "Climate Resilience Score",
    "Environmental Impact Score", "Resource Depletion Rate",
    "Environmental Management System Score", "Eco-Innovation Index",
    "Lifecycle Assessment Score", "Environmental Risk Exposure",
    "Carbon Offset Capacity", "Environmental Liability Index",
    "Sustainable Packaging Score", "Environmental Audit Score",
    "Environmental Investment Ratio", "Eco-Efficiency Ratio",
    "Environmental Product Declaration", "Clean Energy Transition Score",
    "Environmental Compliance Costs", "Environmental Performance Index",
    "Environmental Technology Adoption", "Environmental Impact Ratio",
    "Sustainable Transportation Score", "Environmental Education Index",
    "Environmental Policy Score", "Environmental Monitoring Frequency",
    "Environmental Certification Score", "Environmental Impact Transparency",
    "Environmental Data Accuracy", "Environmental Reporting Quality",
    "Environmental Stakeholder Engagement", "Environmental Impact Mitigation",
    "Environmental Restoration Capacity", "Environmental Impact Duration"
]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.title = "Environmental Impact Analysis Dashboard"
app.config.suppress_callback_exceptions = True


def generate_matrix(rows: int, columns: int, distributions: List[Tuple[float, float]] = None,
                    global_mean_std: Tuple[float, float] = None) -> np.ndarray:
    if global_mean_std:
        mean, std = global_mean_std
        return np.random.normal(loc=mean, scale=std, size=(rows, columns))

    if distributions is None or len(distributions) != columns:
        raise ValueError(
            "Number of distributions must match columns or provide global mean/std")

    matrix = np.zeros((rows, columns))
    for col in range(columns):
        mean, std = distributions[col]
        matrix[:, col] = np.random.normal(loc=mean, scale=std, size=rows)
    return matrix


def Discernibility_Analysis(mat1: np.ndarray, mat2: np.ndarray) -> np.ndarray:
    if mat1.shape[1] != mat2.shape[1]:
        raise ValueError("Matrices must have same number of columns")
    return np.mean(mat1 - mat2 < 0, axis=0)


app.layout = dbc.Container([
    html.H1("Environmental Impact Analysis Dashboard",
            className="mb-4 text-center"),

    # Matrix Generation Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Matrix Generation Parameters"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Rows"),
                                dbc.Input(id="rows-input",
                                          type="number", value=1000)
                            ])
                        ], md=4),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Columns"),
                                dbc.Input(id="columns-input",
                                          type="number", value=10)
                            ])
                        ], md=4),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Matrix Name"),
                                dbc.Input(id="matrix-name", type="text",
                                          placeholder="Enter name")
                            ])
                        ], md=4)
                    ]),
                    html.Br(),
                    dbc.RadioItems(
                        id="dist-type",
                        options=[
                            {"label": "Global Distribution", "value": "global"},
                            {"label": "Per-Column Distribution", "value": "column"}
                        ],
                        value="global"
                    ),
                    html.Div(id="distribution-inputs"),
                    dbc.Button("Generate Matrix", id="generate-btn",
                               color="primary", className="mt-3")
                ])
            ])
        ], md=12)
    ]),

    # Matrix Selection and Analysis
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Matrix Operations"),
                dbc.CardBody([
                    dcc.Store(id="generated-matrices", data={}),
                    dcc.Store(id="selected-matrices", data=[]),
                    html.Div(id="matrix-cards", className="mb-3"),
                    dbc.Textarea(id="factors-input", placeholder="Enter comma-separated factor names...",
                                 className="mb-3", rows=3),
                    dbc.ButtonGroup([
                        dbc.Button("Radar Chart", id="radar-btn",
                                   color="primary"),
                        dbc.Button("Ranking Heatmap",
                                   id="ranking-heatmap-btn", color="success"),
                        dbc.Button("Discernibility",
                                   id="discernibility-btn", color="warning")
                    ])
                ])
            ])
        ], md=12)
    ]),

    # Visualizations
    dcc.Loading(
        id="loading-visualizations",
        type="circle",
        children=html.Div(id="visualization-container", className="mt-4")
    )
], fluid=True)

# Callbacks


@callback(
    Output("distribution-inputs", "children"),
    Input("dist-type", "value"),
    State("columns-input", "value")
)
def update_distribution_inputs(dist_type, columns):
    if dist_type == "global":
        return dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText("Mean"),
                    dbc.Input(id="global-mean", type="number", value=50)
                ])
            ], md=6),
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText("Std"),
                    dbc.Input(id="global-std", type="number", value=10)
                ])
            ], md=6)
        ])
    else:
        inputs = []
        for i in range(columns):
            inputs.append(dbc.Row([
                dbc.Col(html.Strong(f"Col {i+1}"), width=2),
                dbc.Col(dbc.Input(type="number", placeholder="Mean",
                        id={"type": "col-mean", "index": i})),
                dbc.Col(dbc.Input(type="number", placeholder="Std",
                        id={"type": "col-std", "index": i}))
            ], className="mb-2"))
        return inputs


@callback(
    Output("generated-matrices", "data"),
    Output("matrix-cards", "children"),
    Input("generate-btn", "n_clicks"),
    State("rows-input", "value"),
    State("columns-input", "value"),
    State("dist-type", "value"),
    State({"type": "col-mean", "index": ALL}, "value"),
    State({"type": "col-std", "index": ALL}, "value"),
    State("global-mean", "value"),
    State("global-std", "value"),
    State("matrix-name", "value"),
    State("generated-matrices", "data")
)
def generate_and_store_matrix(n, rows, cols, dist_type, col_means, col_stds, g_mean, g_std, name, stored_data):
    if n is None:
        return no_update, no_update

    try:
        if dist_type == "global":
            matrix = generate_matrix(
                rows, cols, global_mean_std=(g_mean, g_std))
        else:
            distributions = list(zip(col_means, col_stds))
            matrix = generate_matrix(rows, cols, distributions=distributions)

        name = name or f"Matrix {len(stored_data)+1}"
        stored_data[name] = matrix.tolist()

        cards = []
        for mat_name in stored_data:
            cards.append(dbc.Col(dbc.Card([
                dbc.CardHeader(mat_name),
                dbc.CardBody([
                    html.P(f"{rows}x{cols} Matrix"),
                    dbc.Button("Select", id={"type": "select-btn", "index": mat_name},
                               color="primary", size="sm")
                ])
            ], className="m-2"), md=3))

        return stored_data, cards
    except Exception as e:
        return no_update, dbc.Alert(str(e), color="danger")


@callback(
    Output("selected-matrices", "data"),
    Input({"type": "select-btn", "index": ALL}, "n_clicks"),
    State("selected-matrices", "data"),
    prevent_initial_call=True
)
def update_selected_matrices(clicks, selected):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    mat_name = eval(button_id)['index']

    if mat_name not in selected:
        return selected + [mat_name]
    return selected


@callback(
    Output("visualization-container", "children"),
    Input("radar-btn", "n_clicks"),
    Input("ranking-heatmap-btn", "n_clicks"),
    Input("discernibility-btn", "n_clicks"),
    State("selected-matrices", "data"),
    State("generated-matrices", "data"),
    State("factors-input", "value"),
    prevent_initial_call=True
)
def update_visualization(radar_clicks, heatmap_clicks, discern_clicks, selected, matrices, factors):
    ctx = dash.callback_context
    if not ctx.triggered or not selected:
        return dbc.Alert("No matrices selected", color="warning")

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    matrix_list = [np.array(matrices[name]) for name in selected]
    factor_list = [f.strip() for f in factors.split(',')] if factors else []

    try:
        if button_id == "radar-btn":
            return dcc.Graph(figure=create_radar_figure(matrix_list, selected, factor_list))
        elif button_id == "ranking-heatmap-btn":
            return dcc.Graph(figure=plot_ranking_probabilities(matrix_list[0], factor_list))
        elif button_id == "discernibility-btn":
            return dcc.Graph(figure=create_discernibility_heatmap(matrix_list, selected, factor_list))

        return dbc.Alert("Select a visualization type", color="info")
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")


def create_radar_figure(matrices, names, factors):
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, (matrix, name) in enumerate(zip(matrices, names)):
        stats = np.median(matrix, axis=0)
        fig.add_trace(go.Scatterpolar(
            r=np.concatenate([stats, [stats[0]]]),
            theta=factors + [factors[0]],
            name=name,
            line_color=colors[idx]
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Environmental Impact Radar Analysis"
    )
    return fig


def plot_ranking_probabilities(matrix, factors):
    df = pd.DataFrame(matrix, columns=factors)
    ranks = df.rank(axis=1, method='first', ascending=False)
    prob_data = pd.DataFrame(index=factors)

    for col in factors:
        prob_data[col] = ranks[col].value_counts(normalize=True)

    return go.Figure(data=go.Heatmap(
        z=prob_data.values,
        x=prob_data.columns,
        y=prob_data.index,
        colorscale='Viridis',
        hoverongaps=False
    ))


def create_discernibility_heatmap(matrices, names, factors):
    comparisons = []
    heatmap_data = []

    for i, j in itertools.combinations(range(len(matrices)), 2):
        prob = Discernibility_Analysis(matrices[i], matrices[j])
        comparisons.append(f"{names[i]} vs {names[j]}")
        heatmap_data.append(prob)

    heatmap_df = pd.DataFrame(heatmap_data, index=comparisons, columns=factors)

    return go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=heatmap_df.index,
        colorscale='Viridis',
        hoverongaps=False
    ))


if __name__ == "__main__":
    app.run(debug=True)
