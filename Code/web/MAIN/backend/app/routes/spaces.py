from flask import Blueprint, request, jsonify
from ..models import Space, House, db
from ..utils.csv_validation import validate_csv_factors
import os

spaces_bp = Blueprint('spaces', __name__, url_prefix='/api/spaces')


@spaces_bp.route('', methods=['GET'])
def get_spaces():
    # Fetch all spaces without filtering by user_id
    spaces = Space.query.all()
    return jsonify([{
        'id': space.id,
        'name': space.name,
        'factors': space.factors,
        'house_count': len(space.houses)
    } for space in spaces])


@spaces_bp.route('', methods=['POST'])
def create_space():
    data = request.get_json()
    if not data or 'name' not in data or 'factors' not in data:
        return jsonify({'error': 'Missing name or factors'}), 400

    new_space = Space(
        name=data['name'],
        factors=data['factors']
    )
    db.session.add(new_space)
    db.session.commit()
    return jsonify({'id': new_space.id, 'name': new_space.name}), 201


@spaces_bp.route('/<int:space_id>', methods=['GET'])
def get_space(space_id):
    space = Space.query.get_or_404(space_id)
    return jsonify({
        'id': space.id,
        'name': space.name,
        'factors': space.factors,
        'houses': [{
            'id': house.id,
            'name': house.name,
            'simulations_count': house.simulations_count,
            'factors_count': house.factors_count
        } for house in space.houses]
    })
