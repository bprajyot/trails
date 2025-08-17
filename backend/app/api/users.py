from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile."""
    user = User.query.get_or_404(user_id)
    if not user.is_active:
        return {'error': 'User not found'}, 404
    
    return {'user': user.to_dict()}

@users_bp.route('/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user statistics."""
    user = User.query.get_or_404(user_id)
    if not user.is_active:
        return {'error': 'User not found'}, 404
    
    return {
        'stats': {
            'rating': user.rating,
            'total_submissions': user.total_submissions,
            'accepted_submissions': user.accepted_submissions,
            'success_rate': user.get_success_rate()
        }
    }