from flask import Blueprint, request, send_file, jsonify
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@analysis_bp.route('/<int:space_id>', methods=['POST'])
def run_analysis(space_id):
    from .your_analysis_module import radar_chart_median_iqr, plot_discernibility_heatmap

    data = request.get_json()
    if not data or 'house_ids' not in data or 'method' not in data:
        return jsonify({'error': 'Missing house_ids or method'}), 400

    houses = House.query.filter(House.id.in_(data['house_ids'])).all()

    dfs = {}
    for house in houses:
        dfs[house.id] = pd.read_csv(house.file_path)

    fig = None  # the figure to save

    if data['method'] == 'discernability_analysis':
        matrices = [df.values for df in dfs.values()]
        labels = [str(h.id) for h in houses]
        factor_names = dfs[houses[0].id].columns.tolist()

        fig = plot_discernibility_heatmap(matrices, labels, factor_names)
    elif data['method'] == 'heijungs_metric':
        if len(houses) != 1:
            return jsonify({'error': 'Only one house must be selected'}), 400
        matrices = [dfs[houses[0].id].values]
        labels = dfs[houses[0].id].columns.tolist()

        fig = radar_chart_median_iqr(matrices, labels, matrix_names=["House " + str(houses[0].id)])
    else:
        return jsonify({'error': 'Invalid method'}), 400

    # Save figure to memory and return
    img_io = BytesIO()
    fig.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close(fig)

    return send_file(img_io, mimetype='image/png')
