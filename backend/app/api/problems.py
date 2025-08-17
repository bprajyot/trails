from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, ValidationError
from ..models.problem import Problem, db
from ..models.test_case import TestCase
from ..models.user import User
from ..utils.validators import (
    validate_problem_title, validate_problem_difficulty, 
    validate_pagination, sanitize_html
)

problems_bp = Blueprint('problems', __name__)

# Validation schemas
class ProblemSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    difficulty = fields.Str(required=True)
    category = fields.Str(required=False)
    time_limit = fields.Int(required=False, missing=2000)
    memory_limit = fields.Int(required=False, missing=256)
    tags = fields.Str(required=False)
    hints = fields.Str(required=False)
    constraints = fields.Str(required=False)
    editorial = fields.Str(required=False)

class TestCaseSchema(Schema):
    input_data = fields.Str(required=True)
    expected_output = fields.Str(required=True)
    is_sample = fields.Bool(required=False, missing=False)
    is_hidden = fields.Bool(required=False, missing=False)
    description = fields.Str(required=False)
    weight = fields.Float(required=False, missing=1.0)

def require_admin():
    """Decorator to require admin privileges."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_admin:
                return {'error': 'Admin privileges required'}, 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@problems_bp.route('', methods=['GET'])
def get_problems():
    """Get list of problems with filtering and pagination."""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    difficulty = request.args.get('difficulty')
    category = request.args.get('category')
    search = request.args.get('search')
    
    try:
        page, per_page = validate_pagination(page, per_page, max_per_page=50)
    except ValidationError as e:
        return {'error': str(e)}, 400
    
    # Build query
    query = Problem.query.filter_by(is_active=True)
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Problem.title.like(search_term),
                Problem.description.like(search_term)
            )
        )
    
    # Order by creation date (newest first)
    query = query.order_by(Problem.created_at.desc())
    
    # Paginate
    problems = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return {
        'problems': [p.to_dict() for p in problems.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': problems.total,
            'pages': problems.pages,
            'has_next': problems.has_next,
            'has_prev': problems.has_prev
        }
    }

@problems_bp.route('/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    """Get a specific problem by ID."""
    problem = Problem.query.get_or_404(problem_id)
    
    if not problem.is_active:
        return {'error': 'Problem not found'}, 404
    
    # Check if user is authenticated to determine what test cases to show
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id) if current_user_id else None
        include_hidden = user and user.is_admin
    except:
        include_hidden = False
    
    return {
        'problem': problem.to_dict(
            include_test_cases=True, 
            include_hidden=include_hidden
        )
    }

@problems_bp.route('/slug/<string:slug>', methods=['GET'])
def get_problem_by_slug(slug):
    """Get a specific problem by slug."""
    problem = Problem.find_by_slug(slug)
    
    if not problem:
        return {'error': 'Problem not found'}, 404
    
    # Check if user is authenticated to determine what test cases to show
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id) if current_user_id else None
        include_hidden = user and user.is_admin
    except:
        include_hidden = False
    
    return {
        'problem': problem.to_dict(
            include_test_cases=True, 
            include_hidden=include_hidden
        )
    }

@problems_bp.route('', methods=['POST'])
@jwt_required()
@require_admin()
def create_problem():
    """Create a new problem (admin only)."""
    try:
        schema = ProblemSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {'error': 'Validation failed', 'messages': err.messages}, 400
    
    # Validate and sanitize data
    try:
        title = validate_problem_title(data['title'])
        difficulty = validate_problem_difficulty(data['difficulty'])
        description = sanitize_html(data['description'])
        
        current_user_id = get_jwt_identity()
        
        problem = Problem.create_problem(
            title=title,
            description=description,
            difficulty=difficulty,
            category=data.get('category'),
            time_limit=data.get('time_limit', 2000),
            memory_limit=data.get('memory_limit', 256),
            created_by=current_user_id,
            tags=data.get('tags'),
            hints=data.get('hints'),
            constraints=data.get('constraints')
        )
        
        return {
            'message': 'Problem created successfully',
            'problem': problem.to_dict()
        }, 201
        
    except ValidationError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Problem creation error: {str(e)}")
        return {'error': 'Problem creation failed'}, 500

@problems_bp.route('/<int:problem_id>', methods=['PUT'])
@jwt_required()
@require_admin()
def update_problem(problem_id):
    """Update a problem (admin only)."""
    problem = Problem.query.get_or_404(problem_id)
    
    try:
        schema = ProblemSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {'error': 'Validation failed', 'messages': err.messages}, 400
    
    try:
        # Update problem fields
        if 'title' in data:
            problem.title = validate_problem_title(data['title'])
        
        if 'description' in data:
            problem.description = sanitize_html(data['description'])
        
        if 'difficulty' in data:
            problem.difficulty = validate_problem_difficulty(data['difficulty'])
        
        if 'category' in data:
            problem.category = data['category']
        
        if 'time_limit' in data:
            problem.time_limit = data['time_limit']
        
        if 'memory_limit' in data:
            problem.memory_limit = data['memory_limit']
        
        if 'tags' in data:
            problem.tags = data['tags']
        
        if 'hints' in data:
            problem.hints = data['hints']
        
        if 'constraints' in data:
            problem.constraints = data['constraints']
        
        if 'editorial' in data:
            problem.editorial = data['editorial']
        
        db.session.commit()
        
        return {
            'message': 'Problem updated successfully',
            'problem': problem.to_dict()
        }
        
    except ValidationError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Problem update error: {str(e)}")
        return {'error': 'Problem update failed'}, 500

@problems_bp.route('/<int:problem_id>', methods=['DELETE'])
@jwt_required()
@require_admin()
def delete_problem(problem_id):
    """Delete a problem (admin only)."""
    problem = Problem.query.get_or_404(problem_id)
    
    try:
        # Soft delete by setting is_active to False
        problem.is_active = False
        db.session.commit()
        
        return {'message': 'Problem deleted successfully'}
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Problem deletion error: {str(e)}")
        return {'error': 'Problem deletion failed'}, 500

@problems_bp.route('/<int:problem_id>/test-cases', methods=['GET'])
@jwt_required()
def get_test_cases(problem_id):
    """Get test cases for a problem."""
    problem = Problem.query.get_or_404(problem_id)
    
    if not problem.is_active:
        return {'error': 'Problem not found'}, 404
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Only show sample test cases to regular users
    # Show all test cases to admins
    if user and user.is_admin:
        test_cases = TestCase.get_all_test_cases(problem_id)
        include_hidden = True
    else:
        test_cases = TestCase.get_sample_test_cases(problem_id)
        include_hidden = False
    
    return {
        'test_cases': [tc.to_dict(include_hidden=include_hidden) for tc in test_cases]
    }

@problems_bp.route('/<int:problem_id>/test-cases', methods=['POST'])
@jwt_required()
@require_admin()
def create_test_case(problem_id):
    """Create a new test case for a problem (admin only)."""
    problem = Problem.query.get_or_404(problem_id)
    
    try:
        schema = TestCaseSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {'error': 'Validation failed', 'messages': err.messages}, 400
    
    try:
        test_case = TestCase.create_test_case(
            problem_id=problem_id,
            input_data=data['input_data'],
            expected_output=data['expected_output'],
            is_sample=data.get('is_sample', False),
            is_hidden=data.get('is_hidden', False),
            description=data.get('description'),
            weight=data.get('weight', 1.0)
        )
        
        return {
            'message': 'Test case created successfully',
            'test_case': test_case.to_dict(include_hidden=True)
        }, 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Test case creation error: {str(e)}")
        return {'error': 'Test case creation failed'}, 500

@problems_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all problem categories."""
    categories = db.session.query(Problem.category)\
        .filter(Problem.is_active == True, Problem.category.isnot(None))\
        .distinct().all()
    
    category_list = [cat[0] for cat in categories if cat[0]]
    category_list.sort()
    
    return {'categories': category_list}

@problems_bp.route('/difficulties', methods=['GET'])
def get_difficulties():
    """Get all problem difficulties with counts."""
    difficulties = db.session.query(
        Problem.difficulty, 
        db.func.count(Problem.id).label('count')
    ).filter(Problem.is_active == True)\
     .group_by(Problem.difficulty).all()
    
    difficulty_data = [
        {
            'difficulty': diff[0], 
            'count': diff[1],
            'color': Problem().get_difficulty_color() if diff[0] else '#74b9ff'
        } 
        for diff in difficulties
    ]
    
    return {'difficulties': difficulty_data}

@problems_bp.route('/stats', methods=['GET'])
def get_problem_stats():
    """Get overall problem statistics."""
    total_problems = Problem.query.filter_by(is_active=True).count()
    
    difficulty_stats = db.session.query(
        Problem.difficulty,
        db.func.count(Problem.id).label('count')
    ).filter(Problem.is_active == True)\
     .group_by(Problem.difficulty).all()
    
    category_stats = db.session.query(
        Problem.category,
        db.func.count(Problem.id).label('count')
    ).filter(Problem.is_active == True, Problem.category.isnot(None))\
     .group_by(Problem.category).all()
    
    return {
        'total_problems': total_problems,
        'difficulty_distribution': [
            {'difficulty': stat[0], 'count': stat[1]} 
            for stat in difficulty_stats
        ],
        'category_distribution': [
            {'category': stat[0], 'count': stat[1]} 
            for stat in category_stats
        ]
    }