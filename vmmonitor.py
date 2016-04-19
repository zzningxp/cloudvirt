#!/usr/bin/env python
import logging, time, threading

import libvirt, sys, os, re, shelve, time
from xml.dom import minidom

workpath = '/root/cloudvirt/'
state = ['NoState','Running','Blocked','Paused ','Shutdwn','Shutoff','Crashed']

def getdomains(pid, macip, logger):
    try:
        conn = libvirt.open("xen+ssh://root@%s/" % pid)
    except:
        logger.info("Lost Contection : %s" % pid)
        return

    for id in conn.listDomainsID():
        if id > 0:
            dominfo = {}
            dom = conn.lookupByID(id)
            try:
                x = dom.XMLDesc(0)
                ifc = minidom.parseString(x).getElementsByTagName('interface')
                mac = ifc[0].getElementsByTagName('mac')[0].attributes['address'].value.upper()
            except Exception, e:
                logger.info("Error Domain Infomation from XML Identifier: " +pid + dom.name() + str(e))
            else:
                ip = macip.get(mac)
                dominfo['pm'] = pid
                dominfo['id_on_pm'] = dom.ID()
                dominfo['name'] = dom.name()
                dominfo['ip'] = ip
                dominfo['mac'] = mac
                dominfo['mem'] = dom.info()[2] / 1024
                dominfo['vcpu'] = dom.info()[3]
                dominfo['cputime'] = dom.info()[4] / 1000000000
                dominfo['status'] = state[dom.info()[0]]
                dominfo['update_time'] = time.localtime()
                shelvemodify(pid + '--' + str(dom.name()), dominfo)
 
def getinstances(logger):
    shelvecreate()
    plist = open(workpath + "/nodelist").read()
    plist = re.split(r"\n", plist)
    plist.remove('')

    mi = open(workpath + "/vmacip").read()
    mi = re.split(r"\n", mi)
    macip = {}
    for i in mi:
        mil = re.split(" ", i)
        if len(mil) == 2:
            macip[mil[1].upper()] = mil[0]

    thr = []
    for pid in plist:
        thr.append(threading.Thread(target=getdomains, args=(pid, macip, logger)))
    for i in range(len(thr)):
        thr[i].start()
    
    #    getdomains(pid, macip, logger)

def getarping(logger):
    os.system(workpath + "/arping 192.168.2 " + workpath)

def shelvecreate():
    try:
        db = shelve.open(workpath + '/db.dat', 'c')
    finally:
        db.close()

def shelvemodify(key, value):
    try:
        db = shelve.open(workpath + '/db.dat', 'w')
        db[key] = value
    finally:
        db.close()

