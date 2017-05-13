#!/usr/bin/env python
#coding=utf-8

import requests
import time
import sys
from bs4 import BeautifulSoup as bs
from util.parseTool import parseTool
from util.MysqlTool import MysqlTool
from Queue import Queue
import threading
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

def getisp(ip_queue, isp_queue):
    header = {
        "User-Agent" : "baiduspider",
    }
    url = "http://ip.chinaz.com/{}"
    while True:
        if ip_queue.empty():
            break
        ip = ip_queue.get()
        try:
            res = requests.get(url.format(ip), headers=header).content
            soup = bs(res, "html.parser")
            local = soup.find_all("span", attrs={"class": "Whwtdhalf w50-0"})[1]
            time.sleep(0.01)
            isp_queue.put((ip, local.text.encode("utf-8")))
        except Exception as e:
            isp_queue.put((ip, "Not Find Or Error Happend"))


def gettitle(port_queue, title_queue):
    headers = {
        "User-Agent": "baiduspider"
    }

    while True:
        if port_queue.empty():
            break
        ip, port, name, banner = port_queue.get()
        url = "http://{0}:{1}".format(ip, port)
        loc = ""
        try:
            #print url
            res = requests.get(url, headers=headers, allow_redirects=True, timeout=(3,6))
            soup = bs(res.content, "lxml")
            title = soup.find("title").text.encode("utf-8")
            if title == "":
                title = res.content[:150]
            title_queue.put((ip, port,name, banner, title))
        except KeyboardInterrupt as e:
            title_queue.put((ip, port,name, banner, ""))
        except Exception as e:
            title_queue.put((ip, port,name, banner, ""))


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
    ip_queue = Queue()
    isp_queue = Queue()
    for ip in ip_set:
        ip_queue.put(ip)
    del ip_set
    # 多线程处理isp
    threads = []
    for i in xrange(30):
        thread = threading.Thread(target=getisp, args=(ip_queue, isp_queue))
        threads.append(thread)

    for i in xrange(len(threads)):
        threads[i].start()

    for i in xrange(len(threads)):
        threads[i].join()


    while not isp_queue.empty():
        values.append(isp_queue.get())
        print "len(value):{0} \t ip:{1} \t isp:{2}".format(len(values), values[-1][0], values[-1][1])

    sql = "insert myip (ip, isp) value (%s, %s)"
    db.executemany(sql, values)

    # parse port and save it to mysql
    data = []
    port_queue = Queue()
    title_queue = Queue()
    sql_insert_port = "insert myport (ip_id, port, name, banner, http_title) value (%s, %s, %s, %s, %s)"
    # 多线程处理title
    for i in result:
        ip = i[0]
        port = i[1]
        name = i[2]
        banner = i[3]
        port_queue.put((ip, port, name, banner))

    threads = []
    for i in xrange(50):
        thread = threading.Thread(target=gettitle, args=(port_queue, title_queue))
        threads.append(thread)
    for i in xrange(len(threads)):
        threads[i].start()
    for i in xrange(len(threads)):
        threads[i].join()

    # get data from queue, and get ip_id, save it to data[]
    count = 0
    while not title_queue.empty():
        ip, port, name, banner, title = title_queue.get()
        ip_id = db.execute("select id from myip where ip = '%s' order by id desc" % ip)[0][0]
        data.append((int(ip_id), port, name, banner, title ))
        print "len(data):{0} \t ip:{1} \t title:{2}".format(len(data), ip, title)
        # count = 100 save it to database
    db.executemany(sql_insert_port, data)







    # for i in result:
    #     ip_id = db.execute("select id from myip where ip = '%s'" % i[0])[0][0]
    #     # exist = db.execute("select * from myport where ip_id = %s" % ip_id)
    #     title = ""
    #     try:
    #         title = gettitle(i[0], i[1])
    #     except Exception as e:
    #         print str(e)
    #         title = ""
    #     data.append((int(ip_id), i[1], i[2], i[3], title))
    #     print data[-1]



    # db.execute(sql)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print help
        sys.exit(0)
    filename = sys.argv[1]
    main(host, port, dbuser, dbpassword, db, filename)
