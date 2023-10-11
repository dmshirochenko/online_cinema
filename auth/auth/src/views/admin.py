import uuid
from functools import wraps
from http import HTTPStatus

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from db.auth_cache import auth_cache
from db.users import db
from models.user import User
from models.role import Role
from utils.jwt import jwt

admin = Blueprint("admin", __name__)


# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["sub"]
#     identity_cached = auth_cache.hgetall(identity)
#
#     if not identity_cached:
#         user = User.query.filter_by(id=identity).one_or_none()
#         if user:
#             auth_cache.hmset(str(identity), user.as_dict())
#         return user
#
#     return User(**identity_cached)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            return (
                jsonify({"message": "User doesn't have admin status."}),
                HTTPStatus.UNAUTHORIZED,
            )
        return f(*args, **kwargs)

    return decorated_function


@admin.route("/auth/admin/create_role", methods=["POST"])
@jwt_required(verify_type=False)
@admin_required
def create_role() -> Response:
    """Creating new role.
    Role data is obtained from POST form fields. Requires admin flag to be accessed.
    ---
    tags:
      - roles-CRUD
    parameters:
      - name: body
        in: body
        required: true
        description: Form with a role name.
        schema:
          required:
            - role
        properties:
          role:
            type: string
    responses:
      200:
        description: Confirmation that the role has been created.
      401:
        description: A role attempted to be created already exists.
    """
    role_name = request.form.get("role", "")

    role = Role.query.filter_by(role=role_name).one_or_none()
    if role is not None:
        return jsonify({"message": "Role existed"}), HTTPStatus.UNAUTHORIZED

    new_role = Role(id=uuid.uuid4(), role=role_name)
    db.session.add(new_role)
    db.session.commit()

    return jsonify({"message": "New role created"}), HTTPStatus.CREATED


@admin.route("/auth/admin/delete_role/<role>", methods=["DELETE"])
@jwt_required(verify_type=False)
@admin_required
def delete_role(role: str) -> Response:
    """Deleting existing role.
    Requires admin flag to be accessed.
    ---
    tags:
      - roles-CRUD
    parameters:
      - in: path
        name: role
        type: string
        required:  true
    responses:
      200:
        description: Confirmation that the role has been deleted.
      404:
        description: A role attempted to be deleted doesn't exist.
    """
    _role = Role.query.filter_by(role=role).one_or_none()
    if _role is None:
        return jsonify({"message": "Role doesn't exist"}), HTTPStatus.NOT_FOUND

    db.session.delete(_role)
    db.session.commit()

    return jsonify({"message": "Role deleted"}), HTTPStatus.OK


@admin.route("/auth/admin/edit_role", methods=["PATCH"])
@jwt_required(verify_type=False)
@admin_required
def edit_role() -> Response:
    """Editing existing role.
    Requires admin flag to be accessed.
    ---
    tags:
      - roles-CRUD
    parameters:
      - name: body
        in: body
        required: true
        description: Form with old and new role names.
        schema:
          required:
            - role
            - new_role
        properties:
          role:
            type: string
          new_role:
            type: string
    responses:
      200:
        description: Confirmation that the role has been edited.
      404:
        description: A role attempted to be edited doesn't exist.
    """
    role_name = request.form.get("role", "")
    new_role_name = request.form.get("new_role", "")

    role = Role.query.filter_by(role=role_name).one_or_none()
    if role is None:
        return jsonify({"message": "Role doesn't exist"}), HTTPStatus.NOT_FOUND

    role.role = new_role_name
    db.session.commit()

    return jsonify({"message": "Role edited"}), HTTPStatus.OK


@admin.route("/auth/admin/all_roles", methods=["GET"])
@jwt_required(verify_type=False)
@admin_required
def get_all_roles() -> Response:
    """Getting all existing roles.
    Requires admin flag to be accessed.
    ---
    tags:
      - roles-CRUD
    responses:
      200:
        description: Confirmation that the role has been edited.
    """
    roles = Role.query.all()
    return jsonify({"foles": [r.role for r in roles]}), HTTPStatus.OK


@admin.route("/auth/admin/assign_user_role", methods=["POST"])
@jwt_required(verify_type=False)
@admin_required
def assign_role_to_user() -> Response:
    """Assigning a role to existing user.
    Requires admin flag to be accessed.
    ---
    tags:
      - admin
    parameters:
      - name: body
        in: body
        required: true
        description: Form with a user login and a form.
        schema:
          required:
            - user_login
            - role
        properties:
          user_login:
            type: string
          role:
            type: string
    responses:
      200:
        description: Confirmation that the role has been assigned successfully.
      404:
        description: A role or user attempted to be edited doesn't exist.
    """
    user_login = request.form.get("user_login", "")
    user = User.query.filter_by(login=user_login).one_or_none()
    if user is None:
        return jsonify({"message": "User doesn't exst"}, HTTPStatus.NOT_FOUND)

    role_name = request.form.get("role", "")
    role = Role.query.filter_by(role=role_name).one_or_none()
    if role is None:
        return jsonify({"message": "Role doesn't exist"}, HTTPStatus.NOT_FOUND)

    user.roles.append(role)
    db.session.commit()

    msg = f"User {user.login} has been assigned {role.role} role"
    return jsonify({"message": msg}), HTTPStatus.OK


@admin.route("/auth/admin/remove_user_role", methods=["POST"])
@jwt_required(verify_type=False)
@admin_required
def remove_role_from_user() -> Response:
    """Removing a role to existing role.
    Requires admin flag to be accessed.
    ---
    tags:
      - admin
    parameters:
      - name: body
        in: body
        required: true
        description: Form with a user login and a form.
        schema:
          required:
            - user_login
            - role
        properties:
          user_login:
            type: string
          role:
            type: string
    responses:
      200:
        description: Confirmation that the role has been removed successfully.
      404:
        description: A role or user attempted to be removed doesn't exist.
    """
    user_login = request.form.get("user_login", "")
    user = User.query.filter_by(login=user_login).one_or_none()
    if user is None:
        return jsonify({"message": "User doesn't exst"}, HTTPStatus.NOT_FOUND)

    role_name = request.form.get("role", "")
    role = Role.query.filter_by(role=role_name).one_or_none()
    if role is None:
        return jsonify({"message": "Role doesn't exist"}, HTTPStatus.NOT_FOUND)

    user.roles.remove(role)
    db.session.commit()

    msg = f"User {user.login} was released from {role.role} role"
    return jsonify({"message": msg}), HTTPStatus.OK
