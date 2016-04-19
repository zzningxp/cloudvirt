#!/usr/bin/env python

import threading
import logging
import monitorip

workpath = "/root/try_cloudvirt/cloudvirt/"

def initlog(logfile):
    logger = logging.getLogger()
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger

def main():
    monitorip.getdhcp(initlog(workpath+"deamon.log"))

if __name__ == "__main__":
    main()
