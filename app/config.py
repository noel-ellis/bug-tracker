CHANGABLE_PROJECT_ENTRIES = ['name', 'description', 'start', 'deadline', 'status']
CHANGABLE_USER_ENTRIES = ['name', 'surname', 'username', 'email', 'access']
CHANGABLE_TICKET_ENTRIES = ['caption', 'description', 'priority', 'status', 'category']
CHANGABLE_COMMENT_ENTRIES = ['body_text']

# FETCH PYDANTIC SETTINGS FROM .env
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()


