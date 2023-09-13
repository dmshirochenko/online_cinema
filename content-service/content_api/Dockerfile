FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat-traditional

COPY requirements.txt /opt/app/requirements.txt

RUN pip install pip --upgrade --no-cache-dir \
     && pip install -r /opt/app/requirements.txt --no-cache-dir

# Copy the entire app
COPY . /opt/app/

# Make start.sh executable
RUN chmod +x /opt/app/start.sh

ENTRYPOINT ["/opt/app/start.sh"]