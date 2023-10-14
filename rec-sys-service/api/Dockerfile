FROM python:3.10
WORKDIR /opt/app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt
COPY . .

ENTRYPOINT uvicorn app.main:app --host 0.0.0.0 --port 8000

