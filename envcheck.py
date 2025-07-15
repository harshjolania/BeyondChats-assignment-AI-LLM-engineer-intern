from dotenv import load_dotenv
import os
import praw

load_dotenv()  # loads .env

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)
print("Read-only mode?", reddit.read_only)
