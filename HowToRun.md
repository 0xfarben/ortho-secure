## 1. Stop and Remove Containers and Volumes:
``` 
docker-compose down -v  
```

docker-compose down: Stops and removes all containers defined in your docker-compose.yml.
-v: Also removes any associated volumes. This ensures that all data is removed, including the MySQL data volume.

## 2. Rebuild Images:

```
docker-compose build
``` 

This will rebuild all images defined in your docker-compose.yml, including the MySQL image.

## 3. Start the Services:

```
docker-compose up -d
```

This will start all services defined in your docker-compose.yml with a clean slate