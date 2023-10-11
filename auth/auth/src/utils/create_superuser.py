import os
import click
import logging

import requests
from models.user import User

from db.users import db
from settings import flask_settings as conf


def _register_superuser_cli_command(app):
    @app.cli.command("create-superuser")
    @click.argument("name")
    def create_user(name):
        create_superuser(name)


def create_superuser(name: str, host: str | None = None):
    password = os.environ.get("AUTH_SUPERUSER_PASSWORD")
    data = {
        "username": name,
        "email": "admin@admin.com",
        "password": password,
        "confirm": password,
    }

    host = conf.host if host is None else host
    url = f"http://{host}:{conf.port}/auth/api/v1/signup"
    requests.post(url, data=data)

    user = User.query.filter_by(email=data["email"]).first()
    user.admin = True
    db.session.commit()
    logging.info("Superuser created.")
