import json
from http import HTTPStatus

from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from db.users import db
from models.user import User
from models.role import Role


# def signup_admin(client, test_admin_user):
#     data = {
#         "username": test_admin_user["username"],
#         "email": test_admin_user["email"],
#         "password": test_admin_user["password"],
#         "confirm": test_admin_user["password"],
#     }
#     client.post("/auth/api/v1/signup", data=data)
#
#     user = User.query.filter_by(email=test_admin_user["email"]).first()
#     user.admin = True
#     db.session.commit()
#
#
# # TODO: Move to the conftest (?)
# def get_access_headers(email: str) -> dict:
#     _id = User.query.filter_by(email=email).first().id
#     access_token = create_access_token(identity=_id)
#     return {"Authorization": "Bearer {}".format(access_token)}
#
#
# def test_create_role(client: FlaskClient, test_admin_user):
#     signup_admin(client, test_admin_user)
#     access_headers = get_access_headers(test_admin_user["email"])
#
#     data = {"role": "common"}
#     num_roles = Role.query.count()
#     response = client.post("/auth/admin/create_role", data=data, headers=access_headers)
#
#     role = Role.query.filter_by(role=data["role"]).first()
#
#     assert response.status_code == HTTPStatus.CREATED
#     assert Role.query.count() - num_roles == 1
#     assert role.role == data["role"]
#
#
# def test_edit_role(client: FlaskClient, test_admin_user):
#     access_headers = get_access_headers(test_admin_user["email"])
#     data = {"role": "common", "new_role": "premium"}
#     response = client.patch("/auth/admin/edit_role", data=data, headers=access_headers)
#
#     role_old = Role.query.filter_by(role=data["role"]).one_or_none()
#     role_new = Role.query.filter_by(role=data["new_role"]).one_or_none()
#
#     assert response.status_code == HTTPStatus.OK
#     assert role_old is None
#     assert role_new.role == data["new_role"]
#
#
# def test_get_all_roles(client: FlaskClient, test_admin_user):
#     access_headers = get_access_headers(test_admin_user["email"])
#     response = client.get("/auth/admin/all_roles", headers=access_headers)
#
#     assert response.status_code == HTTPStatus.OK
#     assert len(json.loads(response.data)) > 0
#
#
# def test_delete_role(client: FlaskClient, test_admin_user):
#     access_headers = get_access_headers(test_admin_user["email"])
#
#     role = "premium"
#     num_roles = Role.query.count()
#     response = client.delete(f"/auth/admin/delete_role/{role}", headers=access_headers)
#
#     role = Role.query.filter_by(role=role).one_or_none()
#
#     assert response.status_code == HTTPStatus.OK
#     assert role is None
#     assert Role.query.count() - num_roles == -1
#
#
# def test_assign_new_role(client: FlaskClient, test_admin_user):
#     access_headers = get_access_headers(test_admin_user["email"])
#
#     user = User.query.first()
#     user_login = user.login
#     new_role = "role1"
#     assert new_role not in user.roles
#
#     # Creating new role for the test
#     client.post("/auth/admin/create_role", data={"role": new_role}, headers=access_headers)
#     role = Role.query.filter_by(role=new_role).one_or_none()
#     assert role is not None
#
#     # Assigning new role for the user
#     data = {"user_login": user.login, "role": role.role}
#     response = client.post("/auth/admin/assign_user_role", data=data, headers=access_headers)
#     user_updated = User.query.filter_by(login=user_login).first()
#
#     assert response.status_code == HTTPStatus.OK
#     assert new_role in [str(r) for r in user_updated.roles]
#
#
# def test_remove_role(client: FlaskClient, test_admin_user):
#     access_headers = get_access_headers(test_admin_user["email"])
#
#     user = User.query.first()
#     user_login = user.login
#     role_to_remove = "role1"
#     assert role_to_remove in [str(r) for r in user.roles]
#
#     data = {"user_login": user.login, "role": role_to_remove}
#     response = client.post("/auth/admin/remove_user_role", data=data, headers=access_headers)
#
#     user_updated = User.query.filter_by(login=user_login).first()
#
#     assert response.status_code == HTTPStatus.OK
#     assert role_to_remove not in [r for r in user_updated.roles]
