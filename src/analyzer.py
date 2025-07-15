"""Persona analysis using LLM."""

import json
from typing import Dict

from openai import OpenAI

import config


class PersonaAnalyzer:
    """Analyze Reddit user data to build persona."""

    def __init__(self, api_key: str = None):
        """Initialize analyzer with OpenAI API key."""
        self.client = OpenAI(api_key=api_key or config.OPENAI_API_KEY)

    def analyze_user(self, user_data: Dict) -> Dict:
        """
        Analyze user data to build persona.

        Args:
            user_data: Dictionary containing posts and comments

        Returns:
            Dictionary containing persona analysis with citations
        """
        # Prepare content for analysis
        content_summary = self._prepare_content_summary(user_data)

        # Generate persona analysis
        persona = self._generate_persona(content_summary, user_data)

        return persona

    def _prepare_content_summary(self, user_data: Dict) -> str:
        """Prepare a summary of user content for analysis."""
        summary_parts = []

        # Add posts summary
        summary_parts.append("POSTS:")
        # Limit to avoid token limits
        for i, post in enumerate(user_data["posts"][:50]):
            summary_parts.append(
                f"Post {i + 1} (r/{post['subreddit']}): {post['title']}"
            )
            if post["content"] and post["content"] != "[Link Post]":
                summary_parts.append(f"Content: {post['content'][:200]}...")

        # Add comments summary
        summary_parts.append("\nCOMMENTS:")
        for i, comment in enumerate(user_data["comments"][:50]):
            summary_parts.append(
                f"Comment {i + 1} (r/{comment['subreddit']}): "
                f"{comment['body'][:200]}..."
            )

        return "\n".join(summary_parts)

    def _generate_persona(self, content_summary: str, user_data: Dict) -> Dict:
        """Generate persona using OpenAI GPT."""

        prompt = f"""Analyze the following Reddit user's posts and comments to create a detailed user persona. 
        For each characteristic you identify, provide specific examples from their content.

        Categories to analyze:
        1. Demographics (age range, location hints, gender if apparent)
        2. Interests and Hobbies
        3. Professional Background
        4. Personality Traits
        5. Values and Beliefs
        6. Communication Style
        7. Areas of Expertise
        8. Lifestyle Indicators

        User Content:
        {content_summary}

        Return the analysis as a JSON object with this structure:
        {{
            "demographics": {{
                "trait_name": {{
                    "description": "description",
                    "evidence": ["quote1", "quote2"]
                }}
            }},
            "interests": {{...}},
            "professional": {{...}},
            "personality": {{...}},
            "values": {{...}},
            "communication": {{...}},
            "expertise": {{...}},
            "lifestyle": {{...}}
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a skilled data analyst "
                            "specializing in user persona creation."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )

            # Parse the response
            persona_raw = json.loads(response.choices[0].message.content)

            # Add citations to the persona
            persona_with_citations = self._add_citations(persona_raw, user_data)

            return persona_with_citations

        except Exception as e:
            print(f"Error generating persona: {e}")
            return self._generate_fallback_persona(user_data)

    def _add_citations(self, persona_raw: Dict, user_data: Dict) -> Dict:
        """Add citations from actual posts/comments to persona traits."""
        persona_with_citations = {}

        all_content = []

        # Combine posts and comments for searching
        for post in user_data["posts"]:
            all_content.append(
                {
                    "type": "post",
                    "text": f"{post['title']} {post['content']}",
                    "url": post["url"],
                    "subreddit": post["subreddit"],
                }
            )

        for comment in user_data["comments"]:
            all_content.append(
                {
                    "type": "comment",
                    "text": comment["body"],
                    "url": comment["url"],
                    "subreddit": comment["subreddit"],
                }
            )

        # Process each category
        for category, traits in persona_raw.items():
            persona_with_citations[category] = {}

            if isinstance(traits, dict):
                for trait_name, trait_info in traits.items():
                    citations = []

                    # Find relevant content for evidence
                    if "evidence" in trait_info:
                        for evidence in trait_info["evidence"]:
                            # Find matching content
                            for content in all_content:
                                evidence_lower = evidence.lower()
                                content_lower = content["text"].lower()

                                # Check if evidence matches content
                                if evidence_lower in content_lower or any(
                                    word in content_lower
                                    for word in evidence_lower.split()[:3]
                                ):
                                    citations.append(
                                        {
                                            "text": content["text"][:200],
                                            "url": content["url"],
                                            "type": content["type"],
                                            "subreddit": content["subreddit"],
                                        }
                                    )
                                    break

                    persona_with_citations[category][trait_name] = {
                        "description": trait_info.get("description", ""),
                        "citations": citations[:3],  # Limit citations
                    }

        return persona_with_citations

    def _generate_fallback_persona(self, user_data: Dict) -> Dict:
        """Generate basic persona when API fails."""
        # Count subreddits
        subreddit_counts = {}
        for post in user_data["posts"]:
            sub = post["subreddit"]
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1
        for comment in user_data["comments"]:
            sub = comment["subreddit"]
            subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1

        top_subreddits = sorted(
            subreddit_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "interests": {
                "Active Subreddits": {
                    "description": (
                        f"Most active in: "
                        f"{', '.join([sub[0] for sub in top_subreddits])}"
                    ),
                    "citations": [],
                }
            },
            "activity": {
                "Post Count": {
                    "description": f"Total posts: {len(user_data['posts'])}",
                    "citations": [],
                },
                "Comment Count": {
                    "description": (f"Total comments: {len(user_data['comments'])}"),
                    "citations": [],
                },
            },
        }
