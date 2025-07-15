#!/usr/bin/env python3
"""
Reddit User Persona Analyzer.

Main executable script for analyzing Reddit user profiles
and generating personas.
"""

import argparse
import sys
import os

from src.scraper import RedditScraper
from src.analyzer import PersonaAnalyzer
from src.utils import extract_username_from_url, format_output, sanitize_filename
import config


def main():
    """Main function to run the Reddit Persona Analyzer."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=(
            "Analyze Reddit user profiles to generate detailed "
            "personas with citations."
        )
    )
    parser.add_argument(
        "url",
        help=(
            "Reddit user profile URL " "(e.g., https://www.reddit.com/user/username/)"
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: output/username.txt)",
        default=None,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Extract username from URL
    username = extract_username_from_url(args.url)
    if not username:
        print(f"Error: Could not extract username from URL: {args.url}")
        print("Please provide a valid Reddit user profile URL.")
        sys.exit(1)

    print(f"Analyzing Reddit user: {username}")

    try:
        # Initialize scraper
        print("Initializing Reddit scraper...")
        scraper = RedditScraper()

        # Scrape user data
        print(f"Scraping posts and comments for u/{username}...")
        user_data = scraper.scrape_user(username)

        if args.verbose:
            print(
                f"Found {len(user_data['posts'])} posts and "
                f"{len(user_data['comments'])} comments"
            )

        # Analyze user data
        print("Analyzing user data to build persona...")
        analyzer = PersonaAnalyzer()
        persona = analyzer.analyze_user(user_data)

        # Format output
        output_text = format_output(username, persona)

        # Determine output file path
        if args.output:
            output_path = args.output
        else:
            filename = f"{sanitize_filename(username)}.txt"
            output_path = os.path.join(config.OUTPUT_DIR, filename)

        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)

        print(f"\nPersona analysis complete! " f"Output saved to: {output_path}")

        # Also print a summary to console
        if args.verbose:
            print("\n" + "=" * 50)
            print("PERSONA SUMMARY")
            print("=" * 50)
            print(output_text[:500] + "...\n[See full analysis in output file]")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
