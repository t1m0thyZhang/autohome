
import redis
import sys

redis_srv_par = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': 'utf-8',
    'db': 1,
    'password': "mypasshahayou",
    'host': "192.168.200.116",
    'port': "6379",
}

redis_srv = redis.StrictRedis(**redis_srv_par)
redis_key = '%s:start_urls' % sys.argv[1]

with open(sys.argv[1], 'w') as f:
    urls = redis_srv.smembers(redis_key)
    for url in urls:
        print >> f, url

