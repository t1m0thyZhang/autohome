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
from car.utils import init_logger
from car.utils import get_redis_svr_par
from scrapy_redis.defaults import PIPELINE_KEY


now_date = datetime.datetime.now().strftime("%H%M")  #20170523
log_fileName = "download_items_" + now_date + ".log"
log_path = "download_items"
logger = init_logger(log_path, log_fileName)
prefix_img_path = "car/ret/img"
prefix_item_path = "car/ret/data"

# redis client参数用作全局变量
redis_srv = None
redis_key = None


# list套dict结构如[{}]转str
def list_dict_to_str(list_dict):
    str = '['
    for i in range(len(list_dict)):
        dict = list_dict[i]
        k = dict.keys()[0]
        v = dict.values()[0]
        str = str + '{\"' + k + '\":\"' + v + '\"}'
        if i != (len(list_dict)-1):
            str += ','
    str += ']'
    return str


def download_items(redis_srv, redis_key, img_path, limit=1, timeout=10, wait=.1):
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
            data = re.sub(ur'\\r+', " ", data)
            data = re.sub(ur'\\n+', " ", data)
            data = re.sub(ur'\\t+', " ", data)
            data = re.sub('[ ]+', " ", data)
            item = json.loads(data)
        except Exception:
            logger.error("failed to load item:%s", data)
            print "failed to load item:%s", data
            continue
        
        if not isinstance(item, dict):
            logger.error("item type error(not dict):%s", item)
            continue

        title = item.get('title')
        url = item.get('url')
        print "[%s] Processing item ",source
        logger.info("[%s] Processing item: %s <%s>", source, title, url)
            
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
    item_data_file = "%s/%s_%s_%s.json" % (item_data_path, spider_name, now_date, str(process_seq))
    
    file = codecs.open(item_data_file,"a+",encoding="utf-8")
    while True:
        items = download_items(redis_srv, redis_key, img_path)
        for item in items:
            item_len = len(item)
            cnt = 0
            file.write("{")
            for k, v in item.items():
                cnt += 1
                # list最后一个对象，不要','
                if cnt == item_len:
                    if k == "user_score":  # v = [{'1': u'http://www.cinn.cn:8888/shtml/zggyb/20170725/m_B3_1.jpg'}]
                        str_v = list_dict_to_str(v)
                        str_tmp = "\"%s\": %s" % (k, str_v)
                        file.write(str_tmp)
                    else:
                        file.write("\"%s\": \"%s\"" % (k, re.sub("\"", "\\\"", v) if v is not None else v))
                    break
                # list前面的每个以','结尾
                else:
                    if k == "user_score":
                        str_v = list_dict_to_str(v)
                        str_tmp = "\"%s\": %s," % (k, str_v)
                        file.write(str_tmp)
                    else:
                        file.write("\"%s\": \"%s\"," % (k, re.sub("\"", "\\\"", v) if v is not None else v))
            file.write("}\n")
        file.flush()
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
    # 设置items结果保存到本地的路径
    now_time = datetime.datetime.now().strftime("%Y%m%d")
    item_data_path = "%s/%s" % (prefix_item_path, now_time)
    if not os.path.exists(item_data_path):
        os.mkdir(item_data_path)
    processes_list = []
    try:
        for i in range(process_num):
            process = multiprocessing.Process(target=do_multi_processing_logic, args=[spider_name, save_type, i, None, item_data_path])
            process.start()
            processes_list.append(process)
        # 等待所有进程完成
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
    """
        help info:
            python download_items_from_redis.py spider_name thread_num save_type
            spider_name 爬虫名字
            thread_num 进程数量
            save_type 结构保存到哪里，save_type='file'保存到文件，save_type='mysql'保存到mysql
    """
    sys.exit(main())
