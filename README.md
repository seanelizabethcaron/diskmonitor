Disk Monitor
------------
Sean Caron (scaron@umich.edu)

Detailed multi-host monitoring of large JBOD arrays

Disk Monitor centralizes the gathering of SMART health data across a cluster of machines with JBOD
disk arrays.

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

Database setup:

```
CREATE DATABASE diskmonitor;
USE diskmonitor
CREATE TABLE hosts (host varchar(32), hostid integer NOT NULL AUTO_INCREMENT PRIMARY KEY);
CREATE USER diskmon@'%';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, REFERENCES, INDEX, ALTER, CREATE TEMPORARY TABLES,
  LOCK TABLES, EXECUTE, CREATE VIEW, SHOW VIEW, CREATE ROUTINE, ALTER ROUTINE, EVENT, TRIGGER
  ON diskmonitor.* to 'diskmon'@'%';
```

Schema for host table:

```
CREATE TABLE hosts (host varchar(32), hostid integer NOT NULL AUTO_INCREMENT PRIMARY KEY);
```

Schema for per-host disk data tables:

```
CREATE TABLE [host] (device varchar(16), memberof_array varchar(16), smart_health varchar(16),
  raw_rd_err_rt integer, realloc_sec_ct integer, realloc_ev_ct integer, current_pending_ct integer,
  offline_uncorr_ct integer, udma_crc_err_ct integer);
```
