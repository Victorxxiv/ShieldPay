# Import necessary modules
from flask import jsonify, request, url_for, redirect
from auth.auth import Authentication
from auth.user_auth import UserAuth
from datetime import datetime
from api.v1.views.user import app_views
#  from auth.verify_user import generate_verification_token, send_verification_email
from flask_jwt_extended import jwt_required
from utils.user_account import AccountService

# Initialize authentication and account service objects
user_auth = UserAuth()
user_authenticator = Authentication()
account_service = AccountService()

# Register a new user
@app_views.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user
    """
    # Get user data from request
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    location = data.get('location')

    # Validate required fields
    if not email:
        return jsonify({"message": "email is required"}), 400
    if not password:
        return jsonify({"message": "password is required"}), 400
    if not first_name:
        return jsonify({"message": "first_name is required"}), 400
    if not last_name:
        return jsonify({"message": "last_name is required"}), 400
    if not phone_number:
        return jsonify({"message": "phone_number is required"}), 400
    if not location:
        return jsonify({"message": "location is required"}), 400

    # Set initial values for user
    is_active = False
    last_login = datetime.utcnow()
    last_login_str = last_login.strftime("%Y-%m-%d %H:%M:%S")

    # Check if user already exists
    user = user_auth.get_user_by_email(email)
    if user:
        return jsonify({"message": "user already exists"}), 409
    else:
        # Create user and account
        usr = user_auth.create_user(email=email, password=password, first_name=first_name, last_name=last_name, phone_number=phone_number, location=location, is_active=is_active, last_login=last_login_str)
        account = account_service.create_account(Total_funds=0, incomming_funds=0, outgoing_funds=0, user_id=usr.id)
        # Generate verification token and send verification email
        # verification_token = generate_verification_token()
        # mail_response = send_verification_email(user_email=email, verification_token=verification_token)
        # Prepare account details for response
        account_deets = { 'account_number': account.account_number, 'Total_funds': account.Total_funds, 'incomming_funds': account.incomming_funds, 'outgoing_funds': account.outgoing_funds, 'user_id': account.user_id }
        # Return success response
        return jsonify({"message": "user created successfully", "user_id": str(usr.id), "account_message": "account created with the following credentials", 'account_details': account_deets}), 201

#@app_views.route('/verify_email/<string: token>', methods=['GET'])
#def verify_email(token):

# Login a user
@app_views.route('/login', methods=['POST'])
def login_user():
    """
    Login a user
    """
    # Get user data from request
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')

    # Validate required fields
    if not email and not phone_number:
        return jsonify({"message": "email or phone number is required"}), 400
    if not password:
        return jsonify({"message": "password is required"}), 400

    if email:
        # Login with email
        user = user_auth.get_user_by_email(email)
        if not user:
            return jsonify({"message": "user not found"}), 404
        if not user_auth.verify_password(password, user.password):
            return jsonify({"message": "invalid password"}), 400
        else:
            # Create access token and set cookie
            access_token = user_authenticator.create_token(user.id)
            response = jsonify({"message": "Logged in successfully!", 'status': 200})
            user_authenticator.set_cookie(response, access_token)
            return response

    if phone_number:
        # Login with phone number
        user = user_auth.get_user_by_phone_number(phone_number)
        if not user:
            return jsonify({"message": "user not found"}), 404
        if not user_auth.verify_password(password, user.password):
            return jsonify({"message": "invalid password"}), 400
        else:
            # Create access token and set cookie
            access_token = user_authenticator.create_token(user.id)
            response = jsonify({"message": "Logged in successfully!", "status": 200, "access_token": access_token})
            user_authenticator.set_cookie(response, access_token)
            return response


# Get a user
@app_views.route('/profile', methods=['GET'])
@jwt_required()
def get_user():
    """
    Get a user
    """
    # Get authenticated user ID
    user_id = user_authenticator.get_authenticated_user()
    user = user_auth.get_user_by_id(user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    # Prepare user data for response
    user_data = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "location": user.location,
        "role": user.role,
        "is_active": user.is_active,
        "last_login": user.last_login
    }

    # Return user data
    return jsonify(user_data), 200


# Logout a user
@app_views.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')

    if auth_header and auth_header.startswith('Bearer '):
        access_token = auth_header.split(' ')[1]

        identity = user_authenticator.get_authenticated_user()
        if identity and access_token:
            # Unset cookie and return success response
            response = jsonify({'message': 'Logged out successfully', 'status': 200})
            user_authenticator.unset_cookie(response, access_token)
            return jsonify({'message': 'Logged out successfully'}), 200
        else:
            return jsonify({'message': 'No access token found'}), 400
