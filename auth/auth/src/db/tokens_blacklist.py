import redis

from settings import redis_setttings as conf


token_blacklist = redis.StrictRedis(host=conf.host, port=conf.port, db=conf.db, decode_responses=True)
