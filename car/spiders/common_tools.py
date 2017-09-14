# -*- coding: utf-8 -*-
# 爬虫常用代码包 since 2017-07-01 by zhangtianrui
# last modified date: 2017-07-03
import re


# -----清洗文字中的常见特殊符号-----
# input:  str（unicode is preferred）
# output: str
# note: 如果不传unicode进来去不掉；适用于处理官网产品详情，供求信息详情等;
def data_cleaning(dirty_str):
    if not isinstance(dirty_str, unicode):
        print "common_tools warning：input is not a unicode string, can not clean chinese"
    middle_str = re.sub("<.*?>", "", dirty_str) # 去html标签
    middle_str = re.sub("\n+|\t+|\r+", "", middle_str)  # 去换行符，制表符
    middle_str = re.sub(" +", " ", middle_str)  # 多个空格替换为1个空格
    user_defined_trash = '[\xa0-\xa9\xaa-\xaf]+'  # 慢慢累积会导致编码报错的字符加入到[]
    middle_str = re.sub(user_defined_trash, '', middle_str)
    trash = u'[’"#■ $%&\'()*+-/<=>★【】《》“”‘’[\\]^_`{|}~\ufb02]+'  # 去常见中文不必要符号 @不要去，有可能是邮箱
    clean_str = re.sub(trash, '', middle_str)
    return clean_str


# -----从字符串中提取出电话-----
# input:  任意字符串
# output: 13812345678 023-12345678 0573-12345678 如有多个电话号码则以'|'隔开 并去重 没找到返回none
# note: 如果不传unicode进来去不掉；适用于处理官网产品详情，供求信息详情等;
def extract_tel(any_str):
    if any_str is None or any_str == "":
        print "input is empty"
        return
    tel_tmp = re.findall("1[0-9]{10}|1[0-9\-]{11,12}|0[0-9]{10,11}|0[0-9\-]{11,12}", any_str)
    # 用set去重
    if len(tel_tmp) > 0:
        tel = set(tel_tmp)
        tel = list(tel)
        tel = "|".join(tel)
        return tel
    else:
        print 'no 11 bit tel found'


# -----从字符串中提取email address-----
# input:  任意字符串
# output: 如有多个邮箱地址则以'|'隔开 并去重 没找到返回none
# note: 如果不传unicode进来去不掉；适用于处理官网产品详情，供求信息详情等;
def extract_email(any_str):
    if any_str is None or any_str == "":
        print "input is empty"
        return
    email_tmp = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", any_str)
    # 用set去重
    if len(email_tmp) > 0:
        email = set(email_tmp)
        email = list(email)
        email = "|".join(email)
        return email
    else:
        print 'no email address found'


# -----规范化日期格式-----
# input:  17-1-2 2017-1-02 17年1月2日 2017年1月2日 2017/1/2
# output: 8位日期 2017-01-02
# note: 有中文要unicode传进来哦
def normalize_date(date):
    if r'/' in date:
        date = re.sub(r'/', '-', date)
    if u'年' in date or u'月' in date or u'日' in date:
        date = re.sub(u'年|月', '-', date)
        date = re.sub(u'日', '', date)
    ymd = date.split("-")
    year = ymd[0];
    month = ymd[1];
    day = ymd[2];
    if len(year) == 2:
        year = "20" + year
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day
    normalized_date = year + "-" + month + "-" + day
    return normalized_date

