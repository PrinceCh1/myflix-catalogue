from flask import Flask, jsonify, render_template, session, request, Blueprint
from datetime import datetime, timezone, timedelta
from microservices.video_service.app.models import Video
import db

video_bp = Blueprint('video', __name__)


def stringify_data(data, include_fields=None):
    # If fields are not provided, include all fields
    include_fields = include_fields or data.keys()

    # Only the specified fields will be included
    filtered_data = {field: data[field] for field in include_fields if field in data}

    # Convert to string
    if '_id' in filtered_data:
        filtered_data['_id'] = str(filtered_data['_id'])
    return filtered_data


@video_bp.route('/')
def display_video_selection():
    all_videos = db.video_collection.find()

    video_list = list(all_videos)

    return render_template('videos.html', videos=video_list)


@video_bp.route('/<int:video_id>/')
def video_player(video_id):
    # Fetch the video details based on the video_id from your data source (e.g., MongoDB)
    # For now, let's assume you have a function get_video_by_id(video_id)
    video = Video.find_by_id(db, video_id)
    if video:
        return render_template('video_player.html', video=video)
    else:
        return "Video not found", 404
