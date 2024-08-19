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
        if 'x-access-token' in request.headers:
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


# Route for user login
@app.route('/login', methods=['POST'])
def login():
    # Get the request data dict
    auth = request.form

    # Check if the request has email and password
    if not auth or not auth.get('email') or not auth.get('password'):
        # Return 401 error if they are not found
        return make_response('Could not verify', 401,
                             {'WWW-Authenticate': 'Basic realm="Login required!"'})

    # Query the user with the email
    user = User.query.filter_by(email = auth.get('email')).first()

    # If user is not found return 401
    if not user:
        return make_response('Could not verify', 401,
                             {'WWW-Authenticate': 'Basic realm="User not found!"'})

    # If user is found, check if the password is correct
    if check_password_hash(user.password, auth.get('password')):
        # Generate token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        # Return the token
        return make_response(jsonify({'token': token}), 201)
    # Return 403 if passsword is incorrect
    return make_response('Could not verify', 403,
                         {'WWW-Authenticate': 'Basic realm="Password incorrect!"'})


# Route for user signup
@app.route('/singup', methods=['POST'])
def signup():
    # Create dict of the request data
    data = request.form

    # Get the data form; name, email and passowrd
    name, email = data.get('name'), data.get('email')
    password = data.get('password')

    # Check if the data is complete/User provided all data
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create a new user with database ORM and save
        user = User(
            public_id = str(uuid.uuid4()),
            name = name,
            email = email,
            password = generate_password_hash(password)
        )
        # Save the user
        db.session.add(user)
        db.session.commit()

        # Return 201 if user is created
        return make_response('Successfully registered', 201)
    else:
        # Return 202 if the user is already created
        return make_response('User already exists. Please Log in.', 202)


if __name__ == "__main__":
    # setting debug to True to enable auto-reload
    # as the code changes and also to show error messages
    app.run(debug=True)
