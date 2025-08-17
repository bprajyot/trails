from __future__ import annotations

from flask import Blueprint, jsonify
from sqlalchemy import select, desc

from db import get_session
from models import User


leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.get("")
def get_leaderboard():
    with get_session() as session:
        users = session.execute(select(User).order_by(desc(User.rating)).limit(50)).scalars().all()
        return jsonify([u.to_dict() for u in users]), 200