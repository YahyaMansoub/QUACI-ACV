# ... (Previous imports remain the same)
import plotly.express as px
from plotly.colors import hex_to_rgb

# Include your existing functions (generate_matrix, Discernibility_Analysis)


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


if __name__ == "__main__":
    app.run(debug=True)
