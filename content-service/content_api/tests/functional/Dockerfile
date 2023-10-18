# Base image with Python 3.10
FROM python:3.10
WORKDIR /opt/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Create tests directory and copy all files there
RUN mkdir -p /opt/app/tests
COPY entrypoint.sh /opt/app/
COPY . /opt/app/tests/functional

# Set pytest options
ENV PYTEST_ADDOPTS="--color=yes"

# Assuming entrypoint.sh is also in the tests folder in your source
RUN chmod +x /opt/app/entrypoint.sh
ENTRYPOINT ["/opt/app/entrypoint.sh"]
