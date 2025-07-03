import os
from flask import current_app

def init_db(app):
    """Initialize database connection and create upload directory"""
    # Create absolute path for upload directory
    upload_folder = os.path.abspath(app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_folder, exist_ok=True)
    
    # Update config with absolute path
    app.config['UPLOAD_FOLDER'] = upload_folder
    print(f"Upload folder set to: {upload_folder}")
    
    # Test MongoDB connection
    try:
        with app.app_context():
            app.mongo.db.command('ping')
            print("MongoDB connection successful!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

def check_mongo_connection():
    """Check if MongoDB connection is working"""
    try:
        current_app.mongo.db.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection check failed: {e}")
        return False

