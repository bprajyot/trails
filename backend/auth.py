from __future__ import annotations

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import select

from db import get_session
from models import User
from utils import hash_password, verify_password, is_valid_email, is_valid_username, error_response


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not is_valid_email(email):
        return error_response("Invalid email")
    if not is_valid_username(username):
        return error_response("Invalid username (3-50 chars, letters/numbers/underscore)")
    if len(password) < 6:
        return error_response("Password too short (min 6)")

    with get_session() as session:
        # Check uniqueness
        existing = session.execute(select(User).where((User.email == email) | (User.username == username))).scalars().first()
        if existing:
            return error_response("Email or username already in use", 409)
        user = User(email=email, username=username, password_hash=hash_password(password))
        session.add(user)
        session.flush()
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(force=True, silent=True) or {}
    email_or_username = (data.get("emailOrUsername") or "").strip().lower()
    password = data.get("password") or ""

    with get_session() as session:
        stmt = select(User).where((User.email == email_or_username) | (User.username == email_or_username))
        user = session.execute(stmt).scalars().first()
        if not user or not verify_password(password, user.password_hash):
            return error_response("Invalid credentials", 401)
        token = create_access_token(identity=str(user.id))
        return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    with get_session() as session:
        user = session.get(User, int(user_id))
        if not user:
            return error_response("User not found", 404)
        return jsonify(user.to_dict()), 200