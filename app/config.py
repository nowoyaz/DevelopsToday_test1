import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "prompts.json")

settings = Settings()
