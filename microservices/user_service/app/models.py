from flask_pymongo import ObjectId


class User:
    def __init__(self, db, username, email, password):
        self.db = db
        self.username = username
        self.email = email
        self.password = password

    def save_to_db(self):
        user_data = {'username': self.username, 'email': self.email,
                     'password': self.password}
        result = self.db.user_collection.insert_one(user_data)
        return str(result.inserted_id)


    @classmethod
    def find_by_username(cls, db, username):
        return db.user_collection.find_one({'username': username})

    @classmethod
    def username_matches_password(cls, db, username, password):
        return db.user_collection.find_one({'username': username, 'password': password})

    @classmethod
    def find_by_email(cls, db, email):
        return db.user_collection.find_one({'email': email})

    @classmethod
    def find_by_id(cls, db, user_id):
        return db.user_collection.find_one({'_id': ObjectId(user_id)})

    @classmethod
    def find_name_by_id(cls, db, user_id):
        user = db.user_collection.find_one({'_id': ObjectId(user_id)})
        return user['username'] if user else None
