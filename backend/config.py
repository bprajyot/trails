import os
from dataclasses import dataclass


@dataclass
class Config:
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")

    mysql_host: str = os.getenv("MYSQL_HOST", "mysql")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_db: str = os.getenv("MYSQL_DB", "code_platform")
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "secret")

    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173")

    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "local-code-platform")
    firebase_database_url: str = os.getenv("FIREBASE_DATABASE_URL", "http://localhost:9000?ns=demo-local")
    firebase_service_account_json: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "/workspace/firebase-service-account.json")

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )