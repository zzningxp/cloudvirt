#!/usr/bin/env python

import os, sys, random, re, threading, time, libThreading, libImage

workpath = libImage.workpath
imagepath = libImage.imagepath
logpath = libImage.logpath
installpath = libImage.installpath
dlport = libImage.dlport

def wgetimage(client, server, imageid, imagename, path, size):
    os.system('ssh %s mkdir -p %s/%s' % (client, path, imageid))
    dlfile = os.path.normpath('%s/%s' % (imageid, imagename))
    svfile = os.path.normpath('%s/%s/%s' % (path, imageid, imagename))
    cmd = 'ssh %s wget http://%s:%d/%s -O %s -q' % (client, server, dlport, dlfile, svfile)
    print cmd, 'Started %s' % time.strftime("%H:%M:%S")
    timestamp = time.time()
    ret =  os.system(cmd)
    if ret == 0:
        timeuse = time.time() - timestamp
        print cmd, 'Finished %s, takes %d s, average %d MB/s' % (time.strftime("%H:%M:%S"), timeuse, size / timeuse / 1024 / 1024)
    else:
        print cmd, 'Error'

def get_split_list(x, y, original_list):
    l = []
    for i in range(y):
        l.append(x / y)
    for i in range(x % y):
        l[i] += 1

    list = []
    index = 0
    for i in l:
        if i > 0:
            list.append(original_list[index : index + i])
            index += i
    return list
 
def dispatch(cluster_nodes, imageid, imagename, imagesize, degree):
    clusternum = len(cluster_nodes)
    if clusternum == 0:
        return
    if clusternum == 1:
        cluster = cluster_nodes[0]
        nodenum = len(cluster)
        if (nodenum <= 1):
            return

        ts = libThreading.threads()
        thr = []
        for client in cluster[1 : degree]:
            thr.append((wgetimage, client, cluster[0], imageid, imagename, imagepath, imagesize))
        ts.set_func_list(thr)
        ts.start()
        
        cs = libThreading.threads()
        thr = []
        clients = cluster[degree : ]
        lists = get_split_list(len(clients), degree, clients)
        for i, list in enumerate(lists):
            ll = []
            list.insert(0, cluster[i])
            ll.append(list)
            print '<x>', ll
            thr.append((dispatch, ll, imageid, imagename, imagesize, degree))
        cs.set_func_list(thr)
        cs.start()

    else:
        list = get_split_list(clusternum, degree, cluster_nodes)

        # cluster_nodes is a list of clusters. cluster_nodes[0][0] is a node
        # list is a list of list of clusters. list[0][0][0] is a node

        ts = libThreading.threads()
        thr = []
        for client in list[1:]:
            thr.append((wgetimage, client[0][0], list[0][0][0], imageid, imagename, imagepath, imagesize))
        ts.set_func_list(thr)
        ts.start()
        
        cs = libThreading.threads()
        thr = []
        for clusters in list:
            thr.append((dispatch, clusters, imageid, imagename, imagesize, degree))
        cs.set_func_list(thr)
        cs.start()

def dispatch_image(cluster_nodes, headnode, imageid, imagename, imagesize, concurrent, is_samelocation):
    if len(cluster_nodes) == 0:
        return

    if is_samelocation:
        first_cluster = cluster_nodes.pop(0)
    else:
        first_cluster = []
    first_cluster.insert(0, headnode)
    cluster_nodes.insert(0, first_cluster)
    
    print cluster_nodes
    dispatch(cluster_nodes, imageid, imagename, imagesize, concurrent + 1)

def get_clusters(nodes, cluster_list, image_nodes):
    x = 0
    cluster_nodes = []
    for i in cluster_list:
        cl = nodes[x : i]
        clx = []
        for n in cl:
            if n in image_nodes:
                clx.append(n)
        if len(clx) > 0:
            cluster_nodes.append(clx)
        x = i

    return cluster_nodes
