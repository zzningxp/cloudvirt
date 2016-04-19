#!/usr/bin/env python

import socket, sys, os
import threading
import libUDS
import monitorvm
import logging

workpath = "/usr/share/cloudvirt/"

def initlog(logfile):
    logger = logging.getLogger()
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

def main():
    monitorvm.getinstances(initlog(workpath+"deamon.log"))
if __name__ == "__main__":
    main()
