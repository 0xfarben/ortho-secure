#!/bin/bash

# MySQL wait script with improvements
host="$1"
shift
cmd="$@"

# Add timeout and better error handling
timeout=60  # 60 second timeout
counter=0

echo "Waiting for MySQL ($host)..."

until mysqladmin ping -h "$host" --silent; do
    echo "MySQL is unavailable - waiting... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
    
    if [ $counter -ge $timeout ]; then
        echo "ERROR: MySQL did not become available within $timeout seconds"
        exit 1
    fi
done

echo "MySQL is up - executing command"
exec "$cmd"