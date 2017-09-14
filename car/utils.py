# -*- coding: utf-8 -*-
import logging
import logging.handlers
from car.settings import REDIS_PARAMS


def get_redis_svr_par():
    """
        获取redis参数信息
        usage:
            redis_srv_par = get_redis_svr_par()
    """
    # redis_srv_par = REDIS_PARAMS.copy()
    # try:
        # from product.settings import REDIS_HOST
        # redis_srv_par['host'] = REDIS_HOST
    # except:
        # pass
    # try:
        # from product.settings import REDIS_PORT
        # redis_srv_par['port'] = REDIS_PORT
    # except:
        # pass
    redis_srv_par = REDIS_PARAMS.copy() 
    return redis_srv_par
    
    
log_path = "car/logs"
def init_logger(logName, filename):
    """
        初始化日志对象
        usage:
            logger = init_logger("download_items", "download_items.log")
    """
    # 生成日志对象

    logger = logging.getLogger(logName)
    # 生成Handler
    hdlr = logging.handlers.TimedRotatingFileHandler("%s/%s" % (log_path, filename), when='D', interval=1, backupCount=5)
    hdlr.suffix = "%Y%m%d.log"  #设置切分后日志文件名
    hdlr.setFormatter(logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'))
    # add handler
    logger.addHandler(hdlr)
    # 设置日志信息输出的级别
    logger.setLevel(logging.DEBUG)
    
    return logger