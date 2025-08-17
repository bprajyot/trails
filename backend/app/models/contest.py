from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for contest-problem many-to-many relationship
contest_problems = db.Table('contest_problems',
    db.Column('contest_id', db.Integer, db.ForeignKey('contests.id'), primary_key=True),
    db.Column('problem_id', db.Integer, db.ForeignKey('problems.id'), primary_key=True),
    db.Column('problem_order', db.Integer, default=0),  # Order of problem in contest
    db.Column('points', db.Integer, default=100),  # Points for solving this problem
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)

# Association table for contest participants
contest_participants = db.Table('contest_participants',
    db.Column('contest_id', db.Integer, db.ForeignKey('contests.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow),
    db.Column('is_registered', db.Boolean, default=True)
)

class Contest(db.Model):
    """Contest model for storing coding contests."""
    
    __tablename__ = 'contests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Contest settings
    max_participants = db.Column(db.Integer)  # Optional participant limit
    registration_start = db.Column(db.DateTime)  # When registration opens
    registration_end = db.Column(db.DateTime)  # When registration closes
    is_rated = db.Column(db.Boolean, default=True)  # Affects user ratings
    
    # Contest type and rules
    contest_type = db.Column(
        db.Enum('Individual', 'Team', 'Educational', name='contest_type_enum'),
        default='Individual'
    )
    scoring_type = db.Column(
        db.Enum('ACM', 'IOI', 'AtCoder', name='scoring_type_enum'),
        default='ACM'
    )
    
    # Penalty settings (for ACM-style contests)
    penalty_per_wrong_submission = db.Column(db.Integer, default=20)  # minutes
    
    # Relationships
    problems = db.relationship('Problem', secondary=contest_problems, backref='contests')
    participants = db.relationship('User', secondary=contest_participants, backref='participated_contests')
    submissions = db.relationship('Submission', backref='contest', lazy='dynamic')
    
    def __repr__(self):
        return f'<Contest {self.title}>'
    
    def is_upcoming(self):
        """Check if contest hasn't started yet."""
        return datetime.utcnow() < self.start_time
    
    def is_ongoing(self):
        """Check if contest is currently running."""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time
    
    def is_finished(self):
        """Check if contest has ended."""
        return datetime.utcnow() > self.end_time
    
    def get_status(self):
        """Get contest status string."""
        if self.is_upcoming():
            return 'Upcoming'
        elif self.is_ongoing():
            return 'Running'
        else:
            return 'Finished'
    
    def get_duration_minutes(self):
        """Get contest duration in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    def can_register(self, user_id=None):
        """Check if registration is open."""
        now = datetime.utcnow()
        
        # Check if registration period is set and valid
        if self.registration_start and now < self.registration_start:
            return False
        if self.registration_end and now > self.registration_end:
            return False
        
        # Check if contest hasn't started
        if not self.is_upcoming():
            return False
        
        # Check participant limit
        if self.max_participants:
            current_participants = len(self.participants)
            if current_participants >= self.max_participants:
                return False
        
        return True
    
    def is_user_registered(self, user_id):
        """Check if user is registered for contest."""
        from .user import User
        user = User.query.get(user_id)
        return user in self.participants if user else False
    
    def get_participant_count(self):
        """Get number of registered participants."""
        return len(self.participants)
    
    def get_leaderboard(self, limit=None):
        """Get contest leaderboard."""
        # This would typically involve complex scoring calculations
        # For now, return a basic structure
        leaderboard = []
        
        for participant in self.participants:
            # Get user's submissions for this contest
            user_submissions = self.submissions.filter_by(user_id=participant.id).all()
            
            # Calculate score based on contest type
            score = self.calculate_user_score(participant.id, user_submissions)
            
            leaderboard.append({
                'user_id': participant.id,
                'username': participant.username,
                'score': score,
                'solved_problems': len([s for s in user_submissions if s.status == 'Accepted']),
                'total_submissions': len(user_submissions)
            })
        
        # Sort by score descending
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        if limit:
            leaderboard = leaderboard[:limit]
        
        return leaderboard
    
    def calculate_user_score(self, user_id, submissions=None):
        """Calculate user's score in this contest."""
        if submissions is None:
            submissions = self.submissions.filter_by(user_id=user_id).all()
        
        if self.scoring_type == 'ACM':
            return self.calculate_acm_score(submissions)
        elif self.scoring_type == 'IOI':
            return self.calculate_ioi_score(submissions)
        else:
            return self.calculate_basic_score(submissions)
    
    def calculate_acm_score(self, submissions):
        """Calculate ACM-style score (problems solved + time penalty)."""
        solved_problems = set()
        total_penalty = 0
        problem_attempts = {}
        
        for submission in submissions:
            problem_id = submission.problem_id
            
            if problem_id not in problem_attempts:
                problem_attempts[problem_id] = 0
            
            if submission.status == 'Accepted' and problem_id not in solved_problems:
                solved_problems.add(problem_id)
                # Time penalty: minutes from contest start + wrong submission penalty
                time_penalty = int((submission.submitted_at - self.start_time).total_seconds() / 60)
                wrong_submission_penalty = problem_attempts[problem_id] * self.penalty_per_wrong_submission
                total_penalty += time_penalty + wrong_submission_penalty
            elif submission.status != 'Accepted':
                problem_attempts[problem_id] += 1
        
        return {
            'problems_solved': len(solved_problems),
            'total_penalty': total_penalty,
            'score': len(solved_problems) * 1000 - total_penalty  # Higher is better
        }
    
    def calculate_ioi_score(self, submissions):
        """Calculate IOI-style score (sum of best scores per problem)."""
        problem_scores = {}
        
        for submission in submissions:
            problem_id = submission.problem_id
            score = float(submission.score) if submission.score else 0.0
            
            if problem_id not in problem_scores:
                problem_scores[problem_id] = 0.0
            
            problem_scores[problem_id] = max(problem_scores[problem_id], score)
        
        total_score = sum(problem_scores.values())
        return {
            'total_score': total_score,
            'problems_attempted': len(problem_scores),
            'score': total_score
        }
    
    def calculate_basic_score(self, submissions):
        """Calculate basic score (number of accepted submissions)."""
        accepted_count = len([s for s in submissions if s.status == 'Accepted'])
        return {
            'accepted_submissions': accepted_count,
            'score': accepted_count
        }
    
    def to_dict(self, include_problems=False, include_participants=False):
        """Convert contest to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.get_duration_minutes(),
            'status': self.get_status(),
            'is_public': self.is_public,
            'is_rated': self.is_rated,
            'contest_type': self.contest_type,
            'scoring_type': self.scoring_type,
            'max_participants': self.max_participants,
            'participant_count': self.get_participant_count(),
            'registration_start': self.registration_start.isoformat() if self.registration_start else None,
            'registration_end': self.registration_end.isoformat() if self.registration_end else None,
            'can_register': self.can_register(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_problems:
            data['problems'] = [p.to_dict() for p in self.problems]
        
        if include_participants:
            data['participants'] = [p.to_dict() for p in self.participants]
        
        return data
    
    @staticmethod
    def get_upcoming_contests():
        """Get all upcoming contests."""
        return Contest.query.filter(
            Contest.start_time > datetime.utcnow(),
            Contest.is_public == True
        ).order_by(Contest.start_time).all()
    
    @staticmethod
    def get_ongoing_contests():
        """Get all ongoing contests."""
        now = datetime.utcnow()
        return Contest.query.filter(
            Contest.start_time <= now,
            Contest.end_time >= now,
            Contest.is_public == True
        ).all()
    
    @staticmethod
    def get_finished_contests():
        """Get all finished contests."""
        return Contest.query.filter(
            Contest.end_time < datetime.utcnow(),
            Contest.is_public == True
        ).order_by(Contest.end_time.desc()).all()
    
    @staticmethod
    def create_contest(title, description, start_time, end_time, 
                      created_by=None, is_public=True, contest_type='Individual',
                      scoring_type='ACM', max_participants=None):
        """Create a new contest."""
        contest = Contest(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            created_by=created_by,
            is_public=is_public,
            contest_type=contest_type,
            scoring_type=scoring_type,
            max_participants=max_participants
        )
        
        db.session.add(contest)
        db.session.commit()
        
        return contest