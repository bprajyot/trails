# Technical Specification: Local Coding Challenge Platform

## System Architecture

- Frontend: React (Vite), Tailwind CSS, Monaco Editor, communicates with Flask via REST and Firebase RTDB for live results.
- Backend: Flask app with JWT auth, SQLAlchemy ORM, Redis client for queueing submissions.
- Databases: MySQL for users/challenges/submissions; Firebase RTDB for submission results and analytics events.
- Executor: Python worker consuming Redis queue; runs user code inside Docker containers with resource limits; updates MySQL and posts results to Firebase RTDB.
- Communication:
  - Frontend -> Backend: HTTPS/HTTP REST
  - Backend -> Redis: job enqueue
  - Worker -> MySQL: status updates
  - Worker -> Firebase RTDB: write submission results

## Database Schema (MySQL)

- `users(id, email, username, password_hash, rating, created_at, updated_at)`
- `challenges(id, slug, title, difficulty, description, starter_code, created_at, updated_at)`
- `test_cases(id, challenge_id, input_text, expected_output, is_hidden, created_at)`
- `submissions(id, user_id, challenge_id, language, code, status, runtime_ms, memory_kb, score, created_at, updated_at)`
- `rating_history(id, user_id, previous_rating, new_rating, reason, created_at)`

Relationships:
- `test_cases.challenge_id -> challenges.id` (ON DELETE CASCADE)
- `submissions.user_id -> users.id` (ON DELETE CASCADE)
- `submissions.challenge_id -> challenges.id` (ON DELETE CASCADE)
- `rating_history.user_id -> users.id` (ON DELETE CASCADE)

Indexes:
- `challenges(difficulty)`, `submissions(user_id)`, `submissions(challenge_id)`, `submissions(status)`

Firebase RTDB structure:
- `/submissions/{submissionId}`: { status, results: [ { testCaseId, passed, runtimeMs, output } ], totalRuntimeMs }
- `/analytics/events/{uuid}`: optional analytics payloads (not implemented but reserved)

## Backend API Design

- Auth
  - POST `/auth/register`: { email, username, password } -> 201 { access_token, user }
  - POST `/auth/login`: { emailOrUsername, password } -> 200 { access_token, user }
  - GET `/auth/me` (JWT): -> 200 user
- Challenges
  - GET `/challenges` -> [ { id, slug, title, difficulty } ]
  - GET `/challenges/:slug` -> { challenge: {..., description, starter_code }, public_test_cases: [ { id, challenge_id, is_hidden } ] }
- Submissions
  - POST `/submissions` (JWT): { challengeSlug, language, code } -> 201 { submissionId, status }
  - GET `/submissions/:id` (JWT) -> submission object
- Leaderboard
  - GET `/leaderboard` -> top users by rating

Authentication:
- JWT access token in `Authorization: Bearer <token>`

Error handling:
- JSON: { error: string } and appropriate HTTP status codes (400, 401, 404, 409)

## Frontend Component Structure

- Routing
  - `/` HomePage: list challenges
  - `/login` LoginPage
  - `/register` RegisterPage
  - `/challenge/:slug` ChallengePage: code editor, submit button, live results
  - `/submissions` SubmissionsPage (placeholder)
- State Management
  - `AuthContext`: stores user + JWT, exposes axios instance with auth interceptor
  - Firebase live updates via RTDB for submissions
- Data fetching
  - Axios client in `AuthContext` for REST calls
- UI/UX flow
  - Login/Register -> browse challenges -> open challenge -> edit code -> submit -> observe live results

## Code Execution Environment

- Docker-based containers per language:
  - Python: `python:3.11-slim` run `python main.py`
  - Node.js: `node:20-alpine` run `node main.js`
  - C++: `gcc:13` compile with `g++ -O2 -std=c++17` then run `./app`
- Security/sandboxing (local):
  - No network `--network=none`
  - Memory limit `--memory=256m`, CPU limit `--cpus=0.5`
  - Read-only bind for source file; working directory isolated temp dir
  - Short runtime timeout (10s)

## Security Best Practices

- Server-side validation for input sizes and allowed languages
- Password hashing with PBKDF2 (Werkzeug)
- JWT for session, HTTPS recommended if exposed
- CORS limited to local dev origin
- Avoid exposing Docker socket in production; local dev only
- No hidden test cases returned to client; worker uses DB to validate

## Deployment (Local)

- Prereqs: Docker, Docker Compose, Node 18+ (optional)
- Env: copy `.env.example` -> `.env`, and `frontend/.env.example` -> `frontend/.env`
- Start: `docker compose up --build`
- Services:
  - Frontend: http://localhost:5173
  - Backend: http://localhost:5000
  - MySQL: port 3306 (initialized with SQL in `db/init`)
  - Redis: port 6379
  - Firebase: use emulator if configured

## Complete Codebase Overview

- `backend/` Flask app with blueprints: `auth`, `challenges`, `submissions`, `leaderboard`; SQLAlchemy models and session handling; Redis queue producer.
- `executor/` Worker that consumes Redis jobs, runs Docker containers, and publishes results to Firebase; updates MySQL submission status.
- `frontend/` Vite React app with Tailwind and Monaco editor; pages and shared auth context.
- `db/init/` MySQL schema and seed SQL for initial challenge and tests.
- `scripts/` helper scripts for setup and migrations.

## Maintainability Practices

- Modular services and well-defined interfaces (REST, Redis queue, Firebase RTDB)
- Clear environment-driven configuration
- ORM models and typed frontend components
- Small, focused blueprints and React components