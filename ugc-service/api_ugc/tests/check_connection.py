import httpx
from uuid import uuid4

# Assume base_url = "http://localhost:8000"
base_url = "http://localhost:8000"

# Make up some UUIDs for the user and movie
user_id = str(uuid4())
movie_id = str(uuid4())

# Make the request
response = httpx.post(
    f"{base_url}/watched/api/v1/add_watched_movie",
    json={"user_id": user_id, "movie_id": movie_id},
)


# Check the status code
print(response.status_code)
print(response)
