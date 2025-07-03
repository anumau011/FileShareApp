from flask import Blueprint, jsonify
from datetime import datetime, timezone
from models.database import check_mongo_connection

utils_bp = Blueprint('utils', __name__)

@utils_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    mongo_status = "connected" if check_mongo_connection() else "disconnected"
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'database': mongo_status
    }), 200

# Error handlers
@utils_bp.app_errorhandler(413)
def file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@utils_bp.app_errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@utils_bp.app_errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

