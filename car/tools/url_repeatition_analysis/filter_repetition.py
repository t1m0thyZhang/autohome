# -*- coding: utf-8 -*-

import time
import os
import sys
import re
import json
import codecs
import traceback


def filter(file):
    unique_urls = set([])
    fw_filter = open("%s_filter_repetition" % file, 'w')
    fw_diffurls = open("%s_diff_urls" % file, 'w')
    fw_repeat_urls = open("%s_repeat_urls" % file, 'w')
    
    repeat_cnt = {}
    repeat_num = 0
    
    line_cnt = 0
    with open(file) as fr:
        for line in fr:
            line_cnt += 1
            r = line.strip()
            try:
                tmp = json.loads(r)
                url = tmp['company_url']
            except:
                #traceback.print_exc()
                #print 'formation error:', r
                
                # todo: 已经替换过"了为啥loads还会失败，但是在json在线格式中检验过格式是Ok的了
                # done: 文字中有此类不正常的字符，去除\，例如：公司秉承\'顾客至上，锐意进取\'的经营理念，坚持\'客户\'的原则
                #       或者例如：1月3日新年伊始,一场大雪让杭城\x26quot;雪舞飞扬\x26quot
                #     去除\符号时会将\"变为"，所以 将字符串中的"替换为\" 放在后面去
                r = re.sub("\\r", "", r)
                r = re.sub("\\n", "", r)
                r = re.sub(u"\\\\", "", r)
                r = re.sub("\\\\x26", "&", r)
                
                s_pos = r.find('company_description') + 23
                e_pos = r.find('", "company_url"')
                #print 's_pos', s_pos, 'e_pos', e_pos
                #print r
                # 将字符串中的"替换为\"
                r = r[0:s_pos] + re.sub("\"", "\\\"", r[s_pos:e_pos]) + r[e_pos:]
                #print r
                try:
                    tmp = json.loads(r)
                    url = tmp['company_url']
                except:
                    traceback.print_exc()
                    s_pos = r.find('company_url') + 15
                    e_pos = r.find('", "contact": "')
                    url = r[s_pos:e_pos]
                    print 'fomation error, line_number:', line_cnt, 'url:', url
                    #break
                print 'line_number:', line_cnt
            if url in unique_urls:
                repeat_num += 1
                if repeat_cnt.__contains__(url):
                    repeat_cnt[url] += 1
                else:
                    repeat_cnt[url] = 2
                continue
            print >> fw_filter, r
            print >> fw_diffurls, url
            unique_urls.add(url)
    print 'before filter number:', line_cnt
    print 'after filter number:', len(unique_urls)
    print 'repeat number:', repeat_num
    for k, v in repeat_cnt.items():
        print >> fw_repeat_urls, "%s\t%d" % (k, v)
        
def main():
    filter(sys.argv[1])

if __name__  == "__main__":
    """
        python filter_repetition.py file
        将file文件里的记录去重，并生成去重后的文件 file_filter_repetition 和去重后的公司url文件 file_diff_urls
    """
    main()
