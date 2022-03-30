//
// Disk Monitor data collection server, Sean Caron, scaron@umich.edu
//

package main

import (
    "net"
    "os"
    "strings"
    "bufio"
    "log"
    "strconv"
    "time"
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
)

var dbUser, dbPass, dbName, dbHost, bindToAddr, bindToPort string

func main() {
    var conffile string

    // Fail if we do not have the correct number of arguments
    if (len(os.Args) != 3) {
        log.Fatalf("Usage: %s -f [configfile]\n", os.Args[0])
    }

    for i := 1; i < len(os.Args); i++ {
        switch os.Args[i] {
            case "-f":
                conffile = os.Args[i+1]
        }
    }

    // Open the config and read it in
    conf, err := os.Open(conffile)
    if err != nil {
        log.Fatalf("Failed opening configuration file for reading")
    }

    inp := bufio.NewScanner(conf)

    for inp.Scan() {
        line := inp.Text()

        if (len(line) > 0) {
            fields := strings.Fields(line)
            key := strings.ToLower(fields[0])

            switch key {
                case "dbuser":
                    dbUser = fields[1]
                case "dbpass":
                    dbPass = fields[1]
                case "dbname":
                    dbName = fields[1]
                case "dbhost":
                    dbHost = fields[1]
                case "bindtoaddr":
                    bindToAddr = fields[1]
                case "bindtoport":
                    bindToPort = fields[1]
                default:
                    log.Print("Ignoring nonsense configuration %s\n", fields[1])
            }
        }
    }

    conf.Close()

    // Start listening on our configured TCP port
    listener, err := net.Listen("tcp", bindToAddr+":"+bindToPort)
    if err != nil {
        log.Fatalf("Failure calling net.Listen()\n")
    }

    // Handle client connections
    for {
        conn, err := listener.Accept()
        if err != nil {
            continue
        }

        go handle_connection(conn)
    }
}

//
// Database schema:
//  CREATE TABLE hosts (host varchar(32), hostid integer NOT NULL AUTO_INCREMENT PRIMARY KEY);
//
// Per-host tables are created dynamically with the following schema:
//  CREATE TABLE [host]_sata (sampletime bigint, device varchar(16), device_type varchar(16), serial varchar(16), memberof_array varchar(16), smart_health varchar(16),
//    raw_rd_err_rt integer, realloc_sec_ct integer, realloc_ev_ct integer, current_pending_ct integer, offline_uncorr_ct integer, udma_crc_err_ct integer);
//
//  CREATE TABLE [host]_sas (sampletime bigint, device varchar(16), device_type varchar(16), serial varchar(16), memberof_array varchar(16), smart_health varchar(16),
//    rd_tot_corr integer, rd_tot_uncorr integer, wr_tot_corr integer, wr_tot_uncorr integer, vr_tot_corr integer, vr_tot_uncorr integer);
//

func handle_connection(c net.Conn) {
    var myDSN string
    var runPerHostTasks bool = true
    
    // Connect to the database
    myDSN = dbUser + ":" + dbPass + "@tcp(" + dbHost + ":3306)/" + dbName

    dbconn, dbConnErr := sql.Open("mysql", myDSN)
    if dbConnErr != nil {
        log.Fatalf("Failed connecting to database")
    }

    dbPingErr := dbconn.Ping()
    if dbPingErr != nil {         
        log.Fatalf("Failed pinging database connection")
    }

    // Generate a timestamp for these samples
    t := time.Now().Unix()
    tt := strconv.FormatInt(t, 10)

    // Set up to read input from the network connection
    input := bufio.NewScanner(c)
    
    // For each line, parse it and insert it into the database where it needs to go
    for input.Scan() {
        inp := input.Text()
        data := strings.Fields(inp)

        // Skip malformed input lines
        if (len(data) != 12) {
            continue
        }
        
        host := data[0]
        // MySQL will not accept table names with hyphens so convert hyphens in host names to underscore
        host = strings.ReplaceAll(host, "-", "_")
      
        device := data[1]
        device_type := data[2]
        serial := data[3]
        memberof_array := data[4]
        smart_health := data[5]
            
        if (runPerHostTasks) {
            //
            // Check to see if the host exists in the host tracking table
            //

            dbCmd := "SELECT COUNT(*) FROM hosts WHERE host = '" + host + "';"
            _, dbExecErr := dbconn.Exec(dbCmd)
            if dbExecErr != nil {
                log.Fatalf("Failed executing SELECT for host " + host)
            }

            var hostp string
            _ = dbconn.QueryRow(dbCmd).Scan(&hostp)
            hostpi, _ := strconv.Atoi(hostp)

            //
            // If not, add it to the hosts table. MySQL will generate an ID
            //

            if (hostpi == 0) {
                dbCmd := "INSERT INTO hosts (host) VALUES ('" + host + "');"
                _, dbExecErr = dbconn.Exec(dbCmd)
                if dbExecErr != nil {
                    log.Fatalf("Failed executing host table INSERT for host " + host)
                }
            }

            // Check to see if a per-host SATA disk data table exists for this host

            dbCmd = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '" + dbName + "' AND table_name = '" + host + "_sata';"
            _, dbExecErr = dbconn.Exec(dbCmd)
            if dbExecErr != nil {
                log.Fatalf("Failed executing SELECT FROM information_schema for host " + host)
            }

            var phdt_ct string
            _ = dbconn.QueryRow(dbCmd).Scan(&phdt_ct)
            phdt_cti, _ := strconv.Atoi(phdt_ct)

            //
            // If not, create a per-host SATA disk data table for the host
            // If so, clear out any old entries in the per-host disk data table
            //
          
            if (phdt_cti == 0) {
                dbCmd := "CREATE TABLE " + host + "_sata (sampletime bigint, device varchar(16), device_type varchar(16), serial varchar(16), memberof_array varchar(16), smart_health varchar(16), raw_rd_err_rt integer, realloc_sec_ct integer, realloc_ev_ct integer, current_pending_ct integer, offline_uncorr_ct integer, udma_crc_err_ct integer);"
                _, dbExecErr = dbconn.Exec(dbCmd)
                if dbExecErr != nil {
                    log.Fatalf("Failed executing CREATE TABLE for host " + host)
                }
            } else {
                dbCmd := "TRUNCATE TABLE " + host + "_sata;"
                _, dbExecErr = dbconn.Exec(dbCmd)
                if dbExecErr != nil {
                    log.Fatalf("Failed executing TRUNCATE for host " + host)
                }
            }
            
            // Check to see if a per-host SAS disk data table exists for this host
            dbCmd = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '" + dbName + "' AND table_name = '" + host + "_sas';"
            _, dbExecErr = dbconn.Exec(dbCmd)
            if dbExecErr != nil {
                log.Fatalf("Failed executing SELECT FROM information_schema for host " + host)
            }

            _ = dbconn.QueryRow(dbCmd).Scan(&phdt_ct)
            phdt_cti, _ = strconv.Atoi(phdt_ct)

            //
            // If not, create a per-host disk data table for the host
            // If so, clear out any old entries in the per-host disk data table
            //
          
            if (phdt_cti == 0) {
                dbCmd := "CREATE TABLE " + host + "_sas (sampletime bigint, device varchar(16), device_type varchar(16), serial varchar(16), memberof_array varchar(16), smart_health varchar(16), rd_tot_corr integer, rd_tot_uncorr integer, wr_tot_corr integer, wr_tot_uncorr integer, vr_tot_corr integer, vr_tot_uncorr integer);"
                _, dbExecErr = dbconn.Exec(dbCmd)
                if dbExecErr != nil {
                    log.Fatalf("Failed executing CREATE TABLE for host " + host)
                }
            } else {
                dbCmd := "TRUNCATE TABLE " + host + "_sas;"
                _, dbExecErr = dbconn.Exec(dbCmd)
                if dbExecErr != nil {
                    log.Fatalf("Failed executing TRUNCATE for host " + host)
                }
            }
            runPerHostTasks = false
        }
        
        //
        // Add this line of disk data entries to the requisite per-host disk data table
        //

        if (dev_type == "SATA") {
            dbCmd := "INSERT INTO " + host + "_sata VALUES (" + tt + ",'" + device + "','" + device_type + "','" + serial + "','" + memberof_array + "','" + smart_health + "'," + data[6] + "," + data[7] + "," + data[8] + "," + data[9] + "," + data[10] + "," + data[11] + ");"
            _, dbExecErr := dbconn.Exec(dbCmd)
            if dbExecErr != nil {
                log.Fatalf("Failed executing per-host disk table INSERT for host " + host)
            }
        } else {            
            dbCmd := "INSERT INTO " + host + "_sas VALUES (" + tt + ",'" + device + "','" + device_type + "','" + serial + "','" + memberof_array + "','" + smart_health + "'," + data[6] + "," + data[7] + "," + data[8] + "," + data[9] + "," + data[10] + "," + data[11] + ");"
            _, dbExecErr := dbconn.Exec(dbCmd)
            if dbExecErr != nil {
                log.Fatalf("Failed executing per-host disk table INSERT for host " + host)
            } 
        }
    }
  
    dbconn.Close()
    
    c.Close()
}
