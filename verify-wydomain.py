#!/usr/bin/env python
#coding=utf-8

import requests
import json
import sys

headers = {
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36",
        }

verified = []
def verify(urls):
    for url in urls:
        if not url.startswith("http"):
            url = "http://" + url
        (visited, new_url) = test(url)
        if visited:
            verified.append(new_url)
        else:
            print "[-] A Bad URL :< "

def test(url):
    try:
        res = requests.get(url, headers = headers, timeout=10, allow_redirects=True)
        if res.status_code == 200:
            return (True, res.url)
        else:
            return (False, "")
    except Exception, e:
        print "[-] Error Happend :< . Dont' warry, TREATE it a Bad URL."
        return (False, "")

if __name__ == '__main__':
    Usage = "python verify.py file_path"
    if len(sys.argv) != 2:
        print Usage
        sys.exit(-1)
    else:
        with open(sys.argv[1], 'r') as fp:
            urls = json.load(fp)

        verify(urls)
        verified = list(set(verified))

        with open("verified.json", "w") as fp:
            json.dump(verified, fp)
        print "[+] Thanks God, no Error Happend"


