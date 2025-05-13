from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from app.services.analysis_service import (
    compute_smd,
    compute_drd,
    discernability_analysis,
    heijungs_analysis,
    ranking_probability_analysis
)

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/upload')

# Global temp store for uploaded CSV
uploaded_df = None


@uploads_bp.route('', methods=['POST'])
def upload_csv():
    global uploaded_df
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Only CSV files are accepted'}), 400

    try:
        uploaded_df = pd.read_csv(file)
        if uploaded_df.empty:
            return jsonify({'error': 'Uploaded CSV is empty'}), 400

        return jsonify({
            'message': 'File uploaded and read successfully',
            'columns': uploaded_df.columns.tolist(),
            'rows': len(uploaded_df)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to process CSV: {str(e)}'}), 500


@uploads_bp.route('/results/<string:method>', methods=['GET'])
def get_analysis_result(method):
    global uploaded_df
    if uploaded_df is None:
        return jsonify({'error': 'No CSV uploaded'}), 404

    try:
        df = uploaded_df.copy()

        # Handle numeric preprocessing
        numeric_df = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
        numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan)
        numeric_df = numeric_df.dropna(axis=1)

        if numeric_df.empty:
            return jsonify({'error': 'No valid numeric data after cleaning'}), 400

        result = {}

        if method == 'smd':
            mid = len(numeric_df) // 2
            df1 = numeric_df.iloc[:mid].dropna(axis=1).values
            df2 = numeric_df.iloc[mid:].dropna(axis=1).values

            if df1.shape[0] < 2 or df2.shape[0] < 2:
                return jsonify({'error': 'Not enough rows in each group to compute SMD'}), 400

            smd_df = compute_smd(df1, df2)
            result = {
                'rows': smd_df.index.tolist(),
                'cols': smd_df.columns.tolist(),
                'data': [[i, j, float(v)] for i, row in enumerate(smd_df.values) for j, v in enumerate(row)]
            }

        elif method == 'drd':
            mid = len(numeric_df) // 2
            df1 = numeric_df.iloc[:mid].dropna(axis=1).values
            df2 = numeric_df.iloc[mid:].dropna(axis=1).values

            if df1.shape[0] < 2 or df2.shape[0] < 2:
                return jsonify({'error': 'Not enough rows in each group to compute DRD'}), 400

            drd_df = compute_drd(df1, df2)
            result = {
                'rows': drd_df.index.tolist(),
                'cols': drd_df.columns.tolist(),
                'data': [[i, j, float(v)] for i, row in enumerate(drd_df.values) for j, v in enumerate(row)]
            }

        elif method == 'uncertainty':
            stats = {}
            for col in numeric_df.columns:
                samples = numeric_df[col].dropna()
                stats[col] = {
                    'mean': float(np.mean(samples)),
                    'median': float(np.median(samples)),
                    'std': float(np.std(samples)),
                    'percentile_5': float(np.percentile(samples, 5)),
                    'percentile_95': float(np.percentile(samples, 95))
                }
            result = stats

        elif method == 'heijungs':
            result = heijungs_analysis({0: numeric_df})

        elif method == 'discernability':
            result = discernability_analysis({0: numeric_df})

        elif method == 'ranking':
            result = ranking_probability_analysis({0: numeric_df})

        else:
            return jsonify({'error': f'Unsupported method: {method}'}), 400

        return jsonify({method: result})

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
