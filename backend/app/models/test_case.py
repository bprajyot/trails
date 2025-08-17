from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TestCase(db.Model):
    """Test case model for storing problem test cases."""
    
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_sample = db.Column(db.Boolean, default=False)
    is_hidden = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional fields for test case management
    description = db.Column(db.String(200))  # Optional description for the test case
    weight = db.Column(db.Float, default=1.0)  # Weight for scoring
    time_limit_override = db.Column(db.Integer)  # Override problem's time limit
    memory_limit_override = db.Column(db.Integer)  # Override problem's memory limit
    
    def __repr__(self):
        return f'<TestCase {self.id} for Problem {self.problem_id}>'
    
    def get_input_preview(self, max_length=100):
        """Get a preview of the input data."""
        if len(self.input_data) <= max_length:
            return self.input_data
        return self.input_data[:max_length] + '...'
    
    def get_output_preview(self, max_length=100):
        """Get a preview of the expected output."""
        if len(self.expected_output) <= max_length:
            return self.expected_output
        return self.expected_output[:max_length] + '...'
    
    def to_dict(self, include_hidden=False):
        """Convert test case to dictionary."""
        data = {
            'id': self.id,
            'problem_id': self.problem_id,
            'is_sample': self.is_sample,
            'is_hidden': self.is_hidden,
            'description': self.description,
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Always include input and output for sample test cases
        # Only include for hidden test cases if explicitly requested
        if self.is_sample or include_hidden:
            data.update({
                'input_data': self.input_data,
                'expected_output': self.expected_output,
                'input_preview': self.get_input_preview(),
                'output_preview': self.get_output_preview()
            })
        else:
            # For hidden test cases, only show previews
            data.update({
                'input_preview': self.get_input_preview(50),
                'output_preview': self.get_output_preview(50)
            })
        
        # Include time and memory limit overrides if set
        if self.time_limit_override:
            data['time_limit'] = self.time_limit_override
        if self.memory_limit_override:
            data['memory_limit'] = self.memory_limit_override
        
        return data
    
    @staticmethod
    def get_sample_test_cases(problem_id):
        """Get all sample test cases for a problem."""
        return TestCase.query.filter_by(
            problem_id=problem_id, 
            is_sample=True
        ).order_by(TestCase.id).all()
    
    @staticmethod
    def get_all_test_cases(problem_id):
        """Get all test cases for a problem."""
        return TestCase.query.filter_by(
            problem_id=problem_id
        ).order_by(TestCase.id).all()
    
    @staticmethod
    def get_hidden_test_cases(problem_id):
        """Get all hidden test cases for a problem."""
        return TestCase.query.filter_by(
            problem_id=problem_id, 
            is_hidden=True
        ).order_by(TestCase.id).all()
    
    @staticmethod
    def create_test_case(problem_id, input_data, expected_output, 
                        is_sample=False, is_hidden=False, description=None, 
                        weight=1.0, time_limit_override=None, memory_limit_override=None):
        """Create a new test case."""
        test_case = TestCase(
            problem_id=problem_id,
            input_data=input_data,
            expected_output=expected_output,
            is_sample=is_sample,
            is_hidden=is_hidden,
            description=description,
            weight=weight,
            time_limit_override=time_limit_override,
            memory_limit_override=memory_limit_override
        )
        
        db.session.add(test_case)
        db.session.commit()
        
        return test_case
    
    @staticmethod
    def bulk_create_test_cases(problem_id, test_cases_data):
        """Create multiple test cases at once."""
        test_cases = []
        
        for tc_data in test_cases_data:
            test_case = TestCase(
                problem_id=problem_id,
                input_data=tc_data.get('input_data', ''),
                expected_output=tc_data.get('expected_output', ''),
                is_sample=tc_data.get('is_sample', False),
                is_hidden=tc_data.get('is_hidden', False),
                description=tc_data.get('description'),
                weight=tc_data.get('weight', 1.0),
                time_limit_override=tc_data.get('time_limit_override'),
                memory_limit_override=tc_data.get('memory_limit_override')
            )
            test_cases.append(test_case)
        
        db.session.add_all(test_cases)
        db.session.commit()
        
        return test_cases