# Backend API (Flask)

Base URL: http://localhost:5000

Auth: JWT Bearer tokens in `Authorization: Bearer <token>` header.

## Endpoints

- POST /auth/register
  - body: { email, username, password }
  - 201: { access_token, user }
- POST /auth/login
  - body: { emailOrUsername, password }
  - 200: { access_token, user }
- GET /auth/me
  - auth required
  - 200: user

- GET /challenges
  - 200: [ { id, slug, title, difficulty } ]
- GET /challenges/:slug
  - 200: { challenge: { id, slug, title, difficulty, description, starter_code }, public_test_cases: [ { id, challenge_id, is_hidden } ] }

- POST /submissions
  - auth required
  - body: { challengeSlug, language: 'python'|'node'|'cpp', code }
  - 201: { submissionId, status }
- GET /submissions/:id
  - auth required
  - 200: { id, user_id, challenge_id, language, status, runtime_ms, memory_kb, score }

- GET /leaderboard
  - 200: [ user ] sorted by rating desc

## Errors

Errors return JSON: { error: string } with appropriate HTTP status codes.

## Validation

- Email/username format validated, password length >= 6
- Languages limited to python, node, cpp

## Queue

- Redis list key `queue:submissions` enqueued with { submission_id, challenge_id, language, code }

## Firebase

- Worker writes results to `/submissions/{submissionId}` in RTDB.