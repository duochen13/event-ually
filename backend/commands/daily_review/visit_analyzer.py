"""
Visit Analyzer

Analyzes browsing visits to estimate time spent and aggregate by domain.
"""

from typing import List, Dict
from urllib.parse import urlparse
from datetime import datetime


# Constants for time estimation
MAX_VISIT_TIME = 1800  # 30 minutes in seconds
DEFAULT_FINAL_VISIT = 60  # 1 minute for the last visit in a sequence
SESSION_GAP = 1800  # 30 minutes - gap indicating new session


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.

    Args:
        url: Full URL

    Returns:
        Domain name (without www. prefix)
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc

        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain or 'unknown'
    except Exception:
        return 'unknown'


def estimate_visit_duration(visits: List[Dict]) -> List[Dict]:
    """
    Estimate duration for each visit based on time to next visit.

    Algorithm:
    - For each visit V[i], calculate time until next visit V[i+1]
    - Cap at MAX_VISIT_TIME (30 min) to handle cases where user left computer
    - For the last visit, use DEFAULT_FINAL_VISIT (1 min)
    - If gap > SESSION_GAP, cap at MAX_VISIT_TIME (new session started)

    Args:
        visits: List of visit dictionaries (must be sorted by visit_time)

    Returns:
        Same list with 'duration_seconds' added to each visit
    """
    if not visits:
        return visits

    # Ensure visits are sorted by time
    visits = sorted(visits, key=lambda v: v['visit_time'])

    for i in range(len(visits)):
        current_visit = visits[i]

        # Check if there's a next visit
        if i < len(visits) - 1:
            next_visit = visits[i + 1]

            # Calculate time difference
            time_diff = (next_visit['visit_time'] - current_visit['visit_time']).total_seconds()

            # Cap at MAX_VISIT_TIME
            if time_diff > SESSION_GAP:
                # Large gap - user probably left, cap at max time
                duration = MAX_VISIT_TIME
            else:
                # Normal browsing - use actual time but cap at max
                duration = min(time_diff, MAX_VISIT_TIME)
        else:
            # Last visit - use default time
            duration = DEFAULT_FINAL_VISIT

        # Ensure duration is non-negative
        current_visit['duration_seconds'] = max(0, int(duration))

    return visits


def aggregate_by_domain(visits: List[Dict]) -> Dict[str, Dict]:
    """
    Aggregate visits by domain.

    Args:
        visits: List of visits with duration_seconds

    Returns:
        Dictionary mapping domain to aggregated data:
        {
            'domain.com': {
                'domain': 'domain.com',
                'total_duration': 3600,  # seconds
                'visit_count': 15,
                'urls': [...],  # list of URL dicts
                'titles': [...]  # list of page titles
            }
        }
    """
    domain_map = {}

    for visit in visits:
        domain = extract_domain(visit['url'])
        duration = visit.get('duration_seconds', 0)

        if domain not in domain_map:
            domain_map[domain] = {
                'domain': domain,
                'total_duration': 0,
                'visit_count': 0,
                'urls': [],
                'titles': set()  # Use set to avoid duplicates
            }

        # Aggregate data
        domain_map[domain]['total_duration'] += duration
        domain_map[domain]['visit_count'] += 1
        domain_map[domain]['urls'].append({
            'url': visit['url'],
            'title': visit['title'],
            'visit_time': visit['visit_time'],
            'duration': duration
        })
        if visit['title']:
            domain_map[domain]['titles'].add(visit['title'])

    # Convert titles set to list
    for domain_data in domain_map.values():
        domain_data['titles'] = list(domain_data['titles'])

    return domain_map


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 15m", "45m", "30s")
    """
    if seconds < 60:
        return f"{seconds}s"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}m"


def get_top_domains(domain_data: Dict[str, Dict], limit: int = 10) -> List[Dict]:
    """
    Get top domains by time spent.

    Args:
        domain_data: Domain aggregation from aggregate_by_domain()
        limit: Maximum number of domains to return

    Returns:
        List of domain data dictionaries, sorted by total_duration descending
    """
    domains = list(domain_data.values())
    domains.sort(key=lambda d: d['total_duration'], reverse=True)
    return domains[:limit]
