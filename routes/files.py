import os
from flask import Blueprint, request, jsonify, send_file, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone, timedelta
from bson.objectid import ObjectId
from utils.decorators import ops_required, client_required
from utils.helpers import handle_file_upload, generate_secure_token

files_bp = Blueprint('files', __name__)

@files_bp.route('/ops/upload', methods=['POST'])
@ops_required
def upload_file():
    """Upload file - Only for operations users"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        user_id = get_jwt_identity()
        
        file_id, filename = handle_file_upload(file, user_id)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': str(file_id),
            'filename': filename
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/client/files', methods=['GET'])
@client_required
def list_files():
    """List all uploaded files for client users"""
    try:
        files = list(current_app.mongo.db.files.find({}, {
            'original_filename': 1,
            'file_size': 1,
            'upload_date': 1,
            'mime_type': 1
        }))
        
        # Convert ObjectId to string and format dates
        for file in files:
            file['_id'] = str(file['_id'])
            file['upload_date'] = file['upload_date'].isoformat()
        
        return jsonify({
            'message': 'Files retrieved successfully',
            'files': files
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/client/download-file/<file_id>', methods=['GET'])
@client_required
def request_download(file_id):
    """Generate secure download link for client users"""
    try:
        # Validate file exists
        file_doc = current_app.mongo.db.files.find_one({'_id': ObjectId(file_id)})
        if not file_doc:
            return jsonify({'error': 'File not found'}), 404
        
        # Generate secure download token
        download_token = generate_secure_token()
        user_id = get_jwt_identity()
        
        # Store download token with expiration (1 hour)
        download_doc = {
            'file_id': ObjectId(file_id),
            'user_id': ObjectId(user_id),
            'download_token': download_token,
            'created_date': datetime.now(timezone.utc),
            'expires_at': datetime.now(timezone.utc) + timedelta(hours=1),
            'used': False
        }
        
        current_app.mongo.db.download_tokens.insert_one(download_doc)
        
        # Generate secure download URL
        download_url = url_for('files.download_file', token=download_token, _external=True)
        
        return jsonify({
            'download_link': download_url,
            'message': 'success',
            'expires_in': '1 hour'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/download-file/<token>')
@jwt_required()
def download_file(token):
    """Secure file download using encrypted token"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify user is client
        user = current_app.mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user or user.get('user_type') != 'client':
            return jsonify({'error': 'Access denied. Client access required.'}), 403
        
        # Find valid download token
        download_doc = current_app.mongo.db.download_tokens.find_one({
            'download_token': token,
            'user_id': ObjectId(current_user_id),
            'expires_at': {'$gt': datetime.now(timezone.utc)},
            'used': False
        })
        
        if not download_doc:
            return jsonify({'error': 'Invalid, expired, or already used download token'}), 403
        
        # Get file information
        file_doc = current_app.mongo.db.files.find_one({'_id': download_doc['file_id']})
        if not file_doc:
            return jsonify({'error': 'File not found'}), 404
        
        # Verify file exists on filesystem
        file_path = file_doc['file_path']
        if not os.path.exists(file_path):
            current_app.logger.error(f"File not found on filesystem: {file_path}")
            return jsonify({'error': 'File not found on server'}), 404
        
        # Mark token as used
        current_app.mongo.db.download_tokens.update_one(
            {'_id': download_doc['_id']},
            {'$set': {'used': True, 'download_date': datetime.now(timezone.utc)}}
        )
        
        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_doc['original_filename'],
            mimetype=file_doc['mime_type']
        )
        
    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500
