from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str

    # Base de données
    database_url: str

    # Stockage de fichiers
    storage_path: str = "./storage"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
