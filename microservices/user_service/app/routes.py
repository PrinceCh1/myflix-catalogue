from flask import Flask, jsonify, render_template, request, Blueprint
from datetime import datetime, timezone, timedelta
from microservices.user_service.app.models import User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import db

user_bp = Blueprint('user', __name__)
authentication_bp = Blueprint('authenticate', __name__)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "05527cbaf81fadfb66a1ab0a5b68394bb20a8d00"
jwt = JWTManager(app)


def stringify_data(data, include_fields=None):
    # If fields are not provided, include all fields
    include_fields = include_fields or data.keys()

    # Only the specified fields will be included
    filtered_data = {field: data[field] for field in include_fields if field in data}

    # Convert to string
    if '_id' in filtered_data:
        filtered_data['_id'] = str(filtered_data['_id'])
    return filtered_data


# Route to get all users
@user_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def get_all_users():
    users = [stringify_data(i, include_fields=['username', 'email']) for i in db.user_collection.find()]
    return jsonify(users)


# Authentication for routes in user_bp
@user_bp.before_request
@authentication_bp.before_request
@jwt_required(optional=True)
def authenticate_user():
    if not get_jwt_identity():
        return 'Authentication required', 401


# Route to get specific users
@user_bp.route('/<string:username>', methods=['GET'])
def get_user(username):
    user = User.find_by_username(db, username)
    if user:
        user = stringify_data(user, include_fields=['username', 'email'])
        return jsonify(user), 200
    else:
        # If user is not found, return a 404 error message
        error_response = {'error': 'User not found'}
        return jsonify(error_response), 404


@authentication_bp.route('/register/', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        new_user = User(db, username, email, password)

        # Validate that all required fields are present
        if not username or not email or not password:
            return 'All fields are required for registration.'

        # Check if the username already exists
        existing_user = User.find_by_username(db, new_user.username)
        if existing_user:
            return 'Username already exists. Choose a different one.'

        # Insert the new user into the database
        user_id = new_user.save_to_db()

        # Create JWT token for the registered user
        access_token = create_access_token(identity=str(user_id))

        return jsonify(access_token=access_token), 200

    return render_template('register.html')


@authentication_bp.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password match
        found_user = User.username_matches_password(db, username, password)
        if found_user:
            # Create JWT token for the authenticated user
            access_token = create_access_token(identity=str(found_user['_id']))

            # Return the token to the client
            return jsonify(access_token=access_token), 200

        return 'Invalid username or password. Please try again.', 401

    return render_template('login.html')


@authentication_bp.route('/')
@jwt_required(optional=True)
def home():
    current_user_id = get_jwt_identity()
    print("Current user id: ", current_user_id)

    if current_user_id:
        username = User.find_name_by_id(current_user_id)
    else:
        username = None
    return render_template('index.html', username=username)


@authentication_bp.route('/logout/')
def logout():
    return 'You have been logged out.'
