## Events API

Simple API with a single route `/apiv/v1/send_event` that sends even via `POST` method to Kafka cluster

![Screenshot 2023-06-12 at 12 57 12 AM](https://github.com/torwards/ugc_sprint_1/assets/23639048/bb120d69-55be-4026-a78f-37c80a244f2a)

### How to run Kafka and Events API

```
docker compose -f docker-compose.yaml up
```

### How to run tests

```
docker compose -f tests/docker-compose.yml up --build
```
