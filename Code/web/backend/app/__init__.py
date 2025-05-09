from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


# Initialize the SQLAlchemy object
db = SQLAlchemy()


def create_app():
    # Create the Flask app
    app = Flask(__name__)

    CORS(app)

    # Load the config from config.py
    app.config.from_object('app.config.Config')

    # Initialize the database with the app
    db.init_app(app)

    # Import models here to ensure they are registered with the app before db.create_all()
    from .models import Space, House  # Import models

    # Create all database tables (this will create the tables defined by your models)
    with app.app_context():
        db.create_all()  # Create tables if they don't exist

    # Register blueprints
    from .routes.spaces import spaces_bp
    from .routes.houses import houses_bp
    from .routes.analysis import analysis_bp

    app.register_blueprint(spaces_bp)
    app.register_blueprint(houses_bp)
    app.register_blueprint(analysis_bp)

    # Route de base pour éviter le 404 sur '/'
    @app.route('/')
    def index():
        return jsonify({'status':'OK','message':'API is running'}), 200

    # Gérer favicon.ico pour éviter le 404
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    return app
