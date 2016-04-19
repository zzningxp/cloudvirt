#!/usr/bin/env python

import os, sys, random, re, threading, time, libThreading

workpath = "/var/run/cloudvirt/vm/"
imagepath = "/var/run/cloudvirt/image/"
logpath = "/var/log/cloudvirt/"
installpath = "/usr/share/cloudvirt"
dlport = 8773
concurrent = 2


def dispatch_nv_thread(n, imageid):
    os.system('ssh %s mkdir -p %s' % (n, installpath))
    os.system("scp nv-* %s:%s 1>/dev/null" % (n, installpath))
    os.system("scp libFileCheck.py %s:%s 1>/dev/null" % (n, installpath))
    os.system("scp libHTTPServer.py %s:%s 1>/dev/null" % (n, installpath))
    os.system("ssh %s mkdir -p %s" % (n, imagepath))
    os.system("ssh %s %s/nv-prepare-image %s %s %s %s %s &" % (n, installpath, n, dlport, imagepath, concurrent, logpath))

def dispatch_nv(nodes, headnode, imageid):
    os.system("./nv-prepare-image %s %s %s %s %s &" % (headnode, dlport, imagepath, concurrent, logpath))
    ts = libThreading.threads()
    thr = []
    for n in nodes:
        thr.append((dispatch_nv_thread, n, imageid))
    ts.set_func_list(thr)
    ts.start()
    
def check_nodes_threading(n, headnode, imageid, imagename, checksum, imagesize):
    img_status = os.system('ssh %s ls -l %s/%s/%s 1>/dev/null 2>/dev/null' %(n, imagepath, imageid, imagename))
    if img_status == 0:
        check_status = os.system('ssh %s %s/nv-filechecker %s/%s/%s %s %s' % (n, installpath, imagepath, imageid, imagename, checksum, imagesize))
        return check_status == 0
    else:
        return False

def check_nodes(nodes, headnode, imageid, imagename, checksum, imagesize):
    ts = libThreading.threads()
    thr = []
    for n in nodes:
        thr.append((check_nodes_threading, n, headnode, imageid, imagename, checksum, imagesize))
    ts.set_func_list(thr)
    ts.start()
    ret = ts.get_return()

    newnodes = []
    for key in ret.keys():
        if not ret[key]:
            newnodes.append(nodes[key])
        else:
            print '%s already have this Image' % (nodes[key])
    return newnodes

def wgetimage(client, server, imageid, imagename, path):
    os.system('ssh %s mkdir -p %s/%s' % (client, path, imageid))
    dlfile = os.path.normpath('%s/%s' % (imageid, imagename))
    svfile = os.path.normpath('%s/%s/%s' % (path, imageid, imagename))
    cmd = 'ssh %s wget http://%s:%d/%s -O %s -q' % (client, server, dlport, dlfile, svfile)
    print cmd, 'Started %s' % time.strftime("%H:%M:%S")
    ret =  os.system(cmd)
    if ret == 0:
        print cmd, 'Finished %s' % time.strftime("%H:%M:%S")
    else:
        print cmd, 'Error'

def dispatch_image(nodes, headnode, imageid, imagename):
    serverlist = []
    serverlist.append(headnode)
    clientlist = []

    while len(serverlist) < len(nodes) + 1:
        servernum = len(serverlist)
        clientlist = nodes[servernum - 1 : servernum * (1 + concurrent) - 1]
        thr = []
        for i in range(len(clientlist)):
            thr.append(threading.Thread(target=wgetimage, \
                args=(clientlist[i], serverlist[i - servernum], imageid, imagename, imagepath)))
        for i in range(len(clientlist)):
            thr[i].start()
        for i in range(len(clientlist)):
            thr[i].join()

        serverlist.extend(clientlist)

def local_copy_threading(pid, num, dom_list, imageid, imagename):
    for j in range(1, num):
        domname = dom_list[j]
        re = os.system('ssh %s mkdir -p %s/%s' % (pid, workpath, domname))
        re += os.system('ssh %s cp %s/%s/%s %s/%s/root' % (pid, imagepath, imageid, imagename, workpath, domname))
        if not re == 0:
            return 1

    domname = dom_list[0]
    re = os.system('ssh %s mkdir -p %s/%s' % (pid, workpath, domname))
    re += os.system('ssh %s mv %s/%s/%s %s/%s/root' % (pid, imagepath, imageid, imagename, workpath, domname))
    if not re == 0:
        return 1
    return 0
    
def local_copy(nodes, num, imageid, imagename, instance_names):
    ts = libThreading.threads()
    thr = []
    for i, pid in enumerate(nodes):
        thr.append((local_copy_threading, pid, num[i], instance_names[i], imageid, imagename))
    ts.set_func_list(thr)
    ts.start()
   
