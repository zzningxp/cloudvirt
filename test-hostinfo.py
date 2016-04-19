import libMysqlHost
hst = libMysqlHost.Hosts()

columns = [hst.col_hostid, hst.col_clustername]
ret = hst.select(' , '.join(columns), '', '')

plist = []
for i in ret:
	plist.append(i[0])
print plist
