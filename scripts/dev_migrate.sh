#!/usr/bin/env bash
set -euo pipefail

echo "Resetting MySQL volume and re-initializing schema..."
docker compose down -v
docker compose up --build -d mysql

echo "Waiting for MySQL..."
sleep 10

docker compose up -d backend redis executor frontend

echo "Done."