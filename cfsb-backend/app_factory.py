# Created for application setup
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from routes import main_routes  # Adjusted to absolute import
import logging
def create_app():
    logging.info("Creating the application")
    app = Flask(__name__)
    cors_allowed_origins = [
        "https://cfsb.cd.nebulouscloud.eu",
        "https://cfsb.dev.nebulouscloud.eu",
        "https://cfsb.prod.nebulouscloud.eu",
    ]
    CORS(app, resources={r"/*": {"origins": cors_allowed_origins}})  # Enable CORS
    app.register_blueprint(main_routes)
    return app




