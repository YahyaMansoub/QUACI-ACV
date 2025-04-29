from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..utils.csv_validation import validate_csv_factors
from ..models import Space, House, db
import pandas as pd
import os

houses_bp = Blueprint('houses', __name__,
                      url_prefix='/api/spaces/<int:space_id>/houses')


@houses_bp.route('', methods=['POST'])
def upload_house(space_id):
    space = Space.query.get_or_404(space_id)

    # Check CSV file
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Validate CSV structure
    try:
        df = pd.read_csv(file.stream)
        validate_csv_factors(df.columns.tolist(), space.factors)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Get the absolute path for the 'instance/data' directory
    file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'instance', 'data')

    # Ensure the directory exists
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    # Save the file
    filename = secure_filename(f"{space_id}_{file.filename}")
    file_path = os.path.join(file_dir, filename)
    file.stream.seek(0)  # Ensure the file stream is at the beginning
    file.save(file_path)

    # Create house record
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
