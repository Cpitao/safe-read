from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies

from . import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    email = data['email']
    password = data['password']

    if db.session.query(User).filter_by(username=username).first() is not None:
        return {"err": "Username taken"}, 409

    if db.session.query(User).filter_by(email=email).first() is not None:
        return {"err": "Email taken"}, 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()
    return {"username": username}, 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user = db.session.query(User).filter_by(username=username).first()
    if user:
        if user.check_password(password):
            response = jsonify({"username": username})
            token = create_access_token(identity=username)
            set_access_cookies(response, token)
            return response, 200
    return {"err": "Invalid username or password"}, 401


@auth.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response
