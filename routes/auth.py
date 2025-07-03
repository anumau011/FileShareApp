from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from bson.objectid import ObjectId
from utils.helpers import generate_secure_token
from utils.email_service import send_verification_email, get_serializer

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/ops/login', methods=['POST'])
def ops_login():
    """Operations user login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = current_app.mongo.db.users.find_one({'email': email, 'user_type': 'ops'})
        
        if user and check_password_hash(user['password'], password):
            access_token = create_access_token(identity=str(user['_id']))
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user_type': 'ops'
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/client/signup', methods=['POST'])
def client_signup():
    """Client user signup - Sends verification email only"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Check if user already exists
        if current_app.mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'User already exists'}), 409
        
        # Generate verification token
        verification_token = generate_secure_token()
        
        # Create user document
        user_doc = {
            'email': email,
            'password': generate_password_hash(password),
            'name': name,
            'user_type': 'client',
            'email_verified': False,
            'verification_token': verification_token,
            'created_date': datetime.now(timezone.utc)
        }
        
        result = current_app.mongo.db.users.insert_one(user_doc)
        
        # Send verification email
        if send_verification_email(email, str(result.inserted_id), verification_token):
            return jsonify({
                'message': 'User registered successfully. Please check your email for verification.'
            }), 201
        else:
            return jsonify({'error': 'Failed to send verification email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/client/verify-email/<token>')
def verify_email(token):
    """Verify client email"""
    try:
        serializer = get_serializer()
        # Decrypt token
        data = serializer.loads(token, max_age=3600)  # Token expires in 1 hour
        user_id = data['user_id']
        verification_token = data['token']
        
        # Find user and verify
        user = current_app.mongo.db.users.find_one({
            '_id': ObjectId(user_id),
            'verification_token': verification_token
        })
        
        if not user:
            return jsonify({'error': 'Invalid verification token'}), 400
        
        if user['email_verified']:
            return jsonify({'message': 'Email already verified'}), 200
        
        # Update user as verified
        current_app.mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'email_verified': True}, '$unset': {'verification_token': ""}}
        )
        
        return jsonify({'message': 'Email verified successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Invalid or expired verification token'}), 400

@auth_bp.route('/client/login', methods=['POST'])
def client_login():
    """Client user login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = current_app.mongo.db.users.find_one({'email': email, 'user_type': 'client'})
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.get('email_verified'):
            return jsonify({'error': 'Please verify your email before logging in'}), 401
        
        if check_password_hash(user['password'], password):
            access_token = create_access_token(identity=str(user['_id']))
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user_type': 'client'
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
