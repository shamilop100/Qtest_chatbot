import os
from dotenv import load_dotenv
load_dotenv()

CLAUDE_KEY = os.getenv("CLAUDE_KEY")
MODEL_NAME = "claude-3-haiku-20240307"