"""Configuration settings for Reddit Persona Analyzer."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API Configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv(
    'REDDIT_USER_AGENT',
    'RedditPersonaAnalyzer/1.0'
)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Scraping Configuration
MAX_POSTS = 100
MAX_COMMENTS = 200
REQUEST_DELAY = 1  # seconds between requests

# Output Configuration
OUTPUT_DIR = 'output'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)