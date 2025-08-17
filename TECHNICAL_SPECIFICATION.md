# Coding Challenge Platform - Technical Specification

## System Architecture

### Overview
A full-stack web application for online coding challenges with real-time code execution, user management, and competitive features.

### Technology Stack
- **Frontend**: React.js 18+ with TypeScript, Tailwind CSS, Monaco Editor
- **Backend**: Python Flask with SQLAlchemy ORM
- **Databases**: 
  - MySQL 8.0+ (primary data storage)
  - Firebase Realtime Database (real-time features)
  - Redis 6.0+ (caching and sessions)
- **Code Execution**: Docker containers with language-specific images
- **Authentication**: JWT tokens with refresh mechanism

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Flask Backend  │    │  Code Executor  │
│   (Port 3000)   │◄──►│   (Port 5000)    │◄──►│   (Docker)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │     Data Layer       │
                    │  ┌────────────────┐  │
                    │  │     MySQL      │  │
                    │  │  (Port 3306)   │  │
                    │  └────────────────┘  │
                    │  ┌────────────────┐  │
                    │  │    Firebase    │  │
                    │  │   Realtime DB  │  │
                    │  └────────────────┘  │
                    │  ┌────────────────┐  │
                    │  │     Redis      │  │
                    │  │  (Port 6379)   │  │
                    │  └────────────────┘  │
                    └──────────────────────┘
```

## Database Schema

### MySQL Tables

#### Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    rating INT DEFAULT 1200,
    total_submissions INT DEFAULT 0,
    accepted_submissions INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### Problems Table
```sql
CREATE TABLE problems (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') NOT NULL,
    category VARCHAR(50),
    time_limit INT DEFAULT 2000,
    memory_limit INT DEFAULT 256,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

#### Test Cases Table
```sql
CREATE TABLE test_cases (
    id INT PRIMARY KEY AUTO_INCREMENT,
    problem_id INT NOT NULL,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    is_sample BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);
```

#### Submissions Table
```sql
CREATE TABLE submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    problem_id INT NOT NULL,
    language VARCHAR(20) NOT NULL,
    code TEXT NOT NULL,
    status ENUM('Pending', 'Running', 'Accepted', 'Wrong Answer', 'Time Limit Exceeded', 'Memory Limit Exceeded', 'Runtime Error', 'Compilation Error') DEFAULT 'Pending',
    runtime INT,
    memory_used INT,
    score DECIMAL(5,2) DEFAULT 0.00,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (problem_id) REFERENCES problems(id)
);
```

#### Contests Table
```sql
CREATE TABLE contests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    created_by INT,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### Firebase Realtime Database Structure
```json
{
  "submissions": {
    "submission_id": {
      "userId": "user_id",
      "problemId": "problem_id",
      "status": "Running",
      "timestamp": "2024-01-01T00:00:00Z",
      "testCaseResults": {
        "0": {"status": "Passed", "runtime": 100, "memory": 1024},
        "1": {"status": "Running", "runtime": null, "memory": null}
      }
    }
  },
  "leaderboard": {
    "contest_id": {
      "user_id": {
        "username": "john_doe",
        "score": 1500,
        "solvedProblems": 3,
        "lastSubmission": "2024-01-01T00:00:00Z"
      }
    }
  },
  "chat": {
    "room_id": {
      "messages": {
        "message_id": {
          "userId": "user_id",
          "username": "john_doe",
          "message": "Great problem!",
          "timestamp": "2024-01-01T00:00:00Z"
        }
      }
    }
  }
}
```

## Backend API Design

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user info

### Problem Endpoints
- `GET /api/problems` - List all problems (with pagination)
- `GET /api/problems/{id}` - Get specific problem
- `POST /api/problems` - Create new problem (admin only)
- `PUT /api/problems/{id}` - Update problem (admin only)
- `DELETE /api/problems/{id}` - Delete problem (admin only)

### Submission Endpoints
- `POST /api/submissions` - Submit solution
- `GET /api/submissions/{id}` - Get submission details
- `GET /api/submissions/user/{user_id}` - Get user's submissions
- `GET /api/submissions/problem/{problem_id}` - Get problem submissions

### Contest Endpoints
- `GET /api/contests` - List contests
- `GET /api/contests/{id}` - Get contest details
- `POST /api/contests` - Create contest (admin only)
- `GET /api/contests/{id}/leaderboard` - Get contest leaderboard

### User Endpoints
- `GET /api/users/{id}` - Get user profile
- `PUT /api/users/{id}` - Update user profile
- `GET /api/users/{id}/stats` - Get user statistics

## Frontend Component Structure

### Page Components
- `HomePage` - Landing page with featured problems
- `ProblemsPage` - Problem list with filters
- `ProblemDetailPage` - Individual problem with code editor
- `ContestsPage` - Contest list and details
- `LeaderboardPage` - Global and contest leaderboards
- `ProfilePage` - User profile and statistics
- `LoginPage` - Authentication forms

### Shared Components
- `Header` - Navigation and user menu
- `Sidebar` - Problem categories and filters
- `CodeEditor` - Monaco editor with language support
- `TestCaseRunner` - Test case execution and results
- `SubmissionHistory` - User's submission timeline
- `Leaderboard` - Ranking display component

### State Management
- Redux Toolkit for global state
- React Query for server state management
- Local state for component-specific data

## Code Execution Environment

### Docker Configuration
- Separate containers for each supported language
- Resource limits (CPU, memory, time)
- Network isolation for security
- File system restrictions

### Supported Languages
- Python 3.9+
- JavaScript (Node.js 18+)
- Java 17+
- C++ (GCC 11+)
- Go 1.19+

### Security Measures
- Sandboxed execution environment
- Input/output size limits
- Process monitoring and termination
- No network access for user code
- File system read-only access

## Security Best Practices

### Input Validation
- SQL injection prevention with parameterized queries
- XSS protection with input sanitization
- CSRF tokens for state-changing operations
- Rate limiting on API endpoints

### Authentication & Authorization
- JWT tokens with short expiration
- Refresh token rotation
- Role-based access control (RBAC)
- Password hashing with bcrypt

### Data Protection
- HTTPS enforcement
- Environment variable configuration
- Database connection encryption
- API key management

## Deployment Configuration

### Environment Variables
```bash
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=coding_platform
MYSQL_USER=platform_user
MYSQL_PASSWORD=secure_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# Firebase Configuration
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project.firebaseio.com
FIREBASE_PROJECT_ID=your_project_id

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Application Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your_flask_secret
ALLOWED_ORIGINS=http://localhost:3000
```

### Local Development Setup
1. Install Docker and Docker Compose
2. Set up MySQL and Redis containers
3. Configure Firebase project
4. Install Python and Node.js dependencies
5. Run database migrations
6. Start development servers

## Performance Considerations

### Caching Strategy
- Redis for session management
- API response caching for static data
- Database query optimization with indexes
- CDN for static assets

### Scalability
- Horizontal scaling with load balancers
- Database read replicas
- Message queues for background tasks
- Microservice architecture for large scale

## Monitoring and Analytics

### Logging
- Structured logging with JSON format
- Error tracking and alerting
- Performance monitoring
- User activity analytics

### Metrics
- API response times
- Database query performance
- Code execution statistics
- User engagement metrics