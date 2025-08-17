from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from ..models.submission import Submission, db
from ..models.problem import Problem
from ..models.user import User
from ..utils.validators import validate_programming_language, validate_code_length, validate_pagination

submissions_bp = Blueprint('submissions', __name__)

# Validation schemas
class SubmissionSchema(Schema):
    problem_id = fields.Int(required=True)
    language = fields.Str(required=True)
    code = fields.Str(required=True)
    contest_id = fields.Int(required=False)

@submissions_bp.route('', methods=['POST'])
@jwt_required()
def submit_code():
    """Submit code for a problem."""
    try:
        schema = SubmissionSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {'error': 'Validation failed', 'messages': err.messages}, 400
    
    current_user_id = get_jwt_identity()
    
    # Validate problem exists
    problem = Problem.query.get(data['problem_id'])
    if not problem or not problem.is_active:
        return {'error': 'Problem not found'}, 404
    
    try:
        # Validate input
        language = validate_programming_language(data['language'])
        code = validate_code_length(data['code'])
        
        # Create submission
        submission = Submission.create_submission(
            user_id=current_user_id,
            problem_id=data['problem_id'],
            language=language,
            code=code,
            contest_id=data.get('contest_id')
        )
        
        # TODO: Queue submission for execution
        # This would typically be handled by a background task queue like Celery
        
        return {
            'message': 'Code submitted successfully',
            'submission': submission.to_dict(include_code=True)
        }, 201
        
    except ValidationError as e:
        return {'error': str(e)}, 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Submission error: {str(e)}")
        return {'error': 'Submission failed'}, 500

@submissions_bp.route('/<int:submission_id>', methods=['GET'])
@jwt_required()
def get_submission(submission_id):
    """Get a specific submission."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    submission = Submission.query.get_or_404(submission_id)
    
    # Users can only see their own submissions unless they're admin
    if submission.user_id != current_user_id and not (user and user.is_admin):
        return {'error': 'Access denied'}, 403
    
    include_code = submission.user_id == current_user_id or (user and user.is_admin)
    include_sensitive = user and user.is_admin
    
    return {
        'submission': submission.to_dict(
            include_code=include_code,
            include_sensitive=include_sensitive
        )
    }

@submissions_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_submissions(user_id):
    """Get submissions for a specific user."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Users can only see their own submissions unless they're admin
    if user_id != current_user_id and not (current_user and current_user.is_admin):
        return {'error': 'Access denied'}, 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        page, per_page = validate_pagination(page, per_page, max_per_page=100)
    except ValidationError as e:
        return {'error': str(e)}, 400
    
    submissions = Submission.get_user_submissions(user_id, page, per_page)
    
    include_code = user_id == current_user_id or (current_user and current_user.is_admin)
    
    return {
        'submissions': [
            s.to_dict(include_code=include_code) 
            for s in submissions.items
        ],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': submissions.total,
            'pages': submissions.pages,
            'has_next': submissions.has_next,
            'has_prev': submissions.has_prev
        }
    }

@submissions_bp.route('/problem/<int:problem_id>', methods=['GET'])
@jwt_required()
def get_problem_submissions(problem_id):
    """Get submissions for a specific problem."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    problem = Problem.query.get_or_404(problem_id)
    if not problem.is_active:
        return {'error': 'Problem not found'}, 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        page, per_page = validate_pagination(page, per_page, max_per_page=100)
    except ValidationError as e:
        return {'error': str(e)}, 400
    
    # Regular users can only see their own submissions
    # Admins can see all submissions
    if user and user.is_admin:
        submissions = Submission.get_problem_submissions(problem_id, page, per_page)
        include_code = True
    else:
        # Filter to only current user's submissions
        submissions = Submission.query.filter_by(
            problem_id=problem_id, 
            user_id=current_user_id
        ).order_by(Submission.submitted_at.desc())\
         .paginate(page=page, per_page=per_page, error_out=False)
        include_code = True
    
    return {
        'submissions': [
            s.to_dict(include_code=include_code) 
            for s in submissions.items
        ],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': submissions.total,
            'pages': submissions.pages,
            'has_next': submissions.has_next,
            'has_prev': submissions.has_prev
        }
    }

@submissions_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_submissions():
    """Get recent submissions across all users (admin only)."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_admin:
        return {'error': 'Admin privileges required'}, 403
    
    limit = request.args.get('limit', 10, type=int)
    if limit > 100:
        limit = 100
    
    submissions = Submission.get_recent_submissions(limit)
    
    return {
        'submissions': [s.to_dict() for s in submissions]
    }

@submissions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_submission_stats():
    """Get submission statistics for current user."""
    current_user_id = get_jwt_identity()
    
    # Get user's submission statistics
    total_submissions = Submission.query.filter_by(user_id=current_user_id).count()
    accepted_submissions = Submission.query.filter_by(
        user_id=current_user_id, 
        status='Accepted'
    ).count()
    
    # Get language distribution
    language_stats = db.session.query(
        Submission.language,
        db.func.count(Submission.id).label('count')
    ).filter(Submission.user_id == current_user_id)\
     .group_by(Submission.language).all()
    
    # Get status distribution
    status_stats = db.session.query(
        Submission.status,
        db.func.count(Submission.id).label('count')
    ).filter(Submission.user_id == current_user_id)\
     .group_by(Submission.status).all()
    
    success_rate = (accepted_submissions / total_submissions * 100) if total_submissions > 0 else 0
    
    return {
        'total_submissions': total_submissions,
        'accepted_submissions': accepted_submissions,
        'success_rate': round(success_rate, 2),
        'language_distribution': [
            {'language': stat[0], 'count': stat[1]} 
            for stat in language_stats
        ],
        'status_distribution': [
            {'status': stat[0], 'count': stat[1]} 
            for stat in status_stats
        ]
    }