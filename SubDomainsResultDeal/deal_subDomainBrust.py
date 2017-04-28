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
from requests import get
import time
from colorama import *
from Queue import Queue
from requests import head


pattern_subDomains = re.compile(r"(\S+)\s+(.*)")
pattern_layer = re.compile(r"(\S+)\t(\S+).*")


url_queue = Queue()
queue_out = Queue()
IP = []
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s**%(threadName)s**:\t %(message)s')#输出格式
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
                url_valid = connect(url)
                if url_valid:
                    self.queue_out.put(url)
            except Exception as e:
                logging.warn(e)
                break

"""
@param url: string,
对传入的参数做访问，如果是可以访问的，就返url,
如果不可以访问，就返回None.
为了时间快这里用的是head方法
"""
def connect( url):
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



"""

解析
"""
def parseArg():
    # 暂不支持同时subDomainsBrute和layer

    parser = argparse.ArgumentParser()
    # group = parser.add_mutually_exclusive_group()
    # group.add_argument("--subDB", help="Input Your fileName to Deal. from subDomainsBrute")
    # group.add_argument("--layer_all", help="input file format is layer all")
    parser.add_argument("file", nargs='+' ,help="file export from subDomainsBrute or Layer")
    parser.add_argument("-ou", "--outurl", help=("Output file to save url,"
                                "if use same file, output will append at the end. default: out_{date}_url.txt"))
    parser.add_argument("-oi", "--outip", help="Output file to save ip, dafult: out_{date}_ip.txt")
    parser.add_argument("-t", "--thread", type=int, default=100, help="thread number, default 100")
    # parser.add_argument("--layer", help="input file format is layer domains, only contains sub")
    
    args = parser.parse_args()
    return args
    # if args.layer is None and args.layer_all is None and args.subDB is None:
    #     parser.print_usage()
    #     sys.exit(0)
    # else:
    #     return args




"""
通过正则来匹配域名和Ip
"""

def format_txt(input_file, pattern):
    global IP
    global url_queue
    _url_list = []
    tmp_ip = set()
    with open(input_file, "r") as fp:
        for line in fp:
            matchs =  pattern.match(line)
            if matchs:
                url = matchs.groups()[0]
                ip = matchs.groups()[1]
                ip = ip.split(",")
                for _ in ip:
                    tmp_ip.add(_.strip())

                _url_list.append(url.strip()) # 删除后边的空格与回车
    IP.extend(list(tmp_ip))
    _url_list = list(set(_url_list))
    for url in _url_list:
        url_queue.put(url)
    # return (self.queue, self.IP)



"""
@param ip_filename: 保存处理后的IP
@param IP:  IP数组
"""
def save_dealed_ip(outip, IP):
    with open(outip, "a") as fp:
        for ip in set(IP):
            fp.write(ip.strip() + "\n")
    logging.info("Ip 已经写完！")
    net_split(outip)


"""
写前10个C段
"""
def net_split(ip_file):
    net = {}
    if not (os.path.exists(ip_file) and os.path.isfile(ip_file)):
        logging.info(Fore.RED + "ip file doesn't exist or it's not a file" + Style.RESET_ALL)
        return 
    with open(ip_file, "r") as f:
        for line in f:
            line = line.strip()
            if line[:line.index(".")] in ["127", "10", "192", "172", "1"]:
                continue
            else:
                tmp = line[:line.rindex(".")]
                if tmp in net:
                    net[tmp] += 1
                else:
                    net[tmp] = 1


    net = sorted(net.items(), lambda x,y:cmp(x[1], y[1]), reverse=True)
    # print net, len(net)
    # 如果大于5， 取前5， 如果小于5， 取全部
    if len(net) > 10:
        result = net[:10]
    else:
        result = net

    suffix = ".1/24"
    save_file = raw_input("input the filename to save:\n")
    while os.path.exists(save_file):
        print "This file already exist, please input anthor:\n"
        save_file = raw_input(">>>>")
    with open(save_file, "w") as f:
        for line in result:
            f.write(line[0] + suffix + "\n")
    logging.info(" Done. please ues: " +  Fore.GREEN + "whatweb --input-file={} -v --no-errors --log-xml={}".format(save_file, "your_log_file") + Style.RESET_ALL)  

def save_dealed_url(outurl, queue_out):
    count = 0
    with open(outurl, "a") as fp:
        while not queue_out.empty():
            count += 1
            fp.write(queue_out.get() + "\n")

    logging.info(Fore.GREEN + "[-]URL handled done. Total: {} useful, i.e [200, 301, 302, 404, 401]".format(count) + Style.RESET_ALL)


def main():
    args = parseArg()

    # 处理参数
    # date = time.ctime().replace(" ", "_").replace(":", "_")
    # # 仅包含域名的文件列表
    # # if args.layer:
    # #     with open(args.layer, "rb") as f:
    # #         for line in f:
    # #             url_queue.put(line.strip())

    # with open(args.file, "r") as f:
    #     line = f.readline()
    # if pattern_layer.match(line):
    #     format_txt(args.file, pattern_layer)
    # else:
    #     format_txt(args.file, pattern_subDomains)

    # if args.outip is None:
    #     # 输出文件名
    #     out_ip_fn = "out_" + date + "_ip.txt"
    # else:
    #     out_ip_fn = args.outip
    # if args.outurl is None:
    #     out_url_fn = "out_" + date + "_url.txt"
    # else:
    #     out_url_fn = args.outurl


    # # 仅保存ip
    # save_dealed_ip(out_ip_fn, IP)
    # logging.info("Thanks God. Did One Thing Right.")

    # threads = []
    # for t in xrange(args.thread):
    #     tt = dealSubDomainBrust(url_queue, queue_out)
    #     threads.append(tt)
    #     tt.start()

    # for tt in threads:
    #     if tt.is_alive():
    #         tt.join()

    # #写入URL
    # save_dealed_url(out_url_fn, queue_out)


if __name__ == '__main__':
    # main()

    a = ['http://106.38.178.36/', 'http://123.125.84.231/', ' http://106.38.178.250/', 'http://101.227.200.240/', 'http://119.188.145.87/', 'http://119.188.145.89', 'http://123.125.84.215', ' http://119.188.145.86/', 'http://211.151.156.82/', 'http://211.151.156.81/', 'http://123.125.117.220/', ' http://119.188.147.95/', 'http://119.188.147.78', 'http://211.151.156.184/', 'http://123.125.111.96/', 'http://123.125.111.90/', ' http://106.38.178.252/', 'http://202.108.14.62/', 'http://106.38.178.187/', 'http://101.227.200.33', 'http://111.206.13.173/', 'http://101.227.200.240/']
    for i in a:
        print get(i).raw
        print "-----------------------------"



