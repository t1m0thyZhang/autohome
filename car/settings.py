# Scrapy settings for product project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
SPIDER_MODULES = ['car.spiders']
NEWSPIDER_MODULE = 'car.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS_PER_DOMAIN = 10
CONCURRENT_REQUESTS = 10

#USER_AGENT = 'scrapy-redis (+https://github.com/rolando/scrapy-redis)'

REDIS_START_URLS_AS_SET = True

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300,
}

LOG_LEVEL = 'DEBUG'

# Introduce an artifical delay to make use of parallelism. to speed up the crawl.
DOWNLOAD_DELAY = 4

DOWNLOAD_TIMEOUT = 8

# DOWNLOADER_MIDDLEWARES = {
#     'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
#     'product.rotate_useragent.RotateUserAgentMiddleware' :400,
#     'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
#     'product.rotate_retry.RotateRetryMiddleware' :500
# }

# Retry many times since proxies often fail
RETRY_TIMES = 3
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408, 520]

# SPIDER_MIDDLEWARES = {
# 'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': True,
# }

# disable cookies
COOKIES_ENABLED = False
COOKIES_ENABLES = False

# redis params
IP_POOL_KEY = '%(name)s:ip_pool'
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': 'utf-8',
    #'db': 1,
   # 'password': "mypasshahayou",
   # 'host': "192.168.200.116",
   'port': "6379",
}