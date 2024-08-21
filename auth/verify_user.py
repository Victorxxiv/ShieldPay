# Import necessary modules
import secrets
from flask import url_for, jsonify
from flask_mail import Mail, Message
from os import getenv

# Function to generate verification token
def generate_verification_token():
    return secrets.token_urlsafe(16)

# Function to send verification email
def send_verification_email(user_email, verification_token):
    # Set email subject
    subject = 'Verification Email for ShieldPay'
    # Get sender email from environment variable
    mail = getenv('VERIFICATION_EMAIL')
    # Create message object
    msg = Message(subject, sender=mail, recipients=[user_email])
    # Create mail object
    mail = Mail()
    # Generate verification URL
    verification_url = url_for('app_views.register', token=verification_token, _external=True)
    # Updated email body with a clear message.
    msg.body = f"Hello,\n\nPlease click the following link to verify your email address for ShieldPay:\n{verification_url}\n\nIf you didn't register for ShieldPay, you can safely ignore this email.\n\nBest regards,\nThe ShieldPay Team"
    
    try:
        # Send the email
        mail.send(msg)
        return jsonify({"Message": "Mail sent successfully", "status": 200})
    except Exception as e:
        return jsonify({"Mail sending Error": str(e), "status": 502})
