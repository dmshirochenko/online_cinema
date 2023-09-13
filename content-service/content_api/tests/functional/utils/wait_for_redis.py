import os
import time

import redis


if __name__ == "__main__":
    host = os.environ.get("REDIS_HOST")
    port = os.environ.get("REDIS_PORT")
    redis = redis.Redis(host=host, port=port)
    while True:
        try:
            if redis.ping():
                print("Connection made for redis")
                break
        except redis.exceptions.ConnectionError:
            time.sleep(1)
            print("Waiting for redis...")
