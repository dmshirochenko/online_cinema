import json

import redis

from settings import DBSimilarSettings


class Manager:
    conf: DBSimilarSettings
    client: redis.Redis

    def __init__(self, conf: DBSimilarSettings):
        self.conf = conf
        self.client = redis.Redis(host=self.conf.host, port=self.conf.port)

    def get(self, id):
        json_data = self.client.get(id)
        if json_data is None:
            return None
        return json.loads(json_data)

    def set(self, id, value):
        return self.client.set(id, json.dumps(value))
