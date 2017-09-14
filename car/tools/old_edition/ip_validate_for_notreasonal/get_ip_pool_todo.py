#! /usr/bin/env python
# -*- coding: utf-8 -*-

import redis
import urllib2
import time
import os
import sys
import traceback
import datetime
import re

# 1、每天获取总的ip数（过滤24小时内提取过的），端口设定80 8080 8118 8123 808等
# 目前最大数量450左右
# 2、间隔十分钟左右检查所有ip是否有效，检查6次，查看6次全通的占比，5次全通的占比，以次所有占比情况
# 3、第二天再次操作步骤2，检查ip第二天的有效情况
# 4、第二天再操作步骤1和2


# 问题：当请求数变多时，会出现请求失败的问题
# =>request ip number: 1
# --> len(ips): 454
# Traceback (most recent call last):
  # File "get_ip_pool.py", line 114, in <module>
    # if redis.getScard("ipPool")>=1000:
  # File "get_ip_pool.py", line 38, in main
    # with open(ip_file) as f:
  # File "get_ip_pool.py", line 22, in get_all_ip
    # req = urllib2.Request(url)
  # File "C:\Users\tpf\AppData\Local\Continuum\Anaconda2\lib\urllib2.py", line 154, in urlopen
    # return opener.open(url, data, timeout)
  # File "C:\Users\tpf\AppData\Local\Continuum\Anaconda2\lib\urllib2.py", line 435, in open
    # response = meth(req, response)
  # File "C:\Users\tpf\AppData\Local\Continuum\Anaconda2\lib\urllib2.py", line 548, in http_response
    # 'http', request, response, code, msg, hdrs)
  # File "C:\Users\tpf\AppData\Local\Continuum\Anaconda2\lib\urllib2.py", line 473, in error
    # return self._call_chain(*args)
  # File "C:\Users\tpf\AppData\Local\Continuum\Anaconda2\lib\urllib2.py", line 407, in _call_chain
    # result = func(*args)
  # File "C:\Users\tpf\AppData\Local\Continuum\Anaconda2\lib\urllib2.py", line 556, in http_error_default
    # raise HTTPError(req.get_full_url(), code, msg, hdrs, fp)
# urllib2.HTTPError: HTTP Error 503: Service Temporarily Unavailable


def statistic():
    # 8080,3128,80,808,1080,8081,8998,8123,8888,9999,8118,9797,3129,87,8083,8090,8799,8000,9000,81,8088
    
    cnt = 0
    ips = set([])
    stime = str(datetime.datetime.now())
    st_s = time.time() # start time second
    while True:
        try:
            url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=8080,3128,80,808,1080,8081,8998,8123,8888,9999,8118,9797,3129,87,8083,8090,8799,8000,9000,81,8088&num=20"
            
            req = urllib2.Request(url)
            res_data = urllib2.urlopen(req)
            ip_ports = res_data.read().split("\r\n")
            print '=>request ip number:', len(ip_ports)
            for ip_port in ip_ports:
                if len(ip_port.split(":")) != 2:
                    print 'error ip:', ip_port
                    continue
                ips.add(ip_port)
            print '--> len(ips):', len(ips)
            if len(ips) >= 20:
                ip_pass_cnt = {}
                for ip_port in ips:
                    ip_pass_cnt[ip_port] = 0
                for id, ip_port in enumerate(ips):
                    s = "curl --connect-timeout 3 -o /dev/null -s -w %{http_code} -x "+ip_port+" https://cn.china.cn"
                    print s
                    ret_code = os.popen(s).read()
                    print ret_code, "----", id
                    if ret_code != '200':
                        continue
                    ip_pass_cnt[ip_port] += 1
                # todo: once again
                # for id, ip_port in enumerate(ips):
                    # s = "curl --connect-timeout 3 -o /dev/null -s -w %{http_code} -x "+ip_port+" https://cn.china.cn"
                    # print s
                    # ret_code = os.popen(s).read()
                    # print ret_code, "----", id
                    # if ret_code != '200':
                        # continue
                    # ip_pass_cnt[ip_port] += 1
                    
                now_time = str(datetime.datetime.now())
                now_time = re.sub("\.[\d]+", "",now_time)
                now_time = re.sub("[\:\- ]+", "",now_time)
                with open('statistic_%s.txt' % now_time, 'w') as f:
                    print >> f, "\t\t\tstart time\t%s" % stime
                    print >> f, "\t\t\tend time\t%s" % str(datetime.datetime.now())
                    print >> f, "\t\t\tcost time\t%ss" % str(time.time()-st_s)
                    # 统计出现不同次数的个数
                    pass_cnt_dict = {}
                    for k, v in ip_pass_cnt.items():
                        print >> f, "%s\t%d" % (k, v)
                        if pass_cnt_dict.__contains__(v):
                            pass_cnt_dict[v] += 1
                        else:
                            pass_cnt_dict[v] = 1
                    print >> f, '\t\t\t----------------------频次统计'
                    for k, v in pass_cnt_dict.items():
                        print >> f, "\t\t\t%s\t%d" % (k, v)
                print '===========================>', cnt
                time.sleep(30)
                cnt += 1
                ips = set([])
                stime = str(datetime.datetime.now())
                st_s = time.time()
                
        except:
            print traceback.format_exc()
            print 'protection, cnt', cnt


def main():
    statistic()
    

def get_all_ip(port, max_num=500):
    """
        至少获取1000个ip以上才停止
    """
    ips = set([])
    try:
        while True:
            #url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=8123,8118,80,8080,808&filter=on&num=30"
            #url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=8123,8118,80,8080,808&num=30"
            
            url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=%s&filter=on&num=30" % port
            #url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=%s&num=30" % port
            # url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=8118&num=30"
            # url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=80&num=30"
            # url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=8080&num=30"
            # url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=808&num=30"
            req = urllib2.Request(url)
            res_data = urllib2.urlopen(req)
            ip_ports = res_data.read().split("\r\n")
            print '=>request ip number:', len(ip_ports)
            for ip_port in ip_ports:
                ips.add(ip_port)
            print '--> len(ips):', len(ips)
            if len(ips) > max_num:
                break
            time.sleep(2)
    except:
        print traceback.format_exc()
        with open('get_all_ip_%s.txt' % port, 'w') as f:
            for one in ips:
                print >> f, one
    with open('get_all_ip_%s.txt' % port, 'w') as f:
        for one in ips:
            print >> f, one
        
def check_ip_valid(ip_file='get_all_ip.txt', retry_num=6, retry_interval=10*60, test_web="https://cn.china.cn"):
    ip_ports = set([])
    with open(ip_file) as f:
        for line in f:
            ip_ports.add(line.strip())

    print "len(ip_ports):", len(ip_ports)
    
    ip_pass_cnt = {}        
    cnt_retry_num = 0
    while cnt_retry_num < retry_num:
        for ip_port in ip_ports:
            s = "curl --connect-timeout 3 -o /dev/null -s -w %{http_code} -x " + ip_port + " " + test_web
            print s
            try:
                ret_code = os.popen(s).read()
                print ret_code
            except:
                #print s
                print 'exception occur'
                continue
            time.sleep(.5)
            if ret_code != '200':
                continue
            if ip_pass_cnt.__contains__(ip_port):
                ip_pass_cnt[ip_port] += 1
            else:
                ip_pass_cnt[ip_port] = 1
        cnt_retry_num += 1
        if cnt_retry_num < retry_num:
            time.sleep(retry_interval)
        
    with open('check_ip_valid.txt', 'w') as f:
        # 统计出现不同次数的个数
        pass_cnt_dict = {}
        for k, v in ip_pass_cnt.items():
            print >> f, "%s\t%d" % (k, v)
            if pass_cnt_dict.__contains__(v):
                pass_cnt_dict[v] += 1
            else:
                pass_cnt_dict[v] = 1
        print >> f, '\t\t\t----------------------频次统计'
        for k, v in pass_cnt_dict.items():
            print >> f, "\t\t\t%s\t%d" % (k, v)

def check_ip_valid_next(pre_file=None, ip_file='get_all_ip.txt', retry_num=6, retry_interval=10*60, test_web="https://cn.china.cn"):
    ip_ports = set([])
    with open(ip_file) as f:
        for line in f:
            ip_ports.add(line.strip())
    print "len(ip_ports):", len(ip_ports)
    
    #init ip_pass_cnt
    ip_pass_cnt = {}
    for ip_port in ip_ports:
        ip_pass_cnt[ip_port] = 0
    with open(pre_file) as f:
        for line in f:
            elems = line.rstrip('\n').split('\t')
            if len(elems) != 2:
                continue
            ip_pass_cnt[elems[0]] = int(elems[1])
    print "len(ip_pass_cnt):", len(ip_pass_cnt)
    #print 'ip_pass_cnt', ip_pass_cnt
    
    cnt_retry_num = 0
    while cnt_retry_num < retry_num:
        for ip_port in ip_ports:
            s = "curl --connect-timeout 3 -o /dev/null -s -w %{http_code} -x " + ip_port + " " + test_web
            print s
            try:
                ret_code = os.popen(s).read()
                print ret_code
            except:
                #print s
                print 'exception occur'
                continue
            time.sleep(.1)
            if ret_code != '200':
                continue
            if ip_pass_cnt.__contains__(ip_port):
                ip_pass_cnt[ip_port] += 1
            else:
                ip_pass_cnt[ip_port] = 1
        cnt_retry_num += 1
        if cnt_retry_num < retry_num:
            time.sleep(retry_interval)
        
    with open('check_ip_valid.txt', 'w') as f:
        # 统计出现不同次数的个数
        pass_cnt_dict = {}
        for k, v in ip_pass_cnt.items():
            print >> f, "%s\t%d" % (k, v)
            if pass_cnt_dict.__contains__(v):
                pass_cnt_dict[v] += 1
            else:
                pass_cnt_dict[v] = 1
        print >> f, '\t\t\t----------------------频次统计'
        for k, v in pass_cnt_dict.items():
            print >> f, "\t\t\t%s\t%d" % (k, v)
            
def _main():
    get_all_ip(sys.argv[1])
    #check_ip_valid(retry_interval=10*60)
    #check_ip_valid_next(pre_file='check_ip_valid20170410_12-14.txt', retry_interval=10*60)

def getIp(num):
    output = set([])
    cnt = 0
    for _i in range(5):
        url = "http://ttvp.daxiangip.com/ip/?tid=559436287116377&delay=1&category=2&foreign=none&ports=8123,8118,80,8080&filter=on&num=10"
        req = urllib2.Request(url)
        res_data = urllib2.urlopen(req)
        res = res_data.read().split("\r\n")
        print len(res),"------->",_i
        
        for ip_port in res:
            test = "curl --connect-timeout 3 -o /dev/null -s -w %{http_code} -x "+ip_port+" https://cn.china.cn"
            print test
            ret_code = os.popen(test).read()
            print ret_code,"----"
            if ret_code != '200':
                continue
            output.add(ip_port)
            cnt += 1
        
        time.sleep(2)
        # once again
        for ip_port in res:
            test = "curl --connect-timeout 3 -o /dev/null -s -w %{http_code} -x "+ip_port+" https://cn.china.cn"
            print test
            ret_code = os.popen(test).read()
            print ret_code,"----"
            if ret_code != '200' and ip_port in output:
                output.remove(ip_port)
                cnt -= 1
        if cnt >= num:
            break
    return output
        
def update_ip():
    try:
        redis=RedisConnect("192.168.200.116",6379,4,"mypasshahayou")
        count=redis.getScard("ipPool")
        if  not count:
            Ips=getIp(10000)
            for i in Ips:
                print "------Is insert ip :%s---------"%i
                redis.setSadd("ipPool",i)
                if redis.getScard("ipPool")>=1000:
                    break 
        else:
            ipList=redis.getSrandmember("ipPool",80)
            for i in ipList:
                test = "curl --connect-timeout 3 -o /dev/null -s -w %{http_code} -x "+i+" http://www.hc360.com/"
                print test
                output = os.popen(test)
                num =  output.read()
                print num,"----"
                if int(num) != 200 :
                    print "xxxxxxxxxxIs delete ip :%sxxxxxxxxxxx"%i
                    redis.srem("ipPool",i)

            Ipss=getIp(10000)
            m=0
            while  m < len(Ipss) :
                print  redis.getScard("ipPool")
                print "------Is update ip :%s---------"%Ipss[m]
                redis.setSadd("ipPool",Ipss[m])
                m+=1
        print "--------------------------Update Ip Success----------------------------"
        print "---------------------------Wait for the update, the next update will be in 60 seconds after the----------------------------------------------"

    except Exception,e:
        redis=RedisConnect("192.168.200.116",6379,4,"mypasshahayou")
        count=redis.getScard("ipPool")
        print e
        #Delete some ip

if __name__  == "__main__":
    main()
    #ret = getIp(20)
    #print ret