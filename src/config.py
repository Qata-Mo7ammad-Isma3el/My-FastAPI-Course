from pydantic_settings import BaseSettings, SettingsConfigDict
#> this Setting class will help the application to read the env variables from .env file
#> every and each env variable that we want to read from .env file should be defined here as attribute 
class Settings(BaseSettings):
    DATABASE_URL:str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
        )


settings = Settings() #> creating an instance of Settings class to be used in other parts of the application