from flask import current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

def get_serializer():
    """Get URL safe serializer"""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def send_verification_email(email, user_id, token):
    """Send email verification"""
    try:
        serializer = get_serializer()
        # Create encrypted token for email
        encrypted_data = serializer.dumps({'user_id': user_id, 'token': token})
        verification_url = url_for('auth.verify_email', token=encrypted_data, _external=True)
        
        msg = Message(
            'Email Verification - File Sharing System',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f'Please click the following link to verify your email: {verification_url}'
        )
        
        current_app.mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False
