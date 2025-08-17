import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config['ALLOWED_ORIGINS'])
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    from .models import User, Problem, TestCase, Submission, Contest
    
    # Register blueprints
    from .api.auth import auth_bp
    from .api.problems import problems_bp
    from .api.submissions import submissions_bp
    from .api.contests import contests_bp
    from .api.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(problems_bp, url_prefix='/api/problems')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    app.register_blueprint(contests_bp, url_prefix='/api/contests')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    return app

def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'Access denied'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {'error': 'Rate limit exceeded', 'message': str(error.description)}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error', 'message': 'Something went wrong'}, 500

def register_cli_commands(app):
    """Register CLI commands."""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command()
    def seed_db():
        """Seed the database with sample data."""
        from .models import User, Problem, TestCase
        
        # Create admin user
        admin = User.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        admin.is_admin = True
        db.session.commit()
        
        # Create sample problem
        problem = Problem.create_problem(
            title='Two Sum',
            description="""Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:
Input: nums = [3,3], target = 6
Output: [0,1]""",
            difficulty='Easy',
            category='Array',
            created_by=admin.id,
            constraints="""Constraints:
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- Only one valid answer exists."""
        )
        
        # Add test cases
        TestCase.create_test_case(
            problem_id=problem.id,
            input_data='[2,7,11,15]\n9',
            expected_output='[0,1]',
            is_sample=True
        )
        
        TestCase.create_test_case(
            problem_id=problem.id,
            input_data='[3,2,4]\n6',
            expected_output='[1,2]',
            is_sample=True
        )
        
        TestCase.create_test_case(
            problem_id=problem.id,
            input_data='[3,3]\n6',
            expected_output='[0,1]',
            is_sample=False,
            is_hidden=True
        )
        
        print('Database seeded with sample data.')
    
    @app.cli.command()
    def create_admin():
        """Create an admin user."""
        username = input('Username: ')
        email = input('Email: ')
        password = input('Password: ')
        
        admin = User.create_user(username, email, password)
        admin.is_admin = True
        db.session.commit()
        
        print(f'Admin user {username} created successfully.')

# JWT token handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'error': 'Token has expired', 'message': 'Please log in again'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'error': 'Invalid token', 'message': 'Please provide a valid token'}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'error': 'Authorization token required', 'message': 'Please provide an access token'}, 401