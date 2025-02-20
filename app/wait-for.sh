#!/bin/bash

host="$1"
shift
cmd="$@"

echo "Waiting for MySQL ($host)..."

until mysqladmin ping -h "$host" --silent; do
  echo "MySQL is unavailable - waiting..."
  sleep 2
done

echo "MySQL is up - executing command"
exec $cmd
