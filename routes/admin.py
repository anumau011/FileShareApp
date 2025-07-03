from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/create-ops-user', methods=['POST'])
def create_ops_user():
    """Create operations user (admin function)"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Check if ops user already exists
        if current_app.mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'User already exists'}), 409
        
        # Create ops user
        ops_user = {
            'email': email,
            'password': generate_password_hash(password),
            'name': name,
            'user_type': 'ops',
            'email_verified': True,  # Ops users are pre-verified
            'created_date': datetime.now(timezone.utc)
        }
        
        result = current_app.mongo.db.users.insert_one(ops_user)
        
        return jsonify({
            'message': 'Operations user created successfully',
            'user_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
