#!/usr/bin/python

import random
from libMysql import datebase as DB

class Images(DB):
    tablename = 'images'

    col_imageid = 'imageid'
    col_userid = 'userid'
    col_filepath = 'filepath'
    col_imageformat = 'imageformat'
    col_virtual_size = 'virtual_size'
    col_actual_size = 'acutal_size'
    col_compress_size = 'compress_size'
    col_chunk_count = 'chunk_count'
    col_chunk_size = 'chunk_size'
    col_registertime = 'registertime'

    columntypes = [
        (col_imageid, DB.type_str + DB.constraint_primary_key),
        (col_userid, DB.type_str),
        (col_filepath, DB.type_str),
        (col_imageformat, DB.type_str),
        (col_virtual_size, DB.type_long),
        (col_actual_size, DB.type_long),
        (col_compress_size, DB.type_long),
        (col_chunk_count, DB.type_int),
        (col_chunk_size, DB.type_int),
        (col_registertime, DB.type_datetime)
        ]

    def get_randid(self, name):
#        idrangemin = 100000000
#        idrangemax = idrangemin * 10 - 1
#        while True:
#            imageid = "img-%s-%d" %(imageostype, random.randint(idrangemin,idrangemax))
#            if not self.select_exist([(self.col_imageid, imageid)]):
#                return imageid
        import time
        i = 0
        while True:
            imageid = 'img-%s-%s-%d' % (name, time.strftime('%y%m%d-%H%M%S'), i)
            if not self.select_exist([(self.col_imageid, imageid)]):
                return imageid
            i += 1
        ## get this id while others generating will wrong!!

    def get_image_format(self, imagefilepath):
        import re, os
        if not os.path.exists(imagefilepath):
            print '%s is not existed' % imagefilepath
            return None
        info = os.popen('/usr/bin/qemu-img info %s' % imagefilepath).read()
        if len(info) == 0: # command not exists
            print "Package kvm-qemu-img is not install, this may cause further errors, try 'yum install kvm-qemu-img'"
            return 'raw', os.stat(imagefilepath).st_size, os.stat(imagefilepath).st_size
        #print info
        try:
            fmt = re.search('file format: (\w+)', info).group(1)
        except Exception, e:
            print e
            fmt = None
        if fmt == 'qcow' or fmt == 'raw':
            try:
                virtual_size = re.search('virtual size: \w.+ \((\d.+) \w+\)', info).group(1)
                virtual_size = int(virtual_size)
            except Exception, e:
                print e
                virtual_size = None
        else:
            virtual_size = None
        try:
            actual_size = os.stat(imagefilepath).st_size
        except Exception, e:
            print e
            actual_size = None
	print fmt, actual_size, virtual_size
        return fmt, actual_size, virtual_size

class ImageBlocks(DB):
    tablename = 'imageblocks'
    
    col_imageblockid = 'imageblockid'
    col_imageid = 'imageid'
    col_blockserial = 'blockserial'
    col_blocksize = 'blocksize'
    col_checksum = 'checksum'

    columntypes = [
        (col_imageblockid, DB.type_serial),
        (col_imageid, DB.type_str),
        (col_blockserial, DB.type_int),
        (col_blocksize, DB.type_long),
        (col_checksum, DB.type_txt)
        ]
    
    def insert_blocks(self, imageid, size_dict, checksum_dict):
        if size_dict.keys() != checksum_dict.keys():
            print 'dicts error'
            return False
        for i in size_dict.keys():
            size = size_dict[i]
            checksum = checksum_dict[i]
            info = {} 
            info[self.col_imageid] = imageid
            info[self.col_blockserial] = i
            info[self.col_blocksize] = size
            info[self.col_checksum] = checksum
            self.insert_dict(info)
    
    def get_checksum(self, imageid):
        ret = self.select('%s, %s' % (self.col_blockserial, self.col_checksum), "%s = '%s'" % (self.col_imageid, imageid), None)
        cksums = {}
        for serial, checksum in ret:
            cksums[serial] = checksum
        if cksums == {}:
	    return None
        return cksums

    def get_block_size(self, imageid):
        ret = self.select('%s, %s' % (self.col_blockserial, self.col_blocksize), "%s = '%s'" % (self.col_imageid, imageid), None)
        sizes = {}
        for serial, size in ret:
            sizes[serial] = size
        if sizes == {}:
	    return None
        return sizes

