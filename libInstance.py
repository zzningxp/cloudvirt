#!/usr/bin/python

import libvirt, threading
import os, sys, random, re, md5, time
import libThreading, libMysqlInstance, libMysqlHost, libXMLdom, libMysqlImages

workpath = "/var/run/cloudvirt/vm/"

def generate_instances_info(nodes, nums, imageid, vcpus, mem):
    dom_list = []
    instc = libMysqlInstance.Instances()
    hs = libMysqlHost.Hosts()

    for i, pid in enumerate(nodes):
        dom0_hash_name = hs.get_hashname(pid)
        list = []
        for j in range(nums[i]):
            domU_rand_name = str(random.randint(100000, 999999))
            instancename = "cvi-%s-%s" %(dom0_hash_name, domU_rand_name)
            ## domU name check from db to avoid reduplication

            list.append(instancename)
            domU_rand_mac = 'd0:0d:%02x:%02x:%02x:%02x' % (random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))
            domU_rand_mac = domU_rand_mac.upper()
            username = None

            tuplelist = []
            tuplelist.append((instc.col_name, instancename))
            tuplelist.append((instc.col_hostname, pid))
            tuplelist.append((instc.col_username, username))
            tuplelist.append((instc.col_imagename, imageid))
            tuplelist.append((instc.col_mac, domU_rand_mac))
            tuplelist.append((instc.col_status, 'Pending'))
            tuplelist.append((instc.col_update_time, time.localtime()))
            tuplelist.append((instc.col_register_time, time.localtime()))
            tuplelist.append((instc.col_cputime, 0))
            tuplelist.append((instc.col_vcpu, vcpus))
            tuplelist.append((instc.col_mem, mem))
            instc.insert(tuplelist)
        dom_list.append(list)
    return dom_list

def create_instance_threading(pid, dom_list):
    conn = libvirt.open("xen+ssh://root@%s/" % pid)
    if conn == None:
        ### clean domains in the list in DB
        print 'Failed to open connection to the hypervisor'
	return 0;

    instc = libMysqlInstance.Instances()
    img = libMysqlImages.Images()
    for name in dom_list:
        dominfo = instc.select_dictlist(" %s = '%s' " % (instc.col_name, name))
        if len(dominfo) == 0:
            print 'Domain info can\'t be loaded from datebase'
            return 255

        dominfo = dominfo[0]
        mem = dominfo[instc.col_mem] * 1000
        vcpu = dominfo[instc.col_vcpu]
        mac = dominfo[instc.col_mac]
        imginfo = img.select_dictlist(" %s = '%s'" % (img.col_imageid, dominfo[instc.col_imagename]))
        if len(imginfo) > 0:
            imgtype = imginfo[0][img.col_imageformat]
        else:
            imgtype = 'raw'

        xml = libXMLdom.getDomainXML(name, mem, vcpu, '%s/%s/root' % (workpath, name), imgtype, mac)
        ## some PM with different hardware: like ethernet. Need to detect the hardwares
	
	tmpfname = "/tmp/tmplibvirt%s.xml" % name
	tmpfile = open(tmpfname, "w")
	tmpfile.write(xml)
	tmpfile.close()
	re = os.system("scp %s %s:%s/%s/libvirt.xml 1>/dev/null 2>/dev/null" % (tmpfname, pid, workpath, name))	

	try:
            dom = conn.createXML(xml, 0)
	    print "Domain [%s] %s Created" % (pid, name)
	except Exception, e:
            print e
            ## instc.delete(name)
            ## clear_disk() # delete image file or mv back to the image cache
            print "Domain [%s] %s create Failed!!!" % (pid, name)

def create_instance(nodes, instance_name):
    ts = libThreading.threads()
    thr = []
    for i, n in enumerate(nodes):
        thr.append((create_instance_threading, n, instance_name[i]))
    ts.set_func_list(thr)
    ts.start()

def restart_instance(pid, name):
    conn = libvirt.open("xen+ssh://root@%s/" % pid)
    if conn == None:
        print 'Failed to open connection to the hypervisor'
        return;

    try:
        dom = conn.lookupByName(name)
    except:
        print 'Instance %s is not running' % (name,)
    else:
        try:
            dom.reboot(0)
        except Exception, e:
            print e
            print 'Reboot %s failed'

def resume_instance(pid, name):
    conn = libvirt.open("xen+ssh://root@%s/" % pid)
    if conn == None:
        print 'Failed to open connection to the hypervisor'
        return;

    try:
        conn.lookupByName(name)
        print 'Instance %s on host %s is running' % (name, pid)
        return
    except:
        pass

    isxml = os.system('ssh %s ls -l %s/%s/libvirt.xml 1>/dev/null 2>/dev/null' % (pid, workpath, name))
    isimg = os.system('ssh %s ls -l %s/%s/root 1>/dev/null 2>/dev/null' % (pid, workpath, name))
    ##check sum this image file!
    tmpfname = "/tmp/tmplibvirt%s.xml" % name
    isscp = os.system("scp %s:%s/%s/libvirt.xml %s 1>/dev/null 2>/dev/null" % (pid, workpath, name, tmpfname))
    if isxml == 0 and isscp == 0:
        xml = open(tmpfname, "r").read()

        if isimg == 0:
            try:
                dom = conn.createXML(xml, 0)
                print "Domain %s resume on %s" % (name, pid)
            except Exception, e:
                print "Domain %s on %s have not been resume. %s" % (name, pid, e )
        else:
            print 'Instance Image File Missing or Modified'
    else:
        print 'Instance Config File Missing or Modified'
