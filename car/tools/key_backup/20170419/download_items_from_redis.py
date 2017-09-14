# -*- coding: utf-8 -*-

import json
import sys
import os
import re
import time
import datetime
import codecs
import redis
import traceback
import multiprocessing
from supplier.utils import init_logger
from supplier.utils import get_redis_svr_par
from scrapy_redis.defaults import PIPELINE_KEY
import urllib
import hashlib
#import chardet

logger = init_logger("download_items", "download_items.log")
#prefix_img_path = "ret/img"
#prefix_item_path = "ret/data"
prefix_img_path = "supplier/ret/img"
prefix_item_path = "supplier/ret/data"

# redis client参数用作全局变量
redis_srv = None
redis_key = None

def md5(addStr):
	m = hashlib.md5()
	m.update(addStr)
	return m.hexdigest()

    
def download_image(img_path, url):
    """
        下载url对应的图片，重命名后保存到img_path路径下，并返回重命名后的图片名字
    """
    img_name = "%s/%s.jpg" % (img_path, md5(url))
    retry_num = 0
    while retry_num < 3 :
        try:
            data = urllib.urlopen(url).read()
            break
        except IOError,e:
            retry_num += 1
            logger.error('failed to download image, retry_num:%d reason:%s' % (retry_num, str(e)))
    if retry_num >= 3:
        return "download_image_error"
    else:
        f = file(img_name, "wb")
        f.write(data)
        f.close()
        return img_name

        
def download_items(redis_srv, redis_key, img_path, limit=1, timeout=5, wait=.1):
    """
        从redis中下载默认20条items后返回该20条结果
        redis_srv: redis client对象
        timeout: 一次pop请求的超时时间
        wait: 未获取到信息时的等待时间
    """
    ret = []
    processed = 0
    while processed < limit:
        # Change ``blpop`` to ``brpop`` to process as LIFO.
        r = redis_srv.blpop(redis_key, timeout)
        if r is None:
            time.sleep(wait)
            continue
        source, data = r
        try:
            #print "tpf:", data
            data = re.sub(ur'\\r+', " ", data)
            data = re.sub(ur'\\n+', " ", data)
            data = re.sub(ur'\\t+', " ", data)
            data = re.sub('[ ]+', " ", data)
            #print 'after:', data
            item = json.loads(data)
        except Exception:
            logger.error("failed to load item:%s", data)
            continue
        
        if not isinstance(item, dict):
            logger.error("item type error(not dict):%s", item)
            continue

        company_name = item.get('company_name')
        company_url = item.get('company_url')
        logger.info("[%s] Processing item: %s <%s>", source, company_name, company_url)
        
        #下载图片，重命名后保存到img_path路径下，并返回重命名后的图片名字
        company_image = item.get('company_image')
        if company_image is not None and company_image != "":
            img_name = download_image(img_path, company_image)
            # todo:图片下载失败暂时置为"download_image_error"
            item['company_image'] = img_name
            
        ret.append(item)
        processed += 1
    return ret


def do_multi_processing_logic(spider_name, save_type, process_seq, img_path, item_data_path):
    redis_srv_par = get_redis_svr_par()
    redis_srv = redis.StrictRedis(**redis_srv_par)
    redis_key = PIPELINE_KEY % {"spider":spider_name}
    logger.info("[process id %d] start to download items in '%s' (server: %s, port: %s)", process_seq, redis_key, 
        redis_srv_par.get('host') if redis_srv_par.get('host') else 'localhost',
        redis_srv_par.get('port') if redis_srv_par.get('port') else '6379')
    
    if save_type != 'file':
        print "parameter(%s) error" % save_type
        return
    
    # 设置具体要保存的文件格式为 当前系统时间/spider_name _ process_seq.json
    item_data_file = "%s/%s_%s.json" % (item_data_path, spider_name, str(process_seq))
    
    file = codecs.open(item_data_file,"a+",encoding="utf-8")
    while True:
        items = download_items(redis_srv, redis_key, img_path)
        for item in items:
            item_len = len(item)
            cnt = 0
            file.write("{")
            for k, v in item.items():
                cnt += 1
                if cnt == item_len:
                    file.write("\"%s\": \"%s\"" % (k, re.sub("\"", "\\\"", v) if v is not None else v))
                    break
                file.write("\"%s\": \"%s\", " % (k, re.sub("\"", "\\\"", v) if v is not None else v))
            file.write("}\n")
        file.flush()
    # items = download_items(redis_srv, redis_key, img_path)
    # for item in items:
        # item_len = len(item)
        # cnt = 0
        # file.write("{")
        # for k, v in item.items():
            # cnt += 1
            # if cnt == item_len:
                # file.write("\"%s\": \"%s\"" % (k, re.sub("\"", "\\\"", v)))
                # break
            # file.write("\"%s\": \"%s\", " % (k, re.sub("\"", "\\\"", v)))
        # file.write("}\n")
    file.close()
    
        
def main():
    """
        save_type 目前只能取'file'（保存到文件）或者'mysql'（保存到mysql）
    """
    if len(sys.argv) != 4:
        print "parameter num(%d) error" % len(sys.argv)
        return 1
        
    spider_name = sys.argv[1]
    process_num = int(sys.argv[2])
    save_type = sys.argv[3]
    
    # global redis_srv, redis_key
    # redis_srv_par = get_redis_svr_par()
    # redis_srv = redis.StrictRedis(**redis_srv_par)
    # redis_key = PIPELINE_KEY % {"spider":spider_name}

    # logger.info("start to download items in '%s' (server: %s, port: %s)", redis_key, 
        # redis_srv_par.get('host') if redis_srv_par.get('host') else 'localhost',
        # redis_srv_par.get('port') if redis_srv_par.get('port') else '6379')

    # todo: 该设置放在进程之外做，放到进程之中需要加锁，目前传入锁参数会出错
    # 设置图片保存到本地的路径，格式为 当前系统时间/spider_name
    now_time = datetime.datetime.now().strftime("%Y%m%d")
    img_path = "%s/%s/%s" % (prefix_img_path, now_time, spider_name)
    img_path_out = "%s/%s" % (prefix_img_path, now_time)
    if not os.path.exists(img_path_out): #路径只能一层一层的创建
        os.mkdir(img_path_out)
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    # 设置items结果保存到本地的路径
    item_data_path = "%s/%s" % (prefix_item_path, now_time)
    if not os.path.exists(item_data_path):
        os.mkdir(item_data_path)
        
    processes_list = []
    try:
        for i in range(process_num):
            #print [spider_name, save_type, i]
            # 注意点：multiprocessing.Process传入参数时，如果传入的是这种参数StrictRedis<ConnectionPool<Connection<host=localhost,port=6379,db=0>>>
            # 一定会出错，还不好查明原因，本处暂不传入redis_srv参数
            process = multiprocessing.Process(target=do_multi_processing_logic, args=[spider_name, save_type, i, img_path, item_data_path])
            process.start()
            processes_list.append(process)

        #等待所有进程完成
        for p in processes_list:
            p.join()
        retcode = 0  # ok
    except Exception, e:
        traceback.print_exc()
        e_str = traceback.format_exc()
        logger.error("Unhandled exception:%s" % e_str)
        retcode = 2

    return retcode


if __name__ == '__main__':
    #print 
    """
        help info:
            python download_items_from_redis.py spider_name thread_num save_type
            spider_name 爬虫名字
            thread_num 进程数量
            save_type 结构保存到哪里，save_type='file'保存到文件，save_type='mysql'保存到mysql
    """
    sys.exit(main())
