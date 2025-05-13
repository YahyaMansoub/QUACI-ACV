from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..utils.csv_validation import validate_csv_factors
from ..models import Space, House, db
import pandas as pd
import os

houses_bp = Blueprint('houses', __name__, url_prefix='/api/spaces/<int:space_id>/houses')


@houses_bp.route('', methods=['POST'])
def upload_house(space_id):
    space = Space.query.get_or_404(space_id)

    # Validate file presence
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400

    # Validate CSV content
    try:
        df = pd.read_csv(file.stream)
        validate_csv_factors(df.columns.tolist(), space.factors)
    except Exception as e:
        return jsonify({'error': f'Invalid CSV: {str(e)}'}), 400

    # Define safe file path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_dir = os.path.join(base_dir, 'instance', 'data')
    os.makedirs(file_dir, exist_ok=True)

    filename = secure_filename(f"{space_id}_{file.filename}")
    file_path = os.path.join(file_dir, filename)

    # Reset file stream and save
    file.stream.seek(0)
    file.save(file_path)

    # Save house in DB
    new_house = House(
        name=request.form.get('name', filename),
        space_id=space_id,
        file_path=file_path,
        simulations_count=len(df),
        factors_count=len(df.columns)
    )
    db.session.add(new_house)
    db.session.commit()

    return jsonify({
        'id': new_house.id,
        'name': new_house.name,
        'simulations': new_house.simulations_count
    }), 201


@houses_bp.route('', methods=['GET'])
def list_houses(space_id):
    space = Space.query.get_or_404(space_id)
    houses = House.query.filter_by(space_id=space.id).all()

    return jsonify({
        'houses': [
            {
                'id': h.id,
                'name': h.name,
                'simulations': h.simulations_count,
                'factors': h.factors_count
            } for h in houses
        ]
    })
