from flask import Flask, request
from flasgger import Swagger
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify


from db.users import init_db
from views.auth.v1.auth import auth as auth_v1
from views.auth.v1.auth_google import auth_google as auth_google_v1
from views.admin import admin
from utils.jwt import jwt
from utils.request import Request_
from utils.create_superuser import _register_superuser_cli_command, create_superuser
from utils.tracer import configure_tracer
from settings import flask_settings, app_settings


def create_app():
    if app_settings.TRACING:
        configure_tracer()

    app = Flask(__name__)
    app.config.from_object("settings.AppSettings")
    app.request_class = Request_
    app.secret_key = app_settings.SECRET_KEY

    _register_superuser_cli_command(app)

    # limiter = Limiter(get_remote_address, app=app, default_limits=["1/second"])
    # limiter.limit("5/minute")(auth_v1)
    # limiter.limit("5/hour")(admin)

    app.register_blueprint(auth_v1)
    app.register_blueprint(auth_google_v1)
    app.register_blueprint(admin)

    # @app.before_request
    # def before_request():
    #     request_id = request.headers.get('X-Request-Id')
    #     if not request_id:
    #         raise RuntimeError('request id is required')

    init_db(app)
    app.app_context().push()

    jwt.init_app(app)

    @app.route("/auth/health", methods=["GET"])
    def health_check():
        # Basic example; you may want to add database checks, etc.
        return jsonify(status="OK", code=200), 200

    return app


def main():
    app = create_app()

    # FlaskInstrumentor().instrument_app(app)
    swagger = Swagger(app)
    app.run(host=flask_settings.host, port=flask_settings.port)


if __name__ == "__main__":
    main()
