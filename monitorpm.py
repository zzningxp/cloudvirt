#!/usr/bin/python
import logging, time, threading, libvirt, sys, os, re, time
from xml.dom import minidom
import libMysqlHost

def getnodeinfo(pid,logger):
    try:
        conn = libvirt.open("xen+ssh://root@%s/" % pid)
    except:
        logger.info("Lost Contection : %s" % pid)
        return

    hs = libMysqlHost.Hosts()   
    ninfo = conn.getInfo()
    wheredict = {}
    wheredict[hs.col_hostid] = pid
    nodeinfo = {}
    nodeinfo['model'] = ninfo[0]
    nodeinfo['memory'] = ninfo[1]
    nodeinfo['cpus'] = ninfo[2]
    nodeinfo['mhz'] = ninfo[3]
    nodeinfo['numa_cell'] = ninfo[4]
    nodeinfo['sockets'] = ninfo[5]
    nodeinfo['cores'] = ninfo[6]
    nodeinfo['threads'] = ninfo[7]
    nodeinfo['update_time'] = time.localtime()
    hs.update_dict(wheredict, nodeinfo)

def getpms(logger):
    hs = libMysqlHost.Hosts()
    plist = hs.select(hs.col_hostid, None, None)

    thr = []
    for pid in plist:
        thr.append(threading.Thread(target=getnodeinfo, args=(pid[0], logger)))
    for i in range(len(thr)):
        thr[i].start()

