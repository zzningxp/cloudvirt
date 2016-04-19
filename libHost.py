#!/usr/bin/python
import logging, time, threading
import libvirt, sys, os, re, time, getopt
import libMysqlHost, libMysqlCluster

def libvirt_connection(host):
    try:
        conn = libvirt.open("xen+ssh://root@%s/" % host)
    except Exception, e:
        print "Lost Contection : " + host + " " + str(e)
        return None
    return conn

def host_register(host, clustername):
    cc = libMysqlCluster.Cluster()    
    if not cc.select_exist([(cc.col_clustername, clustername)]):
        print 'Cluster %s not exist' % clustername
        return

    conn = libvirt_connection(host)
    hs = libMysqlHost.Hosts()
    ninfo = conn.getInfo()
    nodeinfo = {}
    nodeinfo[hs.col_hostid] = host
    nodeinfo[hs.col_clustername] = clustername
    nodeinfo[hs.col_hashname] = hs.get_hashname(host)
    nodeinfo[hs.col_model] = ninfo[0]
    nodeinfo[hs.col_memory] = ninfo[1]
    nodeinfo[hs.col_cpus] = ninfo[2]
    nodeinfo[hs.col_mhz] = ninfo[3]
    nodeinfo[hs.col_numa_cell] = ninfo[4]
    nodeinfo[hs.col_sockets] = ninfo[5]
    nodeinfo[hs.col_cores] = ninfo[6]
    nodeinfo[hs.col_threads] = ninfo[7]
    nodeinfo[hs.col_update_time] = time.localtime()
    nodeinfo[hs.col_register_time] = time.localtime()
    ### clustername/node IP/disk size/
    ret = hs.insert_dict(nodeinfo)
    if ret == 0:
        print 'Host %s registered. Done. ' % host
        return True
    else:
        print 'Something was wrong...'
        return False

def cluster_register(clustername, hostname):
    cc = libMysqlCluster.Cluster()
    clusterinfo = {}
    clusterinfo[cc.col_clustername] = clustername
    clusterinfo[cc.col_host] = hostname
    cc.insert_dict(clusterinfo)
    print 'Cluster %s registered. Done. ' % clustername
