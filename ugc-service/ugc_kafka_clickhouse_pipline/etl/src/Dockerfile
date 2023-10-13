# Dockerfile
FROM python:3.10

WORKDIR /app

RUN apt-get update \
  && apt-get install -y netcat-openbsd

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /app/wait_for_kafka.sh

CMD ["/app/wait_for_kafka.sh"]
