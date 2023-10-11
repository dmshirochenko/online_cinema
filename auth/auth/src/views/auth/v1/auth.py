import uuid
from datetime import datetime
from http import HTTPStatus

from db.auth_cache import auth_cache
from db.tokens_blacklist import token_blacklist
from db.users import db
from flask import Blueprint, Response, jsonify, make_response, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from models.user import LoginRecord, User
from settings import AppSettings, app_settings
from utils.forms import SignUpForm
from utils.jwt import jwt
from werkzeug.security import check_password_hash, generate_password_hash


auth = Blueprint("auth", __name__)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    identity_cached = auth_cache.hgetall(identity)

    if not identity_cached:
        user = User.query.filter_by(login=identity).one_or_none()
        if user:
            auth_cache.hmset(str(identity), user.as_dict())
        return user

    return User(**identity_cached)


@auth.route("/auth/api/v1/user/<user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id: str) -> Response:
    """Getting user by ID.
    Requires authentication.
    ---
    tags:
      - authentication
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
        description: ID of a user.
    responses:
      200:
        description: User data returned successfully.
      404:
        description: User doesn't exist.
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "Not user found"}), HTTPStatus.NOT_FOUND

    user_data = {
        "id": user.id,
        "login": user.login,
        "password": user.password,
        "roles": user.roles,
    }

    return jsonify({"user": user_data}), HTTPStatus.OK


@auth.route("/auth/api/v1/users", methods=["GET"])
# @jwt_required()
def get_all_users() -> Response:
    """Getting all users.
    Requires authentication.
    ---
    tags:
      - authentication
    responses:
      200:
        description: User data returned successfully.
    """
    users = User.query.all()

    output = []
    for user in users:
        user_data = {
            "id": user.id,
            "login": user.login,
            "password": user.password,
            "roles": user.roles,
        }
        output.append(user_data)

    return jsonify({"users": output})


@auth.route("/auth/api/v1/user/<user_id>", methods=["PUT"])
@jwt_required()
def edit_user(user_id: str) -> Response:
    """Editing user data.
    Requires authentication.
    ---
    tags:
      - authentication
    parameters:
      - name: body
        in: body
        required: true
        description: User updated data.
        schema:
          required:
            - username
            - email
            - password
        properties:
          username:
            type: string
          email:
            type: string
          password:
            type: string
    responses:
      200:
        description: Confirmation that a user has been edited.
      404:
        description: User doesn't exist.
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "No user found"}), HTTPStatus.NOT_FOUND

    user.login = request.json.get("username")
    user.email = request.json.get("email")
    user.password = request.json.get("password")
    db.session.commit()

    return jsonify({"message": "User edited."}), HTTPStatus.OK


@auth.route("/user/api/v1/user/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id: str) -> Response:
    """Deleting user.
    Requires authentication.
    ---
    tags:
      - authentication
    parameters:
      - in: path
        name: user_id
        type: string
        required:  true
    responses:
      200:
        description: Confirmation that a user has been deleted.
      404:
        description: User doesn't exist.
    """
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "No user found"}), HTTPStatus.NOT_FOUND

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "The user has been deleted"}), HTTPStatus.OK


@auth.route("/auth/api/v1/login", methods=["GET"])
def login() -> Response:
    """Sign in endpoint.
    ---
    tags:
      - authorization
    parameters:
      - name: body
        in: body
        required: true
        description: User data.
        schema:
          required:
            - username
            - password
        properties:
          username:
            type: string
          password:
            type: string
    responses:
      200:
        description: Confirmation of a successfull login.
      401:
        description: Login and password don't match with an existing account.
    """
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify",
            HTTPStatus.UNAUTHORIZED,
            {"WWW-Authenticate": "Basic realm='Login required!'"},
        )

    user = User.query.filter_by(login=auth.username).first()
    if not user:
        return jsonify({"message": "No user found"}), HTTPStatus.UNAUTHORIZED

    if not check_password_hash(user.password, auth.password):
        return jsonify({"message": "Password do not match"}), HTTPStatus.UNAUTHORIZED

    # Log new login
    agent_str = f"{request.user_agent.platform}_{request.user_agent.browser}"
    login_entry = LoginRecord(id=uuid.uuid4(), user_id=user.id, auth_date=datetime.now(), user_agent=agent_str)
    db.session.add(login_entry)
    db.session.commit()

    access_token = create_access_token(identity=user.login)
    refresh_token = create_refresh_token(identity=user.login)

    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth.route("/auth/api/v1/refresh")
@jwt_required(refresh=True)
def refresh() -> Response:
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@auth.route("/auth/api/v1/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout() -> Response:
    """Logout endpoint.
    ---
    tags:
      - authorization
    responses:
      200:
        description: User logged out successfully.
    """
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"].lower()

    if ttype == "access":
        token_blacklist.set(jti, "", ex=app_settings.JWT_ACCESS_TOKEN_EXPIRES)

    return jsonify(msg=f"{ttype.capitalize()} token successfullly revoked")


@auth.route("/auth/api/v1/signup", methods=["POST"])
def register() -> Response:
    """Sign-up endpoint.
    ---
    tags:
      - authorization
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        description: User updated data.
        schema:
          required:
            - username
            - email
            - password
            - confirm
        properties:
          username:
            type: string
          email:
            type: string
          password:
            type: string
          confirm:
            type: string
    responses:
      200:
        description: Confirmation of a successfull registration.
      401:
        description: User with the same login / email already exists.
    """
    form = SignUpForm(request.form)

    if not form.validate():
        return (
            jsonify({"message": "Invalid sign up credentials"}),
            HTTPStatus.UNAUTHORIZED,
        )

    user = User.query.filter_by(login=form.username.data).one_or_none()
    if user is not None:
        return jsonify({"message": "Username existed"}), HTTPStatus.UNAUTHORIZED

    hashed_password = generate_password_hash(form.password.data, method="sha256")
    new_user = User(
        id=uuid.uuid4(),
        email=form.email.data,
        login=form.username.data,
        password=hashed_password,
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "New user created"}), HTTPStatus.CREATED


@auth.route("/auth/api/v1/login_history/<int:page>", methods=["GET"])
@jwt_required()
def login_history(page: int) -> Response:
    """Getting history of user's login.
    Requires authentication.
    ---
    tags:
      - authentication
    parameters:
      - in: path
        name: page
        type: int
        required:  true
    responses:
      200:
        description: User logins returned successfully.
      404:
        description: Given page doesn't exist.
    """
    logins = db.paginate(
        LoginRecord.query.filter_by(user_id=current_user.id).order_by(LoginRecord.auth_date),
        page=page,
    )
    return jsonify([(log.user_agent, log.auth_date) for log in logins]), HTTPStatus.OK


@auth.route("/auth/api/v1/role_exists", methods=["GET"])
@jwt_required()
def role_exists() -> Response:
    """Getting user's role.
    Requires authentication.
    ---
    tags:
      - authentication
    responses:
      200:
        description: User data returned successfully.
    """

    return jsonify({"login": current_user.login, "roles": current_user.roles})
