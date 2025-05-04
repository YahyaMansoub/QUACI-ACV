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
    # Implement discernability analysis logic
    heatmap = {}
    for house1_id, df1 in dfs.items():
        heatmap[house1_id] = {}
        for house2_id, df2 in dfs.items():
            # Example: compare mean values
            better_count = np.sum(df1.mean(axis=1) < df2.mean(axis=1))
            probability = better_count / len(df1)
            heatmap[house1_id][house2_id] = round(float(probability), 4)
    return {'heatmap_data': heatmap}

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