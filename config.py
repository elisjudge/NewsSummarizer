import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    """Flask configuration settings."""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    ASSISTANT_ID = os.getenv("ASSISTANT_ID")
    THREAD_ID = os.getenv("THREAD_ID")

    @staticmethod
    def ensure_openai_key():
        """Ensure the OpenAI API key is loaded properly."""
        if not Config.OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API Key! Ensure it's set in the .env file or environment variables.")
