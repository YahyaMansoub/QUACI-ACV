from flask import Blueprint, request, jsonify
from ..models import Space, House, db
import pandas as pd
import numpy as np

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')


@analysis_bp.route('/<int:space_id>', methods=['POST'])
def run_analysis(space_id):
    space = Space.query.get_or_404(space_id)
    data = request.get_json()

    # Validate input
    if not data or 'house_ids' not in data or 'method' not in data:
        return jsonify({'error': 'Missing house_ids or method'}), 400

    # Load house data
    houses = House.query.filter(House.id.in_(data['house_ids'])).all()
    if len(houses) < 2:
        return jsonify({'error': 'Need at least 2 houses for comparison'}), 400

    # Load all CSVs into DataFrames
    dfs = {}
    for house in houses:
        dfs[house.id] = pd.read_csv(house.file_path)

    # Perform analysis
    if data['method'] == 'discernability_analysis':
        results = _discernability_analysis(dfs)
    elif data['method'] == 'heijungs_metric':
        results = _heijungs_analysis(dfs)
    else:
        return jsonify({'error': 'Invalid method'}), 400

    return jsonify(results)


def _discernability_analysis(dfs):
    # Get factor names from first house's dataframe
    factors = list(dfs.values())[0].columns.tolist()

    comparisons = []
    house_ids = list(dfs.keys())

    for i in range(len(house_ids)):
        for j in range(i+1, len(house_ids)):
            house1_id = house_ids[i]
            house2_id = house_ids[j]
            df1 = dfs[house1_id]
            df2 = dfs[house2_id]

            # Calculate probability for each factor
            probabilities = []
            for factor in factors:
                better = np.mean(df1[factor] < df2[factor])
                probabilities.append(float(better))

            comparisons.append({
                'house1': house1_id,
                'house2': house2_id,
                'values': probabilities
            })

    return {
        'factors': factors,
        'comparisons': comparisons
    }


def _heijungs_analysis(dfs):
    # Implement Heijungs metric logic
    metrics = {}
    for house1_id, df1 in dfs.items():
        metrics[house1_id] = {}
        for house2_id, df2 in dfs.items():
            # Example implementation
            diff = df1.mean() - df2.mean()
            std = np.sqrt(df1.var() + df2.var())
            metric = np.mean(diff / std)
            metrics[house1_id][house2_id] = round(float(metric), 4)
    return {'heijungs_metrics': metrics}
