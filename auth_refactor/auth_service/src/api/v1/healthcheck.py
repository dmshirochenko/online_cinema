from http import HTTPStatus
from flask import jsonify
from app import app

# from core.init_extension import db
from flasgger.utils import swag_from


@app.route("/healthcheck", methods=["GET"])
@swag_from("./docs/healthcheck.yml")
def health_check():
    try:
        # Try to execute a simple select query
        # db.session.execute('SELECT 1')
        return jsonify({"status": "healthy"}), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy"}), HTTPStatus.SERVICE_UNAVAILABLE
