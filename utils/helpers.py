import os
import hashlib
import secrets
import mimetypes
from datetime import datetime, timezone
from flask import current_app
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

def allowed_file(filename):
    """Check if file extension is allowed"""
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])

def generate_secure_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def get_file_hash(file_path):
    """Generate MD5 hash of file for integrity checking"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def handle_file_upload(file, user_id):
    """Handle file upload process"""
    if not file or file.filename == '':
        raise ValueError('No file selected')
    
    if not allowed_file(file.filename):
        raise ValueError('Only pptx, docx, and xlsx files are allowed')
    
    # Secure filename and save
    filename = secure_filename(file.filename)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_')
    unique_filename = timestamp + filename
    
    # Create absolute path and ensure directory exists
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save file
    try:
        file.save(file_path)
    except Exception as e:
        raise ValueError(f'Failed to save file: {str(e)}')
    
    # Verify file was saved successfully
    if not os.path.exists(file_path):
        raise ValueError('File was not saved successfully')
    
    # Get file info
    file_size = os.path.getsize(file_path)
    file_hash = get_file_hash(file_path)
    
    # Save file metadata to database with normalized path
    file_doc = {
        'original_filename': filename,
        'stored_filename': unique_filename,
        'file_path': os.path.normpath(file_path),  # Normalize path for cross-platform compatibility
        'file_size': file_size,
        'file_hash': file_hash,
        'upload_date': datetime.now(timezone.utc),
        'uploaded_by': ObjectId(user_id),
        'mime_type': mimetypes.guess_type(filename)[0]
    }
    
    result = current_app.mongo.db.files.insert_one(file_doc)
    return result.inserted_id, filename

def create_indexes(app):
    """Create database indexes for better performance"""
    if app.mongo is None:
        print("MongoDB connection not available. Skipping index creation.")
        return
    
    try:
        with app.app_context():
            # Test connection first
            app.mongo.db.command('ping')
            
            # Create indexes
            app.mongo.db.users.create_index("email", unique=True)
            app.mongo.db.files.create_index("upload_date")
            app.mongo.db.download_tokens.create_index("expires_at", expireAfterSeconds=0)
            print("Database indexes created successfully")
    except Exception as e:
        print(f"Note: Could not create database indexes: {e}")
