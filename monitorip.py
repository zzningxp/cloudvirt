#!/usr/bin/python
import logging, time, threading

import libvirt, sys, os, re, time
import libMysqlMacIP, libMysqlHost, libThreading

workpath = "/root/cloudvirt/"

def getdhcp(logger):
    plist = []
    filename = "%sdhcp-list.dat" % workpath
    f = open(filename, 'r')
    plist = f.readlines()
    for i in range(len(plist)):
        plist[i] = plist[i][0:plist[i].find('\n')]
    f.close()

    macip = {}
    for pid in plist:
        tmpfile = os.popen("ssh %s cat /var/lib/dhcpd/dhcpd.leases" % pid)
        tmpstr = tmpfile.read()
        strlist = re.split('lease',tmpstr)
        for str in strlist:
            ip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',str)
            if ip is not None:
                mac = re.search('..:..:..:..:..:..',str)
                if mac is not None:
                    macip[mac.group()] = ip.group()
    return macip

def getarping(logger):
    #getips(logger)
    ipranges = ['10.0.1'] 
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
    #dhcpinfo = getdhcp(logger)
    dhcpinfo = getarping(logger)
    macip = libMysqlMacIP.MacIPs()
    for mac in dhcpinfo.keys():
        ip = macip.getip(mac)
        if ip:
            if ip != dhcpinfo[mac]:
                macip.update_tuples([(macip.col_mac, mac)],[(macip.col_ip, dhcpinfo[mac])])
        else:
            macip.insert([(macip.col_mac, mac),(macip.col_ip, dhcpinfo[mac])])

