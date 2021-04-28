from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url = "sqlite:///schedule_app.db"
