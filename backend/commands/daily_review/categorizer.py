"""
Domain Categorizer

Categorizes domains using AI (Claude) with heuristic fallback.
"""

import os
import json
from typing import Dict, List
from anthropic import Anthropic


# Category definitions
CATEGORIES = {
    'video': ['Video and streaming content'],
    'development': ['Programming, coding, technical documentation'],
    'social_media': ['Social networking platforms'],
    'news': ['News websites and publications'],
    'productivity': ['Email, task management, collaboration tools'],
    'shopping': ['E-commerce and online shopping'],
    'entertainment': ['Music, podcasts, gaming, general entertainment'],
    'search': ['Search engines'],
    'reference': ['Wikipedia, documentation, educational content'],
    'other': ['Everything else']
}

# Heuristic patterns for common domains
DOMAIN_PATTERNS = {
    'video': ['youtube.com', 'vimeo.com', 'twitch.tv', 'netflix.com', 'hulu.com', 'disneyplus.com', 'hbomax.com'],
    'development': ['github.com', 'stackoverflow.com', 'gitlab.com', 'dev.to', 'npmjs.com', 'pypi.org', 'docs.python.org', 'developer.mozilla.org'],
    'social_media': ['twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'linkedin.com', 'reddit.com', 'tiktok.com', 'snapchat.com'],
    'news': ['nytimes.com', 'bbc.com', 'cnn.com', 'techcrunch.com', 'theverge.com', 'wired.com', 'arstechnica.com'],
    'productivity': ['gmail.com', 'outlook.com', 'mail.google.com', 'notion.so', 'slack.com', 'asana.com', 'trello.com', 'monday.com'],
    'shopping': ['amazon.com', 'ebay.com', 'etsy.com', 'walmart.com', 'target.com', 'alibaba.com'],
    'entertainment': ['spotify.com', 'soundcloud.com', 'apple.com/music', 'pandora.com'],
    'search': ['google.com', 'bing.com', 'duckduckgo.com', 'yahoo.com'],
    'reference': ['wikipedia.org', 'wikihow.com', 'britannica.com']
}


def heuristic_categorize(domain: str, titles: List[str] = None) -> str:
    """
    Categorize domain using heuristic pattern matching.

    Args:
        domain: Domain name
        titles: Optional list of page titles for context

    Returns:
        Category name
    """
    domain_lower = domain.lower()

    # Check each category's patterns
    for category, patterns in DOMAIN_PATTERNS.items():
        for pattern in patterns:
            if pattern in domain_lower:
                return category

    # Check titles for video keywords
    if titles:
        titles_text = ' '.join(titles).lower()
        if any(keyword in titles_text for keyword in ['video', 'watch', 'episode', 'movie', 'film']):
            return 'video'

    return 'other'


def batch_categorize_with_ai(domains: List[tuple]) -> Dict[str, str]:
    """
    Categorize a batch of domains using Claude AI.

    Args:
        domains: List of (domain, titles) tuples

    Returns:
        Dictionary mapping domain to category
    """
    try:
        # Get API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        client = Anthropic(api_key=api_key)

        # Prepare domain list with context
        domain_list = []
        for domain, titles in domains:
            title_context = ', '.join(titles[:3]) if titles else 'No titles'
            domain_list.append(f"- {domain} (pages: {title_context})")

        domains_text = '\n'.join(domain_list)

        # Create prompt
        prompt = f"""Categorize these websites/domains into one of these categories:

{json.dumps(CATEGORIES, indent=2)}

Domains to categorize (with sample page titles for context):
{domains_text}

Return ONLY a JSON object mapping each domain to its category name.
Format: {{"domain.com": "category_name"}}

Be specific:
- YouTube videos about programming → "development"
- YouTube entertainment videos → "video"
- GitHub/StackOverflow → "development"
- Twitter/Reddit → "social_media"
- News sites → "news"

JSON response:"""

        # Call Claude API
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        response_text = message.content[0].text.strip()

        # Extract JSON from response (handle potential markdown code blocks)
        if '```' in response_text:
            # Extract JSON from code block
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            response_text = response_text[json_start:json_end]

        categorization = json.loads(response_text)
        return categorization

    except Exception as e:
        print(f"AI categorization error: {str(e)}")
        return {}


def categorize_domains_with_ai(domain_data: Dict[str, Dict]) -> Dict[str, str]:
    """
    Categorize all domains using AI, with heuristic fallback.

    Args:
        domain_data: Domain aggregation data from visit_analyzer

    Returns:
        Dictionary mapping domain to category
    """
    categorization = {}
    uncategorized = []

    # First pass: Use heuristic for known domains
    for domain, data in domain_data.items():
        category = heuristic_categorize(domain, data.get('titles', []))
        if category != 'other':
            categorization[domain] = category
        else:
            # Save for AI categorization
            uncategorized.append((domain, data.get('titles', [])))

    # Second pass: Use AI for uncategorized domains
    if uncategorized:
        # Batch domains (max 20 per request to avoid token limits)
        batch_size = 20
        for i in range(0, len(uncategorized), batch_size):
            batch = uncategorized[i:i + batch_size]

            ai_results = batch_categorize_with_ai(batch)

            # Merge AI results
            for domain, titles in batch:
                if domain in ai_results:
                    categorization[domain] = ai_results[domain]
                else:
                    # AI failed, use heuristic fallback
                    categorization[domain] = heuristic_categorize(domain, titles)

    return categorization


def aggregate_by_category(domain_data: Dict[str, Dict], categorization: Dict[str, str]) -> Dict[str, Dict]:
    """
    Aggregate domain data by category.

    Args:
        domain_data: Domain aggregation data
        categorization: Domain to category mapping

    Returns:
        Dictionary mapping category to aggregated data:
        {
            'category_name': {
                'total_duration': 3600,
                'visit_count': 50,
                'domains': [...]  # list of domains in this category
            }
        }
    """
    category_data = {}

    for domain, data in domain_data.items():
        category = categorization.get(domain, 'other')

        if category not in category_data:
            category_data[category] = {
                'category': category,
                'total_duration': 0,
                'visit_count': 0,
                'domains': []
            }

        category_data[category]['total_duration'] += data['total_duration']
        category_data[category]['visit_count'] += data['visit_count']
        category_data[category]['domains'].append({
            'domain': domain,
            'duration': data['total_duration'],
            'visit_count': data['visit_count'],
            'titles': data.get('titles', [])
        })

    # Sort domains within each category by duration
    for category_info in category_data.values():
        category_info['domains'].sort(key=lambda d: d['duration'], reverse=True)

    return category_data
