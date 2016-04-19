#!/usr/bin/env python
import logging, time, threading

import libvirt, sys, os, re, time
import libMysqlMacIP, libMysqlInstance, libMysqlHost
from xml.dom import minidom

workpath = '/root/cloudvirt/'
state = ['NoState','Running','Blocked','Paused ','Shutdwn','Shutoff','Crashed']

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

def getdomains(pid, logger):
    try:
        conn = libvirt.open("xen+ssh://root@%s/" % pid)
    except Exception, e:
        logger.info("Lost Contection : " + pid + " " + str(e))
        return
    
    macip = libMysqlMacIP.MacIPs()
    
    for id in conn.listDomainsID():
        if id > 0:
            vminfo = {}
            dom = conn.lookupByID(id)
            try:
                x = dom.XMLDesc(0)
                ifc = minidom.parseString(x).getElementsByTagName('interface')
                mac = ifc[0].getElementsByTagName('mac')[0].attributes['address'].value.upper()
            except Exception, e:
                logger.info("Error Domain Infomation from XML Identifier: " +pid + dom.name() + str(e))
            else:
                vminfo['name'] = dom.name()
                vminfo['hostname'] = pid
                vminfo['mac'] = str(mac)
                vminfo['ip'] = macip.getip(str(mac))
                vminfo['status'] = state[dom.info()[0]]
                vminfo['update_time'] = time.localtime()
                vminfo['register_time'] = time.localtime()
                vminfo['start_time'] = time.localtime(time.time() - getcreatetime(pid, dom.name()))
                vminfo['cputime'] = dom.info()[4] / 100000000
                vminfo['vcpu'] = dom.info()[3]
                vminfo['mem'] = dom.info()[2] / 1024
                vminfo['domid'] = dom.ID()

                instc = libMysqlInstance.Instances()
                name = str(vminfo[instc.col_name])
                wheres = [(instc.col_name, name)]
                inslist = instc.select_dict_withtuples(wheres)
                if len(inslist) > 0:
                    dbinfo = inslist[0]
                    s = []
                    s.append((instc.col_update_time, vminfo[instc.col_update_time]))
                    s.append((instc.col_cputime, vminfo[instc.col_cputime]))
                    if dbinfo[instc.col_ip] != vminfo[instc.col_ip]:
                        s.append((instc.col_ip, vminfo[instc.col_ip]))
                    if dbinfo[instc.col_status] != vminfo[instc.col_status]:
                        s.append((instc.col_status, vminfo[instc.col_status]))
                    if dbinfo[instc.col_domid] != vminfo[instc.col_domid]:
                        s.append((instc.col_domid, vminfo[instc.col_domid]))
                    if dbinfo[instc.col_start_time] != vminfo[instc.col_start_time]:
                        s.append((instc.col_start_time, vminfo[instc.col_start_time]))
                    instc.update_tuples(wheres, s)
                else:
                    instc.insert_dict(vminfo)

def getinstances(logger):
    hst = libMysqlHost.Hosts()
    
    columns = [hst.col_hostid, hst.col_clustername]
    ret = hst.select(' , '.join(columns), '', '')
    
    plist = []
    for i in ret:
    	plist.append(i[0])

    thr = []
    for pid in plist:
        thr.append(threading.Thread(target=getdomains, args=(pid, logger)))
    for i in range(len(thr)):
        thr[i].start()

    instc = libMysqlInstance.Instances()
    instc.mark_dead()

