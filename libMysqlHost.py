#!/usr/bin/python

import md5
from libMysql import datebase as DB

class Hosts(DB):
    tablename = 'hosts'
 
    col_hostid = 'hostid'
    col_clustername = 'clustername'
    col_hashname = 'hashname'
    col_ip = 'ip'
    ## multi net card on a single host??
    col_disksize = 'disksize'
    col_memory = 'memory'
    col_cpus = 'cpus'
    col_mhz = 'mhz'
    col_sockets = 'sockets'
    col_cores = 'cores'
    col_threads = 'threads'
    col_update_time = 'update_time'
    col_register_time = 'register_time'
    col_numa_cell = 'numa_cell'
    col_model = 'model'
 
    columntypes = [
            (col_hostid, DB.type_str + DB.constraint_primary_key),
            (col_clustername, DB.type_str),
            (col_hashname, DB.type_str),
            (col_ip, DB.type_str),
            (col_disksize, DB.type_int),
            (col_memory, DB.type_int),
            (col_cpus, DB.type_int),
            (col_mhz, DB.type_int),
            (col_sockets, DB.type_int),
            (col_cores, DB.type_int),
            (col_threads, DB.type_int),
            (col_update_time, DB.type_datetime),
            (col_register_time, DB.type_datetime),
            (col_numa_cell, DB.type_int),
            (col_model, DB.type_str)
            ]

    def get_hashname(self, hostname):
        hashname = self.select(self.col_hashname, ' %s = \'%s\' ' % (self.col_hostid, hostname), None)
        if hashname:
            return hashname[0][0]
        else:
            hash = md5.new(hostname)
            return hash.hexdigest()[:8]
 
