from __future__ import annotations

from flask import Blueprint, jsonify
from sqlalchemy import select

from db import get_session
from models import Challenge, TestCase


challenges_bp = Blueprint("challenges", __name__)


@challenges_bp.get("")
def list_challenges():
    with get_session() as session:
        items = session.execute(select(Challenge)).scalars().all()
        return jsonify([c.to_dict() for c in items]), 200


@challenges_bp.get("/<slug>")
def get_challenge(slug: str):
    with get_session() as session:
        item = session.execute(select(Challenge).where(Challenge.slug == slug)).scalars().first()
        if not item:
            return jsonify({"error": "Not found"}), 404
        # return description but not hidden tests
        public_tests = session.execute(
            select(TestCase).where(TestCase.challenge_id == item.id, TestCase.is_hidden == 0)
        ).scalars().all()
        return jsonify({
            "challenge": item.to_dict(include_description=True, include_starter=True),
            "public_test_cases": [t.to_public_dict() for t in public_tests],
        }), 200