#!/usr/bin/python

import zlib, os, re, urllib2, time, threading
import libFileCheck

#chunksize = 1024 * 1024 * 128 #512MB 
#chunksize = 256 
zliblevel = 1
concur = 1

def chunk_read(f, offset, chunksize):
    f.seek(chunksize * offset, 0)
    t = time.time()
    str = f.read(chunksize)
    t = time.time() - t
    #print 'read:%d' % offset, t
    return str

def chunk_copy(str, fps, offset, chunksize):
    t = time.time()
    for f in fps:
        f.seek(chunksize * offset, 0)
        f.write(str)
    ## don't know whether this is a good way to write disk in 500M per block
    t = time.time() - t
    #print 'write:%d' % offset, t

def chunk_compress(ori, filename, offset, chunksize):
    t = time.time()
    gz = zlib.compress(ori, zliblevel)
    t = time.time() - t
    ratio = 1.0 * len(gz) / len(ori)
    ##print ratio, t
    #print 'comp:%d' % offset, t
    g = open('%s.gz.%d' % (filename, offset), 'wb')
    chunk_copy(gz, [g], 0, chunksize)

def file_compress(origin_filename, target_filename, chunksize):
    offset = 0
    th = []
    cnt = 0
    #print cnt
    while True:
        f = open(origin_filename, "rb")
        ori = chunk_read(f, offset, chunksize)
        lenori = len(ori)
        if lenori == 0:
            break
        cnt += 1
        if len(th) > concur :
            ti = th.pop(0)
            if ti.isAlive():
                ti.join()
        th.append(threading.Thread(target=chunk_compress, args=(ori, target_filename, offset, chunksize)))
        th[-1].start()
        offset += 1
    for ti in th:
        ti.join()
    return cnt

def file_compress_sizecount(filename):
    filelist = os.listdir(os.path.dirname(filename))
    sizes = {} 
    for f in filelist:
        #print f
        m = re.match('%s.gz.(\d+)' % os.path.basename(filename), f)
        if m:
            sizes[int(m.group(1))] = os.stat(os.path.join(os.path.dirname(filename), f)).st_size
    return sizes

def file_compress_checksum(filename):
    filelist = os.listdir(os.path.dirname(filename))
    chksm = {}
    for f in filelist:
        #print f
        m = re.match('%s.gz.(\d+)' % os.path.basename(filename), f)
        if m:
            f = os.path.join(os.path.dirname(filename), f)
            chk = libFileCheck.checksum(f)
            fsm = chk.get_full_checksum()
            if not fsm:
                #print 'File Sum Check Failed'
                return None
            chksm[int(m.group(1))] = fsm
    return chksm

def chunk_decompress(gstr, fps, offset, chunksize):
    t = time.time()
    str = zlib.decompress(gstr)
    t = time.time() - t
    #print 'decomp:%d' % offset, t
    ##print 1.0 * len(gstr) / chunksize, t,
    chunk_copy(str, fps, offset, chunksize)

def file_decompress(filename, dests, chunksize):
    fps = []
    for f in dests:
        fps.append(open(f, "wb"))
    filelist = os.listdir(os.path.dirname(filename)) 
    yl = {}
    for f in filelist:
        m = re.match('%s.gz.(\d+)' % os.path.basename(filename), f)
        if m:
            yl[int(m.group(1))] = 'gz'
    if yl.keys() == range(len(yl)):
        th = []
        for i in yl:
            g = open('%s.%s.%d' % (filename, yl[i], i), 'rb')
            gstr = chunk_read(g, 0, chunksize)
            if len(th) > concur :
                ti = th.pop(0)
                if ti.isAlive():
                    ti.join()
            th.append(threading.Thread(target=chunk_decompress, args=(gstr, fps, i, chunksize)))
            th[-1].start()
        for ti in th:
            ti.join()
    else:
        print 'File Chunk Missing, decompression failed'

def chunk_httpread(url):
    try:
        httpfp = urllib2.urlopen(url)
    except urllib2.HTTPError:
        return None
    except:
        return None
    else:
        t = time.time()
        str = httpfp.read(chunksize)
        t = time.time() - t
        ##print 'read:%d' % i, t

def wget_decompress(url, gz, dest, chunksize):
    if 'http://' not in url:
        url = 'http://' + url
    dest = open(dest, "wb")
    i = 0
    while True:
        str = chunk_httpread('%s/%s.gz.%d' % (url, gz, i), chunksize)
        if not str:
            break
        if len(th) > concur :
            ti = th.pop(0)
            if ti.isAlive():
                ti.join()
        th.append(threading.Thread(target=chunk_decompress, args=(str, dest, i, chunksize)))
        th[-1].start()
        i += 1
    for ti in th:
        ti.join()


