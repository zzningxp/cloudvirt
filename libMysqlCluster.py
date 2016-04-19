#!/usr/bin/python

from libMysql import datebase as DB

class Cluster(DB):
    tablename = 'cluster'

    col_id = 'id'
    col_clustername = 'clustername'
    col_host = 'host'

    columntypes = [
            (col_id, DB.type_serial),
            (col_clustername, DB.type_str),
            (col_host, DB.type_str)
            ]
