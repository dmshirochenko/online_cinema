import redis


class DBConnection:
    def __init__(self, host: str, port: int):
        self.db = redis.Redis(host, port, decode_responses=True)

    def insert_data(self, user_id: str, movie_ids: list[str]) -> None:
        self.db.rpush(user_id, *movie_ids)

    def get_movie_ids(self, user_id: str) -> list[str]:
        ids = []
        for i in range(self.db.llen(user_id)):
            ids.append(self.db.lindex(user_id, i))
        return ids
