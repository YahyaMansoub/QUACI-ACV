import dash
from dash import dcc, html, Input, Output, State, callback, no_update, ALL
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import base64
import io
import itertools
from scipy.stats import rankdata
from typing import List, Dict, Tuple

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
# Suppress callback exceptions to handle components created by callbacks
app.config.suppress_callback_exceptions = True

# Define input control components that will be used in callbacks
upload_component = dcc.Upload(
    id="upload-data",
    children=html.Div(["Drag and Drop or ", html.A("Select CSV File")]),
    style={
        'width': '100%', 'height': '60px', 'lineHeight': '60px',
        'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
        'textAlign': 'center', 'margin': '10px 0'
    }
)

generate_component = dbc.Row([
    dbc.Col([
        dbc.InputGroup([
            dbc.InputGroupText("Simulations"),
            dbc.Input(id="rows-input", type="number", value=1000, min=2)
        ])
    ], md=4),
    dbc.Col([
        dbc.InputGroup([
            dbc.InputGroupText("Number of Factors"),
            dbc.Input(id="factors-count", type="number",
                      value=10, min=1, max=50)
        ])
    ], md=4),
    dbc.Col([
        dbc.Button("Generate Data", id="generate-btn", color="primary")
    ], md=4)
])

# Updated layout with data upload and visualization controls
app.layout = dbc.Container([
    html.H1("Environmental Impact Analysis", className="mb-4 text-center"),

    # Data Input Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Data Input Method"),
                dbc.CardBody([
                    dbc.RadioItems(
                        id="input-method",
                        options=[
                            {"label": "Upload CSV", "value": "upload"},
                            {"label": "Generate Data", "value": "generate"}
                        ],
                        value="generate"
                    ),
                    html.Div(id="input-controls", className="mt-3",
                             children=generate_component)
                ])
            ])
        ], md=12)
    ]),

    # Visualization Controls
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Analysis Tools"),
                dbc.CardBody([
                    dbc.ButtonGroup([
                        dbc.Button("Radar Chart", id="radar-btn",
                                   color="primary"),
                        dbc.Button("Ranking Heatmap",
                                   id="ranking-heatmap-btn", color="success"),
                        dbc.Button("Discernibility",
                                   id="discernibility-btn", color="warning")
                    ]),
                    html.Div(id="visualization-container", className="mt-4")
                ])
            ])
        ], md=12)
    ]),

    # Add Discernibility Parameters card
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Discernibility Parameters"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Alternatives"),
                                dbc.Input(id="num-alternatives",
                                          type="number", value=2, min=2)
                            ])
                        ], md=4),
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.InputGroupText("Simulations per Alt"),
                                dbc.Input(id="sims-per-alt",
                                          type="number", value=500)
                            ])
                        ], md=4)
                    ])
                ])
            ])
        ], md=12)
    ]),

    # Data storage
    dcc.Store(id="stored-data"),
    dcc.Store(id="current-factors")
], fluid=True)

# Data input controls


@app.callback(
    Output("input-controls", "children"),
    Input("input-method", "value")
)
def update_input_controls(method):
    # Always return both components, but control visibility with style
    upload_style = {'display': 'block'} if method == "upload" else {
        'display': 'none'}
    generate_style = {'display': 'block'} if method == "generate" else {
        'display': 'none'}

    return [
        html.Div(upload_component, style=upload_style, id="upload-container"),
        html.Div(generate_component, style=generate_style,
                 id="generate-container")
    ]
# Data processing callbacks


@app.callback(
    Output("stored-data", "data"),
    Output("current-factors", "data"),
    [Input("upload-data", "contents"),
     Input("generate-btn", "n_clicks")],
    [State("input-method", "value"),
     State("rows-input", "value"),
     State("factors-count", "value")],
    prevent_initial_call=True
)
def process_data(contents, n_clicks, method, rows, factors_count):
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "upload-data" and contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        factors = df.columns.tolist()
        return df.to_dict('records'), factors

    elif trigger_id == "generate-btn":
        factors = ENVIRONMENTAL_FACTORS[:factors_count]
        data = {
            'values': np.random.normal(loc=50, scale=10, size=(rows, factors_count)).tolist(),
            'columns': factors
        }
        return data, factors

    return no_update, no_update


def create_radar_figure(df, factors):
    fig = go.Figure()
    stats = df.agg(['mean', 'median', 'std']).reset_index()

    for stat in ['mean', 'median']:
        values = stats[stats['index'] == stat].values[0][1:]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=factors,
            fill='toself',
            name=stat.capitalize()
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title="Environmental Factor Radar Analysis"
    )
    return fig


def plot_ranking_probabilities_heatmap(df, factors):
    # Calculate ranking probabilities
    ranks = df.rank(axis=1, method='first', ascending=False)
    prob_data = pd.DataFrame(index=factors)

    for i in range(1, len(factors) + 1):
        prob_data[i] = 0.0

    for col in factors:
        rank_counts = ranks[col].value_counts(normalize=True)
        for rank, prob in rank_counts.items():
            prob_data.at[col, rank] = prob

    heatmap = go.Heatmap(
        z=prob_data.values,
        x=prob_data.columns,
        y=prob_data.index,
        colorscale='Viridis',
        hoverongaps=False
    )

    layout = go.Layout(
        title="Ranking Probabilities Heatmap",
        xaxis_title="Rank Position",
        yaxis_title="Environmental Factor",
        height=800
    )

    return go.Figure(data=[heatmap], layout=layout)


def create_discernibility_heatmap(df, factors, num_alts, sims_per_alt):
    try:
        # Validate there's enough data for the analysis
        required_rows = num_alts * sims_per_alt
        if len(df) < required_rows:
            return go.Figure().add_annotation(
                text=f"Not enough data. Need {required_rows} rows but only have {len(df)}.",
                showarrow=False,
                font=dict(color="red", size=16)
            )

        # Split data into alternatives
        matrices = []
        for i in range(num_alts):
            start_idx = i * sims_per_alt
            end_idx = (i+1) * sims_per_alt
            if end_idx > len(df):
                raise ValueError(
                    f"Not enough data for {num_alts} alternatives with {sims_per_alt} simulations each")
            matrices.append(df.iloc[start_idx:end_idx][factors].values)

        # Calculate discernibility probabilities
        comparisons = []
        heatmap_data = []

        for i, j in itertools.combinations(range(num_alts), 2):
            prob = np.mean(matrices[i] - matrices[j] < 0, axis=0)
            comparisons.append(f"Alt {i+1} vs Alt {j+1}")
            heatmap_data.append(prob)

        heatmap_df = pd.DataFrame(
            heatmap_data, index=comparisons, columns=factors)

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
            yaxis_title="Alternative Comparisons",
            height=400 + 20*len(comparisons),
            width=800 + 30*len(factors)
        )

        return fig
    except Exception as e:
        return go.Figure().add_annotation(text=f"Error: {str(e)}", showarrow=False)

# Updated visualization callback with discernibility parameters


@app.callback(
    Output("visualization-container", "children"),
    [Input("radar-btn", "n_clicks"),
     Input("ranking-heatmap-btn", "n_clicks"),
     Input("discernibility-btn", "n_clicks")],
    [State("stored-data", "data"),
     State("current-factors", "data"),
     State("num-alternatives", "value"),
     State("sims-per-alt", "value")],
    prevent_initial_call=True
)
def update_visualization(radar_clicks, heatmap_clicks, discern_clicks, data, factors, num_alts, sims_per_alt):
    ctx = dash.callback_context
    if not ctx.triggered or not data:
        return dbc.Alert("No data available", color="warning")

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Convert data to DataFrame
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data['values'], columns=data['columns'])

    if button_id == "radar-btn":
        return dcc.Graph(figure=create_radar_figure(df, factors))
    elif button_id == "ranking-heatmap-btn":
        return dcc.Graph(figure=plot_ranking_probabilities_heatmap(df, factors))
    elif button_id == "discernibility-btn":
        return dcc.Graph(figure=create_discernibility_heatmap(df, factors, num_alts, sims_per_alt))

    return dbc.Alert("Select a visualization type", color="info")


if __name__ == "__main__":
    app.run(debug=True)
