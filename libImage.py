#!/usr/bin/env python

import os, sys, random, re, threading, time, libThreading

workpath = "/var/run/cloudvirt/vm/"
imagepath = "/var/run/cloudvirt/image/"
logpath = "/var/log/cloudvirt/"
installpath = "/usr/share/cloudvirt"
dlport = 8773

def dispatch_nv_thread(n, imageid, concurrent):
    os.system('ssh %s mkdir -p %s' % (n, installpath))
    os.system("scp nv-* %s:%s 1>/dev/null" % (n, installpath))
    os.system("scp libFileCheck.py %s:%s 1>/dev/null" % (n, installpath))
    os.system("scp libHTTPServer.py %s:%s 1>/dev/null" % (n, installpath))
    os.system("ssh %s mkdir -p %s" % (n, imagepath))
    os.system("ssh %s %s/nv-kill-httpd" % (n, installpath))
    os.system("ssh %s %s/nv-prepare-image %s %s %s %s %s &" % (n, installpath, n, dlport, imagepath, concurrent, logpath))
    ## this should be running at background

def dispatch_nv(nodes, headnode, imageid, concurrent):
    dispatch_nv_thread(headnode, imageid, concurrent)
    ts = libThreading.threads()
    thr = []
    for n in nodes:
        if n != headnode:
            thr.append((dispatch_nv_thread, n, imageid, concurrent))
    ts.set_func_list(thr)
    ts.start()
 
def check_nodes_threading(n, imageid, imagename, checksum, imagesize):
    img_status = os.system('ssh %s ls -l %s/%s/%s 1>/dev/null 2>/dev/null' %(n, imagepath, imageid, imagename))
    if img_status == 0:
        check_status = os.system('ssh %s %s/nv-filechecker %s/%s/%s %s %s' % (n, installpath, imagepath, imageid, imagename, checksum, imagesize))
        return check_status == 0
    else:
        return False

def check_nodes(nodes, imageid, imagename, checksum, imagesize):
    ts = libThreading.threads()
    thr = []
    for n in nodes:
        thr.append((check_nodes_threading, n, imageid, imagename, checksum, imagesize))
    ts.set_func_list(thr)
    ts.start()
    ret = ts.get_return()

    newnodes = []
    for key in ret.keys():
        if not ret[key]:
            newnodes.append(nodes[key])
        else:
            print '%s already have this Image' % (nodes[key])
    ## Put some newnodes info
    return newnodes

def kill_httpd_threading(pid):
    os.system("ssh %s %s/nv-kill-httpd" % (pid, installpath))
    
def kill_httpd(nodes):
    ts = libThreading.threads()
    thr = []
    for i, pid in enumerate(nodes):
        thr.append((kill_httpd_threading, pid))
    ts.set_func_list(thr)
    ts.start()

def local_copy_threading(pid, headnode, num, dom_list, imageid, imagename):
    for j in range(1, num):
        domname = dom_list[j]
        re = os.system('ssh %s mkdir -p %s/%s' % (pid, workpath, domname))
        re += os.system('ssh %s cp %s/%s/%s %s/%s/root' % (pid, imagepath, imageid, imagename, workpath, domname))
        if not re == 0:
            return 1

    domname = dom_list[0]
    re = os.system('ssh %s mkdir -p %s/%s' % (pid, workpath, domname))
    if pid == headnode:
        re += os.system('ssh %s cp %s/%s/%s %s/%s/root' % (pid, imagepath, imageid, imagename, workpath, domname))
    else:
        re += os.system('ssh %s mv %s/%s/%s %s/%s/root' % (pid, imagepath, imageid, imagename, workpath, domname))
    if not re == 0:
        return 1
    return 0
    
def local_copy(nodes, headnode, num, imageid, imagename, instance_names):
    ts = libThreading.threads()
    thr = []
    for i, pid in enumerate(nodes):
        thr.append((local_copy_threading, pid, headnode, num[i], instance_names[i], imageid, imagename))
    ts.set_func_list(thr)
    ts.start()

