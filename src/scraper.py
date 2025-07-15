"""Reddit scraping functionality."""

import time
from typing import List, Dict
from datetime import datetime

import praw

import config
from .utils import format_timestamp


class RedditScraper:
    """Scrape Reddit user posts and comments."""

    def __init__(
        self, client_id: str = None, client_secret: str = None, user_agent: str = None
    ):
        """
        Initialize Reddit scraper with API credentials.

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for Reddit API
        """
        self.reddit = praw.Reddit(
            client_id=client_id or config.REDDIT_CLIENT_ID,
            client_secret=client_secret or config.REDDIT_CLIENT_SECRET,
            user_agent=user_agent or config.REDDIT_USER_AGENT,
            check_for_async=False,
        )

    def scrape_user(self, username: str) -> Dict[str, List[Dict]]:
        """
        Scrape posts and comments for a Reddit user.

        Args:
            username: Reddit username to scrape

        Returns:
            Dictionary containing posts and comments
        """
        try:
            user = self.reddit.redditor(username)

            # Check if user exists
            try:
                user.id  # This will fail if user doesn't exist
            except Exception:
                raise ValueError(f"User '{username}' not found or suspended")

            # Scrape posts
            posts = self._scrape_posts(user)

            # Add delay to respect rate limits
            time.sleep(config.REQUEST_DELAY)

            # Scrape comments
            comments = self._scrape_comments(user)

            return {
                "username": username,
                "posts": posts,
                "comments": comments,
                "scrape_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            raise Exception(f"Error scraping user {username}: {str(e)}")

    def _scrape_posts(self, user) -> List[Dict]:
        """Scrape user's posts."""
        posts = []

        try:
            for post in user.submissions.new(limit=config.MAX_POSTS):
                posts.append(
                    {
                        "title": post.title,
                        "content": (post.selftext if post.is_self else "[Link Post]"),
                        "subreddit": str(post.subreddit),
                        "url": f"https://reddit.com{post.permalink}",
                        "created_utc": format_timestamp(post.created_utc),
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "id": post.id,
                    }
                )
        except Exception as e:
            print(f"Error scraping posts: {e}")

        return posts

    def _scrape_comments(self, user) -> List[Dict]:
        """Scrape user's comments."""
        comments = []

        try:
            for comment in user.comments.new(limit=config.MAX_COMMENTS):
                comments.append(
                    {
                        "body": comment.body,
                        "subreddit": str(comment.subreddit),
                        "url": f"https://reddit.com{comment.permalink}",
                        "created_utc": format_timestamp(comment.created_utc),
                        "score": comment.score,
                        "id": comment.id,
                        "parent_id": comment.parent_id,
                    }
                )
        except Exception as e:
            print(f"Error scraping comments: {e}")

        return comments
