from flask import Flask, render_template, request, redirect, session
from microservices.user_service.models import User
from datetime import datetime, timedelta, timezone
import db, json

app = Flask(__name__)
app.config["SECRET_KEY"] = "05527cbaf81fadfb66a1ab0a5b68394bb20a8d00"

# Load the movies in the JSON file
with open('movies.json', 'r') as file:
    movies_data = json.load(file)


@app.before_request
def activity_checker():
    # if activity has been too long between requests log them out.
    if 'user_id' in session and 'last_activity' in session:
        last_activity_time = session['last_activity']

        # Convert last_activity_time to an aware datetime in UTC
        last_activity_time = last_activity_time.replace(tzinfo=timezone.utc)

        # If last logged activity time is greater than 30 minutes, then remove the user
        if datetime.now(timezone.utc) - last_activity_time > timedelta(minutes=30):
            session.pop('user_id', None)


@app.route('/')
def home():
    # update user activity
    session['last_activity'] = datetime.utcnow()
    if 'user_id' in session:
        user_id = session['user_id']
        username = User.find_name_by_id(db, user_id)
        return render_template('index.html', username=username)
    else:
        return render_template('index.html', username=None)


@app.route('/register/', methods=['GET', 'POST'])
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


@app.route('/login/', methods=['GET', 'POST'])
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


@app.route('/videos/')
def videos():
    return render_template('videos.html', movies=movies_data['movies'])


@app.route('/videos/<int:video_id>/')
def video_player(video_id):
    # Fetch the video details based on the video_id from your data source (e.g., MongoDB)
    # For now, let's assume you have a function get_video_by_id(video_id)
    video = next((movie for movie in movies_data['movies'] if movie['id'] == video_id), None)
    if video:
        return render_template('video_player.html', movie=video)
    else:
        return "Video not found", 404


@app.route('/logout/')
def logout():
    # Clear the session
    session.pop('user_id', None)
    return 'You have been logged out.'


if __name__ == '__main__':
    app.run(port=8000)
