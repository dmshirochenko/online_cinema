FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y netcat-openbsd

COPY requirements.txt requirements.txt

RUN pip install pip --upgrade --no-cache-dir \
  && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x /opt/app/start.sh

# copy wait-for-it.sh and make it executable
RUN chmod +x /opt/app/tests/wait-for-it.sh

CMD ["/opt/app/start.sh"]
