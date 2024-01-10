from flask_pymongo import pymongo


CONNECTION_STRING = "mongodb+srv://prince:bkKh1xxktZE61piF@cluster0.6aurx15.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('myFlix')
user_collection = pymongo.collection.Collection(db, 'users')
video_collection = pymongo.collection.Collection(db, 'videos')