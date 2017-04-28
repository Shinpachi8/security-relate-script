#!/usr/bin/env python
# coding=utf-8

"""
to scan some info,include: phpinfo, backupfile, rarfile, and so on


"""
import requests
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s |%(levelname)s|\t %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

vul_list = []
with open("scan_vul.list", "rb") as f:
    for line in f:
        vul_list.append(line.strip())

def scan(url_file):
    with open(url_file, "r") as f:
        for line in f:
            url = line.strip()
            url = url if url.startswith("http") else "http://" + url
            do_scam(url)

def do_scam(url):
    for vul in vul_list:
        res = requests.get(url + vul, verify=False)
        if res.status_code in [200,]:
            logging.info(url + vul + ":\tMayBe one, MayBe not")
            content = res.content
            if "Collection of R" in content:
                logging.info(url + vul + ":\t Maybe .svn VUL.")
            if ".git" in content:
                logging.info(url + vul + ":\t Maybe .svn VUL.")
        else:
            continue


if __name__ == '__main__':
    scan("iqiyi_subDomain.txt")
    # res = requests.get("http://music.iqiyi.com")
    # print res.content
    # print res.status_code
