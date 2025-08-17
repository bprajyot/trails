from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

class Problem(db.Model):
    """Problem model for storing coding challenge problems."""
    
    __tablename__ = 'problems'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Enum('Easy', 'Medium', 'Hard', name='difficulty_enum'), nullable=False)
    category = db.Column(db.String(50))
    time_limit = db.Column(db.Integer, default=2000)  # in milliseconds
    memory_limit = db.Column(db.Integer, default=256)  # in MB
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Additional fields for better problem management
    tags = db.Column(db.String(500))  # JSON string of tags
    hints = db.Column(db.Text)  # JSON string of hints
    editorial = db.Column(db.Text)  # Solution editorial
    constraints = db.Column(db.Text)  # Problem constraints
    
    # Statistics
    total_submissions = db.Column(db.Integer, default=0)
    accepted_submissions = db.Column(db.Integer, default=0)
    
    # Relationships
    test_cases = db.relationship('TestCase', backref='problem', lazy='dynamic', cascade='all, delete-orphan')
    submissions = db.relationship('Submission', backref='problem', lazy='dynamic')
    
    def __repr__(self):
        return f'<Problem {self.title}>'
    
    def get_acceptance_rate(self):
        """Calculate problem's acceptance rate."""
        if self.total_submissions == 0:
            return 0.0
        return (self.accepted_submissions / self.total_submissions) * 100
    
    def get_difficulty_color(self):
        """Get color code for difficulty."""
        colors = {
            'Easy': '#00b894',
            'Medium': '#fdcb6e',
            'Hard': '#e17055'
        }
        return colors.get(self.difficulty, '#74b9ff')
    
    def update_stats(self):
        """Update problem statistics based on submissions."""
        from .submission import Submission
        
        self.total_submissions = self.submissions.count()
        self.accepted_submissions = self.submissions.filter_by(status='Accepted').count()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_sample_test_cases(self):
        """Get sample test cases for display."""
        return self.test_cases.filter_by(is_sample=True).all()
    
    def get_all_test_cases(self):
        """Get all test cases including hidden ones."""
        return self.test_cases.all()
    
    def to_dict(self, include_test_cases=False, include_hidden=False):
        """Convert problem to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'difficulty': self.difficulty,
            'difficulty_color': self.get_difficulty_color(),
            'category': self.category,
            'time_limit': self.time_limit,
            'memory_limit': self.memory_limit,
            'tags': self.tags,
            'hints': self.hints,
            'constraints': self.constraints,
            'total_submissions': self.total_submissions,
            'accepted_submissions': self.accepted_submissions,
            'acceptance_rate': self.get_acceptance_rate(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_test_cases:
            if include_hidden:
                test_cases = self.get_all_test_cases()
            else:
                test_cases = self.get_sample_test_cases()
            
            data['test_cases'] = [tc.to_dict() for tc in test_cases]
        
        return data
    
    @staticmethod
    def find_by_slug(slug):
        """Find problem by slug."""
        return Problem.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def get_problems_by_difficulty(difficulty, page=1, per_page=20):
        """Get problems filtered by difficulty."""
        return Problem.query.filter_by(
            difficulty=difficulty, 
            is_active=True
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def get_problems_by_category(category, page=1, per_page=20):
        """Get problems filtered by category."""
        return Problem.query.filter_by(
            category=category, 
            is_active=True
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def search_problems(query, page=1, per_page=20):
        """Search problems by title or description."""
        return Problem.query.filter(
            db.or_(
                Problem.title.contains(query),
                Problem.description.contains(query)
            ),
            Problem.is_active == True
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def create_problem(title, description, difficulty, category=None, 
                      time_limit=2000, memory_limit=256, created_by=None, 
                      tags=None, hints=None, constraints=None):
        """Create a new problem."""
        # Generate slug from title
        import re
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        
        # Ensure slug is unique
        base_slug = slug
        counter = 1
        while Problem.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        problem = Problem(
            title=title,
            slug=slug,
            description=description,
            difficulty=difficulty,
            category=category,
            time_limit=time_limit,
            memory_limit=memory_limit,
            created_by=created_by,
            tags=tags,
            hints=hints,
            constraints=constraints
        )
        
        db.session.add(problem)
        db.session.commit()
        
        return problem