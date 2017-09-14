#! /usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import urllib2
import time
import os
import sys
import traceback
import datetime
import random
import re
from supplier.utils import init_logger
from supplier.utils import get_redis_svr_par
from supplier.settings import IP_POOL_KEY


ua_pool=["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "  
    "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",  
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "  
    "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",  
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "  
    "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",  
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "  
    "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",  
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "  
    "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",  
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "  
    "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",  
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "  
    "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",  
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",  
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",  
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",  
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",  
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",  
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",  
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",  
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "  
    "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",  
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "  
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",  
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "  
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"]
# for one in ua_pool:
    # print one

def update_ip_pool_logic(spider_name, link, logger):
    """
        1����ȡ20������ip
        2����ip�أ�����redis�У��л�ȡ����ip��¼������ļ�¼����ip port user-agent3����Ϣ(��� ip_port_ua ��3����Ϣ��һ����Ϊ�˷�ֹһ��ipƵ���任���user-agent)
            һ����¼ʾ����171.36.44.47:9797||Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36
        3����1��2��ip���Լ��߸���ip���ϲ���һ�𣬲���curl�����Ƿ�����ɹ����õ�����ɹ���ip
        4��Ϊÿ��ip���ua����ua��������ӣ��������ua����ȡ����ip�ϲ�Ϊip�ص�һ����¼ip_port_ua��������redis��
        5��sleep 30��
        6���ز���1-5
    """
    # ����redis
    redis_srv_par = get_redis_svr_par()
    redis_srv = redis.StrictRedis(**redis_srv_par)
    ip_pool_key = IP_POOL_KEY % {'name': spider_name}
    
    # �߸��ʳɹ���IP����
    high_prob_ips = set(["211.141.64.50:80", "115.29.2.139:80"])
    
    cnt = 0
    ips = set([])
    stime = str(datetime.datetime.now())
    st_s = time.time() # start time second
    while True:
        try:
            # 8080,3128,80,808,1080,8081,8998,8123,8888,9999,8118,9797,3129,87,8083,8090,8799,8000,9000,81,8088 ���ö˿ں�
            url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=8080,3128,80,808,1080,8081,8998,8123,8888,9999,8118,9797,3129,87,8083,8090,8799,8000,9000,81,8088&num=20"
            
            req = urllib2.Request(url)
            res_data = urllib2.urlopen(req)
            ip_ports = res_data.read().split("\r\n")
            print '%s|fetching raw ip number: %d' % (spider_name, len(ip_ports))
            logger.info('fetching raw (every turn) ip number: %d' % len(ip_ports))
            for ip_port in ip_ports:
                if len(ip_port.split(":")) != 2:
                    print 'error ip:', ip_port
                    logger.error('error ip: %s' % ip_port)
                    continue
                ips.add(ip_port)
            print '%s|fetching true (cumulative turn) ip number: %d' % (spider_name, len(ips))
            logger.info('fetching true (cumulative turn) ip number: %d' % len(ips))
            if len(ips) >= 20:
                # ��ip�ػ�ȡip
                ip_port_uas = redis_srv.smembers(ip_pool_key)
                ip_pool = set([])
                indexs = {} # ip��redis�м�¼������
                for id, ip_port_ua in enumerate(ip_port_uas):
                    ip = ip_port_ua.split("||")[0]
                    ip_pool.add(ip)
                    indexs[ip] = ip_port_ua
                m_ips = set( list(ip_pool) + list(ips) + list(high_prob_ips) )
                
                # ͳ�Ʋ�����ʼ��
                ip_pass_cnt = {}
                for ip_port in m_ips:
                    ip_pass_cnt[ip_port] = 0
                    
                for id, ip_port in enumerate(m_ips):
                    s = "curl --connect-timeout 3 -m 3 -o /dev/null -s -w %{http_code} -x " + ip_port + " " + link
                    print s
                    ret_code = os.popen(s).read()
                    print ret_code, "----", id
                    if ret_code != '200':
                        continue
                    ip_pass_cnt[ip_port] += 1
                
                success_num = 0.0
                for k, v in ip_pass_cnt.items():
                    logger.info("%s\t%d" % (k, v))
                    if v == 0:
                        if k in ip_pool:
                            # ɾ��redis��ʧЧ��ip
                            redis_srv.srem(ip_pool_key, indexs[k])
                        continue
                    success_num += 1
                    if k not in ip_pool:
                        # ��redis
                        ua = random.choice(ua_pool) or ""
                        redis_srv.sadd(ip_pool_key, "%s||%s" % (k, ua))
                    
                logger.info("request num( %s ), success num(%d), proportion(%f)" % (len(ip_pass_cnt), success_num, success_num/len(ip_pass_cnt)))
                logger.info("request start time(%s), end time(%s), cost time(%s)" % (stime, str(datetime.datetime.now()), str(time.time()-st_s)))
                
                print '===========================> round: %d' % cnt
                logger.info('===========================> round: %d' % cnt)
                time.sleep(30)
                cnt += 1
                ips = set([])
                stime = str(datetime.datetime.now())
                st_s = time.time()
        except redis.exceptions.ConnectionError:
            redis_srv = redis.StrictRedis(**redis_srv_par)
            logger.error('redis connection error, restart redis')
        except:
            # �����쳣ʱͨ����־��ظ��쳣
            print traceback.format_exc()
            logger.error( traceback.format_exc() )
            print 'protection, cnt', cnt
            logger.error('protection, cnt: %d' % cnt)
            break


def main():
    spider_name = sys.argv[1]
    link = sys.argv[2]
    
    # ��ʼ��log
    logger = init_logger("update_ip_pool_%s" % spider_name, "update_ip_pool_%s.log" % spider_name)
    
    print 'spider name: %s, web link: %s' % (spider_name, link)
    logger.info('spider name: %s, web link: %s' % (spider_name, link))
    update_ip_pool_logic(spider_name, link, logger)
    


if __name__  == "__main__":
    #print
    """
        help info:
            python update_ip_pool.py spider_name link
            spider_name ��������, eg. hc360
            link ��������ȡ����վ��ҳ����, eg. http://www.hc360.com/
    """
    main()
