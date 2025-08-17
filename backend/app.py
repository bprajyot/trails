from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from db import init_engine_and_session
from auth import auth_bp
from challenges import challenges_bp
from submissions import submissions_bp
from leaderboard import leaderboard_bp


def create_app() -> Flask:
    app = Flask(__name__)
    cfg = Config()

    app.config["SECRET_KEY"] = cfg.secret_key
    app.config["JWT_SECRET_KEY"] = cfg.jwt_secret_key

    CORS(app, resources={r"/*": {"origins": cfg.cors_allow_origins.split(",")}})

    # Initialize database engine and scoped session
    init_engine_and_session(cfg.sqlalchemy_database_uri)

    # JWT
    JWTManager(app)

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(challenges_bp, url_prefix="/challenges")
    app.register_blueprint(submissions_bp, url_prefix="/submissions")
    app.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")

    @app.get("/health")
    def health() -> tuple[dict, int]:
        return jsonify({"status": "ok"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)