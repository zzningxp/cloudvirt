#!/usr/bin/env python

import libvirt, threading
import os, sys, random, re, md5, time
import libshelve, libThreading

workpath = "/var/run/cloudvirt/vm/"
db4vm = "/root/cloudvirt/db4vm.dat"

def get_host_hashname(pid):
    hash = md5.new(pid)
    return hash.hexdigest()[:8]
    
def generate_instances_info(nodes, nums, imageid, vcpus, mem):
    dom_list = []
    for i, pid in enumerate(nodes):
        ## dom0 name load from db
        dom0_hash_name = get_host_hashname(pid)

        list = []
        for j in range(nums[i]):
            domU_rand_name = str(random.randint(100000, 999999))
            instancename = "cvi-%s-%s" %(dom0_hash_name, domU_rand_name)
            ## domU name check from db to avoid reduplication

            list.append(instancename)
            domU_rand_mac = 'd0:0d:%02x:%02x:%02x:%02x' % (random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))
            domU_rand_mac = domU_rand_mac.upper()

            dbkey = '%s--%s' % (pid, instancename)
            dominfo = {}
            dominfo['pm'] = pid
            dominfo['id_on_pm'] = None
            dominfo['name'] = instancename
            dominfo['ip'] = None
            dominfo['mac'] = domU_rand_mac
            dominfo['mem'] = mem
            dominfo['vcpu'] = vcpus
            dominfo['cputime'] = 0 
            dominfo['status'] = 'Pending'
            dominfo['update_time'] = time.localtime()
            dominfo['create_time'] = None
            dominfo['register_time'] = time.localtime()
            dominfo['image_id'] = imageid
            libshelve.modify('db4vm.dat', dbkey, dominfo)

        dom_list.append(list)

    return dom_list

def create_instance_threading(pid, dom_list):
    conn = libvirt.open("xen+ssh://root@%s/" % pid)
    if conn == None:
        print 'Failed to open connection to the hypervisor'
	return 0;

    for dom in dom_list:
        dbkey = '%s--%s' %(pid, dom)
        dominfo = libshelve.getkey(db4vm, dbkey)
        if dominfo == None:
            ##print sth.
            return
        name = dominfo['name']
        mem = dominfo['mem'] * 1000
        vcpu = dominfo['vcpu']

        xml = open("/root/cloudvirt/libvirt.xml").read()
        xml = xml % (name, 'restart', mem, vcpu, '%s/%s/root' % (workpath, name), dominfo['mac'])
        ## some PM with different hardware: like ethernet. Need to detect the hardwares
        ## I think it should be modified this part
	
	tmpfname = "/tmp/tmplibvirt%s.xml" % name
	tmpfile = open(tmpfname, "w")
	tmpfile.write(xml)
	tmpfile.close()
	re = os.system("scp %s %s:%s/%s/libvirt.xml 1>/dev/null 2>/dev/null" % (tmpfname, pid, workpath, name))	

	try:
            dom = conn.createXML(xml, 0)
	    print "Domain [%s] %s Created" % (pid, name)
	except:
            libshelve.delkey(db4vm, dbkey)
            ## clear_disk() # delete image file or mv back to the image cache
            print "Domain [%s] %s create Failed!!!" % (pid, name)

def create_instance(nodes, instance_name):
    ts = libThreading.threads()
    thr = []
    for i, n in enumerate(nodes):
        thr.append((create_instance_threading, n, instance_name[i]))
    ts.set_func_list(thr)
    ts.start()
