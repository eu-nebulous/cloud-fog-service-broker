# Created for application setup
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from routes import main_routes  # Adjusted to absolute import
import logging
def create_app():
    logging.info("Creating the application")
    app = Flask(__name__)
    #CORS(app)
    CORS(app, supports_credentials=True)  # Enable CORS and allow credentials
    #CORS(app, resource={r"/*":{"origins":"*"}})
    #CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(main_routes)
    return app




