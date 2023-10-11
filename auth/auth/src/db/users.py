from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import pg_settings as pg

db = SQLAlchemy()


def init_db(app: Flask):
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{pg.user}:{pg.password}@{pg.host}/{pg.db}"
    db.init_app(app)
