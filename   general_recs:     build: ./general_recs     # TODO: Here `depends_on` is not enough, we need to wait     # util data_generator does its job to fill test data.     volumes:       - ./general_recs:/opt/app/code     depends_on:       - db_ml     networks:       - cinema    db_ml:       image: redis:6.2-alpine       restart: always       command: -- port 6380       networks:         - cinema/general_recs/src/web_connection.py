import requests
from requests.exceptions import RequestException
from fake_useragent import UserAgent

from src.utils.backoff import backoff

ua = UserAgent()


@backoff(max_retries=3)
def fetch_users(auth_token):
    users_url = "http://auth:5000/auth/api/v1/users"
    headers = {"Authorization": f"Bearer {auth_token}", "User-Agent": ua.random}
    try:
        response = requests.get(users_url, headers=headers)
        response.raise_for_status()
        return response.json()["users"]
    except RequestException as err:
        print(f"Error: {err}")
        return []


@backoff(max_retries=3)
def fetch_liked_movies(ugc_api_url: str, user_id, auth_token):
    liked_movies_url = f"{ugc_api_url}/ratings/api/v1/get_liked_movies?user_id={user_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {auth_token}",
        "User-Agent": ua.random,
    }
    try:
        response = requests.get(liked_movies_url, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        if isinstance(json_response, list) and isinstance(json_response[0], dict):
            return json_response[0].get("liked_movies", [])
        else:
            return []
    except RequestException as err:
        print(f"Error: {err}")
        return []
