#!/usr/bin/python

import os, commands, sys, random, re, threading, time, libThreading, xmlrpclib

workpath = "/var/run/cloudvirt/vm/"
imagepath = "/var/run/cloudvirt/image/"
logpath = "/var/log/cloudvirt/"
installpath = "/usr/share/cloudvirt"
zfillwidth = 2
dlport = 8773
rpcport = 8772
snowballtrees = 4 
concurrent = 2
degree = concurrent + 1
semaphores = []
timestamp = time.time()
rpcretry = 3

## NOTICE: Both RPC server/client and the HTTP server need to get through the firewall.
## So, you need to close the iptables on both side.
##
#------------------------------------------------------------#
# Dispatching Image Files::
#------------------------------------------------------------#
def wgetimage(client, server, imageid, imagename, path, next, semaphore, semindex):
    global timestamp
    #show = '[%s] -> [%s](%s)' % (server.ljust(12), client.ljust(12), dlfile)
    show = '%s %s(%d)' % (server.ljust(14), client.ljust(14), semindex)
    dlfile = os.path.normpath('%s/%s' % (imageid, imagename))
    svfile = os.path.normpath('%s/%s/%s' % (path, imageid, imagename))
    rpcserver = xmlrpclib.ServerProxy("http://%s:%s" % (client, rpcport))
    #cmd = 'wget http://%s:%d/%s -O %s -q' % (server, dlport, dlfile, svfile)
    cmd = 'wget http://%s:%d/%s -O %s' % (server, dlport, dlfile, svfile)
    if semaphore.acquire():
        starttime = time.time() - timestamp
        #print show, 'Started %f' % (starttime)
        for i in range(rpcretry):
            try:
                ret, debugout = rpcserver.command(cmd)
            except Exception, e:
                ret = -1
                debugout = e 
                print 'retry'
                continue
            break
        if ret == 0:
            print show, '%f %f' % (starttime, time.time() - timestamp)
            pass
        else:
            print 'Error:', ret, show, next, '%f %f' % (starttime, time.time() - timestamp), debugout
            #print 'Error Debug:', debugout
        semaphore.release()
    dispatch(next, imageid, imagename, semindex)

def waitdispatch(cluster_nodes, imageid, imagename, semindex):
    time.sleep(0.1)
    dispatch(cluster_nodes, imageid, imagename, semindex)

def dispatch(cluster_nodes, imageid, imagename, semindex):
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
        clients = cluster[degree : ]
        lists = get_split_list(len(clients), clients)
        #print lists
        #print cluster
        for i, client in enumerate(cluster[1 : degree]):
            if i + 1 < len(lists):
                next = [[cluster[i + 1]] + lists[i + 1]]
            else:
                next = []
            semaphore = semaphores[semindex][cluster[0]]
            thr.append((wgetimage, client, cluster[0], imageid, imagename, imagepath, next, semaphore, semindex))
        if len(lists) > 0:
            next = [[cluster[0]] + lists[0]]
            thr.append((waitdispatch, next, imageid, imagename, semindex))
        ts.set_func_list(thr)
        ts.start()
    else:
        list = get_split_list(clusternum, cluster_nodes)
        # cluster_nodes is a list of clusters. cluster_nodes[0][0] is a node
        # list is a list of list of clusters. list[0][0][0] is a node
        ts = libThreading.threads()
        thr = []
        for client in list[1:]:
            semaphore = semaphores[semindex][list[0][0][0]]
            thr.append((wgetimage, client[0][0], list[0][0][0], imageid, imagename, imagepath, client, semaphore, semindex))
        thr.append((waitdispatch, list[0], imageid, imagename, semindex))
        ts.set_func_list(thr)
        ts.start()
 
def dispatch_image(nodes, cluster_list, image_nodes, headnode, imageid, imagename, compresscount, is_samelocation):
    cluster_nodes = get_clusters(nodes, cluster_list, image_nodes)
    if len(cluster_nodes) == 0:
        return
    cluster_nodes = handle_headnode(cluster_nodes, headnode, is_samelocation)
    #print cluster_nodes
    index = 0
    global timestamp
    timestamp = time.time()
    sortedfiles = os.popen('ls -lS %s/%s | awk \'{print $9}\'' % (imagepath, imageid)).read().split('\n')[1:-1]
    ##check files names?
    while index < compresscount:
        ts = time.time()
        sbt = libThreading.threads()
        thr = []
        global semaphores
        semaphores = []
        treedegree = snowballtrees
        if compresscount - index < treedegree:
            treedegree = compresscount - index
        for i in range(treedegree):
            nodes = sbtree_design(cluster_nodes, i, treedegree)
            #print nodes
            sem = gen_semaphore(nodes)
            semaphores.append(sem)
            thr.append((dispatch, nodes, imageid, '%s' % (sortedfiles[index]), i))
            index += 1
        sbt.set_func_list(thr)
        sbt.start()
        #print time.time() - ts

def gen_semaphore(nodes):
    ret = {}
    for cluster in nodes:
        for node in cluster:
            ret[node] = threading.Semaphore(concurrent)
    return ret

def get_split_list(x, original_list):
    # this function is :
    # depart the list to a two-level list for dispatching parting
    l = []
    for i in range(degree - x % degree):
        l.append(x / degree)
    for i in range(x % degree):
        l.append(x / degree + 1)
    list = []
    index = 0
    for i in l:
        if i > 0:
            list.append(original_list[index : index + i])
            index += i
    return list

def sbtree_design(cluster_nodes, i, sbts):
    ret = []
    for cluster in cluster_nodes:
        head = cluster[0]
        cluster = cluster[1:]
        cl = i * len(cluster) / sbts
        nw = [head] + cluster[cl:] + cluster[:cl]
        ret.append(nw)
    return ret

def handle_headnode(cluster_nodes, headnode, is_samelocation):
    if is_samelocation:
        first_cluster = cluster_nodes.pop(0)
    else:
        first_cluster = []
    first_cluster.insert(0, headnode)
    cluster_nodes.insert(0, first_cluster)
    #print cluster_nodes
    return cluster_nodes

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

#------------------------------------------------#
# Prepare to dispatch image files
#------------------------------------------------#
def dispatch_nv_thread(n, imageid):
    ret = 0
    #ret += os.system("ssh %s %s/nv-kill-httpd" % (n, installpath))
    #time.sleep(5)
    ret += os.system('ssh %s mkdir -p %s' % (n, installpath))
    ret += os.system("scp nv-* %s:%s 1>/dev/null" % (n, installpath))
    ret += os.system("scp libFileCheck.py %s:%s 1>/dev/null" % (n, installpath))
    ret += os.system("scp libGZip.py %s:%s 1>/dev/null" % (n, installpath))
    ret += os.system("scp libHTTPServer.py %s:%s 1>/dev/null" % (n, installpath))
    ret += os.system("ssh %s mkdir -p %s/%s" % (n, imagepath, imageid))
    ret += os.system("ssh %s 'nohup %s/nv-image-daemon %s %s %s %s %s 0</dev/null 1>/dev/null 2>/dev/null'" % (n, installpath, n, dlport, imagepath, concurrent * snowballtrees, logpath))
    ret, out = commands.getstatusoutput("ssh %s 'nohup %s/nv-rpc-daemon %d 0</dev/null 1>/dev/null 2>/dev/null'" % (n, installpath, snowballtrees))
    #print ret, out
    return ret

def dispatch_nv(nodes, headnode, imageid):
    dispatch_nv_thread(headnode, imageid)
    ts = libThreading.threads()
    thr = []
    for n in nodes:
        if n != headnode:
            thr.append((dispatch_nv_thread, n, imageid))
    ts.set_func_list(thr)
    ts.start()
 
def check_nodes_threading(n, imageid, imagename, checksum, imagesizes, compresscount):
    ## this must be changed to check each file splits.
    ## if the whole image is modified by little part, maybe the splits needed dispatch is little too.
    for cno in range(compresscount):
        filename = "%s/%s/%s.gz.%s" % (imagepath, imageid, imagename, str(cno).zfill(zfillwidth))
        img_status = os.system('ssh %s ls -l %s 1>/dev/null 2>/dev/null' %(n, filename))
        if img_status == 0:
            cmd = 'ssh %s %s/nv-filechecker %s %s %s' % (n, installpath, filename, checksum[cno], imagesizes[cno])
            check_status = os.system(cmd)
            if check_status != 0:
                return False
        else:
            return False
    return True

def check_nodes(nodes, imageid, imagename, checksum, imagesizes, compresscount):
    ts = libThreading.threads()
    thr = []
    for n in nodes:
        thr.append((check_nodes_threading, n, imageid, imagename, checksum, imagesizes, compresscount))
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

def local_decompress_threading(pid, headnode, num, dom_list, imageid, imagename):
    dest = []
    for j in range(0, num):
        domname = dom_list[j]
        re = os.system('ssh %s mkdir -p %s/%s' % (pid, workpath, domname))
        dest.append('%s/%s/root' % (workpath, domname))
        if not re == 0:
            return 1
    print 'Local Decompressing on %s' % pid
    cmd = 'ssh %s %s/nv-localdecompress %s/%s/%s %s' % (pid, installpath, imagepath, imageid, imagename, ' '.join(dest))
    ret = os.system(cmd)
    print 'Local Decompress on %s .. Done.' % pid
    return ret

def local_decompress(nodes, headnode, num, imageid, imagename, instance_names):
    ts = libThreading.threads()
    thr = []
    for i, pid in enumerate(nodes):
        thr.append((local_decompress_threading, pid, headnode, num[i], instance_names[i], imageid, imagename))
    ts.set_func_list(thr)
    ts.start()

def read_nodes(nodes_file):
    f = open(nodes_file)
    nodes = []
    num = []
    cluster_list = []
    for n in f.readlines():
        n = n.rstrip("\r\n")
        if len(n) == 0:
            cluster_list.append(len(nodes))
            continue
        n = re.split(r"\s", n)
        try:
            n.remove('')
        except:
            pass
        if not len(n) == 2:
            print 'Nodes File has a Wrong Format'
            usage()
            sys.exit()
        nodes.append(n[0])
        num.append(int(n[1]))

    cluster_list.append(len(nodes))
    return nodes, num, cluster_list


