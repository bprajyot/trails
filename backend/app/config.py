import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'coding_platform')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Redis Configuration
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}" if REDIS_PASSWORD else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 604800)))
    JWT_ALGORITHM = 'HS256'
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # Firebase Configuration
    FIREBASE_CONFIG = {
        'apiKey': os.environ.get('FIREBASE_API_KEY'),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'databaseURL': os.environ.get('FIREBASE_DATABASE_URL'),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.environ.get('FIREBASE_APP_ID'),
    }
    FIREBASE_PRIVATE_KEY_PATH = os.environ.get('FIREBASE_PRIVATE_KEY_PATH')
    
    # Code Execution Configuration
    DOCKER_HOST = os.environ.get('DOCKER_HOST', 'unix:///var/run/docker.sock')
    CODE_EXECUTION_TIMEOUT = int(os.environ.get('CODE_EXECUTION_TIMEOUT', 30))
    MAX_MEMORY_MB = int(os.environ.get('MAX_MEMORY_MB', 256))
    MAX_CPU_TIME = int(os.environ.get('MAX_CPU_TIME', 10))
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 100))
    RATE_LIMIT_PER_HOUR = int(os.environ.get('RATE_LIMIT_PER_HOUR', 1000))
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Pagination
    PROBLEMS_PER_PAGE = 20
    SUBMISSIONS_PER_PAGE = 50
    
    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'python': {
            'name': 'Python',
            'version': '3.9',
            'extension': '.py',
            'docker_image': 'coding-platform-python'
        },
        'javascript': {
            'name': 'JavaScript',
            'version': 'Node.js 18',
            'extension': '.js',
            'docker_image': 'coding-platform-javascript'
        },
        'java': {
            'name': 'Java',
            'version': '17',
            'extension': '.java',
            'docker_image': 'coding-platform-java'
        },
        'cpp': {
            'name': 'C++',
            'version': 'GCC 11',
            'extension': '.cpp',
            'docker_image': 'coding-platform-cpp'
        },
        'go': {
            'name': 'Go',
            'version': '1.19',
            'extension': '.go',
            'docker_image': 'coding-platform-go'
        }
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}