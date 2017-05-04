#!/usr/bin/env python
#coding=utf-8

import requests
import time
from bs4 import BeautifulSoup as bs
from util.parseTool import parseTool
from util.MysqlTool import MysqlTool
import json
import logging

logging.getLogger("requests").setLevel(logging.WARNING)


masscan = "/Users/jiaxiaoyan/Desktop/tmp/tmp_rsync.xml"
result = (parseTool.parse_masscan(masscan))
# masscan return ip, port, name, banner

def getisp(ip):
    header = {
        "User-Agent" : "baiduspider",
    }
    url = "http://ip.taobao.com/service/getIpInfo.php?ip={}"
    res = requests.get(url.format(ip), headers=header)
    js = json.loads(res.content)
    time.sleep(0.1)
    return js["data"]["isp"].encode("utf-8")
def gettitle(ip, port=80):
    headers = {
        "User-Agent": "baiduspider"
    }
    url = "http://{}:{}".format(ip, port)
    try:
        res = requests.get(url, headers=headers, allow_redirects=True)

        soup = bs(res.content, "lxml")
        title = soup.find("title").text
        return title
    except Exception as e:
        return "Not Find"


def main():
    db = MysqlTool("127.0.0.1", 3307, "root", "root")
    db.execute("use myipdb;")

    result = parseTool.parse_masscan("/Users/jiaxiaoyan/Desktop/tmp/baidu_b.xml")
    values = []
    ip_set = set()
    for i in result:
        ip = i[0]
        ip_set.add(ip)
    print len(ip_set)
    for ip in ip_set:
        ip_isp = getisp(ip)
        values.append((ip, ip_isp))
        # db.execute("insert myip value ('', '%s', '%s')" % (ip, ip_isp))
        print "ip:{},  isp:{}".format(ip, ip_isp)
    sql = "insert myip value ('', %s, %s)"
    db.executemany(sql, data)

if __name__ == '__main__':
    # getisp("180.76.169.198")
    # gettitle("122.144.172.49")
    main()
