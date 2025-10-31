#!/bin/bash

# Prompt for the stock ticker
#read -p "Input stock ticker: " ticker

# Bring down the current Docker Compose setup
docker-compose down

# Create the Docker volume
docker volume create cache_volume

# Build the new Docker Compose setup
docker-compose build

# List all containers and get their IDs
CONTAINERS=$(docker ps -a -q)

# Convert the list of container IDs into an array
CONTAINER_ARRAY=($CONTAINERS)

# Ensure containers are running in privileged mode
#for container_id in "${CONTAINER_ARRAY[@]}"; do
#  docker update --privileged=true $container_id
#done

# Start the first and second containers
docker start ${CONTAINER_ARRAY[0]}
docker start ${CONTAINER_ARRAY[1]}

# Remove the existing cache file in the cache volume
docker exec -it stock_app-app sh -c "rm /app/cache.json"

# Run the app container interactively with the ticker environment variable
docker-compose run -e TICKER=$ticker app