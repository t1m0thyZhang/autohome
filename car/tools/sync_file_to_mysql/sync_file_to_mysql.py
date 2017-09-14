# -*- decoding: utf8 -*-
import json
import os
import sys
import MySQLdb
import time
import traceback
import re


if False:
    #mysql配置
    mysql_ip = "192.168.200.16"
    mysql_user = "azkaban"
    mysql_pwd = "azkaban"
    mysql_database = "test"
    table = "spider_company"
else:
    #mysql配置
    mysql_ip = "192.168.200.116"
    mysql_user = "yunsom_scm"
    mysql_pwd = "yunsom_scm.com"
    mysql_database = "yunsom_scm"
    table = "spider_company"


def execute_sql(conn, sql):
    """ 
        重连数据库
    """
    cursor = conn.cursor()
    count = 0
    try:
        count = cursor.execute(sql)
    except (AttributeError, MySQLdb.OperationalError):
        conn = MySQLdb.connect(host=mysql_ip, user=mysql_user, passwd=mysql_pwd, db=mysql_database, charset = 'utf8')
        cursor = conn.cursor()
        count = cursor.execute(sql)
    return conn, cursor, count


def sync_file_to_mysql(file):

    try:
        #连接producer数据库
        conn = MySQLdb.connect(host=mysql_ip, user=mysql_user, passwd=mysql_pwd, db=mysql_database, charset = 'utf8')
        cursor = conn.cursor()
        
        # 每500条数据往数据里insert
        interval = 500
        insert_flag = 0
        sql_para = ""
        
        repeat_num = 0
        unique_urls = set([])
        line_cnt = 0
        with open(file) as fr:
            for line in fr:
                line_cnt += 1
                r = line.strip()
                # https://baibanjinshu.cn.china.cn/company-information.html
                # 该格式错误，特殊去除html标签特殊处理
                #r = re.sub(ur'<.*?>|<p.*?>|</p>', "", r)
                try:
                    info = json.loads(r)
                    url = info['company_url']
                except:
                    # todo: 已经替换过"了为啥loads还会失败，但是在json在线格式中检验过格式是Ok的了
                    # done: 文字中有此类不正常的字符，例如：公司秉承\'顾客至上，锐意进取\'的经营理念，坚持\'客户\'的原则
                    #       或者例如：1月3日新年伊始,一场大雪让杭城\x26quot;雪舞飞扬\x26quot
                    #     去除\符号时会将\"变为"，所以 将字符串中的"替换为\" 放在后面去
                    r = re.sub("\\r", "", r)
                    r = re.sub("\\n", "", r)
                    r = re.sub(u"\\\\", "", r)
                    r = re.sub("\\\\x26", "&", r)
                    
                    s_pos = r.find('company_description') + 23
                    e_pos = r.find('", "company_url"')
                    # 将字符串中的"替换为\"
                    r = r[0:s_pos] + re.sub("\"", "\\\"", r[s_pos:e_pos]) + r[e_pos:]
                    
                    try:
                        info = json.loads(r)
                        url = info['company_url']
                    except:
                        s_pos = r.find('company_url') + 15
                        e_pos = r.find('", "contact": "')
                        url = r[s_pos:e_pos]
                        print 'fomation error, line_number:', line_cnt, 'url:', url
                        continue
                    #print 'recover, line_number:', line_cnt
                if url in unique_urls:
                    repeat_num += 1
                    continue
                unique_urls.add(url)
                
                if info.get('company_name', '') == '':
                    print 'company_name is null, line_cnt:%d' % line_cnt
                    continue
                
                # 批量插入数据库
                insert_flag += 1
                # 将字符串中的括号()替换为\(和\)，将'替换为\'
                sql_para += "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'), " \
                    % (\
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['company_name'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['company_address'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['contact'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['tel'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['establishment_date'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['registered_capital'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['registered_address'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['employees_num'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['company_description'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['company_url'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['main_business'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['business_mode'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['business_scope'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['annual_turnover'] or ''))), \
                    # re.sub('\)', '\\)', re.sub('\(', '\\(', re.sub('\'', '\\\'', info['company_image'] or ''))) \
                    re.sub('\'', '\\\'', info.get('company_name', '')), \
                    re.sub('\'', '\\\'', info.get('company_address', '')), \
                    re.sub('\'', '\\\'', info.get('contact', ''))[0:20], \
                    re.sub('\'', '\\\'', info.get('tel', '')), \
                    re.sub('\'', '\\\'', info.get('establishment_date', '')), \
                    re.sub('\'', '\\\'', info.get('registered_capital', '')), \
                    re.sub('\'', '\\\'', info.get('registered_address', '')), \
                    re.sub('\'', '\\\'', info.get('employees_num', '')), \
                    re.sub('\'', '\\\'', info.get('company_description', '')), \
                    re.sub('\'', '\\\'', info.get('company_url', '')), \
                    re.sub('\'', '\\\'', info.get('main_business', '')), \
                    re.sub('\'', '\\\'', info.get('business_mode', '')), \
                    re.sub('\'', '\\\'', info.get('business_scope', '')), \
                    re.sub('\'', '\\\'', info.get('annual_turnover', '')), \
                    re.sub('\'', '\\\'', info.get('company_image', '')) \
                    )
                if insert_flag >= interval:
                    insert_sql = "replace into %s.%s(enterprise_name, address, contact, contact_tel, establishment_date, registered_capital, registered_address, employees_num, company_description, company_url, main_business, business_mode, business_scope, annual_turnover, company_image) values %s" % (mysql_database, table, sql_para[:-2])
                    #print '======================>', insert_sql
                    conn, cursor, res_num = execute_sql(conn, insert_sql)
                    conn.commit()
                    insert_flag = 0
                    sql_para = ''
                    # break # debug
            if sql_para != '':
                insert_sql = "replace into %s.%s(enterprise_name, address, contact, contact_tel, establishment_date, registered_capital, registered_address, employees_num, company_description, company_url, main_business, business_mode, business_scope, annual_turnover, company_image) values %s" % (mysql_database, table, sql_para[:-2])
                conn, cursor, res_num = execute_sql(conn, insert_sql)
                conn.commit()
    except:
        print 'line_cnt', line_cnt
        #print '======================>', insert_sql
        print "Error: operate MySql failed "
        print traceback.format_exc()
        conn.rollback()
    # 关闭数据库连接
    cursor.close()
    conn.close()


def main():
    file = sys.argv[1]
    print "process file: %s" % file
    sync_file_to_mysql(file)


if __name__ == '__main__':
    """
        /usr/local/python2.7/bin/python sync_file_to_mysql.py file
        同步文件内容到mysql
    """
    main()


