#!/usr/bin/env python
#coding=utf-8

import requests
import time
import sys
from bs4 import BeautifulSoup as bs
from util.parseTool import parseTool
from util.MysqlTool import MysqlTool
import json
import re
import logging

logging.getLogger("requests").setLevel(logging.WARNING)

# global config

host = "127.0.0.1"
port = 3306
dbuser = "root"
dbpassword = ""
db = "myipdb"

help =  """
        Usage:  python xx.py filename

        """

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
    loc = ""
    try:
        #print url
        res = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        soup = bs(res.content, "lxml")
        title = soup.find("title").text.encode("utf-8")
        if title == "":
            title = res.content[:100]
        return title
    except KeyboardInterrupt as e:
        return "KeyInterrupt"
    except Exception as e:
        return "Error Happend"


def main(host, port, dbuser, dbpassword, db, filename):
    db = MysqlTool(host, port, dbuser, dbpassword)
    db.execute("use {db};".format(db=db))

    result = parseTool.parse(filename)

    # parse ip , get isp and save it to mysql
    # next version. turn it to mutithread
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
    sql = "insert myip (ip, isp) value (%s, %s)"
    db.executemany(sql, values)

    # parse port and save it to mysql
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print help
        sys.exit(0)
    filename = sys.argv[1]
    main(host, port, dbuser, dbpassword, db, filename)
