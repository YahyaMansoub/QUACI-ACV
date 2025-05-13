from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from app.services.analysis_service import (
    compute_smd,
    compute_drd,
    discernability_analysis,
    heijungs_analysis,
    ranking_probability_analysis,
    AnalysisService
)

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# Variable globale pour stocker le DataFrame uploadé
uploaded_csv_df = None
analysis_results = None

@analysis_bp.route('/upload', methods=['POST'])
def upload_csv():
    global uploaded_csv_df, analysis_results
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'File is not a CSV'}), 400
    try:
        uploaded_csv_df = pd.read_csv(file)
        # Exécuter analyses
        impact_results = AnalysisService.calculate_environmental_impact(uploaded_csv_df.to_dict(orient='records'))
        uncertainty_results = AnalysisService.generate_uncertainty_analysis(uploaded_csv_df.to_dict(orient='records'))
        data_array = uploaded_csv_df.values
        smd_results = compute_smd(data_array, data_array).to_dict()
        drd_results = compute_drd(data_array, data_array).to_dict()
        dfs = {0: uploaded_csv_df}
        heijungs_results = heijungs_analysis(dfs)
        ranking_results = ranking_probability_analysis(dfs)
        analysis_results = {
            'impact': impact_results,
            'uncertainty': uncertainty_results,
            'smd': smd_results,
            'drd': drd_results,
            'heijungs': heijungs_results,
            'ranking': ranking_results
        }
        return jsonify({'message': 'CSV uploaded and analyzed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/results', methods=['GET'])
def get_analysis_results():
    global analysis_results
    if not analysis_results:
        return jsonify({'error': 'No analysis results available'}), 404
    return jsonify(analysis_results)

@analysis_bp.route('/environmental-impact/<int:house_id>', methods=['GET'])
def get_environmental_impact(house_id):
    # Récupérer les données d'impact environnemental pour une maison
    results = AnalysisService.calculate_environmental_impact({'house_id': house_id})
    return jsonify(results)

@analysis_bp.route('/uncertainty/<int:house_id>', methods=['GET'])
def get_uncertainty_analysis(house_id):
    results = AnalysisService.generate_uncertainty_analysis(house_id)
    if results is None:
        return jsonify({'error': 'House not found or invalid data'}), 404
    return jsonify(results)

@analysis_bp.route('/smd', methods=['POST'])
def smd_analysis():
    data = request.get_json()
    a1 = np.array(data.get('a1'))
    a2 = np.array(data.get('a2'))
    smd_df = compute_smd(a1, a2)
    return jsonify(smd_df.to_dict())

@analysis_bp.route('/drd', methods=['POST'])
def drd_analysis():
    data = request.get_json()
    a1 = np.array(data.get('a1'))
    a2 = np.array(data.get('a2'))
    drd_df = compute_drd(a1, a2)
    return jsonify(drd_df.to_dict())

@analysis_bp.route('/discernability', methods=['POST'])
def discernability():
    data = request.get_json()
    dfs = {int(k): pd.DataFrame(v) for k, v in data.get('dfs', {}).items()}
    results = discernability_analysis(dfs)
    return jsonify(results)

@analysis_bp.route('/heijungs', methods=['POST'])
def heijungs():
    data = request.get_json()
    dfs = {int(k): pd.DataFrame(v) for k, v in data.get('dfs', {}).items()}
    results = heijungs_analysis(dfs)
    return jsonify(results)

@analysis_bp.route('/ranking-probabilities', methods=['POST'])
def ranking_probabilities():
    data = request.get_json()
    dfs = {int(k): pd.DataFrame(v) for k, v in data.get('dfs', {}).items()}
    results = ranking_probability_analysis(dfs)
    return jsonify(results)

@analysis_bp.route('/environmental', methods=['GET'])
def get_environmental():
    global analysis_results
    if not analysis_results or 'impact' not in analysis_results:
        return jsonify({'error': 'No environmental impact data available'}), 404
    return jsonify(analysis_results['impact'])

@analysis_bp.route('/uncertainty', methods=['GET'])
def get_uncertainty():
    global analysis_results
    if not analysis_results or 'uncertainty' not in analysis_results:
        return jsonify({'error': 'No uncertainty data available'}), 404
    return jsonify(analysis_results['uncertainty'])

@analysis_bp.route('/smd', methods=['GET'])
def get_smd():
    global analysis_results
    if not analysis_results or 'smd' not in analysis_results:
        return jsonify({'error': 'No SMD data available'}), 404
    return jsonify(analysis_results['smd'])

@analysis_bp.route('/drd', methods=['GET'])
def get_drd():
    global analysis_results
    if not analysis_results or 'drd' not in analysis_results:
        return jsonify({'error': 'No DRD data available'}), 404
    return jsonify(analysis_results['drd'])

@analysis_bp.route('/heijungs', methods=['GET'])
def get_heijungs():
    global analysis_results
    if not analysis_results or 'heijungs' not in analysis_results:
        return jsonify({'error': 'No Heijungs data available'}), 404
    return jsonify(analysis_results['heijungs'])

@analysis_bp.route('/ranking', methods=['GET'])
def get_ranking():
    global analysis_results
    if not analysis_results or 'ranking' not in analysis_results:
        return jsonify({'error': 'No ranking data available'}), 404
    return jsonify(analysis_results['ranking'])