#!/usr/bin/python

import sys,urllib2,httplib,urlparse

def check_file_exists(url):
    host, path=urlparse.urlsplit(url)[1:3]
    print host, ' ', path
    if ':' in host:
        host,port=host.split(':',1)
        try:
            port=int(port)
        except ValueError:
            print 'invalid port number %r' %(port,)
            sys.exit(1)
    else:
         port=80

    connection=httplib.HTTPConnection(host,port)
    connection.request("HEAD",path)
    resp=connection.getresponse()
    return resp.status

def get(url, files):
    if 'http://' not in url:
        url = 'http://' + url
    i=url.rfind('/')
    try:
        httpfp = urllib2.urlopen(url)
    except urllib2.HTTPError:
        print "not exist!"
        return False
    except:
        return False
    localfps = []
    for f in files:
        localfps.append(open(f, 'wb'))
    bs = 1024*8
    while 1:
        block = httpfp.read(bs)
        if block == "":
             break
        #read += len(block)
        for l in localfps:
            l.write(block)
    return True

if __name__=='__main__':
    url = sys.argv[2] 

    import time, os, shutil
    ll = int(sys.argv[1])
    timestamp = time.time()
#    print '\n%s %d' % (urls, ll)

    get(url, [sys.argv[3]])
    print '%d' % (time.time() - timestamp)
#    get(urls, ['0.zzz']
#    print 'Single Time: %d  %dMB/s' % (time.time() - timestamp, os.path.getsize('0.zzz') / (time.time() - timestamp) / 1024 / 1024)
#    for i in range(ll)[1:]:
#        shutil.copyfile('0.zzz', '%d.zzz' %i)
#    print 'Local Copy Time: %d' % (time.time() - timestamp)
#    for i in range(ll):
#        os.remove('%d.zzz' % i)
#
#    timestamp = time.time()
#    for i in range(ll):
#        ts2 = time.time()
#        get(urls, ['%d.zzz' % i])
#        ts2 = time.time() - ts2
#        sz = os.path.getsize('%d.zzz' % i)
#        print '    Serial Time: %d, %d' % (time.time() - timestamp, sz / ts2)
#    print 'Serial Time: %d' % (time.time() - timestamp)
#
#    for i in range(ll):
#        os.remove('%d.zzz' % i)
#
#    timestamp = time.time()
#    fs = []
#    for i in range(ll):
#        fs.append('%d.zzz' % i)
#    get(urls, fs)
#    print 'Parallel Time: %d' % (time.time() - timestamp)
#    for i in range(ll):
#        os.remove('%d.zzz' % i)


