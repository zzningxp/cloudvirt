#!/usr/bin/python

import MySQLdb
import time

class datebase(object):
    type_int = ' INTEGER ' 
    type_serial = ' SERIAL ' 
    type_long = ' BIGINT ' 
    type_double = ' DOUBLE '
    type_date = ' DATE '
    type_time = ' TIME '
    type_datetime = ' DATETIME '

    type_str = ' VARCHAR(255) '
    type_txt = ' TEXT '
    type_none = ' NULL '
    type_binary = ' BLOB '

    constraint_primary_key = ' PRIMARY KEY '
    constraint_foreign_key = ' FOREIGN KEY '
    constraint_not_null = ' NOT NULL '
    constraint_unique = ' UNIQUE '

    split_where = 'and'
    split_update = ','

    __dbname = 'clovd'
    tablename = None
    columntypes = []

    prterr = False

    def __init__(self, dbname=__dbname):
        self.__dbname = dbname
        try:
            self.conn = MySQLdb.connect(db=dbname)
        except:
            self.__create_database(dbname)
            self.conn = MySQLdb.connect(db=dbname)

        self.__create_table()

    def __del__(self):
        self.conn.commit() 
        self.conn.close()

    def __execute_commit(self, cmd):
        try:
            try:
                cur = self.conn.cursor()
                cur.execute(cmd)
                return 0
            except Exception, e:
                if self.prterr:
                    print cmd
                    print e
                ## should log here
                #print cmd, e
                return 255
        finally:
            cur.close()

    def __execute_fetch(self, cmd):
        try:
            try:
                cur = self.conn.cursor()
                cur.execute(cmd)
                ret = cur.fetchall()
                ret = list(ret)
                return ret
            except Exception, e:
                if self.prterr:
                    print cmd
                    print e
                ## should log here
                return None
        finally:
            cur.close()

    def str2time(self, val):
        return "%s" % time.strftime('%Y-%m-%d %H:%M:%S', val)

    def __val_handle(self, val):
        if type(val) == time.struct_time:
            return "'%s'" % self.str2time(val)
        if type(val) == str:
            return repr(val)
        if val == None:
            return self.type_none
        return val

    def __set_condition(self, tuples, split):
        condition = ''
        for col, val in tuples:
            val = self.__val_handle(val)
            condition += '%s %s = %s ' % (split, col, val)
        return condition[len(split):]

    def __create_database(self, dbname):
        cmd = 'create database %s' % dbname
        conn = MySQLdb.connect()
        conn.query(cmd)
        conn.commit()
        conn.close()
        print cmd

    def __create(self, tablename, columns):
        return self.__execute_commit('create table %s (%s)' % (tablename, columns))

    def __create_table(self):
        tabcol = ''
        for col, typ in self.columntypes:
            tabcol += ', %s %s' % (col, typ)
        tabcol = tabcol[1:]
        return self.__create(self.tablename, tabcol)

    def __insert(self, tablename, valuelist):
        values = ''
        for val in valuelist:
            val = self.__val_handle(val)
            values += ', %s ' % val
        values = values[1:]
        return self.__execute_commit('insert into %s values (%s)' % (tablename, values))

    def __update(self, tablename, condition, updates):
        #ret = self.__select_count(tablename,  condition)
        #if ret == 0:
        #    return 255
        return self.__execute_commit('update %s set %s where %s' % (tablename, updates, condition))

    def __delete(self, tablename, condition):
        return self.__execute_commit('delete from %s where %s' % (tablename, condition))

    def __select(self, tablename, selected, condition, order):
        cmd = 'select %s from %s ' % (selected, tablename)
        if condition:
            cmd += ' where %s ' % condition
        if order:
            cmd += ' order by %s ' % order
        return self.__execute_fetch(cmd)
    
    def __select_count(self, tablename, condition):
        ret = self.__select(tablename, 'count(*)', condition, None)
        print ret
        return ret[0][0]

    #
    #public database access interfaces:
    #

    def get_columns_list(self):
        ret = []
        for col, val in self.columntypes:
            ret.append(col)
        return ret
    
    def insert(self, tuplelist):
        columns = ''
        values = []
        for col, val in tuplelist:
            columns += ', %s' % col
            values.append(val)
        tabandcol = '%s (%s)' % (self.tablename, columns[1:])
        return self.__insert(tabandcol, values)
        
    def insert_only_value(self, valuelist):
        return self.__insert(self.tablename, valuelist)

    def insert_dict(self, dict):
        list = []
        for key in dict.keys():
            list.append((key, dict[key]))
        return self.insert(list)

    def update(self, where_str, set_str):
        return self.__update(self.tablename, where_str, set_str)

    def update_tuples(self, where_tuples, set_tuples):
        updates = self.__set_condition(set_tuples, self.split_update)
        condition = self.__set_condition(where_tuples, self.split_where)
        return self.__update(self.tablename, condition, updates)

    def update_dict(self, where_dict, set_dict):
        where_tuples = []
        for key in where_dict.keys():
            where_tuples.append((key, where_dict[key]))
        set_tuples = []
        for key in set_dict.keys():
            set_tuples.append((key, set_dict[key]))
        return self.update_tuples(where_tuples, set_tuples)

    def delete(self, where_tuples):
        condition = self.__set_condition(where_tuples, self.split_where)
        return self.__delete(self.tablename, condition)

    # select all
    # return a list of tuples of columns
    def select_all(self):
        return self.__select(self.tablename, '*', None, None)

    # select by a tuples equals condition
    # return a list of tuples of columns
    def select_where_tuple(self, where_tuples):
        condition = self.__set_condition(where_tuples, self.split_where)
        return self.__select(self.tablename, '*', condition, None)
    
    # select by a string condition, string orders, 
    # return a list of tuples of columns
    def select(self, column_str, where_str, order_str):
        return self.__select(self.tablename, column_str, where_str, order_str)

    # select by a tuples equals condition, 
    # return existance.
    def select_exist(self, where_tuples):
        condition = self.__set_condition(where_tuples, self.split_where)
        ret = self.__select_count(self.tablename, condition)
        return ret > 0

    # select by a string condition, 
    # return a list of dictionary of full columns and values
    def select_dict_withtuples(self, where_tuples):
        condition = self.__set_condition(where_tuples, self.split_where)
        return self.select_dictlist(condition)

    def select_dictlist(self, where_str):
        columns = self.get_columns_list()
        vals = self.__select(self.tablename, ','.join(columns), where_str, None)
        ret = []
        for inst in vals:
            dict = {}
            for col, val in zip(columns, inst):
                dict[col] = val
            ret.append(dict)
        return ret

