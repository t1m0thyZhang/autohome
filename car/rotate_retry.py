# -*- coding: utf-8 -*-
import redis
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from product.utils import get_redis_svr_par


class RotateRetryMiddleware(RetryMiddleware):
    """
        设置重试中间件逻辑
    """
    def _retry(self, request, reason, spider):
        # 重试失败后把公司主页url重新放回到 start_urls 调度队列
        if request.meta.__contains__('proxy'):
            spider.logging.info('no need to retry, request is:%s, failed reason:%s, proxy ip:%s' % (request, reason, request.meta['proxy']))
        else:
            spider.logging.info('no need to retry, request is:%s, failed reason:%s' % (request, reason))
        
        if request.meta.__contains__('main_page_url'):
            url = request.meta['main_page_url']
        else:
            url = request.url
        
        try:
            spider.redis_srv.sadd(spider.redis_key, url)
        except:
            redis_srv_par = get_redis_svr_par()
            spider.redis_srv = redis.StrictRedis(**redis_srv_par)
            spider.logging.info('RotateRetryMiddleware: redis can not connect, retry once ok')
            spider.redis_srv.sadd(spider.redis_key, url)



