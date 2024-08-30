#!/usr/bin/python3
"""
Flask App sends and accept json api requests to the set frontend
"""
from datetime import datetime, timedelta
from functools import wraps
import uuid
from flask import Flask, jsonify, make_response, request, render_template
from flask_sqlalchemy import SQLAlchemy  # Database ORM
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from db import storage
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from auth.auth import Authentication
from api.v1.views.user import app_views
from api.v1.views.transactions import user_trans
from db.storage import DB
from celery import Celery


db = DB()
db.reload()

Auth = Authentication()


load_dotenv()


app = Flask(__name__)
# Configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('PG_URL', 'sqlite:///Database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)


broker_url = os.getenv('CELERY_BROKER_URL')
celery = Celery(
    app.import_name,
    broker=broker_url
)

celery.conf.update(app.config, broker_connection_retry_on_startup=True)
# JWT config
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_SAMESITE'] = "None"
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True






# Mail server config
# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
# app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL')
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


app.url_map.strict_slashes = False

app.register_blueprint(app_views, url_prefix='/api/v1/user')
app.register_blueprint(user_trans, url_prefix='/api/v1/transactions')


host = os.getenv("APP_HOST", "0.0.0.0")
port = os.getenv("APP_PORT", 5000)
environ = os.getenv("APP_ENV")

if environ == 'development':
    app.debug = True
else:
    app.debug = False

# Configure CORS
# cors = CORS(app, origins="0.0.0.0")
# cors = CORS(app, resources={r'/*': {'origins': host}})
# cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
# CORS(app_views, resources={r"/api/v1/views": {"origins": "http://localhost:5432"}},
#    supports_credentials=True)


#@app.route("/")
#def home():
#    return jsonify({"Message": "Landing page display"}), 200

@app.route('/home')  # Home route
def home():
    return render_template('home.html')

@app.route("/health")
def health():
    return jsonify({"Message": "Healthy!"}), 200

# @jwt.expired_token_loader
# def handle_expired_token_callback():
#   return redirect('/api/v1/views/login')


# User model and database ORM
class User(db.Model):
    # User table
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(110), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


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
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query\
                .filter_by(public_id=data['public_id']).first()
        except Exception as e:
            print(e)  # For debugging
            return jsonify({'message': 'Token is invalid!'}), 401
        # Return the current user
        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/about')
def about():
    return render_template('about.html')

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
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Get the request data dict
    auth = request.form
    # Check if the request has email and password
    if not auth or not auth.get('email') or not auth.get('password'):
        # Return 401 error if they are not found
        return make_response(
            'Could not verify', 401,
            {'WWW-Authenticate': 'Basic realm="Login required!"'}
        )

    # Query the user with the email
    user = User.query.filter_by(email=auth.get('email')).first()
    # If user is not found return 401
    if not user:
        return make_response(
            'Could not verify', 401,
            {'WWW-Authenticate': 'Basic realm="User not found!"'}
        )

    # If user is found, check if the password is correct
    if check_password_hash(user.password, auth.get('password')):
        # Generate token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])
        # Return the token
        return jsonify({'token': token}), 201  # 201 if login is successful

    # Return 403 if passsword is incorrect
    return make_response(
        'Could not verify', 403,
        {'WWW-Authenticate': 'Basic realm="Password incorrect!"'}
    )


# Route for register page
@app.route('/register')
def register():
    return render_template('register.html')

# Route for user signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Create dict of the request data
    data = request.form
    # Get the data form; name, email and passowrd
    name, email = data.get('name'), data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        # Return 400 if the data is incomplete
        return make_response('Missing data', 400)

    # Check if the data is complete/User provided all data
    user = User.query.filter_by(email=email).first()

    if not user:
        # Create a new user with database ORM and save
        new_user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        # Save the user
        db.session.add(new_user)
        db.session.commit()

        # Return 201 if user is created
        return make_response('Successfully registered', 201)
    else:
        # Return 202 if the user is already created
        return make_response('User already exists. Please Log in.', 202)


@app.before_request
def check_content_type():
    if request.method in ["POST", "PUT", "PATCH", "DELETE"] and request.headers.content-type != "application/json":
        return jsonify({"message": "Content-Type must be application/json"}), 400

@app.teardown_appcontext
def teardown_db(exception):
    """
    after each request, this method calls .close() (i.e. .remove()) on
    the current SQLAlchemy Session
    """
    storage.close()


@app.errorhandler(404)
def handle_404(exception):
    """
    handles 404 errors, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    message = {'error': description}
    return make_response(jsonify(message), code)


@app.errorhandler(400)
def handle_400(exception):
    """
    handles 400 errors, in the event that global error handler fails
    """
    code = exception.__str__().split()[0]
    description = exception.description
    message = {'error': description}
    return make_response(jsonify(message), code)


@app.errorhandler(Exception)
def global_error_handler(err):
    """
        Global Route to handle All Error Status Codes
    """
    if isinstance(err, HTTPException):
        if type(err).__name__ == 'NotFound':
            err.description = "Not found"
        message = {'error': str(err)}
        code = err.code
    else:
        message = {'error': str(err)}
        code = 500
    return make_response(jsonify(message), code)


@app.after_request
def add_cors_headers(response):
    frontend_url = "http://localhost:5432"
    response.headers.extend({
        'X-Content-Type-Options': 'no-sniff',
        'Access-Control-Allow-Origin': frontend_url,
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'Content-Type, Cache-Control, X-Requested-With, Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, DELETE'
    })


    return response


def setup_global_errors():
    """
    This updates HTTPException Class with custom error function
    """
    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, global_error_handler)

@app.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "Test route works!"}), 200

if __name__ == "__main__":
    """
    MAIN Flask App
    """
    with app.app_context():
        print(app.url_map)
    # initializes global error handling
    setup_global_errors()
    # start Flask app
    app.run(host=host, port=port, debug=True)
