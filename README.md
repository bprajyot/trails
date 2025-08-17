# Online Coding Challenge Platform (Local)

A minimal LeetCode-like platform for local development.

- Front-End: React (Vite), Tailwind CSS, Monaco Editor
- Back-End: Flask (REST), SQLAlchemy, JWT Auth, Redis
- Databases: MySQL (users, challenges, submissions), Firebase RTDB (submission results, analytics)
- Executor: Python worker running sandboxed jobs in Docker containers

## Quick Start (Local)

1) Prerequisites
- Docker Desktop or Docker Engine + Docker Compose
- Node.js 18+ and npm (optional if you run frontend via Docker)

2) Environment
- Copy `.env.example` to `.env` and adjust values
- Copy `frontend/.env.example` to `frontend/.env` and adjust

3) Start stack
```bash
docker compose up --build
```

4) First run notes
- MySQL will initialize schema using `db/init/001_init.sql`
- Backend available at `http://localhost:5000`
- Frontend available at `http://localhost:5173`
- Redis at `localhost:6379`

5) Firebase Emulator (optional)
- Install firebase-tools: `npm i -g firebase-tools`
- Run emulator in another terminal: `firebase emulators:start --only database` (or connect to a real project)
- Configure `VITE_USE_FIREBASE_EMULATOR=true` in `frontend/.env`

## Services

- Frontend (Vite React): serves UI, connects to Flask API and Firebase RTDB
- Backend (Flask): authentication, challenge metadata, submission creation and status, leaderboard
- Executor (Worker): consumes jobs from Redis, runs them in language containers, updates MySQL + Firebase
- MySQL: persistent relational store
- Redis: queues, caches

## Code Execution

- Jobs are enqueued by backend to `queue:submissions` (Redis)
- Executor pulls jobs, creates a temp workspace, runs user code inside Docker (restricted resources)
- Test results posted to Firebase `/submissions/{submissionId}` and MySQL `submissions`

## Authentication

- JWT access tokens (HTTP Authorization: Bearer <token>)
- Passwords hashed with Werkzeug (PBKDF2)

## Directory Structure

```
backend/
executor/
frontend/
db/init/
scripts/
```

## Common Commands

- Start: `docker compose up --build`
- Stop: `docker compose down`
- Reset DB: `docker compose down -v && docker compose up --build`

## Security Notes (Local)

- The executor mounts Docker socket to run language containers. This is acceptable for local dev only.
- Never expose this configuration to the internet.
- Validate inputs on both client and server.