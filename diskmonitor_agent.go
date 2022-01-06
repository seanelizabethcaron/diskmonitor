//
// Disk monitor agent, Sean Caron, scaron@umich.edu
//

package main

import (
    "os"
    "strings"
    "log"
    "net"
    "fmt"
    "bufio"
)

func main() {
    var serverFound, portFound, fileFound int
    var server, port, file string

    // Fail if we do not have the correct number of arguments
    if (len(os.Args) != 5) {
        log.Fatalf("Usage: %s -h [server] -p [port] -f [collection file]\n", os.Args[0])
    }

    // Filter out argument data
    for i := 1; i < len(os.Args); i++ {
        switch os.Args[i] {
            case "-h":
                server = os.Args[i+1]
                serverFound = 1
            case "-p":
                port = os.Args[i+1]
                portFound = 1
            case "-f":
                file = os.Args[i+1]
                fileFound = 1
        }
    }

    // Fail if a mandatory argument is missing
    if ((serverFound != 1) || (fileFound != 1) || (portFound != 1)) {
        log.Fatalf("Usage: %s -h [server] -p [port] -f [collection file]\n", os.Args[0])
    }

    // Determine our hostname
    host, _ := os.Hostname()

    if (strings.Index(host, ".") != -1) {
        host = host[0:strings.Index(host, ".")]
    }

    //
    // Read in disk data collection file
    //

    fi, err := os.Open(file)
    if err != nil {
        log.Fatalf("Error opening disk data collection file for reading")
    }

    defer fi.Close()

    var lines []string
    scanner := bufio.NewScanner(fi)
    for scanner.Scan() {
        lines = append(lines, scanner.Text())
    }

    //
    // Open the connection to the collection host
    //

    conn, err := net.Dial("tcp", server+":"+port)
    if err != nil {
        log.Fatalf("Error calling net.Dial()")
    }

    //
    // Send each line of the disk data file to the collection host
    //

    for _, li := range lines {
        fmt.Fprintf(conn, "%s %s\n", host, li)
    }

    conn.Close()
}
