#!/usr/bin/env python
#coding=utf-8

import requests
import time
from bs4 import BeautifulSoup as bs
from util.parseTool import parseTool
from util.MysqlTool import MysqlTool
import json
import re
import logging

logging.getLogger("requests").setLevel(logging.WARNING)


masscan = "/Users/jiaxiaoyan/Desktop/tmp/tmp_rsync.xml"
result = (parseTool.parse_masscan(masscan))
# masscan return ip, port, name, banner

def getisp(ip):
    header = {
        "User-Agent" : "baiduspider",
    }
    url = "http://ip.chinaz.com/{}"
    try:
        res = requests.get(url.format(ip), headers=header).content
        soup = bs(res, "html.parser")
        local = soup.find_all("span", attrs={"class": "Whwtdhalf w50-0"})[1]


        time.sleep(0.1)
        return local.text
    except Exception as e:
        return ""


def gettitle(ip, port=80):
    headers = {
        "User-Agent": "baiduspider"
    }
    url = "http://{}:{}".format(ip, port)
    try:
        print url
        res = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        soup = bs(res.content, "lxml")
        title = soup.find("title").text
        return title
    except Exception as e:
        return ""


def main():
    db = MysqlTool("127.0.0.1", 3307, "root", "root")
    db.execute("use myipdb;")

    result = parseTool.parse_masscan("/Users/jiaxiaoyan/Desktop/tmp/baidu_b.xml")
    # print result[0][0]
    data = []
    sql_insert_port = "insert myport (ip_id, port, name, banner, http_title) value (%s, %s, %s, %s, %s)"
    for i in result:
        ip_id = db.execute("select id from myip where ip = '%s'" % i[0])[0][0]
        # exist = db.execute("select * from myport where ip_id = %s" % ip_id)

        title = ""
        try:
            title = gettitle(i[0], i[1])
        except Exception as e:
            print str(e)
            title = ""
        data.append((int(ip_id), i[1], i[2], i[3], title))
        print data[-1]

    db.executemany(sql_insert_port, data)

    # db.execute(sql)
    # values = []
    # ip_set = set()
    # for i in result:
    #     ip = i[0]
    #     ip_set.add(ip)
    # print len(ip_set)
    # for ip in ip_set:
    #     ip_isp = getisp(ip)
    #     values.append((ip, ip_isp))
    #     # db.execute("insert myip value ('', '%s', '%s')" % (ip, ip_isp))
    #     print "ip:{},  isp:{}".format(ip, ip_isp)
    # sql = "insert myip value (,%s, %s)"
    # db.executemany(sql, values)

if __name__ == '__main__':
    print getisp("180.76.169.198")
    main()
    select b.ip, a.port ,a.http_title from myport a join myip b on b.id=a.ip_id where a.http_title like '%百度%' or a.http_title like '%管理%' or a.http_title like '后台' or a.http_title like '%w登录%';

