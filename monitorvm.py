#!/usr/bin/env python
import logging, time, threading

import libvirt, sys, os, re, shelve, time
from xml.dom import minidom

workpath = '/root/cloudvirt/'
state = ['NoState','Running','Blocked','Paused ','Shutdwn','Shutoff','Crashed']
ipdb = 'db4ip.dat'
vmdb = 'db4vm.dat'

def sformat(t):
    t = re.split("\:", t)
    return int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2])

def tformat(t):
    if "days," in t:
        t = re.split("days,", t)
        return int(t[0]) * 24 * 3600 + sformat(t[1])
    elif "day," in t:
        t = re.split("day,",t)
        return int(t[0]) * 24 * 3600 + sformat(t[1])
    else:
        return sformat(t)

def getcreatetime(pid, domname):
    cmd = "ssh %s xm uptime | awk '{print $1 \" \" $3 $4 $5}'" % pid
    ut = os.popen(cmd).read()
    ut = re.split(r"\n", ut)
    ut.remove('')
    ut = ut[2:]
    for iut in ut:
        iut = re.split(" ", iut)
        if domname == iut[0]:
            return tformat(iut[1])
    return 0

def getdomains(pid, macip, logger):
    try:
        conn = libvirt.open("xen+ssh://root@%s/" % pid)
    except:
        logger.info("Lost Contection : %s" % pid)
        return

    db = shelveload(vmdb)
    dbkey = db.keys()

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
                dbname = pid + '--' + str(dom.name())
                dominfo['create_time'] = 'None'
                if dbname in dbkey:
                    dbv = db[dbname]
                    if type(dbv['create_time']) == str:
                        ct = getcreatetime(pid, dom.name())
                        if ct > 0:
                            dominfo['create_time'] = time.localtime(time.time() - ct)
                    else:
                        dominfo['create_time'] = dbv['create_time']

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
                shelvemodify(vmdb, dbname, dominfo)

def shelvecreate(datefile):
    try:
        db = shelve.open(workpath + '/' + datefile, 'c')
    finally:
        db.close()

def shelvemodify(datefile, key, value):
    try:
        db = shelve.open(workpath + '/' + datefile, 'w')
        db[key] = value
    finally:
        db.close()

def shelveload(datefile):
    ret = {}
    try:
        db = shelve.open(workpath + '/' + datefile, 'w')
        ret.update(db)
    finally:
        db.close()
    return ret

def getinstances(logger):

    shelvecreate(vmdb)
    plist = open(workpath + "/nodelist").read()
    plist = re.split(r"\n", plist)
    plist.remove('')

    macip = shelveload(ipdb)

    thr = []
    for pid in plist:
        thr.append(threading.Thread(target=getdomains, args=(pid, macip, logger)))
    for i in range(len(thr)):
        thr[i].start()

