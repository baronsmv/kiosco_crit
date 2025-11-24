#!/bin/sh

chmod +x scripts/clean_output.sh
chmod +x scripts/carousel/fetch_espacios.sh
chmod +x scripts/carousel/run_carousel.sh

docker compose down
docker compose build
docker compose up
