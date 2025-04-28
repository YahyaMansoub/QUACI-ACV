import dash
from dash import dcc, html, Input, Output, State, callback, no_update, ALL
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
import pandas as pd
from typing import List, Tuple, Union, Dict
import plotly.express as px
from plotly.colors import hex_to_rgb


# Include your provided functions here


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


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.title = "Matrix Analysis Dashboard"


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
                    dbc.Input(id="global-mean", type="number", value=3)
                ])
            ], md=6),
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText("Std"),
                    dbc.Input(id="global-std", type="number", value=1)
                ])
            ], md=6)
        ])
    else:
        inputs = []
        for i in range(columns):
            inputs.append(dbc.Row([
                dbc.Col(html.Strong(f"Column {i+1}"), width=2),
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
    Output("selected-matrices-display", "children"),
    Input("selected-matrices", "data")
)
def show_selected_matrices(selected):
    if not selected:
        return dbc.Alert("No matrices selected. Select at least 2 matrices.", color="info")
    return [
        dbc.Badge(name, color="primary", className="m-1") for name in selected
    ]


@callback(
    Output("heatmap-container", "children"),
    Input("heatmap-btn", "n_clicks"),
    State("selected-matrices", "data"),
    State("generated-matrices", "data"),
    State("factors-input", "value")
)
def generate_heatmap(n, selected, matrices, factors):
    if n is None:
        return no_update

    if len(selected) < 2:
        return dbc.Alert("Please select at least 2 matrices", color="danger")

    try:
        factor_list = [f.strip()
                       for f in factors.split(',')] if factors else []
        matrix_list = [np.array(matrices[name]) for name in selected]

        if any(m.shape[1] != matrix_list[0].shape[1] for m in matrix_list):
            return dbc.Alert("All matrices must have same number of columns", color="danger")

        if len(factor_list) != matrix_list[0].shape[1]:
            return dbc.Alert("Number of factors must match matrix columns", color="danger")

        # Create heatmap data
        comparisons = []
        heatmap_data = []
        for i in range(len(matrix_list)):
            for j in range(i+1, len(matrix_list)):
                comp = f"{selected[i]} vs {selected[j]}"
                comparisons.append(comp)
                heatmap_data.append(Discernibility_Analysis(
                    matrix_list[i], matrix_list[j]))

        heatmap_df = pd.DataFrame(
            heatmap_data, index=comparisons, columns=factor_list)

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale='Viridis',
            hoverongaps=False,
            text=np.around(heatmap_df.values, decimals=2),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))

        fig.update_layout(
            title="Discernibility Analysis",
            xaxis_title="Factors",
            yaxis_title="Comparisons",
            height=400 + 20*len(comparisons),
            width=800 + 30*len(factor_list))

        return dcc.Graph(figure=fig)
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")


def create_radar_figure(matrices, matrix_names, factors, title="Radar Chart with Median and IQR"):
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly  # Default color palette

    for idx, (matrix, name) in enumerate(zip(matrices, matrix_names)):
        # Compute statistics
        median = np.median(matrix, axis=0)
        mean = np.mean(matrix, axis=0)
        q1 = np.percentile(matrix, 25, axis=0)
        q3 = np.percentile(matrix, 75, axis=0)

        # Close the loop for theta and values
        theta = list(factors) + [factors[0]]
        median_closed = np.concatenate([median, [median[0]]])
        mean_closed = np.concatenate([mean, [mean[0]]])
        q3_closed = np.concatenate([q3, [q3[0]]])
        q1_closed = np.concatenate([q1, [q1[0]]])

        # Color for this matrix
        color = colors[idx % len(colors)]
        color_rgb = hex_to_rgb(color)
        fillcolor = f'rgba({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]}, 0.2)'

        # Add median line
        fig.add_trace(go.Scatterpolar(
            r=median_closed,
            theta=theta,
            mode='lines',
            line=dict(color=color, width=2),
            name=f'{name} Median',
            showlegend=True
        ))

        # Add mean line
        fig.add_trace(go.Scatterpolar(
            r=mean_closed,
            theta=theta,
            mode='lines',
            line=dict(color=color, width=2, dash='dash'),
            name=f'{name} Mean',
            showlegend=True
        ))

        # Add IQR fill
        theta_fill = theta + theta[::-1]  # Original theta + reversed theta
        r_fill = np.concatenate([q3_closed, q1_closed[::-1]])
        fig.add_trace(go.Scatterpolar(
            r=r_fill,
            theta=theta_fill,
            fill='toself',
            fillcolor=fillcolor,
            line=dict(color='rgba(0,0,0,0)'),
            name=f'{name} IQR',
            showlegend=False  # Omit from legend to reduce clutter
        ))

    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(
                direction="clockwise",
                rotation=45  # Rotate labels if needed
            )
        ),
        title=dict(text=title, x=0.5),
        legend=dict(
            title='Matrices',
            font=dict(size=10),
            yanchor="top",
            y=1.1,
            xanchor="left",
            x=1.0
        ),
        margin=dict(l=50, r=50, b=50, t=50)
    )

    return fig


# Update the app layout to include the radar chart button and container
app.layout = dbc.Container([
    html.H1("Matrix Analysis Dashboard", className="mb-4 text-center"),

    # Control Panel and Workspace (existing code remains the same)

    # Generated Matrices Display (existing code)

    # Heatmap and Radar Display
    dcc.Loading(
        id="loading-heatmap",
        type="circle",
        children=html.Div(id="heatmap-container", className="mt-4")
    ),
    dcc.Loading(
        id="loading-radar",
        type="circle",
        children=html.Div(id="radar-container", className="mt-4")
    )
], fluid=True)

# Add the new callback for the radar chart


@callback(
    Output("radar-container", "children"),
    Input("radar-btn", "n_clicks"),
    State("selected-matrices", "data"),
    State("generated-matrices", "data"),
    State("factors-input", "value"),
    prevent_initial_call=True
)
def generate_radar_chart(n_clicks, selected, matrices, factors):
    if n_clicks is None:
        return no_update

    if len(selected) < 1:
        return dbc.Alert("Please select at least one matrix.", color="danger")

    try:
        factor_list = [f.strip()
                       for f in factors.split(',')] if factors else []
        matrix_list = [np.array(matrices[name]) for name in selected]

        if factor_list and len(factor_list) != matrix_list[0].shape[1]:
            return dbc.Alert("Number of factors must match matrix columns.", color="danger")
        elif not factor_list:
            factor_list = [
                f"Factor {i+1}" for i in range(matrix_list[0].shape[1])]

        fig = create_radar_figure(matrix_list, selected, factor_list)
        return dcc.Graph(figure=fig)
    except Exception as e:
        return dbc.Alert(f"Error generating radar chart: {str(e)}", color="danger")


# App layout
app.layout = dbc.Container([
    html.H1("Matrix Analysis Dashboard", className="mb-4 text-center"),

    # Control Panel
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
                                          type="number", value=10)
                            ])
                        ], md=6),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Columns"),
                                dbc.Input(id="columns-input",
                                          type="number", value=10)
                            ])
                        ], md=6)
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
                    dbc.InputGroup([
                        dbc.InputGroupText("Matrix Name"),
                        dbc.Input(id="matrix-name", type="text",
                                  placeholder="Enter matrix name")
                    ]),
                    dbc.Button("Generate Matrix", id="generate-btn",
                               color="primary", className="mt-3")
                ])
            ])
        ], md=4),

        # Workspace
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Analysis Workspace"),
                dbc.CardBody([
                    dcc.Store(id="generated-matrices", data={}),
                    dcc.Store(id="selected-matrices", data=[]),
                    html.Div(id="selected-matrices-display", className="mb-3"),
                    dbc.Textarea(id="factors-input", placeholder="Enter comma-separated factor names...",
                                 className="mb-3", rows=3),
                    dbc.Button("Generate Heatmap",
                               id="heatmap-btn", color="success")
                ])
            ])
        ], md=8)
    ]),

    # Generated Matrices Display
    html.Div(id="matrix-cards", className="row mt-4"),

    # Heatmap Display
    dcc.Loading(
        id="loading-heatmap",
        type="circle",
        children=html.Div(id="heatmap-container", className="mt-4")
    ),
    dcc.Loading(
        id="loading-radar",
        type="circle",
        children=html.Div(id="radar-container", className="mt-4")
    )
], fluid=True)


if __name__ == "__main__":
    app.run(debug=True)
