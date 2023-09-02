FROM python:3.10

WORKDIR /opt/app


# Заведите необходимые переменные окружения
ENV DJANGO_SETTINGS_MODULE 'config.settings'
ENV PATH="/opt/app/scripts:${PATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 4
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240


COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN apt-get update && apt-get install -y netcat-openbsd

RUN  mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY . .


#Give permission to script
RUN chmod +x scripts/*

#ENTRYPOINT ["uwsgi", "--strict", "--ini", "uwsgi.ini"]
ENTRYPOINT ["run_uwsgi.sh"]