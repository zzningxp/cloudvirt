#!/usr/bin/env python

from libSqlite import datebase as DB

class Instances(DB):
    tablename = 'hosts'
    
    col_numa_cell = 'numa_cell'
    col_model = 'model'
    col_memory = 'memory'
    col_cpus = 'cpus'
    col_mhz = 'mhz'
    col_sockets = 'sockets'
    col_cores = 'cores'
    col_threads = 'threads'
    col_update_time = 'update_time'

    columns = [col_numa_cell, col_model, col_memory, col_cpus, \
               col_mhz, col_sockets, col_cores, col_threads, col_update_time]
    types = []

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
