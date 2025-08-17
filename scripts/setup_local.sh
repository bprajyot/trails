#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
cp -n frontend/.env.example frontend/.env || true

echo "Building and starting services..."
docker compose up --build -d

echo "Waiting for services to become ready..."
sleep 8

echo "Services running. Backend: http://localhost:5000, Frontend: http://localhost:5173"