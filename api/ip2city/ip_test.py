#!/usr/bin/env python
# -*- coding: utf-8 -*-

# code from https://github.com/17mon/python
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import os
import random
import socket
import struct
import time

from ipip import IP

IP.load(os.path.abspath("../../insurance/data/17monipdb20170909.dat"))

begin = time.time()

for n in range(1000):
    ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
    city = IP.find(ip)
# if city:
# print city[0]
cost = time.time() - begin
print 'cost===:', cost

city = IP.find('222.175.96.1')
print ','.join(city)
city = IP.find('36.149.244.81')
print ','.join(city)
city = IP.find('27.187.54.201')
print ','.join(city)
print ','.join(IP.find('171.82.163.120'))
print ','.join(IP.find('124.160.213.235'))

#
# IPX.load(os.path.abspath("./17monipdb.dat"))
# print IPX.find("118.28.8.8")
