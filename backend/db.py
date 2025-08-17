from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, Session


engine = None
SessionLocal: Optional[scoped_session] = None
Base = declarative_base()


def init_engine_and_session(database_uri: str) -> None:
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(database_uri, pool_pre_ping=True, pool_recycle=3600)
        SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


@contextmanager
def get_session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("Database session not initialized. Call init_engine_and_session first.")
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()