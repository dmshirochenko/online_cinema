FROM python:3.10
WORKDIR /opt/app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN cd ml_content && pip install -r requirements.txt && pip install -e .

ENTRYPOINT python src/main.py
