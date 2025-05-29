from flask import Blueprint, request, jsonify
import pandas as pd
import os
from ..quaci_class import QUACI

simulations_bp = Blueprint('simulations', __name__,
                           url_prefix='/api/simulations')


@simulations_bp.route('/quaci', methods=['POST'])
def run_quaci_simulation():
    data = request.get_json()

    # Validate required fields
    if not data or 'comp_quantity' not in data or 'building_type' not in data \
            or 'dur_vie_mean' not in data or 'dur_vie_std_dev' not in data:
        return jsonify({'error': 'Missing required fields: comp_quantity, building_type, dur_vie_mean, dur_vie_std_dev'}), 400

    try:
        # Convert comp_quantity dict to pandas Series with building_type as name
        comp_quantity = pd.Series(
            data['comp_quantity'],
            name=data['building_type']
        )

        # Initialize QUACI instance
        quaci = QUACI(
            comp_quantity=comp_quantity,
            dur_vie_mean=float(data['dur_vie_mean']),
            dur_vie_std_dev=float(data['dur_vie_std_dev']),
            path='Material_Statistics'  # Path to material statistics
        )

        # Run simulation and get result dataframe
        result_df = quaci.final(data['building_type'])

        # Convert dataframe to JSON-friendly format
        result_json = result_df.where(pd.notnull(
            result_df), None).to_dict(orient='records')

        return jsonify(result_json), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid numeric value: {str(e)}'}), 400
    except FileNotFoundError as e:
        return jsonify({'error': f'Material data not found: {str(e)}'}), 500
    except KeyError as e:
        return jsonify({'error': f'Missing material data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Simulation failed: {str(e)}'}), 500
