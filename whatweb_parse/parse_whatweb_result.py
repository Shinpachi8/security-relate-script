#!/usr/bin/env python
#coding=utf-8

"""
this script's purpos:
    to parse whatweb xml result
    find 200, 302, 404, 401
    ignor 403,500,502

"""

import os
import argparse
import re
import json
from bs4 import BeautifulSoup as bs

avilable = {
    200: set(),  # 返回值为200的
    901: set(),  # 返回值为200，但是是nginx/tengine的欢迎界面的
    301: set(),  # 返回值为301、302的
    401: set(),  # 返回值为401的
    404: set()   # 返回值为404的
}

nginx_pattern = re.compile(r".*(<string>Welcome to (nginx|[T|t]engine)!</string>).*", re.S)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="input result path, witch contains xml format file")
    parser.add_argument("-f", "--file", help="input a single xml file")
    parser.add_argument("-o", "--outfile", help="ouput file, default result.json")
    args = parser.parse_args()

    if args.path is None and args.file is None:
        print "[-] There Must Be One Input Format, Either path or file"
        parser.print_usage()
        exit(-1)
    if args.path and args.file:
        print "[-] There Must Be One Input Format, Either path or file"
        parser.print_usage()
        exit(-1)

    return args


def parse_folder(folder):
    path, folder, files = os.walk(folder).next()
    result_files = []
    for file in files:
        if file.endswith("xml"):
            result_files.append(os.path.join(path, file))
    # print result_files
    for file in result_files:
        parse_result(file)
        print "[+] Parse File: {} \tDone".format(file)

def parse_result(file):
    # print file\
    global avilable
    global nginx_pattern
    with open(file, "rb") as f:
        content = f.read()

    soup = bs(content, "xml")
    targets = soup.find_all("target")

    
    for target in targets:
        http_status = target.find("http-status").text
        if http_status in ["301", "302"]:
            avilable[301].add(target.uri.text)
        if http_status == "401":
            avilable[401].add(target.uri.text)
        if http_status == "200":
            # judge if find welcome to nginx
            plugins = target.find_all("plugin")
            nginx_flag = False
            for plugin in plugins[::-1]:
                if nginx_pattern.match(str(plugin)):
                    avilable[901].add(target.uri.text)
                    nginx_flag = True
                    break

            if not nginx_flag:
                avilable[200].add(target.uri.text)
    # print avilable
def save_result(outfile):
    global avilable
    for i in avilable.keys():
        avilable[i] = list(avilable[i])
    
    with open(outfile, "wb") as f:
        json.dump(avilable, f)


def main():
    args = parse_args()

    if args.outfile is None:
        outfile = "result.json"
    else:
        outfile = args.outfile

    if args.path:
        folder = args.path
        parse_folder(folder)
    if args.file:
        file = args.file
        parse_result(file)

    save_result(outfile)





if __name__ == '__main__':
    main()
    # parse_folder("E:\\target\\iqiyi\\whatweb\\iqiyi")
    # save_result()