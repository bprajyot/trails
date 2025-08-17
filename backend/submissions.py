from __future__ import annotations

import time
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import select

from db import get_session
from models import Submission, Challenge
from queue import SubmissionQueue
from utils import error_response


submissions_bp = Blueprint("submissions", __name__)
queue = SubmissionQueue()


@submissions_bp.post("")
@jwt_required()
def create_submission():
    data = request.get_json(force=True, silent=True) or {}
    challenge_slug = (data.get("challengeSlug") or "").strip()
    language = (data.get("language") or "").strip().lower()
    code = data.get("code") or ""

    if language not in {"python", "node", "cpp"}:
        return error_response("Unsupported language. Use python, node, or cpp.")
    if len(code) < 1:
        return error_response("Code is required")

    user_id = int(get_jwt_identity())

    with get_session() as session:
        challenge = session.execute(select(Challenge).where(Challenge.slug == challenge_slug)).scalars().first()
        if not challenge:
            return error_response("Challenge not found", 404)
        submission = Submission(
            user_id=user_id,
            challenge_id=challenge.id,
            language=language,
            code=code,
            status="queued",
        )
        session.add(submission)
        session.flush()
        payload = {
            "submission_id": submission.id,
            "challenge_id": challenge.id,
            "language": language,
            "code": code,
        }
        queue.enqueue(payload)
        return jsonify({"submissionId": submission.id, "status": submission.status}), 201


@submissions_bp.get("/<int:submission_id>")
@jwt_required()
def get_submission(submission_id: int):
    user_id = int(get_jwt_identity())
    with get_session() as session:
        submission = session.get(Submission, submission_id)
        if not submission or submission.user_id != user_id:
            return error_response("Not found", 404)
        return jsonify(submission.to_dict()), 200