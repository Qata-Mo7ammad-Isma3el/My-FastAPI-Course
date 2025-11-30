from pydantic_settings import BaseSettings, SettingsConfigDict


# > this Setting class will help the application to read the env variables from .env file
# > every and each env variable that we want to read from .env file should be defined here as attribute
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGO: str
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    ACCESS_TOKEN_EXPIRY : int
    REFRESH_TOKEN_EXPIRY: int
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = (
    Settings()
)  # > creating an instance of Settings class to be used in other parts of the application
