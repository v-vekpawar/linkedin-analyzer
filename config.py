import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# LinkedIn Configuration
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_BASE_URL = "https://www.linkedin.com"

# Selenium Configuration
SELENIUM_TIMEOUT = 10  # seconds
SELENIUM_IMPLICIT_WAIT = 5  # seconds

# Flask Configuration
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True