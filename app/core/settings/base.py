import os
from enum import Enum
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'), override=True)

class AppEnvTypes(Enum):
    dev: str = "dev"
    local: str = "local"
    prod: str = "prod"


class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes(os.getenv("ENV", "local"))
    
    class Config:
        extra = "allow"
        env_file = ".env"
