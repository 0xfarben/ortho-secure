#!/bin/bash

# Use environment variables for secrets (from K8s Secret or Docker Compose)
export MYSQL_USER=${MYSQL_USER}
export MYSQL_PASSWORD=${MYSQL_PASSWORD}
export MYSQL_DATABASE=${MYSQL_DATABASE}

host="${MYSQL_HOST:-$1}"
shift
cmd="$@"

echo "Final values:"
echo "MYSQL_USER: $MYSQL_USER"
echo "MYSQL_PASSWORD length: ${#MYSQL_PASSWORD}"
echo "MYSQL_DATABASE: $MYSQL_DATABASE"

echo "Waiting for MySQL ($host)..."
echo "Host: $host, User: $MYSQL_USER, DB: $MYSQL_DATABASE"

until mysql -h "$host" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "USE $MYSQL_DATABASE; SHOW TABLES;" 2>/dev/null; do
  echo "MySQL is unavailable or DB not ready - waiting..."
  sleep 2
done

echo "MySQL and DB are ready - executing command"
exec $cmd