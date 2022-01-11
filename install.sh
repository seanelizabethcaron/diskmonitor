#!/bin/bash

#
# Usage:
#  ./install.sh [destination directory]
#

# Check command line arguments
if [ -z "$1" ]; then
    INSTALL_DIR=/opt/csg
else
    INSTALL_DIR=$1
fi

go build diskmonitor_agent.go

go get github.com/go-sql-driver/mysql

go build diskmonitor_server.go

mkdir -p $INSTALL_DIR/{bin,etc}

cp diskmonitor_agent $INSTALL_DIR/bin
cp diskmonitor_server $INSTALL_DIR/bin
cp collector $INSTALL_DIR/bin
cp run_collection $INSTALL_DIR/bin

cp diskmonitor_server.conf $INSTALL_DIR/etc
cp dashboard.ini $INSTALL_DIR/etc
chmod 400 $INSTALL_DIR/etc/*

mkdir -p /usr/lib/cgi-bin/diskmonitor
cp diskmonitor.py /usr/lib/cgi-bin/diskmonitor/diskmonitor
chmod 755 /usr/lib/cgi-bin/diskmonitor/diskmonitor
