from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, Enum, JSON, ForeignKey, BigInteger, TIMESTAMP
from sqlalchemy.orm import relationship

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False, default=1500)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP)

    submissions = relationship("Submission", back_populates="user", cascade="all,delete")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "rating": self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    slug = Column(String(100), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    difficulty = Column(Enum("easy", "medium", "hard", name="difficulty"), nullable=False)
    description = Column(Text, nullable=False)
    starter_code = Column(JSON)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP)

    test_cases = relationship("TestCase", back_populates="challenge", cascade="all,delete")

    def to_dict(self, include_description: bool = False, include_starter: bool = False) -> dict:
        data = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "difficulty": self.difficulty,
        }
        if include_description:
            data["description"] = self.description
        if include_starter:
            data["starter_code"] = self.starter_code
        return data


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    challenge_id = Column(BigInteger, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    input_text = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, nullable=False)

    challenge = relationship("Challenge", back_populates="test_cases")

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "challenge_id": self.challenge_id,
            "is_hidden": bool(self.is_hidden),
        }


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(BigInteger, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(32), nullable=False)
    code = Column(Text, nullable=False)
    status = Column(Enum("queued", "running", "passed", "failed", "error", name="status"), nullable=False)
    runtime_ms = Column(Integer)
    memory_kb = Column(Integer)
    score = Column(Integer)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="submissions")
    challenge = relationship("Challenge")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "challenge_id": self.challenge_id,
            "language": self.language,
            "status": self.status,
            "runtime_ms": self.runtime_ms,
            "memory_kb": self.memory_kb,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RatingHistory(Base):
    __tablename__ = "rating_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    previous_rating = Column(Integer, nullable=False)
    new_rating = Column(Integer, nullable=False)
    reason = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "previous_rating": self.previous_rating,
            "new_rating": self.new_rating,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }