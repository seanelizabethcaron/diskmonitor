#!/usr/bin/python

# Pull data from the Disk Monitor database and generate the Web dashboard
#  Sean Caron (scaron@umich.edu)

import cgi, time, sys, MySQLdb, ConfigParser

print('Content-type: text/html\n')
print('<html>')
print('<head>')
print('<title>Disk Monitor</title>')
print('<meta http-equiv="refresh" content="600">')
print('<style type="text/css">* { border-radius: 5px; } h1 { font-family: Arial, Helvetica; } h2 { font-family: Arial, Helvetica; } p { font-size: x-large; font-weight: bold; font-family: Arial, Helvetica; width: 90%; margin: 10px auto; } table { table-layout: fixed; margin: 10px auto; width: 90%; } th { font-size: medium; font-family: Arial, Helvetica; } td { 0px; font-size: medium; font-family: Courier; }</style>')
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

# Print table of contents at top of page
for host in hosts:
    displayhost = host[0].replace("_", "-")

    print('<li><font face="Arial, Helvetia"><a href=\"#' + displayhost + '\">' + displayhost + '</a></font></li>')

print('</ul>')

# Print disk information for each host
for host in hosts:
    # Print the header
    displayhost = host[0].replace("_", "-")
    print('<p><a name=\"' + displayhost + '\">' + displayhost + '</a></p>')
    
    # Determine how many SATA disks we have
    query = 'SELECT COUNT(*) FROM ' + host[0] + '_sata;'
    curs.execute(query)
    num_sata = curs.fetchone()
    
    # If there are SATA disks for this host, print their statistics
    if (num_sata[0] > 0):
        query = 'SELECT * FROM ' + host[0] + '_sata;'
        curs.execute(query)

        disks = curs.fetchall()

        toggle = 0

        print('<table>')
        print('<tr><th>device</th><th>type</th><th>serial</th><th>memberof_array</th><th>smart_health</th><th>raw_rd_err_rt</th><th>realloc_sec</th><th>realloc_ev</th><th>curr_pend</th><th>offline_uncorr</th><th>udma_crc_err</th></tr>')
        for row in disks:
            if 'FAIL' in row[3]:
                print('<tr bgcolor=#ffcccc><td>')
                red_disks = red_disks + 1
            elif row[7] > 0 or row[8] > 0 or row[9] > 0 or row[10] > 0:
                if row[7] > 100 or row[8] > 100 or row[9] > 100 or row[10] > 100:
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
            print('</td><td>')
            print(row[10])
            print('</td><td>')
           print('</td><td>')
            print(row[11])
            print('</td></tr>')

            toggle = not toggle
            total_disks = total_disks + 1

    print('</table>')

    # Determine how many SAS disks we have
    query = 'SELECT COUNT(*) FROM ' + host[0] + '_sas;'
    curs.execute(query)
    num_sas = curs.fetchone()
    
    # If there are SAS disks for this host, print their statistics
    if (num_sas[0] > 0):
        query = 'SELECT * FROM ' + host[0] + '_sas;'
        curs.execute(query)

        disks = curs.fetchall()

        toggle = 0

        print('<table>')
        print('<tr><th>device</th><th>type</th><th>serial</th><th>memberof_array</th><th>smart_health</th><th>rd_tot_corr</th><th>rd_tot_uncorr</th><th>wr_tot_corr</th><th>wr_tot_uncorr</th><th>vr_tot_corr</th><th>vr_tot_uncorr</th></tr>')
        for row in disks:
            if 'FAIL' in row[3]:
                print('<tr bgcolor=#ffcccc><td>')
                red_disks = red_disks + 1
            elif row[7] > 0 or row[8] > 0 or row[9] > 0 or row[10] > 0:
                if row[7] > 100 or row[8] > 100 or row[9] > 100 or row[10] > 100:
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
            print('</td><td>')
            print(row[10])
            print('</td><td>')
            print(row[11])
            print('</td></tr>')

            toggle = not toggle
            total_disks = total_disks + 1

    print('</table>')

# Print some statistics for all disks in total
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
