#!/usr/bin/env python
import logging, time, threading

import libvirt, sys, os, re, libshelve, time
from xml.dom import minidom

workpath = '/root/cloudvirt/'
ipdb = 'db4ip.dat'
dbpm = 'db4pm.dat'
ipranges = ['192.168.2']
ips = []

"""
def getipsthread(logger, host):
    cmd = "ssh %s \"grep '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' /var/log/messages\"" % host
    msg = os.popen(cmd).read()
    ip = re.findall('\d+\.\d+\.\d+\.\d+', msg)
    ip = list(set(ip))
    global ips
    ips.extend(ip)
    ips = list(set(ips))

def getips(logger):
    plist = libshelve.getkeys(dbpm)
    gth = []

    for i in plist:
        gth.append(threading.Thread(target=getipsthread, args=(logger, i)))
    for i in range(len(plist)):
        gth[i].start()
    for i in range(len(plist)):
        gth[i].join()

    return ips
"""

def getarping(logger):
    #getips(logger)
    
    ips = []
    for iprange in ipranges: 
        for i in range(254):
            ips.append('%s.%d' % (iprange, i))

    pingthr = []
    for ip in ips:
        pingcmd = 'ping -c 1 %s 2>/dev/null' % ip
        pingthr.append(threading.Thread(target=os.popen, args=(pingcmd,)))

    for i in range(len(pingthr)):
        pingthr[i].start()
    for i in range(len(pingthr)):
        pingthr[i].join()

    arpmap = os.popen('cat /proc/net/arp | grep : | awk \'{print $1 " " $4}\'').read()
    mi = re.split(r"\n", arpmap)
    macip = {}
    for i in mi:
        mil = re.split(" ", i)
        if len(mil) == 2:
            macip[mil[1].upper()] = mil[0]

    return macip

def updateipdb(logger):
    macip = getarping(logger)
    for k in macip.keys():
        libshelve.modify(ipdb, k, macip[k])

