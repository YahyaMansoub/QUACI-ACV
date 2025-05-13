from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize the SQLAlchemy object (will be bound later)
db = SQLAlchemy()

def create_app():
    # Create the Flask app
    app = Flask(__name__)

    # Apply CORS to all /api routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Load configuration
    app.config.from_object('app.config.Config')

    # Initialize database with app
    db.init_app(app)

    # Import models so SQLAlchemy knows about them
    from .models import Space, House

    with app.app_context():
        db.create_all()

    # Register blueprints
    from .routes.spaces import spaces_bp
    from .routes.houses import houses_bp
    from .routes.analysis import analysis_bp
    from .routes.uploads import uploads_bp  # Optional: for custom CSV upload handling

    app.register_blueprint(spaces_bp)
    app.register_blueprint(houses_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(uploads_bp)

    # Default index route
    @app.route('/')
    def index():
        return jsonify({'status': 'OK', 'message': 'API is running'}), 200

    # Avoid 404 for favicon.ico
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    return app
