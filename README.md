# Coding Challenge Platform

A comprehensive online coding challenge platform similar to LeetCode, built with modern technologies for scalable and secure code execution.

## 🚀 Features

- **User Management**: Registration, authentication, and user profiles
- **Problem Management**: Create, edit, and organize coding problems
- **Code Editor**: Monaco editor with syntax highlighting and multiple language support
- **Real-time Code Execution**: Secure, sandboxed code execution with Docker
- **Contest System**: Organize and participate in coding contests
- **Leaderboards**: Track user rankings and performance
- **Submission History**: View and analyze past submissions
- **Admin Panel**: Comprehensive admin tools for platform management

## 🏗️ Architecture

### Technology Stack

- **Frontend**: React.js 18 with TypeScript, Tailwind CSS, Monaco Editor
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

## 📋 Prerequisites

- **Docker & Docker Compose**: For containerized services
- **Node.js 18+**: For frontend development
- **Python 3.9+**: For backend development
- **Git**: For version control

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd coding-challenge-platform
```

### 2. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This script will:
- Check prerequisites
- Install dependencies
- Create environment files
- Build Docker images
- Start database services
- Initialize the database with sample data

### 3. Configure Environment

Update the environment files with your configuration:

**Backend (`backend/.env`):**
```bash
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PASSWORD=secure_password

# Firebase Configuration
FIREBASE_API_KEY=your_api_key
FIREBASE_PROJECT_ID=your_project_id

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
```

**Frontend (`frontend/.env`):**
```bash
REACT_APP_API_URL=http://localhost:5000
REACT_APP_FIREBASE_API_KEY=your_api_key
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
```

### 4. Start Development Servers

```bash
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
```

Or start manually:

**Backend:**
```bash
cd backend
source venv/bin/activate
python run.py
```

**Frontend:**
```bash
cd frontend
npm start
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs

## 🔐 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

## 📁 Project Structure

```
coding-challenge-platform/
├── backend/                 # Flask backend
│   ├── app/                # Application package
│   │   ├── models/         # Database models
│   │   ├── api/           # API endpoints
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   ├── migrations/        # Database migrations
│   ├── tests/            # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API services
│   │   ├── store/        # Redux store
│   │   └── types/        # TypeScript types
│   └── package.json      # Node dependencies
├── docker/                # Docker configuration
│   ├── executor/         # Code execution containers
│   └── docker-compose.yml
├── scripts/              # Setup and deployment scripts
└── docs/                # Documentation
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user

### Problems
- `GET /api/problems` - List problems (with pagination)
- `GET /api/problems/{id}` - Get problem details
- `POST /api/problems` - Create problem (admin only)
- `PUT /api/problems/{id}` - Update problem (admin only)

### Submissions
- `POST /api/submissions` - Submit code
- `GET /api/submissions/{id}` - Get submission details
- `GET /api/submissions/user/{user_id}` - User's submissions

### Contests
- `GET /api/contests` - List contests
- `GET /api/contests/{id}` - Contest details
- `GET /api/contests/{id}/leaderboard` - Contest leaderboard

## 🐳 Docker Services

### Code Execution Containers

The platform supports multiple programming languages through dedicated Docker containers:

- **Python 3.9+**: `coding-platform-python`
- **JavaScript (Node.js 18+)**: `coding-platform-javascript`
- **Java 17+**: `coding-platform-java`
- **C++ (GCC 11+)**: `coding-platform-cpp`
- **Go 1.19+**: `coding-platform-go`

Each container is sandboxed with:
- Resource limits (CPU, memory, time)
- Network isolation
- File system restrictions
- Process monitoring

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Production Deployment

### Using Docker Compose

1. Update environment variables for production
2. Build production images:
   ```bash
   docker-compose -f docker/docker-compose.prod.yml build
   ```
3. Start services:
   ```bash
   docker-compose -f docker/docker-compose.prod.yml up -d
   ```

### Manual Deployment

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm run build
   # Serve build folder with nginx or similar
   ```

## 🔒 Security Features

- **Input Validation**: SQL injection and XSS prevention
- **Authentication**: JWT with refresh tokens
- **Authorization**: Role-based access control
- **Code Execution**: Sandboxed Docker containers
- **Rate Limiting**: API endpoint protection
- **HTTPS**: SSL/TLS encryption (production)

## 🚀 Performance Optimizations

- **Caching**: Redis for session and API response caching
- **Database**: Indexed queries and connection pooling
- **Frontend**: Code splitting and lazy loading
- **CDN**: Static asset delivery (production)

## 📊 Monitoring

- **Logging**: Structured JSON logging
- **Metrics**: API response times and error rates
- **Health Checks**: Service availability monitoring
- **Analytics**: User activity and submission statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` folder for detailed guides
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join our community discussions

## 🗺️ Roadmap

- [ ] Mobile responsive design improvements
- [ ] Additional programming languages support
- [ ] Advanced contest features (teams, divisions)
- [ ] Machine learning problem recommendations
- [ ] Code plagiarism detection
- [ ] Integration with external judges
- [ ] Advanced analytics dashboard

---

Built with ❤️ for the coding community