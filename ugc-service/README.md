## UGC Service


This project provides a User-Generated Content (UGC) service, utilizing multiple components including Kafka, an API for events, ETL jobs, ClickHouse database, and MongoDB. The services are containerized and orchestrated using Docker and Docker Compose.

Services
The project consists of the following services, each running in its own Docker container and defined in the docker-compose.yml:

Kafka Services: This includes Zookeeper and Kafka.
Events API: An API service for handling events.
ETL: A series of ETL jobs that transform and load data into ClickHouse.
ClickHouse: A cluster of ClickHouse servers used for storing processed data.
MongoDB: Used in production environment.
UGC API: API for user-generated content.
Logging: Logstash, Elasticsearch, Kibana, and Filebeat for logs management.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Instructions

To get started with the CINEMA_NOTIFICATION project, you'll need to start the services. You can do this with the provided Makefile:

```bash ```
make start

This command will build and start all the containers defined in the docker-compose.yml file. If the containers are already running, they will be restarted.

If you want to stop all the running containers, you can use:

```bash ```
make stop



**Ratings:**

- **POST /ratings/api/v1/add_like:** This endpoint is for adding a like to a movie. The Like data that needs to be sent in the request body is specified in the schema.

- **DELETE /ratings/api/v1/remove_like:** This endpoint is for removing a like from a movie. Similar to the above, it expects a Like data in the request body.

- **GET /ratings/api/v1/get_num_movie_likes:** This endpoint is for fetching the number of likes for a specific movie. The movie's ID should be sent as a query parameter.

- **GET /ratings/api/v1/get_liked_movies:** This endpoint retrieves all movies that a specific user has liked. The user's ID should be sent as a query parameter.

**Reviews:**

- **POST /reviews/api/v1/add_review_like:** This endpoint is for adding a like to a review. It expects a ReviewLike data in the request body.

- **POST /reviews/api/v1/add_review_dislike:** Similar to the above but for adding a dislike to a review. It also expects a ReviewLike data in the request body.

- **POST /reviews/api/v1/add_review:** This endpoint is for adding a review. It expects a Review data in the request body.

**Bookmarks:**

- **POST /bookmarks/api/v1/save_bookmark:** This endpoint is for saving a bookmark. It expects a Bookmark data in the request body.

- **DELETE /bookmarks/api/v1/delete_bookmark:** This endpoint is for deleting a bookmark. Similar to the above, it expects a Bookmark data in the request body.

**Watched:**

- **POST /watched/api/v1/add_watched_movie:** This endpoint is for marking a movie as watched by a user. It expects a WatchedMovie data in the request body.

- **GET /watched/api/v1/is_movie_watched:** This endpoint checks if a movie has been watched by a user. It requires user's ID and movie's ID as query parameters.

- **GET /watched/api/v1/get_watched_movies_count:** This endpoint retrieves the number of movies watched by a specific user. The user's ID should be sent as a query parameter.

- **GET /watched/api/v1/get_most_watched_movies:** This endpoint retrieves the most-watched movies. It optionally accepts the number of movies to return as a query parameter, defaulting to 100 if not provided.


Mongo DB cluster may need to be used on production