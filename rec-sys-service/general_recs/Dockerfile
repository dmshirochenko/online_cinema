ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8

FROM python:3.9-slim-buster AS py3
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}

COPY --from=py3 / /

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install PySpark
ARG PYSPARK_VERSION=3.2.0
RUN pip --no-cache-dir install pyspark==${PYSPARK_VERSION}

# Set work directory
WORKDIR /opt/app/general_recs

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    curl

# Install Python dependencies
COPY requirements.txt /opt/app/general_recs
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install ml_collab lib for RecSys
COPY ml_collab /opt/app/ml_collab
RUN pip install -e /opt/app/ml_collab/

# Copy project
COPY . /opt/app/general_recs/

CMD ["python", "main.py"]
