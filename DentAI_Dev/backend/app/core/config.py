from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/dentai_db"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # App
    APP_ENV: str = "development"

    # FRONTEND_URL can be a single URL or comma-separated list
    # e.g. "http://localhost:3000,https://dentai.vercel.app"
    FRONTEND_URL: str = "http://localhost:3000"

    @property
    def allowed_origins(self) -> list[str]:
        return [url.strip() for url in self.FRONTEND_URL.split(",") if url.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
