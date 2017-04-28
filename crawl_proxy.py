#!/usr/bin/env python
#coding=utf-8



import requests
import threading
import time
from Queue import Queue
from bs4 import BeautifulSoup

"""
@author shinpachi8
@date   17/04/07
@describe

从西刺代理(IP84)上爬160页的代理 ，并用100个线程去验证
最后结果写入valid_proxy.txt

"""
inqueue = Queue()
outqueue = Queue()

def xici_crawl():
    # of = open('xici_proxy.txt' , 'w')
    headers = {
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"
    }

    for page in range(1, 160):
        try:
            html_doc = requests.get('http://www.xici.net.co/nn/' + str(page), headers=headers ).content
            soup = BeautifulSoup(html_doc, "lxml")
            trs = soup.find('table', id='ip_list').find_all('tr')
            for tr in trs[1:]:
                tds = tr.find_all('td')
                ip = tds[1].text.strip()
                port = tds[2].text.strip()
                protocol = tds[5].text.strip()
                if protocol == 'HTTP' or protocol == 'HTTPS':
                    inqueue.put('%s=%s:%s\n' % (protocol, ip, port))
                    # of.write('%s=%s:%s\n' % (protocol, ip, port) )
                    print '%s=%s:%s' % (protocol, ip, port)
        except Exception as e:
            break

    # of.close()

"""
# 这个代理的质量不好
def ip84_crawl():
    of = open('ip84_proxy.txt' , 'w')
    headers = {
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"
    }

    for page in range(1, 160):
        html_doc = requests.get('http://123.57.213.19/dlgn/' + str(page), headers=headers ).content
        soup = BeautifulSoup(html_doc, "lxml")
        trs = soup.find('table', attrs={"class":"list"}).find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            protocol = tds[4].text.strip()
            if protocol == 'HTTP' or protocol == 'HTTPS':
                of.write('%s=%s:%s\n' % (protocol, ip, port) )
                print '%s=%s:%s' % (protocol, ip, port)

    of.close()
"""
def test():

    while not inqueue.empty():
        proxy_line = inqueue.get()
        protocol, proxy = proxy_line.split("=")
        pr = {protocol.lower(): protocol.lower() + "://" + proxy.strip(),}
        # print pr
        try:
            # 延时5s
            res = requests.get("http://1212.ip138.com/ic.asp", headers=headers, timeout=5.0, proxies=pr)
            if proxy.split(":")[0] in res.content:
            # lock.acquire()
                print proxy + "[ok!]"
                outqueue.put(protocol + "://" + proxy)
            # lock.release()
        except Exception, e:
            pass


crawl_time = time.time()
xici_crawl()
print "[+] Crawl Proxy Done. Use :\t {} s".format((time.time() - crawl_time) / 1000)

print "[+] Now Start Test Valid....."

threads = []
valid_time = time.time()
for i in range(100):
    t = threading.Thread(target=test)
    threads.append(t)
    t.start()

for thread in threads:
    thread.join()


with open("valid_proxy.txt", "a") as fp:
    while not outqueue.empty():
        fp.write(outqueue.get() + "\r\n")

valid_end = time.time()
print "[+] Test Valid Use :\t {}s".format((valid_end - valid_time) / 1000)
print "[*Done]"


