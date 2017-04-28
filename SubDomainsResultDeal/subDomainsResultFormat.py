# coding=utf-8

"""
format out the subdomains result, for now : support layer and subDomainsBruet

"""

import re
import threading
import sys
import argparse
import logging
import time
from FormatOutput import FormatOutput
from colorama import *
from Queue import Queue
from requests import head

logging.basicConfig(level=logging.INFO,
                    format='%(threadname)s**%(filename)s**:\t %(message)s')#输出格式
logging.getLogger("requests").setLevel(logging.WARNING)

class dealSubDomainBrust(threading.Thread):
    """docstring for ClassName"""
    def __init__(self, url_queue, queue_out):
        threading.Thread.__init__(self)
        self.queue = url_queue # 队列
        self.queue_out = queue_out

    def run(self):
        while True:
            if self.queue.empty():
                break
            try:
                url = self.queue.get_nowait()
                if not url.startswith("http"):
                    url = "http://" + url
                url_valid = check_url(url)
                if url_valid:
                    self.queue_out.put(url)
            except Exception as e:
                logging.warn(Fore.RED + str(e) + Style.RESET_ALL)
                break

"""
@param url: string,
对传入的参数做访问，如果是可以访问的，就返url,
如果不可以访问，就返回None.
为了时间快这里用的是head方法
"""
def check_url( url):
    headers = {
            "User-Agent" : ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4)"
                " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 "
                "Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
    try:
        res = head(url, headers=headers, timeout=10, verify=False, allow_redirects=True)
        
        if res.status_code == 200:
            logging.info("Checking:\t {:<30}\tres:{}".format(Fore.GREEN + url + Style.RESET_ALL, res.status_code))
            return url
        elif res.status_code in [301, 302]:
            logging.info("Checking:\t {:<30}\tres:{}".format(Fore.RED + res.url + Style.RESET_ALL, res.status_code))
            return res.url
        else:
            logging.info("Checking:\t {:<30}\tres:{}".format(Fore.YELLOW + url + Style.RESET_ALL, res.status_code))
            return None
    except Exception as e:
        # print "[-]Connect Error Happend"
        return None

def parseArg():
    # 暂不支持同时subDomainsBrute和layer

    parser = argparse.ArgumentParser()
    # group = parser.add_mutually_exclusive_group()
    # group.add_argument("--subDB", help="Input Your fileName to Deal. from subDomainsBrute")
    # group.add_argument("--layer_all", help="input file format is layer all")
    parser.add_argument("file", nargs='+', help="file export from subDomainsBrute or Layer")
    parser.add_argument("-ou", "--outurl", help=("Output file to save url,"
                                "if use same file, output will append at the end. default: out_{date}_url.txt"))
    parser.add_argument("-oi", "--outip", help="Output file to save ip, dafult: out_{date}_ip.txt")
    parser.add_argument("-t", "--thread", type=int, default=100, help="thread number, default 100")
    # parser.add_argument("--layer", help="input file format is layer domains, only contains sub")
    
    args = parser.parse_args()
    return args


def main():
    # 默认的两个匹配模式
    pattern_subDomains = re.compile(r"(\S+)\s+(.*)")
    pattern_layer = re.compile(r"(\S+)\t(\S+).*")

    # 默认的url_list, ip_list
    url_list = []
    ip_list = []

    
    # 处理参数
    date = time.ctime().replace(" ", "_").replace(":", "_")
    args = parseArg()
    for file in args.file:
        with open(file, "r") as f:
            line = f.readline()
        if pattern_layer.match(line):
            tmp_url_list, tmp_ip_list = FormatOutput.format(pattern_layer, file)
        else:
            tmp_url_list, tmp_ip_list = FormatOutput.format(pattern_subDomains, file)
            print "length:  {}".format(len(tmp_ip_list))
        url_list.extend(tmp_url_list)
        ip_list.extend(tmp_ip_list)


    if args.outip is None:
        # 输出文件名
        out_ip_fn = "out_" + date + "_ip.txt"
    else:
        out_ip_fn = args.outip
    if args.outurl is None:
        out_url_fn = "out_" + date + "_url.txt"
    else:
        out_url_fn = args.outurl


    
    # 多线程验证域名是否可访问 。
    url_queue = Queue()
    queue_out = Queue()
    for url in url_list:
        url_queue.put(url)

    threads = []
    for t in xrange(args.thread):
        tt = dealSubDomainBrust(url_queue, queue_out)
        threads.append(tt)
        tt.start()

    for tt in threads:
        if tt.is_alive():
            tt.join()

    #写入URL
    url_list = []
    while not queue_out.empty():
        url_list.append(queue_out.get())

    FormatOutput.save2file(out_url_fn, url_list)
    #仅保存ip
    print "ip_list: {}".format(ip_list)
    ip_list = list(set(ip_list))
    FormatOutput.save2file(out_ip_fn, ip_list)
    FormatOutput.net_section(out_ip_fn)

if __name__ == '__main__':
    main()





        