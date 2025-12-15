import os
from dotenv import load_dotenv

# Load .env once at startup
load_dotenv()


class Settings:
    def __init__(self):
        # Application
        self.APP_NAME = os.getenv("APP_NAME", "ChatBot_AI")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        # Server
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 5001))
        # Database
        self.MONGODB_URI = os.getenv("MONGODB_URI", "")
        # AI Provider
        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "")
        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")
        # API Settings
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
        # Scoring weights
        self.GRAMMAR_WEIGHT = float(os.getenv("GRAMMAR_WEIGHT", 0.3))
        self.VOCABULARY_WEIGHT = float(os.getenv("VOCABULARY_WEIGHT", 0.3))
        self.FLUENCY_WEIGHT = float(os.getenv("FLUENCY_WEIGHT", 0.2))
        self.NATURALNESS_WEIGHT = float(os.getenv("NATURALNESS_WEIGHT", 0.2))
        # CORS
        self.CORS_ORIGIN = [
            os.getenv("CORS_ORIGIN", "http://localhost:3000")
        ]
        # Keycloak
        self.KEYCLOAK_ISSUER_URI = os.getenv("KEYCLOAK_ISSUER_URI", "").rstrip("/")
        self.KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "")
        self.JWKS_URL = (
            f"{self.KEYCLOAK_ISSUER_URI}/protocol/openid-connect/certs"
            if self.KEYCLOAK_ISSUER_URI
            else None
        )
        # External services
        self.COURSE_SERVICE_BASE_URL = os.getenv(
            "COURSE_SERVICE_BASE_URL",
            "http://localhost:9002/course-service",
        ).rstrip("/")
        self.COURSE_SERVICE_TIMEOUT = int(os.getenv("COURSE_SERVICE_TIMEOUT", 5))


settings = Settings()
print(f"[config] COURSE_SERVICE_BASE_URL={settings.COURSE_SERVICE_BASE_URL}")
print(f"[config] COURSE_SERVICE_TIMEOUT={settings.COURSE_SERVICE_TIMEOUT}s")