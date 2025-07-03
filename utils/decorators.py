from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

def ops_required(f):
    """Decorator to require operations user access"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        if current_app.mongo is None:
            return jsonify({'error': 'Database connection not available'}), 500
        
        current_user_id = get_jwt_identity()
        user = current_app.mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user or user.get('user_type') != 'ops':
            return jsonify({'error': 'Operations user access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    """Decorator to require client user access"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        if current_app.mongo is None:
            return jsonify({'error': 'Database connection not available'}), 500
        
        current_user_id = get_jwt_identity()
        user = current_app.mongo.db.users.find_one({'_id': ObjectId(current_user_id)})
        if not user or user.get('user_type') != 'client':
            return jsonify({'error': 'Client user access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

