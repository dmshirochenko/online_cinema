from typing import Generator
import json

import redis

from settings import DBEmbeddingsSettings


class Manager:
    conf: DBEmbeddingsSettings
    client: redis.Redis

    def __init__(self, conf: DBEmbeddingsSettings):
        self.conf = conf
        self.client = redis.Redis(host=self.conf.host, port=self.conf.port)

    def get(self, id: str):
        json_data = self.client.get(id)
        if json_data is None:
            return None
        return json.loads(json_data)

    def set(self, id: str, embs: list[float]):
        embs = list(map(float, embs))
        return self.client.set(id, json.dumps(embs))

    def get_count(self) -> int:
        return self.client.dbsize()

    def get_emb_size(self) -> int | None:
        k = self.client.randomkey()
        emb = self.get(k)
        if emb is None:
            return None
        return len(emb)

    def iterate_all_embeddings(self) -> Generator:
        for _id in self.client.keys():
            yield {"emb": self.get(_id), "id": _id.decode()}
