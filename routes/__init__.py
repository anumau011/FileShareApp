from .auth import auth_bp
from .files import files_bp
from .admin import admin_bp
from .utils import utils_bp

def register_routes(app):
    """Register all route blueprints"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(utils_bp)
