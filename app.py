from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from config import Config
from routes import register_routes
from models.database import init_db
from utils.helpers import create_indexes
import logging

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    mongo = PyMongo(app)
    jwt = JWTManager(app)
    mail = Mail(app)
    
    # Store extensions in app context
    app.mongo = mongo
    app.mail = mail
    
    # Initialize database
    init_db(app)
    
    # Register routes
    register_routes(app)
    
    # Create indexes for better performance
    create_indexes(app)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)

