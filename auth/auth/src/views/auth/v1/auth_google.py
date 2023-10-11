import logging
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Tuple
from uuid import UUID

import cachecontrol
import flask
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import requests
from db.users import db
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from google.oauth2 import id_token
from models.social import SocialAccount
from models.user import LoginRecord, User
from settings import app_settings, google_auth_settings, AuthType
from utils.auth import get_login_from_name, get_random_password
from werkzeug.security import generate_password_hash

auth_google = Blueprint("auth_google", __name__)


def _register_common_account(login: str, email: str) -> User:
    random_password = get_random_password()
    hashed_password = generate_password_hash(random_password, method="sha256")
    # TODO: Add option for sending temporary password to user's email

    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        email=email,
        login=login,
        password=hashed_password,
    )
    db.session.add(new_user)
    db.session.commit()
    logging.info(f"User {login} ({email}) registered as Google user.")

    return new_user


# TODO: Switch to the class-based approach with choosing between multiple authentications
def _register_google_account(user: User, g_email: str):
    soc_acc = SocialAccount(
        id=uuid.uuid4(),
        user_id=user.id,
        user=user,
        social_id=g_email,
        social_name=AuthType.GOOGLE,
    )
    db.session.add(soc_acc)
    db.session.commit()
    logging.info(f"User {g_email} registered as Google user.")


def _register_user_login(user_id: UUID):
    agent_str = f"{request.user_agent.platform}_{request.user_agent.browser}"
    dt = datetime.now()
    login_entry = LoginRecord(id=uuid.uuid4(), user_id=user_id, auth_date=dt, user_agent=agent_str)
    db.session.add(login_entry)
    db.session.commit()
    logging.info(f"User {user_id} login at {dt} registered.")


def find_existing_user(login: str | None, email: str | None) -> Tuple[User | None, str]:
    user = User.get_user_by_universal_login(login, email)
    if user is not None:
        return user, "common"

    social_acc = SocialAccount.get_user_by_universal_login(login, email)
    if social_acc is not None:
        return social_acc.user, social_acc.social_name

    return None, ""


@auth_google.route("/api/v1/authorize_google")
def authorize_google() -> Response:
    if "credentials" not in flask.session:
        return flask.redirect("authorize")

    email = flask.session["user_info"]["email"]
    name = flask.session["user_info"]["name"]
    login = get_login_from_name(name)
    logging.info(f"Resistering user with login {login} and email {email}")

    user, auth_source = find_existing_user(login=None, email=email)

    if not user:
        user = _register_common_account(login, email)
        _register_google_account(user, email)
    else:
        logging.info(f"Found existing authorization for user {login}")

        # Register missing authorization in case if user is registered in another resource
        if auth_source != AuthType.GOOGLE:
            _register_google_account(user, email)
            logging.info(f"Registering missing google account for user {login}")

    _register_user_login(user.id)

    access_token = create_access_token(identity=user.login)
    refresh_token = create_refresh_token(identity=user.login)

    return (
        jsonify(access_token=access_token, refresh_token=refresh_token),
        HTTPStatus.OK,
    )


@auth_google.route("/api/v1/authorize")
def authorize() -> Response:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app_settings.AUTH_SECRET, scopes=google_auth_settings.SCOPES
    )

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for("auth_google.oauth2callback", _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true",
    )

    flask.session["state"] = state

    return flask.redirect(authorization_url)


@auth_google.route("/oauth2callback")
def oauth2callback() -> Response:
    state = flask.session["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app_settings.AUTH_SECRET, scopes=google_auth_settings.SCOPES, state=state
    )
    flow.redirect_uri = flask.url_for("auth_google.oauth2callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = credentials_to_dict(flow.credentials)
    flask.session["credentials"] = credentials

    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=flow.credentials._id_token,
        request=token_request,
        audience=credentials["client_id"],
    )
    flask.session["user_info"] = {"email": id_info["email"], "name": id_info["name"]}

    return flask.redirect(flask.url_for("auth_google.authorize_google"))


@auth_google.route("/api/v1/revoke")
def revoke():
    if "credentials" not in flask.session:
        return 'You need to <a href="/authorize">authorize</a> before ' + "testing the code to revoke credentials."

    credentials = google.oauth2.credentials.Credentials(**flask.session["credentials"])

    revoke = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    status_code = getattr(revoke, "status_code")
    if status_code == HTTPStatus.OK:
        return "Credentials successfully revoked."
    return "An error occurred."


@auth_google.route("/api/v1/clear")
def clear_credentials() -> Response:
    if "credentials" in flask.session:
        del flask.session["credentials"]
    return jsonify({"message": "Credentials have been cleared."}), HTTPStatus.OK


def credentials_to_dict(credentials) -> dict[str, str]:
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
