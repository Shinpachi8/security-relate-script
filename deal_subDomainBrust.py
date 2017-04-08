#!/usr/bin/env python
#coding=utf-8

"""
@version 1.0
@author shinpachi8
@describe
用来对lijiejie的subDomainBrust工具生成的
txt文件做处理， 即分隔开域名与IP，
并对域名进行访问，如果是200，保留
如果是301、302,那么保留跳转后的地址，
如果是其他的，不管。

"""

import re
import threading
import sys
import argparse
import logging
from Queue import Queue
from requests import head


pattern = re.compile(r"(.*\.cn|.*\.com)\s*?(.*)")
lock = threading.Lock()
url_queue = Queue()
queue_out = Queue()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s**%(threadName)s**:\t %(message)s')#输出格式




class dealSubDomainBrust(threading.Thread):
    """docstring for ClassName"""
    def __init__(self, args, url_queue, queue_out):
        threading.Thread.__init__(self)
        self.args = args
        self.queue = url_queue # 队列
        self.queue_out = queue_out

    def run(self):
        while not self.queue.empty():
            url = self.queue.get()
            if not url.startswith("http"):
                url = "http://" + url

            url_valid = self.connect(url)
            if url_valid is not None:
                # lock.acquire()
                self.queue_out.put(url)
                logging.info(url)
                # lock.release()
                self.queue.task_done()


    """
    @param url: string,
    对传入的参数做访问，如果是可以访问的，就返url,
    如果不可以访问，就返回None.
    为了时间快这里用的是head方法
    """
    def connect(self, url):
        headers = {
                "User-Agent" : ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4)"
                    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 "
                    "Safari/537.36"),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
        try:
            res = head(url, headers=headers, timeout=10)
            if res.status_code == 200:
                return url
            elif res.status_code in [301, 302]:
                return res.headers["Location"]
            else:
                return None
        except Exception as e:
            # print "[-]Connect Error Happend"
            return None






"""

解析
"""
def parseArg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input Your fileName to Deal.")
    parser.add_argument("-ou", "--outurl", help="Output file to save url")
    parser.add_argument("-oi", "--outip", help="Output file to save ip")
    parser.add_argument("-t", "--thread", type=int, default=100, help="thread number, default 100")

    args = parser.parse_args()
    if args.input is None:
        parser.print_usage()
        sys.exit(0)
    else:
        return args




"""
通过正则来匹配域名和Ip
"""

def format_txt(input_file):
    _url_list = []
    IP = []
    with open(input_file, "r") as fp:
        for line in fp:
            matchs =  pattern.match(line)
            if matchs:
                url = matchs.groups()[0]
                ip = matchs.groups()[1]
                ip = ip.split(",")
                IP.extend(ip)
                _url_list.append(url.strip()) # 删除后边的空格与回车
    IP = list(set(IP))
    _url_list = list(set(_url_list))
    for url in _url_list:
        url_queue.put(url)
    return IP
    # return (self.queue, self.IP)



"""
@param ip_filename: 保存处理后的IP
@param IP:  IP数组
"""
def save_dealed_ip(outip, IP):
    with open(outip, "w") as fp:
        for ip in IP:
            fp.write(ip.strip() + "\r\n")
    logging.info("Ip 已经写完！")

def save_dealed_url(outurl, queue_out):
    with open(outurl, "w") as fp:
        while not queue_out.empty():
            fp.write(queue_out.get() + "\r\n")

    logging.info("Thanks God. URL Done TOO")


def choice1(input_file, outurl, outip):
    ou = []
    oi = []
    with open(input_file, "r") as fp:
        for line in fp:
            matchs = pattern.match(line)
            if matchs:
                ou.append(matchs.groups()[0])
                ip = matchs.groups()[1].split(",")
                oi.extend(ip)
    ou = list(set((ou)))
    oi = list(set((oi)))

    with open(outurl, "w") as fp:
        for url in ou:
            fp.write(url + "\r\n")
    with open(outip, "w") as fp:
        for ip in oi:
            fp.write(ip.strip() + "\r\n")
    logging.info(u"客人，您的1号套餐已经就绪，请您就餐")


def main():
    args = parseArg()
    # 处理参数
    if args.outip is None:
        outip = args.input.split(".")[0] + "_ip.txt"
    else:
        outip = args.outip
    if args.outurl is None:
        outurl = args.input.split(".")[0] + "_url.txt"
    else:
        outurl = args.outurl

    if args.thread is None:
        thread = 100   # 默认线程
    else:
        thread = args.thread

    while True:
        print u"只想分离URL和IP, 输入1, 想执行全过程, 输入2"
        choice = raw_input()
        if choice in ["1", "2"]:
            break
    if choice == "1":
        choice1(args.input, outurl, outip)
        sys.exit(0)
    # 单线程走一波
    # save_dealed_url(URL_QUEUE, fp)
    IP = format_txt(args.input)
    save_dealed_ip(outip, IP)
    logging.info("Thanks God. Did One Thing Right.")

    threads = []
    for t in xrange(thread):
        tt = dealSubDomainBrust(args, url_queue, queue_out)
        threads.append(tt)

    for tt in threads:
        tt.setDaemon(True)
        tt.start()

    try:
        while True:
            count = 0
            for tt in threads:
                if tt.is_alive():
                    pass
                else:
                    count += 1
            if count == thread:
                break
    except KeyboardInterrupt as e:
        logging.info("[-]Oh, U kill ME. U murderer.")


    save_dealed_url(outurl, queue_out)


if __name__ == '__main__':
    main()

