# Project Structure

```
coding-challenge-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── problem.py
│   │   │   ├── submission.py
│   │   │   ├── contest.py
│   │   │   └── test_case.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── problems.py
│   │   │   ├── submissions.py
│   │   │   ├── contests.py
│   │   │   └── users.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── code_executor.py
│   │   │   ├── firebase_service.py
│   │   │   └── redis_service.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── decorators.py
│   │   │   ├── validators.py
│   │   │   └── helpers.py
│   │   └── config.py
│   ├── migrations/
│   │   ├── init_database.sql
│   │   └── seed_data.sql
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_problems.py
│   │   └── test_submissions.py
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Loading.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── problems/
│   │   │   │   ├── ProblemList.tsx
│   │   │   │   ├── ProblemCard.tsx
│   │   │   │   ├── ProblemDetail.tsx
│   │   │   │   └── ProblemFilters.tsx
│   │   │   ├── editor/
│   │   │   │   ├── CodeEditor.tsx
│   │   │   │   ├── TestCaseRunner.tsx
│   │   │   │   └── SubmissionResults.tsx
│   │   │   ├── contests/
│   │   │   │   ├── ContestList.tsx
│   │   │   │   ├── ContestDetail.tsx
│   │   │   │   └── Leaderboard.tsx
│   │   │   └── profile/
│   │   │       ├── UserProfile.tsx
│   │   │       ├── SubmissionHistory.tsx
│   │   │       └── UserStats.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── ProblemsPage.tsx
│   │   │   ├── ProblemDetailPage.tsx
│   │   │   ├── ContestsPage.tsx
│   │   │   ├── LeaderboardPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   └── LoginPage.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useProblems.ts
│   │   │   ├── useSubmissions.ts
│   │   │   └── useFirebase.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── firebase.ts
│   │   │   └── websocket.ts
│   │   ├── store/
│   │   │   ├── index.ts
│   │   │   ├── authSlice.ts
│   │   │   ├── problemsSlice.ts
│   │   │   └── submissionsSlice.ts
│   │   ├── types/
│   │   │   ├── auth.ts
│   │   │   ├── problem.ts
│   │   │   ├── submission.ts
│   │   │   └── contest.ts
│   │   ├── utils/
│   │   │   ├── constants.ts
│   │   │   ├── helpers.ts
│   │   │   └── validators.ts
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   └── components.css
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── setupTests.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── .env.example
├── docker/
│   ├── executor/
│   │   ├── python/
│   │   │   ├── Dockerfile
│   │   │   └── execute.py
│   │   ├── javascript/
│   │   │   ├── Dockerfile
│   │   │   └── execute.js
│   │   ├── java/
│   │   │   ├── Dockerfile
│   │   │   └── Execute.java
│   │   ├── cpp/
│   │   │   ├── Dockerfile
│   │   │   └── execute.cpp
│   │   └── go/
│   │       ├── Dockerfile
│   │       └── execute.go
│   └── docker-compose.yml
├── scripts/
│   ├── setup.sh
│   ├── start-dev.sh
│   ├── build-docker.sh
│   └── deploy.sh
├── docs/
│   ├── API.md
│   ├── SETUP.md
│   └── DEPLOYMENT.md
├── .gitignore
├── README.md
└── TECHNICAL_SPECIFICATION.md
```

## File Descriptions

### Backend Files
- **app/models/**: SQLAlchemy database models
- **app/api/**: Flask API route handlers
- **app/services/**: Business logic and external service integrations
- **app/utils/**: Utility functions and decorators
- **migrations/**: Database schema and seed data
- **tests/**: Unit and integration tests

### Frontend Files
- **components/**: Reusable React components organized by feature
- **pages/**: Top-level page components
- **hooks/**: Custom React hooks for data fetching and state
- **services/**: API clients and external service integrations
- **store/**: Redux store configuration and slices
- **types/**: TypeScript type definitions

### Docker Files
- **docker/executor/**: Language-specific execution containers
- **docker-compose.yml**: Local development environment setup

### Scripts
- **setup.sh**: Initial project setup and dependency installation
- **start-dev.sh**: Start development servers
- **build-docker.sh**: Build Docker images for code execution
- **deploy.sh**: Production deployment script