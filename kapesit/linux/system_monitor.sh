#!/bin/bash

# Monitor system resources
function monitor_resources() {
    echo "CPU Usage: $(mpstat 1 1 | tail -n 1 | awk '{print $13}')%"
    echo "Memory Usage: $(free | grep Mem | awk '{print $3/$2 * 100.0}')%"
    echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"
}

# Check for system updates
function check_updates() {
    if [ -f /var/run/reboot-required ]; then
        echo "System reboot required"
    fi
    
    update_count=$(apt list --upgradable 2>/dev/null | wc -l)
    echo "Pending updates: $((update_count-1))"
}

# Monitor network connections
function monitor_network() {
    echo "Active connections:"
    netstat -tulpn | grep LISTEN
}

# Main monitoring loop
while true; do
    clear
    echo "=== System Monitoring ==="
    echo "$(date)"
    echo ""
    
    monitor_resources
    echo ""
    check_updates
    echo ""
    monitor_network
    
    sleep 5

done
