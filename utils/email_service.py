from flask import current_app, url_for
from flask_mail import Message

def send_verification_email(email, encrypted_data):
    """Send email verification"""
    try:
        # Create encrypted token for email
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
