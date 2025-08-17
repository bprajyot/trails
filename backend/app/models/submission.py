from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

class Submission(db.Model):
    """Submission model for storing user code submissions."""
    
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    language = db.Column(db.String(20), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum(
            'Pending', 'Running', 'Accepted', 'Wrong Answer', 
            'Time Limit Exceeded', 'Memory Limit Exceeded', 
            'Runtime Error', 'Compilation Error', 'System Error',
            name='submission_status_enum'
        ), 
        default='Pending',
        nullable=False
    )
    runtime = db.Column(db.Integer)  # in milliseconds
    memory_used = db.Column(db.Integer)  # in KB
    score = db.Column(db.Numeric(5, 2), default=0.00)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional fields for better submission tracking
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'))  # Optional contest submission
    compiler_output = db.Column(db.Text)  # Compilation messages
    error_message = db.Column(db.Text)  # Runtime error details
    test_cases_passed = db.Column(db.Integer, default=0)
    total_test_cases = db.Column(db.Integer, default=0)
    
    # Execution details
    execution_id = db.Column(db.String(100))  # Unique execution identifier
    judged_at = db.Column(db.DateTime)  # When judging completed
    
    def __repr__(self):
        return f'<Submission {self.id} by User {self.user_id}>'
    
    def get_status_color(self):
        """Get color code for submission status."""
        colors = {
            'Pending': '#74b9ff',
            'Running': '#fdcb6e',
            'Accepted': '#00b894',
            'Wrong Answer': '#e17055',
            'Time Limit Exceeded': '#fd79a8',
            'Memory Limit Exceeded': '#a29bfe',
            'Runtime Error': '#e84393',
            'Compilation Error': '#636e72',
            'System Error': '#2d3436'
        }
        return colors.get(self.status, '#74b9ff')
    
    def get_success_rate(self):
        """Get test case pass rate."""
        if self.total_test_cases == 0:
            return 0.0
        return (self.test_cases_passed / self.total_test_cases) * 100
    
    def is_successful(self):
        """Check if submission was accepted."""
        return self.status == 'Accepted'
    
    def is_finished(self):
        """Check if submission judging is complete."""
        return self.status not in ['Pending', 'Running']
    
    def calculate_score(self):
        """Calculate submission score based on test cases passed."""
        if self.total_test_cases == 0:
            return 0.0
        
        # Full score for accepted submissions
        if self.status == 'Accepted':
            return 100.0
        
        # Partial score based on test cases passed
        return (self.test_cases_passed / self.total_test_cases) * 100
    
    def update_score(self):
        """Update submission score and save to database."""
        self.score = self.calculate_score()
        db.session.commit()
    
    def to_dict(self, include_code=False, include_sensitive=False):
        """Convert submission to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'language': self.language,
            'status': self.status,
            'status_color': self.get_status_color(),
            'runtime': self.runtime,
            'memory_used': self.memory_used,
            'score': float(self.score) if self.score else 0.0,
            'test_cases_passed': self.test_cases_passed,
            'total_test_cases': self.total_test_cases,
            'success_rate': self.get_success_rate(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'judged_at': self.judged_at.isoformat() if self.judged_at else None,
            'contest_id': self.contest_id
        }
        
        # Include code if requested (for user's own submissions)
        if include_code:
            data['code'] = self.code
        
        # Include sensitive debugging information if requested
        if include_sensitive:
            data.update({
                'compiler_output': self.compiler_output,
                'error_message': self.error_message,
                'execution_id': self.execution_id
            })
        
        return data
    
    @staticmethod
    def get_user_submissions(user_id, page=1, per_page=50):
        """Get paginated submissions for a user."""
        return Submission.query.filter_by(user_id=user_id)\
            .order_by(Submission.submitted_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_problem_submissions(problem_id, page=1, per_page=50):
        """Get paginated submissions for a problem."""
        return Submission.query.filter_by(problem_id=problem_id)\
            .order_by(Submission.submitted_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_user_problem_submissions(user_id, problem_id):
        """Get all submissions by a user for a specific problem."""
        return Submission.query.filter_by(
            user_id=user_id, 
            problem_id=problem_id
        ).order_by(Submission.submitted_at.desc()).all()
    
    @staticmethod
    def get_accepted_submissions(user_id=None, problem_id=None):
        """Get accepted submissions with optional filtering."""
        query = Submission.query.filter_by(status='Accepted')
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if problem_id:
            query = query.filter_by(problem_id=problem_id)
        
        return query.order_by(Submission.submitted_at.desc()).all()
    
    @staticmethod
    def get_recent_submissions(limit=10):
        """Get recent submissions across all users."""
        return Submission.query.order_by(
            Submission.submitted_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_contest_submissions(contest_id, user_id=None):
        """Get submissions for a contest."""
        query = Submission.query.filter_by(contest_id=contest_id)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(Submission.submitted_at.desc()).all()
    
    @staticmethod
    def create_submission(user_id, problem_id, language, code, contest_id=None):
        """Create a new submission."""
        submission = Submission(
            user_id=user_id,
            problem_id=problem_id,
            language=language,
            code=code,
            contest_id=contest_id,
            status='Pending'
        )
        
        db.session.add(submission)
        db.session.commit()
        
        return submission
    
    @staticmethod
    def update_submission_status(submission_id, status, runtime=None, 
                               memory_used=None, test_cases_passed=0, 
                               total_test_cases=0, compiler_output=None, 
                               error_message=None):
        """Update submission status and execution details."""
        submission = Submission.query.get(submission_id)
        if not submission:
            return None
        
        submission.status = status
        submission.runtime = runtime
        submission.memory_used = memory_used
        submission.test_cases_passed = test_cases_passed
        submission.total_test_cases = total_test_cases
        submission.compiler_output = compiler_output
        submission.error_message = error_message
        submission.judged_at = datetime.utcnow()
        
        # Update score
        submission.score = submission.calculate_score()
        
        db.session.commit()
        return submission