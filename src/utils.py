"""Utility functions for Reddit Persona Analyzer."""

import re
from datetime import datetime
from typing import Optional


def extract_username_from_url(url: str) -> Optional[str]:
    """
    Extract Reddit username from profile URL.

    Args:
        url: Reddit user profile URL

    Returns:
        Username if found, None otherwise
    """
    patterns = [
        r"reddit\.com/user/([^/\?]+)",
        r"reddit\.com/u/([^/\?]+)",
        r"old\.reddit\.com/user/([^/\?]+)",
        r"old\.reddit\.com/u/([^/\?]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def format_timestamp(timestamp: float) -> str:
    """Convert Unix timestamp to readable date."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def clean_text(text: str, max_length: int = 200) -> str:
    """Clean and truncate text for display."""
    # Remove excessive whitespace
    text = " ".join(text.split())

    # Truncate if necessary
    if len(text) > max_length:
        text = text[:max_length] + "..."

    return text


def format_output(username: str, persona_data: dict) -> str:
    """
    Format persona data into readable output.

    Args:
        username: Reddit username
        persona_data: Dictionary containing persona analysis

    Returns:
        Formatted string output
    """
    output = []
    output.append(f"{'=' * 50}")
    output.append(f"Reddit User Persona: {username}")
    output.append(f"{'=' * 50}")
    output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")

    # Add each persona category
    for category, data in persona_data.items():
        output.append(f"\n{category.upper()}")
        output.append("-" * len(category))

        if isinstance(data, dict):
            for trait, info in data.items():
                output.append(f"\n• {trait}")
                if "description" in info:
                    output.append(f"  {info['description']}")
                if "citations" in info:
                    output.append("  Citations:")
                    # Limit to 3 citations
                    for citation in info["citations"][:3]:
                        output.append(f"    - {citation['text'][:100]}...")
                        output.append(f"      Link: {citation['url']}")
        else:
            output.append(str(data))

    return "\n".join(output)


def sanitize_filename(username: str) -> str:
    """Sanitize username for use as filename."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", username)
