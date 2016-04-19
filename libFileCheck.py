#!/usr/bin/env python

import md5

def full_filechecker(filepath):
    try: 
        blocksize = 1024 * 64 
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

def fast_filechecker(filepath):
    try: 
        blocksize = 1024 * 1024
        checksize = blocksize * 63

        f = open(filepath, "rb")
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
