from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    API_URL: str = "https://nbd-rest.herokuapp.com/api/v1"
    ACCESS_TOKEN: Optional[str] = None


settings = Settings()
