#!/usr/bin/env python

from libSqlite import datebase as DB

class Instances(DB):
    tablename = 'instances'
    
    col_name = 'name'
    col_host = 'host'
    col_imageid = 'instanceid'
    col_userid = 'userid'
    col_imageid = 'imageid'
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

    columns = [col_name, col_host, col_imageid, col_userid, col_imageid, col_ip, col_mac, col_status, \
               col_update_time, col_register_time, col_start_time, col_cputime, col_vcpu, col_mem, col_domid]
    types = [DB.type_str, DB.type_str, DB.type_str, DB.type_str, DB.type_str, DB.type_str, DB.type_str, DB.type_str, \
             DB.type_int, DB.type_int, DB.type_int, DB.type_int, DB.type_int, DB.type_int, DB.type_int]

    def create_table(self):
        DB.create_table(self, self.tablename, self.columns, self.types)

    def insert_withcolumns(self, columns, valueslist):
        DB.insert_withcolumns(self, self.tablename, columns, valueslist)

    def insert(self, valueslist):
        DB.insert(self, self.tablename, valueslist)

    def select(self, condition):
        return DB.select(self, self.tablename, condition)

    def select_all(self):
        return DB.select_all(self, self.tablename)
