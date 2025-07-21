FROM container-registry.oracle.com/mysql/community-server:8.4

# Copy SQL dump to initialization folder - This will Import the SQL files to DB for the first time.
COPY ./init.sql /docker-entrypoint-initdb.d/
