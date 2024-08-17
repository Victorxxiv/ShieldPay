# flask imports
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy  # Database ORM
import os  # for environment variables
import jwt  # PyJWt for authentication, token generation
from datetime import datetime, timedelta  # for token expiration
import uuid  # for public id, unique id
from functools import wraps  # for decorator

# Create Flask app
app = Flask(__name__)
# Configuring the database
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# Database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# Create database app
db = SQLAlchemy(app)

# User model and database ORM
class User(db.Model):
    # User table
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(110))
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))


# Decorator for token required
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if toke is in the header
        if 'x-access-token' in requast.headers:
            token = request.headers['x-access-token']
        # If token is not found  return 401
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query\
                .filter_by(public_id=data['public_id']).first()

        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        # Return the current user
        return f(current_user, *args, **kwargs)

    return decorated

# Route to register users
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    # Query all users
    users = User.query.all()
    # Convert the users to a list of jsons and return
    output = []
    for user in users:
        # Append user to the output list
        output.append({
            'public_id': user.public_id,
            'name': user.name,
            'email': user.email
        })

    # Return the list of users
    return jsonify({'users': output})


if __name__ == "__main__":
    # setting debug to True to enable auto-reload
    # as the code changes and also to show error messages
    app.run(debug=True)
