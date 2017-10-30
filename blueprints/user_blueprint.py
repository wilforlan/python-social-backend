from flask import Blueprint
from flask import request
from custom.JSONEncoder import render_json
from flask import json, jsonify
import pymongo
from config.models import Users
from config.models import Stories
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
)
from bson.objectid import ObjectId
from datetime import date
from bson.json_util import dumps
from bson.json_util import loads

user_blueprint = Blueprint('user_blueprint', __name__)


@user_blueprint.route("/<user_id>", methods=['GET'])
@jwt_required
def profile(user_id):
    try:
        user = Users.find_one({'_id' : ObjectId(user_id)})
        if user:
            return jsonify(status='success', payload=loads(render_json(user))), 200
        else:
            return jsonify(status='error', msg="User not found"), 404
    except:
        return jsonify(status='error', msg="An Error Occured"), 500

@user_blueprint.route("/story", methods=['POST'])
@jwt_required
def add_story():
    # if len(request.form['user_id']) < 1:
    #     return jsonify(status='error', msg="User ID Must be present")
    # elif len(request.form['story_type']) < 1:
    #     story_type = 'text'
    # elif len(request.form['story_type']) > 1:
    #     story_type = request.form['story_type']
    
    # story_type = request.form['story_type'] if request.form['story_type'] else 'text'
    story_type = 'text'
    StoryObject = {
        'user_id' : ObjectId(request.form['user_id']),
        'created_on' : date.today().isoformat(),
        'story_type' : 'text',
        'updated_on' : date.today().isoformat(),
        'deleted' : False
    }
    # if story_type == 'text':
    StoryObject['story_content'] = request.form['story_text']
    # else:
    #     return jsonify(status='error', msg="Only story of type text is supported "), 500
    try:
        new_story_id = Stories.insert_one(StoryObject).inserted_id
        return jsonify(status='success', msg='Story Added Successfully', payload= str(new_story_id)), 200
    except:
        return jsonify(status='error', msg="An Error Occured"), 500


@user_blueprint.route("/story/<story_id>", methods=['GET'])
@jwt_required
def get_story(story_id):
    try:
        story = Stories.aggregate([
            {
                '$match' : {'_id': ObjectId(story_id)}
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "user_id",
                    'foreignField': "_id",
                    'as': "user_details"
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "likes",
                    'foreignField': "_id",
                    'as': "likers"
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "dislikes",
                    'foreignField': "_id",
                    'as': "dislikers"
                }
            }
        ])
        if story:
            return jsonify(status='success', payload=dumps(story)), 200
        else:
            return jsonify(status='error', msg="User not found"), 404
    except:
        return jsonify(status='error', msg="An Error Occured"), 500


@user_blueprint.route("/<user_id>/story", methods=['GET'])
@jwt_required
def get_user_story(user_id):
    limit = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    offset = (page - 1) * limit
    try:
        story = Stories.aggregate([
            {
                '$match' : {'user_id': ObjectId(user_id)}
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "user_id",
                    'foreignField': "_id",
                    'as': "user_details"
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "likes",
                    'foreignField': "_id",
                    'as': "likers"
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "dislikes",
                    'foreignField': "_id",
                    'as': "dislikers"
                }
            },
            {
                '$sort' : { 
                    'created_on' : -1
                }
            },
            { 
                '$limit' : limit 
            },
            {
                '$skip' : offset
            }
        ])
        # pages = range(1, Stories.count() / limit + 1)
        # print pages
        if story:
            return jsonify(status='success', payload=dumps(story)), 200
        else:
            return jsonify(status='error', msg="No Story Available"), 404
    except:
        return jsonify(status='error', msg="An Error Occured"), 500

@user_blueprint.route("/<user_id>/newsfeed", methods=['GET'])
@jwt_required
def get_user_newsfeed(user_id):
    limit = int(request.args.get('limit'))
    page = int(request.args.get('page'))
    offset = (page - 1) * limit
    try:

        current_user = Users.find_one({'_id': ObjectId(user_id)})
        current_user_json = loads(render_json(current_user))
        if 'following' in current_user:
            current_user_follwing = current_user_json['following']
        else:
            return jsonify(status="success", msg="You do not have any followers, Follow Someone to see their story",payload=[])
        if len(current_user_follwing) < 1:
            return jsonify(status="success", msg="You do not have any followers, Follow Someone to see their story",payload=[])
        mapped_user_following = list(map((lambda id: ObjectId(id)), current_user_follwing))

        story = Stories.aggregate([
            {
                '$match' : {
                    '$and': [ 
                        {'user_id': {'$in': mapped_user_following } }, 
                    ]
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "user_id",
                    'foreignField': "_id",
                    'as': "user_details"
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "likes",
                    'foreignField': "_id",
                    'as': "likers"
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "dislikes",
                    'foreignField': "_id",
                    'as': "dislikers"
                }
            },
            {
                '$sort' : { 
                    'created_on' : -1
                }
            },
            { 
                '$limit' : limit 
            },
            {
                '$skip' : offset
            }
        ])
        # pages = range(1, Stories.count() / limit + 1)
        # print pages
        if story:
            return jsonify(status='success', payload=dumps(story)), 200
        else:
            return jsonify(status='error', msg="No Story Available"), 404
    except:
        return jsonify(status='error', msg="An Error Occured"), 500

@user_blueprint.route("/<user_id>/like/<story_id>", methods=['PUT', 'POST'])
@jwt_required
def user_like_story(user_id, story_id):
    try:
        already_liked = Stories.find_one({ '_id': ObjectId(story_id),'likes' : ObjectId(user_id) })
        if already_liked:
            return jsonify(status='error', msg="You already like this story"), 200
        else:
            Stories.update({'_id': ObjectId(story_id)},{"$addToSet":{"likes": ObjectId(user_id)}})
            return jsonify(status='success', msg="Story Liked Successfully"), 200
    except:
        return jsonify(status='error', msg="An Error Occured"), 500

@user_blueprint.route("/<user_id>/unlike/<story_id>", methods=['PUT', 'POST'])
@jwt_required
def user_unlike_story(user_id, story_id):
    try:
        already_liked = Stories.find_one({ '_id': ObjectId(story_id),'likes' : ObjectId(user_id) })
        if already_liked:
            Stories.update({'_id': ObjectId(story_id)},{"$pull":{"likes": ObjectId(user_id)}})
            return jsonify(status='success', msg="Story UnLiked Successfully"), 200
        else:
            return jsonify(status='error', msg="You didnot like this story"), 200

    except:
        return jsonify(status='error', msg="An Error Occured"), 500

@user_blueprint.route("/<user_id>/follow/<to_follow>", methods=['PUT', 'POST'])
@jwt_required
def user_follow_request(user_id, to_follow):
    # try:
    already_followed = Users.find_one({ '_id': ObjectId(user_id),'following' : ObjectId(to_follow) })
    if already_followed:
        return jsonify(status='error', msg="You already following this person"), 200
    else:
        Users.update({'_id': ObjectId(user_id)},{"$addToSet":{"following": ObjectId(to_follow)}})
        Users.update({'_id': ObjectId(to_follow)},{"$addToSet":{"active_followers": ObjectId(user_id)}})
        return jsonify(status='success', msg="User followed successfully"), 200
    # except:
    #     return jsonify(status='error', msg="An Error Occured"), 500

@user_blueprint.route("/<user_id>/unfollow/<to_unfollow>", methods=['PUT', 'POST'])
@jwt_required
def user_unfollow_request(user_id, to_unfollow):
    # try:
    already_followed = Users.find_one({ '_id': ObjectId(user_id),'following' : ObjectId(to_unfollow) })
    if already_followed:
        Users.update({'_id': ObjectId(user_id)},{"$pull":{"following": ObjectId(to_unfollow)}})
        Users.update({'_id': ObjectId(to_unfollow)},{"$pull":{"active_followers": ObjectId(user_id)}})
        return jsonify(status='succes', msg="Unfollow Successful"), 200
    else:
        return jsonify(status='error', msg="You are not following this person"), 200
    # except:
    #     return jsonify(status='error', msg="An Error Occured"), 500


@user_blueprint.route("/clear_story", methods=['GET'])
def clear_all_user_story():
    Stories.drop()
    return jsonify({'status': 'success', 'payload': "null"})

@user_blueprint.route("/find_all_users", methods=['GET'])
def find_all_user():
    users = Users.find()
    return jsonify({'status': 'success', 'payload': dumps(users)})



    
