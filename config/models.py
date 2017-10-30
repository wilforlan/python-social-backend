from pymongo import MongoClient
import pymongo
from config.db import db

Users = db.users
# User Collection Properties

# {
#     username = String
#     firstname = String
#     lastname = String
#     email = String
#     password = Hash sha224
#     facebook_id = String
#     twitter_id = String
#     pending_followers = [] | <ObjectID>
#     following = [] | <ObjectID>
#     active_followers = [] | <ObjectID>
#     blocked_followers = [] | <ObjectID>
#     profile_love = [] | <ObjectID>
# }

# User Collection Indexes
Users.create_index([('username', pymongo.ASCENDING)],unique=True)
Users.create_index([('email', pymongo.ASCENDING)],unique=True)
Users.create_index([('facebook_id', pymongo.ASCENDING)],unique=True)
Users.create_index([('twitter_id', pymongo.ASCENDING)],unique=True)


Stories = db.stories

# Stories Collection Properties

# {
#     user_id = ObjectID
#     story_type = enum['picture','video','text']
#     story_content = String (if image or video, contains url to file)
#     likes = [] | <ObjectID>
#     dislikes = [] | <ObjectID>
#     created_on = DateTime
#     updated_on = DateTime
#     deleted = Boolean
# }
