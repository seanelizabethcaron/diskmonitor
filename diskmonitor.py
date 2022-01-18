#!/usr/bin/python

# Pull data from the Disk Monitor database and generate the Web dashboard
#  Sean Caron (scaron@umich.edu)

import cgi, time, sys, MySQLdb, ConfigParser

print('Content-type: text/html\n')
print('<html>')
print('<head>')
print('<title>Disk Monitor</title>')
print('<meta http-equiv="refresh" content="600">')
print('<style type="text/css">* { border-radius: 5px; } h1 { font-family: Arial, Helvetica; } h2 { font-family: Arial, Helvetica; } p { font-size: x-large; font-weight: bold; font-family: Arial, Helvetica; width: 80%; margin: 10px auto; } table { height: 15%; margin: 10px auto; width: 80%; } th { font-family: Arial, Helvetica; } td { 0px; font-family: Courier; }</style>')
print('</head>')
print('<body bgcolor=White text=Black vlink=Black link=Black>')
print('<h2>Disk Monitor: ' + time.strftime("%A %b %d %H:%M:%S %Z", time.localtime()) + '</h2>')

cfg = ConfigParser.ConfigParser()
cfg.read('/opt/csg/etc/dashboard.ini')

dbuser = cfg.get('database', 'user')
dbpass = cfg.get('database', 'passwd')
dbname = cfg.get('database', 'db')
dbhost = cfg.get('database', 'host')

total_disks = 0
yellow_disks = 0
red_disks = 0

db = MySQLdb.connect(host=dbhost,user=dbuser,passwd=dbpass,db=dbname)

curs = db.cursor()

query = 'SELECT host,hostid from hosts ORDER BY host ASC;'
curs.execute(query)
hosts = curs.fetchall()

print('<ul>')

for host in hosts:
    displayhost = host[0].replace("_", "-")

    print('<li><font face="Arial, Helvetia"><a href=\"#' + displayhost + '\">' + displayhost + '</a></font></li>')

print('</ul>')

for host in hosts:
    query = 'SELECT * FROM ' + host[0] + ';'

    curs.execute(query)

    disks = curs.fetchall()

    toggle = 0

    displayhost = host[0].replace("_", "-")

    print('<p><a name=\"' + displayhost + '\">' + displayhost + '</a></p>')
    print('<table>')
    print('<tr><th>device</th><th>memberof_array</th><th>smart_health</th><th>raw_rd_err_rt</th><th>realloc_sec_ct</th><th>realloc_ev_ct</th><th>current_pending_ct</th><th>offline_uncorr_ct</th><th>udma_crc_err_ct</th></tr>')
    for row in disks:
        if 'FAIL' in row[3]:
            print('<tr bgcolor=#ffcccc><td>')
            red_disks = red_disks + 1
        elif row[5] > 0 or row[6] > 0 or row[7] > 0 or row[8] > 0:
            if row[5] > 100 or row[6] > 100 or row[7] > 100 or row[8] > 100:
                print('<tr bgcolor=#ffcccc><td>')
                red_disks = red_disks + 1
            else:
                print('<tr bgcolor=#ffffcc><td>')
                yellow_disks = yellow_disks + 1
        else:
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
        print('</td><td>')
        print(row[5])
        print('</td><td>')
        print(row[6])
        print('</td><td>')
        print(row[7])
        print('</td><td>')
        print(row[8])
        print('</td><td>')
        print(row[9])
        print('</td><tr>')

        toggle = not toggle
        total_disks = total_disks + 1

    print('</table>')

print('<font face="Arial, Helvetica">')
print('<br>')
print('Total disks monitored: ' + str(total_disks))
print('<br>')
print('Total disks in RED status: ' + str(red_disks))
print('<br>')
print('Total disks in YELLOW status: ' + str(yellow_disks))
print('</font>')

print('</body>')
print('</html>')

db.close()
