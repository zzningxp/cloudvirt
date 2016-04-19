#!/usr/bin/env python

import md5
blocksize = 1024 * 1024
checksize = blocksize * 63

def full_filechecker(filepath):
    try: 
        f = open(filepath, "rb") 
        str = f.read(blocksize) 
        m = md5.new()
        while(len(str) != 0): 
            m.update(str) 
            str = f.read(blocksize) 
        f.close() 
    except: 
        print 'get file crc error!' 
        return 0 
    return m.hexdigest()

def fast_filechecker(filepath, offset):
    try: 
        f = open(filepath, "rb")
        f.seek(blocksize * offset, 1)
        str = f.read(blocksize) 
        m = md5.new()
        while(len(str) != 0):
            m.update(str)
            str = f.read(blocksize)
            f.seek(checksize, 1)
        f.close()
    except: 
        print 'get file crc error!' 
        return 0 
    return m.hexdigest()
