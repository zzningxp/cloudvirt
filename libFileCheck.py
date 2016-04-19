#!/usr/bin/python

import md5, random 

class checksum(object):

    stripcount = 64
    blocksize = 1024 * 64 #64K a block
    checksize = blocksize * (stripcount - 1)

    filepath = ''
    spliter = ','
    
    def __init__(self, filepath):
        self.filepath = filepath

    def get_full_checksum(self):
        list = []
        for i in range(self.stripcount):
            list.append(self.fast_filechecker(i))
        return self.spliter.join(list)
    
    def random_check(self, strsum, count):
        sumlist = strsum.split(self.spliter)
        s = self.fast_filechecker(0)
        if s != sumlist[0]:
            return False
        for i in range(count - 1):
            offset = random.randint(1, self.stripcount - 1)
            s = self.fast_filechecker(offset)
            if s != sumlist[offset]:
                return False
        return True

    def fast_filechecker(self, offset):
        try: 
            f = open(self.filepath, "rb")
            f.seek(self.blocksize * offset, 1)
            str = f.read(self.blocksize) 
            m = md5.new()
            while(len(str) != 0):
                m.update(str)
                str = f.read(self.blocksize)
                f.seek(self.checksize, 1)
            f.close()
        except:
            ### raise a exception
            print 'get file crc error!' 
        return m.hexdigest()
