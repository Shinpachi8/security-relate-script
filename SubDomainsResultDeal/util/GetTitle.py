#! /usr/bin/env python
# coding=utf-8

import threading
import re
import logging
import requests

logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO,  format='%(asctime)s %(filename)s [line:%(lineno)d] %(message)s')

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0"
    }
pattern = re.compile(r"<title>(.*)</title>")


class GetTitle(threading.Thread):
    """docstring for GetTitle"""
    def __init__(self, port_queue, title_queue):
        threading.Thread.__init__(self)
        self.port_queue = port_queue
        self.title_queue = title_queue

    def run(self):
        while True:
            if self.port_queue.empty():
                break
            ip, port, name, banner = self.port_queue.get(timeout=3)
            if str(port) == '443':
                url = "https://{0}:{1}".format(ip, port)
            else:
                url = "http://{0}:{1}".format(ip, port)

            try:
                #print url

                title = ""
                res = requests.get(url, headers=headers, allow_redirects=True, timeout=(3,6))
                matchs = pattern.findall(res.content)[0]
                if matchs:
                    title = matchs
                else:
                    title = re.content.strip()[:200]
                self.title_queue.put((ip, port,name, banner, title))
                logging.info("len(port_queue):{0}\t url:{1}\t title:{2}".format(self.port_queue.qsize(), url, title))
            except KeyboardInterrupt as e:
                self.title_queue.put((ip, port,name, banner, "#"))
                logging.error(str(e))
            except Exception as e:
                # print "[-] [Lineno]:84\t\t", str(e)
                self.title_queue.put((ip, port,name, banner, "#"))
                # logging.error(str(e))

