import logging
import logging.config
import requests
from requests.auth import HTTPBasicAuth
from fake_useragent import UserAgent

from src.utils.backoff import backoff
from src.utils.gen_data import generate_users

# Load the logging configuration
logging.config.fileConfig("logging.conf")

# Create a custom logger
logger = logging.getLogger(__name__)

ua = UserAgent()

EXTRA_USER = 1


@backoff(max_retries=3)
def post(url, data):
    try:
        headers = {"User-Agent": ua.random}
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as err:
        logger.error(f"RequestException: {err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")


@backoff(max_retries=3)
def login(username, password):
    login_url = "http://auth:5000/auth/api/v1/login"
    try:
        headers = {"User-Agent": ua.random}
        basic_auth = HTTPBasicAuth(username, password)
        response = requests.get(login_url, auth=basic_auth, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as err:
        logger.error(f"RequestException: {err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")


def fake_sign_up():
    url = "http://auth:5000/auth/api/v1/signup"
    # Create an additional user after generating the required users
    additional_user_data = next(generate_users(EXTRA_USER))
    post(url, additional_user_data)

    username = additional_user_data["username"]
    password = additional_user_data["password"]
    access_token = login(username, password)
    return access_token
