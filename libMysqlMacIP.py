#!/usr/bin/python

from libMysql import datebase as DB

class MacIPs(DB):
    tablename = 'macips'
 
    col_id = 'id'
    col_mac = 'mac'
    col_ip = 'ip'

    columntypes = [(col_id, DB.type_serial),
            (col_mac, DB.type_str),
            (col_ip, DB.type_str)
            ]
    
    def getip(self, mac):
        iplist = self.select(self.col_ip, '%s = \'%s\'' %(self.col_mac, mac), None)
        if iplist:
            return iplist[0][0]
        return None
