import os, time, BaseHTTPServer, SimpleHTTPServer, sys, threading

SIGKILL = 9 # Linux System Signal
cnt = 0
status = True

def server_daemon(httpd, logpath):
    try:
        os.mkdir(logpath)
    except:
        pass
    sys.stdout = open(logpath + 'http_access.log', 'w')
    sys.stderr = open(logpath + 'http_errors.log', 'w')
    while status:
        httpd.handle_request()
    
def server_start(HOST_NAME, PORT_NUMBER, path, concurrent, logpath):

    server_class = BaseHTTPServer.HTTPServer
    try:
        httpd = server_class((HOST_NAME, PORT_NUMBER), SimpleHTTPServer.SimpleHTTPRequestHandler)
    except:
        return False
    #print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)

    os.chdir(path)
    thr = []
    for i in range(concurrent):
        thr.append(threading.Thread(target=server_daemon, args=(httpd, logpath)))
    for i in range(concurrent):
        thr[i].start()

    return True
   
def server_status():
    return status

def server_shutdown():
    #print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
    global status
    status = False
