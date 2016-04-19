#!/usr/bin/env python
import logging, time, threading, libvirt, sys, os, re, libshelve, time
from xml.dom import minidom

workpath = '/root/cloudvirt/'
dbpm = 'db4pm.dat'

def getnodeinfo(pid,logger):
    try:
        conn = libvirt.open("xen+ssh://root@%s/" % pid)
    except:
        logger.info("Lost Contection : %s" % pid)
        return
    
    ninfo = conn.getInfo()
    nodeinfo = {}
    nodeinfo['model'] = ninfo[0]
    nodeinfo['memory'] = ninfo[1]
    nodeinfo['cpus'] = ninfo[2]
    nodeinfo['mhz'] = ninfo[3]
    nodeinfo['numa_cell'] = ninfo[4]
    nodeinfo['sockets'] = ninfo[5]
    nodeinfo['cores'] = ninfo[6]
    nodeinfo['threads'] = ninfo[7]
    #nodeinfo['update_time'] = time.localtime() 
    shelvemodify(pid, nodeinfo)

def getpms(logger):
    plist = libshelve.getkeys(dbpm)

    thr = []
    for pid in plist:
        thr.append(threading.Thread(target=getnodeinfo, args=(pid, logger)))
    for i in range(len(thr)):
        thr[i].start()

