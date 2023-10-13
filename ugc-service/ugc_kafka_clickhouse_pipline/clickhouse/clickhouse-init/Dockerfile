FROM python:3.10.9-slim-buster

WORKDIR /app

# Install netcat for checking postgres availability
RUN apt-get update && apt-get install -y netcat

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add a bash script to check if ClickHouse is up
COPY wait-for-clickhouse.sh /app/wait-for-clickhouse.sh

# Make the entrypoint script executable
RUN chmod +x /app/wait-for-clickhouse.sh

CMD ["./wait-for-clickhouse.sh", "python", "init.py"]
