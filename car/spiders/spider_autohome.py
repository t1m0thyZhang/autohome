# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
import redis
import traceback
import re
from scrapy_redis.utils import bytes_to_str
from scrapy.http import Request
from car.utils import init_logger
from car.utils import get_redis_svr_par
from car.items import CarItem
import datetime
import common_tools


class AutohomeSpider(RedisSpider):
    """spider that reads urls from redis queue (cc:start_urls)."""
    name = 'autohome'
    redis_key = 'autohome:start_urls'
    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT' : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    }

    def __init__(self, *args, **kwargs):
        # 本地环境
        redis_srv_par = get_redis_svr_par()
        self.redis_srv = redis.StrictRedis(**redis_srv_par)
        # 清本地redis缓存
        self.redis_srv.delete(self.redis_key)
        requests_key_str = self.name + ":requests"
        requests_key_str2 = self.name + ":dupefilter"
        self.redis_srv.delete(requests_key_str)
        self.redis_srv.delete(requests_key_str2)

        with open("all_cars_urls.txt",'r') as f:
            init_urls = f.readlines()
        for i in range(20):
            self.redis_srv.sadd(self.redis_key, init_urls[i])

        # url = "http://k.autohome.com.cn/spec/30299/view_1650538_1.html?st=1&piap=0|3170|9871|0|1|0|0|0|0|0|1"
        # self.redis_srv.sadd(self.redis_key, url)

        # logging
        now_date = datetime.datetime.now().strftime("%H%M")
        log_fileName = "%s_%s.log" % (self.name,now_date)
        self.logging = init_logger(self.name,log_fileName)
        # dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(AutohomeSpider, self).__init__(*args, **kwargs)

    def make_request_from_data(self, data):
        url = bytes_to_str(data, self.redis_encoding)
        return Request(url)

    def parse(self, response):
        self.logging.info("url is: %s." % response.url)
        try:
            urls = response.xpath("//span[@class='count']/a/@href").extract()
            if urls:
                url = "http:" + urls[0]
                request = Request(url, callback=self.parse2)
                yield request
        except:
            self.logging.error("layer1 failed, url is:(%s), error info is:(%s)" \
                           % (response.url, traceback.format_exc()))

    # 找到同一个车型的所有评论页
    def parse2(self, response):
        self.logging.info("layer 2 url is: %s." % (response.url))
        try:
            pages_num = response.xpath("//span[@class='page-item-info']").extract()  # 评论页数
            if pages_num:
                pages_num = re.sub("<.*?>|\n|\t|\r", "", pages_num[0])
                pages_num = re.sub(u'共|页', '', pages_num)
                pages_num = int(pages_num)
                tmp_url = (response.url).split('?')[0] + 'index_'
                for i in range(1, pages_num+1):
                    url = tmp_url + str(i) + ".html?GradeEnum=0#dataList"
                    request = Request(url, callback=self.parse3)
                    yield request
            # 评论只有一页
            else:
                request = Request(response.url, callback=self.parse3)
                yield request
        except:
            self.logging.error("layer 2 failed:  url is:(%s), error info is:(%s)" \
                           % ( response.url, traceback.format_exc()))

    # 找评论详情页
    def parse3(self, response):
        self.logging.info("url is: %s." % response.url)
        try:
            item = CarItem()
            urls = response.xpath("//div[@class='title-name name-width-01']/a/@href").extract()
            website_name = response.xpath("//div[@class='subnav-title-name']/a").extract()
            if website_name:
                website_name = common_tools.data_cleaning(website_name[0])
                item['website_name'] = website_name
            website_price = response.xpath("//div[@class='price']/span[@class='font-16']").extract()
            if website_price:
                website_price = re.sub('<.*?>|\r|\n|\t', '', website_price[0])
                item['website_price'] = website_price
            website_score = response.xpath("//span[@class='font-arial number-fen']").extract()
            if website_score:
                website_score = re.sub('<.*?>|\r|\n|\t', '', website_score[0])
                item['website_score'] = website_score
            website_feeling = response.xpath("//div[@class='revision-impress impress-small']").extract()
            if website_feeling:
                website_feeling = re.sub('<.*?>|\r|\n|\t| ', '', website_feeling[0])
                item['website_feeling'] = website_feeling
            if urls:
                for url in urls:
                    url = "http:" + url
                    request = Request(url, meta={'item': item}, callback=self.parse4)
                    yield request
        except:
            self.logging.error("layer 3 failed, url is:(%s), error info is:(%s)" \
                           % (response.url, traceback.format_exc()))

    # 解析评论详情页
    def parse4(self, response):
        self.logging.info("detail is being parsed, url is: %s." % (response.url))
        try:
            item = response.meta['item']
            item['url'] = response.url
            # 评论标题
            comment_title = response.xpath("//div[@class='kou-tit']/h3").extract()
            if comment_title:
                comment_title = common_tools.data_cleaning("".join(comment_title))
                item['comment_title'] = comment_title
            # 评论内容
            comment_content = response.xpath("//div[@class='text-con']").extract()
            if comment_content:
                comment_content = "".join(comment_content)
                comment_content = comment_content.split("<!--@HS_BASE64@-->")[-1]
                comment_content = comment_content.split("<!--@HS_ZY@-->")[0]
                comment_content = re.sub("<.*?>|\n|\t|\r", "", comment_content)
                comment_content = re.sub(u'【最的一点】', u'【最满意的一点】', comment_content)
                comment_content = re.sub(u'【最不的一点】', u'【最不满意的一点】', comment_content)
                item['comment_content'] = comment_content
            # 评论时间
            comment_date = response.xpath("//div[@class='title-name name-width-01']/b").extract()
            if comment_date:
                comment_date = common_tools.data_cleaning(comment_date[0])
                comment_date = common_tools.normalize_date(comment_date)
                item['comment_date'] = comment_date
            # 用户油耗
            user_oil = response.xpath("//dl[@class='choose-dl']/dd[@class='font-arial bg-blue']/p[1]").extract()
            user_oil = re.sub("<.*?>|\r|\n|\t| ", "", "".join(user_oil))
            if user_oil and user_oil != "":
                item["user_oil"] = user_oil
            # 行驶里程
            user_miles = response.xpath("//dl[@class='choose-dl']/dd[@class='font-arial bg-blue']/p[2]").extract()
            user_miles = common_tools.data_cleaning("".join(user_miles))
            if user_miles and user_miles != "":
                item["user_miles"] = user_miles

            # 用户车辆详情
            user_score = []  # 用户评分list [{},{}]
            detail_lines = response.xpath("//dl[@class='choose-dl']").extract()
            if detail_lines:
                for line in detail_lines:
                    key = re.findall("<dt>.*?</dt>", line)
                    if key:
                        key = common_tools.data_cleaning(key[0])
                    else:
                        continue
                    value = re.sub(key, "", line)
                    value = re.sub('<.*?>|\r|\n|\t| ', '', value)
                    value = re.sub(u' ', '', value)
                    # value为空key也不要
                    if value == "":
                        continue
                    if key == u'购买车型':
                        item["user_name"] = value
                    elif key == u'购买地点':
                        item["user_address"] = value
                    elif key == u'购买时间':
                        if value[-1] == u"月":
                            value += u"01日"
                        value = common_tools.normalize_date(value)
                        item["user_date"] = value
                    elif key == u'购买裸车价':
                        item["user_price"] = value
                    elif key == u'购买目的':
                        item["user_intent"] = value
                    elif key == u'空间':
                        score = {}
                        score[u'空间'] = value
                        user_score.append(score)
                    elif key == u'动力':
                        score = {}
                        score[u'动力'] = value
                        user_score.append(score)
                    elif key == u'操控':
                        score = {}
                        score[u'操控'] = value
                        user_score.append(score)
                    elif key == u'油耗':
                        score = {}
                        score[u'油耗'] = value
                        user_score.append(score)
                    elif key == u'舒适性':
                        score = {}
                        score[u'舒适性'] = value
                        user_score.append(score)
                    elif key == u'外观':
                        score = {}
                        score[u'外观'] = value
                        user_score.append(score)
                    elif key == u'内饰':
                        score = {}
                        score[u'内饰'] = value
                        user_score.append(score)
                    elif key == u'性价比':
                        score = {}
                        score[u'性价比'] = value
                        user_score.append(score)
            item['user_score'] = user_score
            return item

        except:
            self.logging.error("layer 4 failed:  url is:(%s), error info is:(%s)" \
                           % ( response.url, traceback.format_exc()))
