#!/usr/bin/python

# Pull data from the Disk Monitor database and generate the Web dashboard
#  Sean Caron (scaron@umich.edu)

import cgi, time, sys, MySQLdb, ConfigParser

print('Content-type: text/html\n')
print('<html>')
print('<head>')
print('<title>Disk Monitor</title>')
print('<meta http-equiv="refresh" content="600">')
print('<style type="text/css">* { border-radius: 5px; } h1 { font-family: Arial, Helvetica; } p { font-size: medium; font-weight: bold; font-family: Arial, Helvetica; width: 80%; margin: 10px auto; } table { height: 15%; margin: 10px auto; width: 80%; } td { 0px; font-family: Courier; }</style>')
print('</head>')
print('<body bgcolor=White text=Black vlink=Black text=Black>')
print('<h1>Disk Monitor: ' + time.strftime("%A %b %d %H:%M:%S %Z", time.localtime()) + '</h1>')

cfg = ConfigParser.ConfigParser()
cfg.read('/opt/csg/diskmonitor/etc/dashboard.ini')

dbuser = cfg.get('database', 'user')
dbpass = cfg.get('database', 'passwd')
dbname = cfg.get('database', 'db')
dbhost = cfg.get('database', 'host')

db = MySQLdb.connect(host=dbhost,user=dbuser,passwd=dbpass,db=dbname)

curs = db.cursor()

query = 'SELECT host,hostid from hosts ORDER BY host ASC;'
curs.execute(query)
hosts = curs.fetchall()

for host in hosts:
    query = 'SELECT * FROM ' + host[0] + ';'

    curs.execute(query)

    utmps = curs.fetchall()

    toggle = 0

    # user port fromhost time

    print('<p>' + host[0] + '</p>')
    print('<table>')
    print('<th><td>device</td><td>memberof_array</td><td>smart_health</td><td>raw_rd_err_rt</td><td>realloc_sec_ct</td><td>realloc_ev_ct</td><td>current_pending_ct</td><td>offline_uncorr_count</td><td>udma_crc_err_ct</td></th>')
    for row in utmps:
        if toggle == 0:
            print('<tr bgcolor=#ccffcc><td>')
        else:
            print('<tr><td>')

        print(row[1])
        print('</td><td>')
        print(row[2])
        print('</td><td>')
        print(row[3])
        print('</td><td>')
        print(row[4])
        print('</td></tr>')
        print(row[5])
        print('</td></tr>')
        print(row[6])
        print('</td></tr>')
        print(row[7])
        print('</td></tr>')
        print(row[8])
        print('</td></tr>')
        print(row[9])
        print('</td></tr>')

        toggle = not toggle

    print('</table>')

print('</body>')
print('</html>')

db.close()
