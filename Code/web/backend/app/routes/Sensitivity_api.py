from flask import Blueprint, request, jsonify
import pandas as pd
from ..quaci_class import QUACI
from ..Sensitivity_Analysis import SensitivityAnalyzer


'''
For This moment this part is unusable but it could be 
in the future , What we are using for Sensitivity Analysis 
is Embedded within the frontend ,  instead of Calculating 
the Sensitivity Analysis in the backend then forwarding it 
to the frontend. This technic Showed to have some major 
errors due to the Json communication structure.
Instead I opted to make the frontend forward  requests to calculate
the Environmental Impacts through the quaci_class. This might be slow
but it was a solution we needed as we had no time to solve 
the errors manifested by the first technique.

'''


simulations_bp = Blueprint('simulations', __name__,
                           url_prefix='/api/simulations')


@simulations_bp.route('/quaci/sensitivity', methods=['POST'])
def run_sensitivity_analysis():
    data = request.get_json()

    # Validate required fields
    required_fields = ['comp_quantity', 'building_type',
                       'dur_vie_mean', 'dur_vie_std_dev']
    if not data or any(field not in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Convert comp_quantity to pandas Series
        comp_quantity = pd.Series(
            {k: float(v) for k, v in data['comp_quantity'].items()},
            name=data['building_type']
        )

        # Create base QUACI instance
        base_quaci = QUACI(
            comp_quantity=comp_quantity,
            dur_vie_mean=float(data['dur_vie_mean']),
            dur_vie_std_dev=float(data['dur_vie_std_dev']),
            path='Material_Statistics'
        )

        # Get perturbation percentage (default to 10%)
        perturbation = float(data.get('perturbation_percent', 0.1))

        # Run analysis
        analyzer = SensitivityAnalyzer(base_quaci)
        full_results = analyzer.run_analysis(perturbation_percent=perturbation)
        top_results = analyzer.get_most_influential(5)

        # Convert results to JSON format
        response_data = {
            'baseline': analyzer.baseline,
            'perturbation_percent': perturbation,
            'full_results': full_results.where(pd.notnull(full_results), None).to_dict(orient='records'),
            'top_parameters': top_results.where(pd.notnull(top_results), None).to_dict(orient='records')
        }

        return jsonify(response_data), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid numeric value: {str(e)}'}), 400
    except FileNotFoundError as e:
        return jsonify({'error': f'Material data not found: {str(e)}'}), 500
    except KeyError as e:
        return jsonify({'error': f'Missing material data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Sensitivity analysis failed: {str(e)}'}), 500
