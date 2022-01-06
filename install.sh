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

mkdir -p $INSTALL_DIR/diskmonitor/{bin,etc}

cp diskmonitor_agent $INSTALL_DIR/diskmonitor/bin
cp diskmonitor_server $INSTALL_DIR/diskmonitor/bin
cp collector $INSTALL_DIR/diskmonitor/bin
cp run_collection $INSTALL_DIR/diskmonitor/bin

cp diskmonitor_server.conf $INSTALL_DIR/diskmonitor/etc
cp dashboard.ini $INSTALL_DIR/diskmonitor/etc
