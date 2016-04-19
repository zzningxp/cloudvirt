#!/usr/bin/env python

from libSqlite import datebase as DB

class Images(DB):
    tablename = 'images'
    
    col_imageid = 'imageid'
    col_userid = 'userid'
    col_filepath = 'filepath'
    col_filesize = 'filesize'
    col_ostype = 'ostype'
    col_registertime = 'registertime'
    col_checksum = 'checksum'

    columns = [col_imageid, col_userid, col_filepath, col_filesize, col_ostype, col_registertime, col_checksum]
    types = [DB.type_str, DB.type_str, DB.type_str, DB.type_int, DB.type_str, DB.type_int, DB.type_str]

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
