# -*- coding: utf-8 -*-
import redis
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from product.utils import get_redis_svr_par
from product.settings import IP_POOL_KEY


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """
        设置user agent和ip代理
    """
    def __inti__(self, user_agent=""):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        # 随机取出一个ip_port_useragent
        key = IP_POOL_KEY % {'name': spider.name}
        try:
            ip_port_ua = spider.redis_srv.srandmember(key)
        except:
            redis_srv_par = get_redis_svr_par()
            spider.redis_srv = redis.StrictRedis(**redis_srv_par)
            spider.logging.info('RotateUserAgentMiddleware: redis can not connect, retry once ok')
            ip_port_ua = spider.redis_srv.srandmember(key)
        
        # todo: ip_port_ua可能获取失败为None
        # 这里还没调好应该抛出什么异常会让框架丢掉该请求，暂时先不处理ip_port_ua为None的异常
        if ip_port_ua is None:
            # 把公司主页url重新放回到 start_urls 调度队列
            if request.meta.__contains__('main_page_url'):
                url = request.meta['main_page_url']
            else:
                url = request.url
            spider.redis_srv.sadd(spider.redis_key, url)
        
        ip_port = ip_port_ua.split("||")[0]
        ua = ip_port_ua.split("||")[1]
        
        # 设置user-agent和ip代理
        if ua != "":
            request.headers.setdefault("User-Agent", ua)
        request.meta['proxy'] = "http://%s" % ip_port
        print "set proxy ip:%s" % ip_port



