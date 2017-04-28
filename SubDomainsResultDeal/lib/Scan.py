#coding=utf-8

"""
Scan class. 
to Scan IP.

111.206.13.65
"""

from masscan import masscan
import netaddr

class Scan(object):
    """docstring for Scan"""
    # 默认的port是873, 6379,1433,1434,80,8000-9000,11211,27017-27018,64175,80-100,3389,3306
    @staticmethod
    def scan(ip, port=None, argument="oX"):
        if port is None:
            port = "873, 6379,1433,1434,80,8000-9000,11211,27017-27018,64175,80-100,3389,3306"
        mas = masscan.PortScanner()
        mas.scan(ip, port)


if __name__ == '__main__':
    Scan.scan("111.206.13.65")


