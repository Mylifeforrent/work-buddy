#!/bin/bash
# Check all mock services
for port in 8090 8081 8082 9200 9300 3001; do
    if curl -s -f http://localhost:$port/health > /dev/null; then
        echo "Service on port $port is UP"
    else
        echo "Service on port $port is DOWN"
        exit 1
    fi
done
echo "All mock services are healthy."
