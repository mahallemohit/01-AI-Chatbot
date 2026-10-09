
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Please check your .env file."
    )
