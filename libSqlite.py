#!/usr/bin/env python

import sqlite3 as sqlite

class datebase(object):
    type_int = 'INTEGER'
    type_long = 'INTEGER'
    type_real = 'REAL'
    type_str = 'TEXT'
    type_none = 'NULL'
    type_buffer = 'BLOB'

    #dbf = '/tmp/sqlite'
    dbf = 'D:\\utmp\\sqlite'

    def __init__(self, dbf=dbf):
        self.conn = sqlite.connect(dbf)

    def __del__(self):
        self.conn.commit() 
        self.conn.close()

    def __execute_commit(self, cmd):
        print cmd
        try:
            cur = self.conn.cursor()
            cur.execute(cmd)
            self.conn.commit()
        except Exception, e:
            print e
    def __execute_fetch(self, cmd):
        try:
            cur = self.conn.cursor()
            cur.execute(cmd)
            return cur.fetchall()
        except Exception, e:
            print e

    def __insert(self, tablename, valuelist):
        values = ''
        for v in valuelist:
            values += ', '
            if type(v) == str:
                values += "'%s'" % v
            else:
                values += "%s" % v
        values = values[1:]
        self.__execute_commit('insert into %s values (%s)' % (tablename, values))

    def create_table(self, tablename, columns, types):
        tabcol = ''
        for col, typ in zip(columns, types):
            tabcol += ', %s %s' % (col, typ)
        tabcol = tabcol[1:]
        self.__execute_fetch('create table %s (%s)' % (tablename, tabcol))

    def insert_withcolumns(self, tablename, columns, valuelist):
        col = ''
        for c in columns:
            col += ',%s' % c
        tablename = '%s (%s)' % (tablename, col[1:])
        self.__insert(tablename, valuelist)

    def insert(self, tablename, valuelist):
        self.__insert(tablename, valuelist)

    def select_all(self, tablename):
        return self.__execute_fetch('select * from %s' % tablename)

    def select(self, tablename, condition):
        return self.__execute_fetch('select * from %s where %s' % (tablename, condition))
