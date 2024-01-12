from flask_pymongo import ObjectId


class Video:

    def __init__(self, db, _id, title, description, genre, release, director, actor, duration, embed_code, thumbnail):
        self.db = db
        self._id = _id
        self.title = title
        self.description = description
        self.genre = genre
        self.release = release
        self.director = director
        self.actor = actor
        self.duration = duration
        self.embed_code = embed_code
        self.thumbnail = thumbnail

    def save_to_db(self):
        video_data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'release': self.release,
            'director': self.director,
            'actor': self.actor,
            'duration': self.duration,
            'embed_code': self.embed_code,
            'thumbnail': self.thumbnail
        }
        result = self.db.video_collection.insert_one(video_data)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, db, video_id):
        return db.video_collection.find_one({'id': video_id})

    @classmethod
    def find_attribute_by_id(cls, db, video_id, attribute):
        video = db.video_collection.find_one({'_id': ObjectId(video_id)})
        return video[attribute] if video and attribute in video else None
