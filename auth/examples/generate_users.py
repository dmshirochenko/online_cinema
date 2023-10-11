import argparse
import requests
from requests.auth import HTTPBasicAuth

from faker import Faker


def parse_args():
    parser = argparse.ArgumentParser(description="Generate batch of users for the auth service.")
    parser.add_argument("--n_users", type=int, default=1000, help="Number of users to generate.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    fake = Faker()

    url = "http://127.0.0.1:5001/auth/api/v1/signup"
    for i_user in range(args.n_users):
        passwd = fake.password(length=10)
        form_data = {
            "username": fake.lexify("User-?????"),
            "email": fake.free_email(),
            "password": passwd,
            "confirm": passwd,
        }
        requests.post(url, data=form_data)
        if i_user % 100 == 0:
            print(f"Generating {i_user}-th user...")

    # Login
    url = "http://127.0.0.1:5001/auth/api/v1/login"
    basic = HTTPBasicAuth(form_data["username"], form_data["password"])
    response = requests.get(url, auth=basic)
    access_token = response.json()["access_token"]
    print("User logged in successfully.")

    # Get all users
    url = "http://127.0.0.1:5001/auth/api/v1/users"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    response_data = requests.get(url, headers=auth_headers).json()
    print("Number of users: ", len(response_data["users"]))

    # Logout
    url = "http://127.0.0.1:5001/auth/api/v1/logout"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.delete(url, headers=auth_headers)
    print("User logged out successfully.")
