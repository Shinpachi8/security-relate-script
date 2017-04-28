#!/usr/bin/env python
# coding=utf-8


IP = []
with open("iqiyi_ip.txt", "r") as f:
    for line in f:
        IP.append(line.strip())

IP = list(set(IP))

with open("no_repeate.txt", "w") as f:
    for ip in IP:
        f.write(ip + "\r\n")

print "Done"