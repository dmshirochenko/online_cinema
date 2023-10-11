import redis

from settings import redis_setttings as conf


auth_cache = redis.StrictRedis(host=conf.host, port=conf.port, db=conf.db, decode_responses=True)
