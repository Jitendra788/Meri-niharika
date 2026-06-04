from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_asyncpg_url(url: str) -> str:
    """Neon/Render often give postgresql:// — SQLAlchemy async needs postgresql+asyncpg://."""
    u = url.strip()
    if u.startswith("postgres://"):
        u = "postgresql://" + u[len("postgres://") :]
    if u.startswith("postgresql://") and "+asyncpg" not in u:
        u = "postgresql+asyncpg://" + u[len("postgresql://") :]
    return u


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/magazine"
    allowed_origins: str = "http://localhost:4200"
    admin_key: str = "change-me"
    uploads_dir: str = "uploads"
    jwt_secret: str = "change-me-too"
    admin_username: str = "admin"
    admin_password: str = "admin123"

    @property
    def async_database_url(self) -> str:
        return _normalize_asyncpg_url(self.database_url)

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
