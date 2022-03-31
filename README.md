Disk Monitor
------------
Sean Caron (scaron@umich.edu)

Detailed multi-host monitoring of large JBOD arrays

Disk Monitor centralizes the gathering of SMART health data across a cluster of machines with JBOD
disk arrays composed of Enterprise SATA and SAS drives.

On the client, a UNIX shell script gathers SMART health data from each disk and prepares a properly
formatted output file aggregating the health data. A lightweight agent written in Go sends the disk
health data to a centralized collection server. The collection process is intended to run out of
cron, at any frequency desired by the user.

A collection server also written in Go accepts connections from clients and records each line of disk
health data in a per-host disk health table in a MySQL database.

A web dashboard written in Python allows for easy review of the aggregate disk health statistics for
all machines at a glance.

Disk Monitor offers a centralized system for monitoring the health of many disk drives across many
machines, permitting potential failures to be manually identified by system administrators that may
otherwise be missed by smartd or the standard md RAID disk failure process.

#### Database Setup

```
CREATE DATABASE diskmonitor;
USE diskmonitor

CREATE TABLE hosts (host varchar(32), hostid integer NOT NULL AUTO_INCREMENT PRIMARY KEY);

CREATE USER diskmon@'%';
SET PASSWORD FOR diskmon'@'%' = PASSWORD('as desired');
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, CREATE TEMPORARY TABLES,
  LOCK TABLES, EXECUTE, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, EVENT, TRIGGER
  ON diskmonitor.* to 'diskmon'@'%';
```

#### Installation

```
git clone http://github.com/seantcaron/diskmonitor
cd diskmonitor
chmod +x install.sh
./install.sh
```

##### Server

1. Edit configuration files to reflect the parameters that you used to set up the backing database.

2. Edit /etc/rc.local to start the collector service:

```
# Start up Disk Monitor server
/opt/csg/bin/diskmonitor_server -f /opt/csg/etc/diskmonitor_server.conf > /dev/null 2>&1 &
```

##### Client

1. Edit /opt/csg/bin/run_collection to set INSTALL_DIR.

2. Edit crontab for root on each client to add a line such as:

```
# Run Disk Monitor collection agent
0 0 * * * /opt/csg/bin/run_collection csgadmin.csgstat.sph.umich.edu > /dev/null 2>&1
```

#### Schema

Schema for host table:

```
CREATE TABLE hosts (host varchar(32), hostid integer NOT NULL AUTO_INCREMENT PRIMARY KEY);
```

Schema for per-host disk data tables:

```
CREATE TABLE [host]_sata (sampletime bigint, device varchar(16), device_type varchar(16), serial varchar(16), memberof_array varchar(16), smart_health varchar(16),
  raw_rd_err_rt integer, realloc_sec_ct integer, realloc_ev_ct integer, current_pending_ct integer, offline_uncorr_ct integer, udma_crc_err_ct integer);

CREATE TABLE [host]_sas (sampletime bigint, device varchar(16), device_type varchar(16), serial varchar(16), memberof_array varchar(16), smart_health varchar(16),
  rd_tot_corr integer, rd_tot_uncorr integer, wr_tot_corr integer, wr_tot_uncorr integer, vr_tot_corr integer, vr_tot_uncorr integer);
```
