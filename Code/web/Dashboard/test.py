import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_leaflet as dl
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Sample data generation (replace with your actual data)


def generate_sample_data(num_houses=50):
    np.random.seed(42)
    cities = {
        "Paris": {"lat": 48.8566, "lon": 2.3522},
        "London": {"lat": 51.5074, "lon": -0.1278},
        "New York": {"lat": 40.7128, "lon": -74.0060}
    }

    data = []
    for city, coords in cities.items():
        for i in range(num_houses):
            data.append({
                "id": f"{city[:3].upper()}-{i}",
                "address": f"{np.random.randint(1, 200)} {np.random.choice(['Main', 'Oak', 'Pine', 'Maple'])} St",
                "city": city,
                "lat": coords["lat"] + np.random.uniform(-0.1, 0.1),
                "lon": coords["lon"] + np.random.uniform(-0.1, 0.1),
                "price": np.random.randint(200000, 1000000),
                "area": np.random.randint(50, 300),
                "rooms": np.random.randint(1, 6),
                "year_built": np.random.randint(1950, 2023),
                "energy_rating": np.random.choice(["A", "B", "C", "D", "E"]),
                "last_renovation": np.random.randint(2000, 2023)
            })
    return pd.DataFrame(data)


# Initialize app
app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='house-data-store', data={}),
    dcc.Store(id='selected-city-store', data=None)
])

# Location selection page
location_selection_page = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Building Statistics Dashboard",
            className="text-center my-4"))),
    dbc.Row(dbc.Col(
        html.P("Please select a location to analyze:", className="text-center"))),
    dbc.Row([
        dbc.Col(width=1),  # spacer
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Select City", className="card-title"),
                    dcc.Dropdown(
                        id='city-selector',
                        options=[
                            {'label': 'Paris', 'value': 'Paris'},
                            {'label': 'London', 'value': 'London'},
                            {'label': 'New York', 'value': 'New York'}
                        ],
                        placeholder="Select a city..."
                    ),
                    dbc.Button("Load Data", id='load-data-btn',
                               color="primary", className="mt-3")
                ])
            ])
        ], width=10),
        dbc.Col(width=1)  # spacer
    ], className="my-5")
], fluid=True)

# Main dashboard page
dashboard_page = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Button("Back to Location Selection", id='back-btn',
                       color="secondary", className="mb-3"),
            html.H3(id='city-title', className="mb-4"),
            dbc.Card([
                dbc.CardBody([
                    dl.Map(
                        id='map',
                        style={'width': '100%', 'height': '70vh',
                               'margin': "auto", "display": "block"},
                        center=[48.8566, 2.3522],  # Default to Paris
                        zoom=12,
                        children=[
                            dl.TileLayer(),
                            dl.LayerGroup(id="house-markers")
                        ]
                    )
                ])
            ])
        ], md=8),

        # Sidebar for house details
        dbc.Col([
            html.Div(id='house-details-sidebar', children=[
                dbc.Card([
                    dbc.CardHeader(
                        "Select a house on the map to view details"),
                    dbc.CardBody([
                        html.Div(id='house-details-content')
                    ])
                ])
            ])
        ], md=4)
    ]),

    # Detailed view modal
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("House Detailed Information")),
        dbc.ModalBody(id='house-details-modal-body'),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ml-auto")
        )
    ], id="house-details-modal", size="lg")
])

# Callbacks


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    [State('selected-city-store', 'data')]
)
def display_page(pathname, selected_city):
    if pathname == '/dashboard' and selected_city:
        return dashboard_page
    return location_selection_page


@app.callback(
    [Output('url', 'pathname'),
     Output('selected-city-store', 'data'),
     Output('house-data-store', 'data')],
    [Input('load-data-btn', 'n_clicks')],
    [State('city-selector', 'value')]
)
def load_data(n_clicks, city):
    if n_clicks is None:
        raise PreventUpdate

    if not city:
        return dash.no_update, dash.no_update, dash.no_update

    # Generate or load your actual data here
    df = generate_sample_data()
    city_df = df[df['city'] == city]

    return '/dashboard', city, city_df.to_dict('records')


@app.callback(
    [Output('city-title', 'children'),
     Output('map', 'center'),
     Output('house-markers', 'children')],
    [Input('selected-city-store', 'data'),
     Input('house-data-store', 'data')]
)
def update_map(selected_city, house_data):
    if not selected_city or not house_data:
        raise PreventUpdate

    df = pd.DataFrame(house_data)
    city_data = df.iloc[0]  # Get first row for city info

    # Calculate center from mean of all houses
    center = [df['lat'].mean(), df['lon'].mean()]

    # Create markers for each house
    markers = []
    for _, row in df.iterrows():
        markers.append(
            dl.CircleMarker(
                center=[row['lat'], row['lon']],
                radius=5,
                color="#3182CE",
                fill=True,
                fillColor="#63B3ED",
                fillOpacity=0.7,
                children=[
                    dl.Popup(f"House ID: {row['id']}"),
                    dl.Tooltip(f"Click for details: {row['address']}")
                ],
                id={'type': 'house-marker', 'index': row['id']}
            )
        )

    return f"Building Statistics: {selected_city}", center, markers


@app.callback(
    [Output('house-details-content', 'children'),
     Output('house-details-modal-body', 'children')],
    [Input({'type': 'house-marker', 'index': dash.dependencies.ALL}, 'n_clicks')],
    [State('house-data-store', 'data')],
    prevent_initial_call=True
)
def show_house_details(clicks, house_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    house_id = ctx.triggered[0]['prop_id'].split(
        '"index":')[1].split('}')[0].strip('"')
    df = pd.DataFrame(house_data)
    house = df[df['id'] == house_id].iloc[0]

    # Create sidebar content
    sidebar_content = [
        html.H4(f"House {house['id']}"),
        html.Hr(),
        html.P(f"Address: {house['address']}, {house['city']}"),
        html.P(f"Price: ${house['price']:,}"),
        html.P(f"Area: {house['area']} m²"),
        html.P(f"Rooms: {house['rooms']}"),
        dbc.Button("View Full Details", id='view-details-btn',
                   color="primary", className="mt-3")
    ]

    # Create modal content (detailed view)
    modal_content = [
        dbc.Row([
            dbc.Col([
                html.H4(f"Complete Details for House {house['id']}"),
                dash_table.DataTable(
                    columns=[{"name": i, "id": i} for i in house.index],
                    data=[house.to_dict()],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'height': 'auto',
                        'minWidth': '100px', 'width': '150px', 'maxWidth': '180px',
                        'whiteSpace': 'normal'
                    }
                )
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Statistics", className="mt-4"),
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': ['Price', 'Area', 'Rooms'],
                             'y': [house['price']/100000, house['area'], house['rooms']*2],
                             'type': 'bar', 'name': 'Metrics'}
                        ],
                        'layout': {
                            'title': 'House Metrics Comparison'
                        }
                    }
                )
            ], width=12)
        ])
    ]

    return sidebar_content, modal_content


@app.callback(
    Output("house-details-modal", "is_open"),
    [Input("view-details-btn", "n_clicks"),
     Input("close-modal", "n_clicks")],
    [State("house-details-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('back-btn', 'n_clicks')],
    prevent_initial_call=True
)
def go_back(n_clicks):
    if n_clicks:
        return '/'
    raise PreventUpdate


if __name__ == '__main__':
    app.run(debug=True)
