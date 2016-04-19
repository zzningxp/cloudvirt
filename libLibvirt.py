#!/usr/bin/python

import libvirt

class connection(object):
    conn = None
    def __init__(self, pid):
        try:
            self.conn = libvirt.open("xen+ssh://root@%s/" % pid)
        except Exception, e:
            print "Lost Contection : %s %s" % (pid, e)

    def __del__(self):
        if conn:
            self.conn.close()
    
