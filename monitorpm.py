#!/usr/bin/env python
import logging, time, threading

import libvirt, sys, os, re, shelve, time
from xml.dom import minidom

workpath = '/root/cloudvirt/'

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

def shelvecreate():
    try:
        db = shelve.open(workpath + '/db4pm.dat', 'c')
    finally:
        db.close()

def shelvemodify(key, value):
    try:
        db = shelve.open(workpath + '/db4pm.dat', 'w')
        db[key] = value
    finally:
        db.close()

def getpms(logger):
    shelvecreate()
    plist = open(workpath + "/nodelist").read()
    plist = re.split(r"\n", plist)
    plist.remove('')

    thr = []
    for pid in plist:
        thr.append(threading.Thread(target=getnodeinfo, args=(pid, logger)))
    for i in range(len(thr)):
        thr[i].start()

