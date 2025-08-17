from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from typing import Any, Dict, List

import redis
import firebase_admin
from firebase_admin import credentials, db as fb_db
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import Session as OrmSession

# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "code_platform")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "secret")
FIREBASE_DB_URL = os.getenv("FIREBASE_DATABASE_URL", "http://localhost:9000?ns=demo-local")
FIREBASE_SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "/workspace/firebase-service-account.json")

# SQLAlchemy setup (read test cases, update submissions)
engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}",
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Simple table metadata access using raw queries


def get_test_cases(session: OrmSession, challenge_id: int) -> List[Dict[str, Any]]:
    rows = session.execute(
        "SELECT id, input_text, expected_output, is_hidden FROM test_cases WHERE challenge_id = :cid",
        {"cid": challenge_id},
    ).mappings().all()
    return [dict(r) for r in rows]


def update_submission_status(session: OrmSession, submission_id: int, status: str, runtime_ms: int | None = None) -> None:
    session.execute(
        "UPDATE submissions SET status = :st, runtime_ms = :rt WHERE id = :sid",
        {"st": status, "rt": runtime_ms, "sid": submission_id},
    )


# Firebase init
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
    except Exception:
        firebase_admin.initialize_app(options={"databaseURL": FIREBASE_DB_URL})


# Redis client
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
QUEUE_KEY = "queue:submissions"

LANG_TO_IMAGE = {
    "python": "python:3.11-slim",
    "node": "node:20-alpine",
    "cpp": "gcc:13"
}


def run_in_container(language: str, code: str, input_text: str) -> tuple[str, int, str]:
    with tempfile.TemporaryDirectory() as tmpdir:
        if language == "python":
            source_file = os.path.join(tmpdir, "main.py")
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)
            run_cmd = [
                "docker", "run", "--rm",
                "--network=none",
                "--memory=256m", "--cpus=0.5",
                "-v", f"{source_file}:/work/main.py:ro",
                "-w", "/work",
                LANG_TO_IMAGE[language],
                "python", "main.py"
            ]
        elif language == "node":
            source_file = os.path.join(tmpdir, "main.js")
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)
            run_cmd = [
                "docker", "run", "--rm",
                "--network=none",
                "--memory=256m", "--cpus=0.5",
                "-v", f"{source_file}:/work/main.js:ro",
                "-w", "/work",
                LANG_TO_IMAGE[language],
                "node", "main.js"
            ]
        elif language == "cpp":
            source_file = os.path.join(tmpdir, "main.cpp")
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(code)
            # Build then run
            build_cmd = [
                "docker", "run", "--rm",
                "--network=none",
                "-v", f"{tmpdir}:/work",
                "-w", "/work",
                LANG_TO_IMAGE[language],
                "bash", "-lc", "g++ -O2 -std=c++17 main.cpp -o app"
            ]
            build = subprocess.run(build_cmd, capture_output=True, text=True, timeout=60)
            if build.returncode != 0:
                return build.stderr, 0, "error"
            run_cmd = [
                "docker", "run", "--rm",
                "--network=none",
                "--memory=256m", "--cpus=0.5",
                "-v", f"{tmpdir}:/work",
                "-w", "/work",
                LANG_TO_IMAGE[language],
                "bash", "-lc", "./app"
            ]
        else:
            return "Unsupported language", 0, "error"

        try:
            start = time.time()
            proc = subprocess.run(run_cmd, input=input_text, capture_output=True, text=True, timeout=10)
            runtime_ms = int((time.time() - start) * 1000)
            if proc.returncode != 0:
                return proc.stderr, runtime_ms, "error"
            return proc.stdout.strip(), runtime_ms, "ok"
        except subprocess.TimeoutExpired:
            return "Time Limit Exceeded", 10000, "error"


def process_job(payload: Dict[str, Any]) -> None:
    submission_id = int(payload["submission_id"])
    challenge_id = int(payload["challenge_id"])
    language = payload["language"]
    code = payload["code"]

    with SessionLocal() as session:
        update_submission_status(session, submission_id, "running")
        session.commit()

        tests = get_test_cases(session, challenge_id)
        all_passed = True
        total_runtime = 0
        results = []

        for t in tests:
            output, runtime_ms, state = run_in_container(language, code, t["input_text"])
            total_runtime += runtime_ms or 0
            passed = (state == "ok" and output == t["expected_output"].strip())
            all_passed = all_passed and passed
            results.append({
                "testCaseId": t["id"],
                "passed": passed,
                "runtimeMs": runtime_ms,
                "output": output if not t["is_hidden"] else ("<hidden>" if passed else output),
            })

        status = "passed" if all_passed else "failed"
        update_submission_status(session, submission_id, status, runtime_ms=total_runtime)
        session.commit()

    # Write results to Firebase RTDB
    try:
        ref = fb_db.reference(f"/submissions/{submission_id}")
        ref.set({
            "status": status,
            "results": results,
            "totalRuntimeMs": total_runtime,
        })
    except Exception:
        pass



def main() -> None:
    while True:
        data = r.blpop(QUEUE_KEY, timeout=5)
        if not data:
            continue
        _, raw = data
        try:
            payload = json.loads(raw)
            process_job(payload)
        except Exception as e:
            # Log and continue
            print("Worker error:", e)


if __name__ == "__main__":
    main()