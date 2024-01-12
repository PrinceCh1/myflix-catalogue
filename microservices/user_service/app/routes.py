from flask import Flask, jsonify, render_template, session, request, Blueprint
from datetime import datetime, timezone, timedelta
from microservices.user_service.app.models import User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import db

user_bp = Blueprint('user', __name__)
authentication_bp = Blueprint('authenticate', __name__)


def stringify_data(data, include_fields=None):
    # If fields are not provided, include all fields
    include_fields = include_fields or data.keys()

    # Only the specified fields will be included
    filtered_data = {field: data[field] for field in include_fields if field in data}

    # Convert to string
    if '_id' in filtered_data:
        filtered_data['_id'] = str(filtered_data['_id'])
    return filtered_data


@user_bp.before_request
@authentication_bp.before_request
def activity_checker():
    # if activity has been too long between requests log them out.
    if 'user_id' in session and 'last_activity' in session:
        last_activity_time = session['last_activity']

        # Convert last_activity_time to an aware datetime in UTC
        last_activity_time = last_activity_time.replace(tzinfo=timezone.utc)

        # If last logged activity time is greater than 30 minutes, then remove the user
        if datetime.now(timezone.utc) - last_activity_time > timedelta(minutes=30):
            session.pop('user_id', None)


# Route to get all users
@user_bp.route('/', methods=['GET'])
def get_all_users():
    users = [stringify_data(i, include_fields=['username', 'email']) for i in db.user_collection.find()]
    return jsonify(users)


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
    # update user activity
    session['last_activity'] = datetime.utcnow()
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

        # Set user session
        session['user_id'] = str(user_id)
        return 'Registration successful. You are now logged in.'

    return render_template('register.html')


@authentication_bp.route('/login/', methods=['GET', 'POST'])
def login():
    # update user activity
    session['last_activity'] = datetime.utcnow()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password match
        found_user = User.username_matches_password(db, username, password)
        if found_user:
            # Set user session
            session['user_id'] = str(found_user['_id'])
            return render_template('login_correct.html', username=username)

        return 'Invalid username or password. Please try again.'

    return render_template('login.html')


@authentication_bp.route('/')
def home():
    # update user activity
    session['last_activity'] = datetime.utcnow()
    if 'user_id' in session:
        user_id = session['user_id']
        username = User.find_name_by_id(db, user_id)
        return render_template('index.html', username=username)
    else:
        return render_template('index.html', username=None)


@authentication_bp.route('/logout/')
def logout():
    # Clear the session
    session.pop('user_id', None)
    return 'You have been logged out.'
