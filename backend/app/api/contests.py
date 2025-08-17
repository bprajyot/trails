from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.contest import Contest

contests_bp = Blueprint('contests', __name__)

@contests_bp.route('', methods=['GET'])
def get_contests():
    """Get all contests."""
    contests = Contest.query.filter_by(is_public=True).order_by(Contest.start_time.desc()).all()
    return {'contests': [c.to_dict() for c in contests]}

@contests_bp.route('/<int:contest_id>', methods=['GET'])
def get_contest(contest_id):
    """Get a specific contest."""
    contest = Contest.query.get_or_404(contest_id)
    return {'contest': contest.to_dict(include_problems=True)}

@contests_bp.route('/<int:contest_id>/leaderboard', methods=['GET'])
def get_contest_leaderboard(contest_id):
    """Get contest leaderboard."""
    contest = Contest.query.get_or_404(contest_id)
    leaderboard = contest.get_leaderboard()
    return {'leaderboard': leaderboard}