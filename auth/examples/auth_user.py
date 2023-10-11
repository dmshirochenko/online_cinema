import requests
from requests.auth import HTTPBasicAuth


if __name__ == "__main__":
    # Sign-up
    url = "http://127.0.0.1:5001/auth/api/v1/signup"
    form_data = {
        "username": "igor",
        "email": "igor@gmail.com",
        "password": 1234,
        "confirm": 1234,
    }
    response = requests.post(url, data=form_data)
    print("Sign-up Response: ", response.status_code)

    # Login
    url = "http://127.0.0.1:5001/auth/api/v1/login"
    basic = HTTPBasicAuth("igor", "1234")
    response = requests.get(url, auth=basic)
    access_token = response.json()["access_token"]
    print("User logged in successfully.")

    # Get all users
    url = "http://127.0.0.1:5001/auth/api/v1/users"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=auth_headers)
    print("All users: ", response.json()["users"])

    # Logout
    url = "http://127.0.0.1:5001/auth/api/v1/logout"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.delete(url, headers=auth_headers)
    print("User logged out successfully.")
