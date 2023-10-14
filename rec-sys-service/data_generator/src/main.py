import os
import logging
import logging.config
import requests
import random
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException
from requests.auth import HTTPBasicAuth

from fake_useragent import UserAgent
from pydantic import BaseSettings

from utils.utils import generate_users
from utils.backoff import backoff
from settings import app_settings as conf


# Load the logging configuration
logging.config.fileConfig("logging.conf")

# Create a custom logger
logger = logging.getLogger(__name__)

ua = UserAgent()


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


@backoff(max_retries=3)
def fetch_users(access_token):
    users_url = "http://auth:5000/auth/api/v1/users"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(users_url, headers=auth_headers)
        response.raise_for_status()
        # Extract all user ids
        user_ids = [user["id"] for user in response.json()["users"]]
        return user_ids

    except requests.exceptions.RequestException as err:
        logger.error(f"RequestException: {err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")


@backoff(max_retries=3)
def fetch_all_films(access_token, page_size=20):
    page_number = 1
    all_film_ids = []

    while True:
        films_url = (
            f"http://service-content:80/api/v1/films/all_films?page[number]={page_number}&page[size]={page_size}"
        )
        auth_headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": ua.random,
        }

        try:
            response = requests.get(films_url, headers=auth_headers)
            logging.info(response.text)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            logger.error(f"RequestException: {err}")
            break
        except Exception as err:
            logger.error(f"An unexpected error occurred: {err}")
            break

        films_data = response.json()
        if films_data["result"]:  # If the result list is not empty
            # Extract only the film IDs
            film_ids = [film["id"] for film in films_data["result"]]
            all_film_ids.extend(film_ids)
            page_number += 1  # Move on to the next page
        else:
            break  # If the result list is empty, break the loop

    return all_film_ids


@backoff(max_retries=3)
def add_random_like(user, movie):
    add_like_url = "http://ugc_api:8000/ratings/api/v1/add_like"
    data = {"user_id": user, "movie_id": movie}
    response = requests.post(add_like_url, json=data)
    response.raise_for_status()
    return response.json()


def add_random_likes(users, movies, n_likes):
    with ThreadPoolExecutor(max_workers=2) as executor:
        for _ in range(n_likes):
            user = random.choice(users)
            movie = random.choice(movies)
            executor.submit(add_random_like, user, movie)


def generate_test_users(n_users: int, auth_url: str, access_token: str):
    futures = []

    with ThreadPoolExecutor(max_workers=2) as executor:
        users_generator = generate_users(n_users)
        for i_user, user_data in enumerate(users_generator):
            if i_user < n_users:
                future = executor.submit(post, auth_url, user_data)
                futures.append(future)
                if i_user % 100 == 0:
                    logger.info(f"Generating {i_user}-th user...")
            else:
                logger.info("Finishing the loop...")
                break

    for future in futures:
        # try:
        future.result()
        # except Exception as err:
        #     logger.error(f"An error occurred in a thread: {err}")

    users = fetch_users(access_token)
    if users:
        logging.info(f"Users fetched: {len(users)}")

    return users


class SuperuserAuth:
    def __init__(self, conf: BaseSettings):
        self.conf = conf

    def __enter__(self):
        username = os.environ.get("AUTH_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("AUTH_SUPERUSER_PASSWORD")

        url = f"{self.conf.auth_url}/auth/api/v1/login"
        basic = HTTPBasicAuth(username, password)
        response = requests.get(url, auth=basic)
        self.access_token = response.json()["access_token"]
        return self.access_token

    def __exit__(self, exc_type, exc_value, exc_tb):
        url = f"{self.conf.auth_url}/auth/api/v1/logout"
        auth_headers = {"Authorization": f"Bearer {self.access_token}"}
        requests.delete(url, headers=auth_headers)


if __name__ == "__main__":
    with SuperuserAuth(conf) as access_token:
        users = generate_test_users(
            n_users=conf.n_users, auth_url=f"{conf.auth_url}/auth/api/v1/signup", access_token=access_token
        )
        logging.info("Test users generated.")

        movies = fetch_all_films(access_token)
        logging.info("Movies fetched.")

        add_random_likes(users, movies, conf.n_likes)
        logging.info("Likes added.")
