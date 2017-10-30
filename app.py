from flask import Flask
from flask import request
from blueprints.auth_blueprint import auth_blueprint
from blueprints.user_blueprint import user_blueprint
from flask import json, jsonify
from config.models import *
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from custom.JSONEncoder import JSONEncoder, render_json

app = Flask(__name__)

# Work on using ENV file
# file = open(".env", "r")
# DOTENV = file.read()

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(user_blueprint, url_prefix='/users')


@app.route('/', methods=['GET'])
def index():
    return "You are all set"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)