from flask import Blueprint
from flask import request
import hashlib
from custom.JSONEncoder import render_json
from flask import json, jsonify
import pymongo
from config.models import Users
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
)
from datetime import timedelta

auth_blueprint = Blueprint('auth_blueprint', __name__)

@auth_blueprint.route("/login", methods=['POST'])
def login():
    UserObject = {
        '$or': [ { 'username': { '$eq': request.json.get('index') } }, { 'email': request.json.get('index') } ],
        'password' :hashlib.sha224(request.json.get('password')).hexdigest()
    }

    try:
        user = Users.find_one(UserObject)
        if user:
            access_token = create_access_token(identity=render_json(user), expires_delta=timedelta(days=2, hours=23, minutes=59, seconds=59, microseconds=999999))
            return jsonify(status='success', payload=render_json(user), access_token=access_token), 200
        else:
            return jsonify(status='error', message='Account not Found')
    except:
        return jsonify(status='error', message='An Error Occured'), 500

@auth_blueprint.route("/register", methods=['POST'])
def register():
    UserObject = {
        'username' : request.json.get('username'),
        'email' : request.json.get('email'),
        'firstname' : request.json.get('firstname'),
        'lastname' : request.json.get('lastname'),
        'facebook_id' : request.json.get('facebook_id'),
        'twitter_id' : request.json.get('twitter_id'),
        'password' :hashlib.sha224(request.json.get('password').encode('utf-8')).hexdigest()
    }

    try :
        new_user = Users.insert_one(UserObject)
        return jsonify({'status': 'success', 'message':'Account created successfully'})
    except:
        return jsonify({'status': 'error', 'message': "One Or More Record Exists"})

@auth_blueprint.route("/clean_db")
def clean_db():
    Users.drop()
    return jsonify({'status': 'success', 'payload': "null"})

