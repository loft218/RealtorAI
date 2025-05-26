# app/core/config.py

from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    DEEPSEEK_API_KEY: str = os.getenv("DEESEEK_API_KEY")
    DEEPSEEK_API_URL: str = os.getenv("DEESEEK_API_URL")


settings = Settings()
