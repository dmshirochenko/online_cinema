import os
import time

from elasticsearch import Elasticsearch


if __name__ == "__main__":
    host, port = os.environ.get("ES_HOST"), os.environ.get("ES_PORT")
    es_client = Elasticsearch(hosts=f"{host}:{port}", validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            print("Connection made to elastic")
            break
        time.sleep(1)
        print("Waiting for elastic...")
