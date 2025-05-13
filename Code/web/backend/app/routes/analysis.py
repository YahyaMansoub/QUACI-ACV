from flask import Blueprint, request, jsonify
from ..models import Space, House, db
import pandas as pd
import numpy as np
from app.services.analysis_service import (
    compute_smd,
    compute_drd,
    compute_pairwise_probabilities,
    generate_heatmap_data,
    discernability_analysis,
    heijungs_analysis,
    ranking_probability_analysis,
    AnalysisService
)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@analysis_bp.route('/<int:space_id>', methods=['POST'])
def run_analysis(space_id):
    space = Space.query.get_or_404(space_id)
    data = request.get_json()

    if not data or 'house_ids' not in data or 'method' not in data:
        return jsonify({'error': 'Missing house_ids or method'}), 400

    houses = House.query.filter(House.id.in_(data['house_ids'])).all()
    if len(houses) < 2:
        return jsonify({'error': 'Need at least 2 houses for comparison'}), 400

    dfs = {}
    for house in houses:
        try:
            dfs[house.id] = pd.read_csv(house.file_path)
        except Exception as e:
            return jsonify({'error': f'Failed to read CSV for house {house.id}: {str(e)}'}), 500

    method = data['method']

    if method == 'discernability_analysis':
        results = discernability_analysis(dfs)
    elif method == 'heijungs_metric':
        results = heijungs_analysis(dfs)
    elif method == 'ranking_probability':
        results = ranking_probability_analysis(dfs)
    elif method == 'smd_drd':
        results = {}
        house_ids = list(dfs.keys())
        smd_results = []
        drd_results = []

        for i in range(len(house_ids)):
            for j in range(i + 1, len(house_ids)):
                id1, id2 = house_ids[i], house_ids[j]
                df1, df2 = dfs[id1].values, dfs[id2].values
                smd_df = compute_smd(df1, df2)
                drd_df = compute_drd(df1, df2)
                smd_results.append({
                    'house1': id1,
                    'house2': id2,
                    'smd': smd_df.to_dict()
                })
                drd_results.append({
                    'house1': id1,
                    'house2': id2,
                    'drd': drd_df.to_dict()
                })

        results['smd'] = smd_results
        results['drd'] = drd_results
    elif method == 'heatmap_data':
        matrices = {house.id: df.values for house, df in dfs.items()}
        results = generate_heatmap_data(matrices)
    else:
        return jsonify({'error': 'Invalid method'}), 400

    return jsonify(results)


@analysis_bp.route('/<int:house_id>/uncertainty', methods=['POST'])
def run_uncertainty_analysis(house_id):
    data = request.get_json() or {}
    simulations = data.get('simulations', 1000)

    results = AnalysisService.generate_uncertainty_analysis(house_id, simulations)
    if results is None:
        return jsonify({'error': 'House not found or invalid data'}), 404

    return jsonify(results)


@analysis_bp.route('/materials/compare', methods=['POST'])
def compare_materials():
    data = request.get_json()
    material_ids = data.get('material_ids')
    impact_category = data.get('impact_category')

    if not material_ids or not impact_category:
        return jsonify({'error': 'Missing material_ids or impact_category'}), 400

    results = AnalysisService.compare_materials(material_ids, impact_category)
    return jsonify(results)


@analysis_bp.route('/materials/environmental-impact', methods=['POST'])
def calculate_environmental_impact():
    data = request.get_json()
    materials_data = data.get('materials_data')
    lifespan = data.get('lifespan', 50)

    if not materials_data:
        return jsonify({'error': 'Missing materials_data'}), 400

    results = AnalysisService.calculate_environmental_impact(materials_data, lifespan)
    return jsonify(results)


@analysis_bp.route('/upload/results/drd', methods=['POST'])
def upload_drd_results():
    try:
        files = request.files.getlist("files")
        if not files or len(files) != 2:
            return jsonify({"error": "Exactly two CSV files must be uploaded."}), 400

        dfs = [pd.read_csv(file) for file in files]
        df1, df2 = dfs[0].values, dfs[1].values
        drd_df = compute_drd(df1, df2)
        return jsonify({"drd": drd_df.to_dict(orient='records')})
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
