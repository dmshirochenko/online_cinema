FROM python:3.10

WORKDIR /opt/auth

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/opt/auth'

COPY requirements.txt requirements.txt

RUN apt-get update -y \
	 &&	pip install --upgrade pip \
     && pip install -r requirements.txt 

COPY . .

EXPOSE 5000

ENTRYPOINT [ "bash", "/opt/auth/docker_init/docker-entrypoint.sh" ]
