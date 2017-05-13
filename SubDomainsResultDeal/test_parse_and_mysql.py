#!/usr/bin/env python
#coding=utf-8

import requests
import time
import sys
from bs4 import BeautifulSoup as bs
from util.parseTool import parseTool
from util.MysqlTool import MysqlTool
from util.GetTitle import GetTitle
import MySQLdb as mdb
from Queue import Queue
import threading
import json
import re
import logging

logging.getLogger("requests").setLevel(logging.WARNING)

# global config

host = "127.0.0.1"
port = 3307
dbuser = "root"
dbpassword = "root"
db = "myipdb"

help =  """
        Usage:  python xx.py filename

        """

def getisp(ip_queue, isp_queue):
    header = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0",
    }
    url = "http://ip.chinaz.com/{0}"
    while True:
        if ip_queue.empty():
            break
        #print "len(ip_queue): {0}".format(ip_queue.qsize())
        ip = ip_queue.get()
        print "len(ip_queue): {0}\t ip:{1}".format(ip_queue.qsize(), ip)
        try:
            print url.format(ip)
            res = requests.get(url.format(ip), headers=header).content
            soup = bs(res, "html.parser")
            local = soup.find_all("span", attrs={"class": "Whwtdhalf w50-0"})[1]
            time.sleep(0.01)
            print local.text.encode("utf-8")
            isp_queue.put((ip, local.text.encode("utf-8")))
        except Exception as e:
            isp_queue.put((ip, "Not Find Or Error Happend"))


def gettitle(port_queue, title_queue):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0"
    }

    while port_queue.qsize() > 0:
        # if port_queue.empty():
        #     break
        ip, port, name, banner = port_queue.get()
        if str(port) == '443':
            url = "https://{0}:{1}".format(ip, port)
        else:
            url = "http://{0}:{1}".format(ip, port)
        try:
            #print url
            res = requests.get(url, headers=headers, allow_redirects=True, timeout=(3,6))
            soup = bs(res.content, "html.parser")
            title = soup.find("title").text.encode("utf-8")
            if title == "":
                title = res.content[:150]
            title_queue.put((ip, port,name, banner, title))
            print "len(port_queue):{0}\t url:{1}\t title:{2}".format(port_queue.qsize(), url, title)
        except KeyboardInterrupt as e:
            title_queue.put((ip, port,name, banner, "#"))
        except Exception as e:
            # print "[-] [Lineno]:84\t\t", str(e)
            title_queue.put((ip, port,name, banner, "#"))


def main(host, port, dbuser, dbpassword, db, filename):
    #db = MysqlTool(host, port, dbuser, dbpassword)
    #db.execute("use myipdb;")
    conn = mdb.connect(host=host, port=port, user=dbuser, passwd=dbpassword, db=db)
    cursor = conn.cursor()
    result = parseTool.parse(filename)

    # parse ip , get isp and save it to mysql
    # next version. turn it to mutithread
    # values = []
    # ip_set = set()
    # for i in result:
    #     ip = i[0]
    #     ip_set.add(ip)
    # print len(ip_set)
    # ip_queue = Queue()
    # isp_queue = Queue()
    # for ip in ip_set:
    #     ip_queue.put(ip)
    # del ip_set
    # # 多线程处理isp
    # threads = []
    # for i in xrange(60):
    #     thread = threading.Thread(target=getisp, args=(ip_queue, isp_queue))
    #     threads.append(thread)

    # for i in xrange(len(threads)):
    #     threads[i].start()

    # for i in xrange(len(threads)):
    #     if threads[i].is_alive():
    #         threads[i].join()


    # while True:
    #     if isp_queue.empty():
    #         break
    #     ip, isp = isp_queue.get()
    #     print "len(value):{0} \t ip:{1} \t isp:{2}".format((isp_queue.qsize()), ip, isp)
    #     try:
    #         count = cursor.execute("SELECT * FROM myip WHERE ip = '{0}'".format(ip))
    #         if count:
    #             tmp = cursor.fetchone()
    #             if tmp == isp:
    #                 continue
    #             else:
    #                 count = cursor.execute("UPDATE myip set isp = '%s' WHERE id=%d" %(isp, tmp[0]))
    #                 print "[+] UPDATE success!!!"
    #         else:
    #             count = cursor.execute("INSERT myip (ip, isp) value (%s, %s)", [ip, isp])
    #             print "[+] INSERT success!!!"
    #         conn.commit()
    #     except Exception as e:
    #         print str(e)
    #         conn.rollback()

       # first method
       #values.append(isp_queue.get())

       # print "len(value):{0} \t ip:{1} \t isp:{2}".format(len(values), values[-1][0], values[-1][1])

    # sql = "insert myip (ip, isp) value (%s, %s)"
    # db.executemany(sql, values)

    # parse port and save it to mysql
    data = []
    port_queue = Queue()
    title_queue = Queue()
    sql_insert_port = "insert myport (ip_id, port, name, banner, http_title) value (%s, %s, %s, %s, %s)"
    # 多线程处理title
    for i in result:
        ip = i[0]
        port = i[1]
        name = i[2].strip()
        banner = i[3].strip()
        # print (ip, port, name, banner)
        port_queue.put((ip, port, name, banner))

    threads = []
    for i in xrange(100):
        thd = GetTitle(port_queue, title_queue)
        threads.append(thd)

    for thd in threads:
        thd.start()

    for thd in threads:
        if thd.is_alive():
            thd.join()


    # get data from queue, and get ip_id, save it to data[]
    while True:
        if title_queue.empty():
            break
        ip, port, name, banner, title = title_queue.get()
        print "len(title_queue): {0}\t ip:{1}\t port:{2}\t title:{3}".format((title_queue.qsize()), ip, port, title)
        try:
            cursor.execute("SELECT id FROM myip WHERE ip = '%s' ORDER BY id DESC" % ip)
            ip_id = cursor.fetchone()[0]
            print ip_id
            count = cursor.execute("SELECT * FROM myport WHERE ip_id = %s AND port = %s", [ip_id, port])
            if count:
                cursor.execute("UPDATE myport set name=%s, banner=%s, http_title=%s WHERE ip_id=%s and port=%s", [name, banner, title, (ip_id), port])
                print "UPDATE success!!!"
            else:
                cursor.execute("INSERT myport (ip_id, port, name, banner, http_title) value (%s,%s,%s,%s,%s)", [str(ip_id), port, name, banner, title])
            conn.commit()
        except Exception as e:
            print "[-]:[Lineno]:193\t\t ", str(e)
            conn.rollback()
        except KeyboardInterrupt as e:
            print "[-] KeyboardInterrupt"
            conn.rollback

    conn.close()






if __name__ == '__main__':
    if len(sys.argv) != 2:
        print help
        sys.exit(0)
    filename = sys.argv[1]
    main(host, port, dbuser, dbpassword, db, filename)
