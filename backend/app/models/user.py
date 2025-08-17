from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for storing user account information."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    rating = db.Column(db.Integer, default=1200)
    total_submissions = db.Column(db.Integer, default=0)
    accepted_submissions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    created_problems = db.relationship('Problem', backref='creator', lazy='dynamic')
    created_contests = db.relationship('Contest', backref='creator', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_success_rate(self):
        """Calculate user's success rate."""
        if self.total_submissions == 0:
            return 0.0
        return (self.accepted_submissions / self.total_submissions) * 100
    
    def update_stats(self):
        """Update user statistics based on submissions."""
        from .submission import Submission
        
        self.total_submissions = self.submissions.count()
        self.accepted_submissions = self.submissions.filter_by(status='Accepted').count()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'rating': self.rating,
            'total_submissions': self.total_submissions,
            'accepted_submissions': self.accepted_submissions,
            'success_rate': self.get_success_rate(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
        
        if include_sensitive:
            data.update({
                'email': self.email,
                'is_admin': self.is_admin,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })
        
        return data
    
    @staticmethod
    def find_by_username(username):
        """Find user by username."""
        return User.query.filter_by(username=username, is_active=True).first()
    
    @staticmethod
    def find_by_email(email):
        """Find user by email."""
        return User.query.filter_by(email=email, is_active=True).first()
    
    @staticmethod
    def create_user(username, email, password, first_name=None, last_name=None):
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user