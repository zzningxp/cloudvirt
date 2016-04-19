#!/usr/bin/python

import time
from libMysql import datebase as DB

class Instances(DB):
    tablename = 'instances'

    col_instanceid = 'instanceid'
    col_name = 'name'
    col_hostname = 'hostname'
    col_username = 'username'
    col_imagename = 'imagename'
    col_ip = 'ip'
    col_mac = 'mac'
    col_status = 'status'

    col_update_time = 'update_time'
    col_register_time = 'register_time'
    col_start_time = 'start_time'
    col_cputime = 'cputime'
    col_vcpu = 'vcpu'
    col_mem = 'mem'
    col_domid = 'domid'

    columntypes = [
        (col_instanceid, DB.type_serial),
        (col_name, DB.type_str+DB.constraint_unique),
        (col_hostname, DB.type_str),
        (col_username, DB.type_str),
        (col_imagename, DB.type_str),
        (col_ip, DB.type_str),
        (col_mac, DB.type_str),
        (col_status, DB.type_str),
        (col_update_time, DB.type_datetime),
        (col_register_time, DB.type_datetime),
        (col_start_time, DB.type_datetime),
        (col_cputime, DB.type_int),
        (col_vcpu, DB.type_int),
        (col_mem, DB.type_int),
        (col_domid, DB.type_int)]
    
    def get_hostname_byname(self, name):
        wheres = ' %s = \'%s\' ' % (self.col_name, name)
        host = self.select(self.col_hostname, wheres, None)
        if len(host) > 0:
            return host[0][0]
        return None
   
    def mark_dead(self):
        sqltimediff = 'timestampdiff(second, update_time, \'%s\')' % self.str2time(time.localtime())
        markdead_internal = 180 # 3 minutes to mark dead of runnings
        self.update(
                ' %s > %d and %s != \'%s\' ' % (sqltimediff, markdead_internal, self.col_status, 'Pending'), 
                ' %s = \'%s\'' % (self.col_status, 'Dead'))
        pending_markdead_internal = 7200 # 2 hours to mark dead of pendings
        self.update(
                ' %s > %d and %s = \'%s\' ' % (sqltimediff, pending_markdead_internal, self.col_status, 'Pending'), 
                ' %s = \'%s\'' % (self.col_status, 'Dead'))
 
