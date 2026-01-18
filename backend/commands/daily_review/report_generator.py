"""
Report Generator

Generates formatted markdown reports from browsing history analysis.
"""

import json
from typing import List, Dict
from datetime import datetime
from . import visit_analyzer
from . import categorizer


def generate_report(
    visits: List[Dict],
    domain_data: Dict[str, Dict],
    categories: Dict[str, str],
    user_question: str = ''
) -> str:
    """
    Generate a formatted markdown report.

    Args:
        visits: List of visits with duration
        domain_data: Domain aggregation data
        categories: Domain to category mapping
        user_question: Original user question/args

    Returns:
        Markdown formatted report string
    """
    # Aggregate by category
    category_data = categorizer.aggregate_by_category(domain_data, categories)

    # Generate chart data
    chart_data = generate_chart_data(category_data)

    # Build report sections
    report_parts = []

    # Add chart data as JSON (will be parsed by frontend)
    chart_json = json.dumps(chart_data)
    report_parts.append(f'```chart\n{chart_json}\n```')

    # Header
    report_parts.append(format_header())

    # Summary
    report_parts.append(format_summary(visits, domain_data, category_data))

    # Category breakdown
    report_parts.append(format_category_breakdown(category_data))

    # Video section (if applicable)
    video_section = format_video_section(domain_data, categories)
    if video_section:
        report_parts.append(video_section)

    # Insights
    report_parts.append(format_insights(domain_data, category_data))

    # Join all parts
    report = '\n\n'.join(report_parts)

    return report


def generate_chart_data(category_data: Dict[str, Dict]) -> Dict:
    """
    Generate chart data for frontend visualization.

    Args:
        category_data: Aggregated category data

    Returns:
        Dictionary with chart configuration and data
    """
    # Sort categories by duration
    categories = list(category_data.values())
    categories.sort(key=lambda c: c['total_duration'], reverse=True)

    # Prepare data for bar chart
    chart_items = []
    for cat in categories:
        if cat['total_duration'] > 0:
            category_name = cat['category'].replace('_', ' ').title()
            duration_minutes = cat['total_duration'] / 60

            chart_items.append({
                'category': category_name,
                'minutes': round(duration_minutes, 1),
                'hours': round(duration_minutes / 60, 2),
                'visits': cat['visit_count']
            })

    return {
        'type': 'bar',
        'title': 'Time Spent by Category',
        'data': chart_items,
        'xAxis': 'category',
        'yAxis': 'minutes',
        'yAxisLabel': 'Time (minutes)'
    }


def format_header() -> str:
    """Generate report header with date."""
    today = datetime.now().strftime('%B %d, %Y')
    return f"# Daily Browsing Review - {today}"


def format_summary(
    visits: List[Dict],
    domain_data: Dict[str, Dict],
    category_data: Dict[str, Dict]
) -> str:
    """Generate summary section."""
    total_duration = sum(d['total_duration'] for d in domain_data.values())
    total_visits = len(visits)
    unique_sites = len(domain_data)
    categories_explored = len([c for c in category_data.values() if c['visit_count'] > 0])

    summary = [
        "## Summary",
        f"- **Total browsing time:** {visit_analyzer.format_duration(total_duration)} (estimated)",
        f"- **Pages visited:** {total_visits}",
        f"- **Unique websites:** {unique_sites}",
        f"- **Categories explored:** {categories_explored}"
    ]

    return '\n'.join(summary)


def format_category_breakdown(category_data: Dict[str, Dict]) -> str:
    """Generate category breakdown section."""
    if not category_data:
        return "## Time by Category\n\nNo categories found."

    # Calculate total time for percentages
    total_duration = sum(c['total_duration'] for c in category_data.values())

    # Sort categories by duration
    categories = list(category_data.values())
    categories.sort(key=lambda c: c['total_duration'], reverse=True)

    lines = ["## Time by Category"]

    for cat in categories:
        duration = cat['total_duration']
        if duration == 0:
            continue

        percentage = int((duration / total_duration * 100)) if total_duration > 0 else 0
        category_name = cat['category'].replace('_', ' ').title()

        lines.append(f"\n### {category_name} ({visit_analyzer.format_duration(duration)} - {percentage}%)")

        # Show top domains in this category
        top_domains = cat['domains'][:5]  # Top 5 domains
        for domain_info in top_domains:
            domain = domain_info['domain']
            domain_duration = domain_info['duration']
            visit_count = domain_info['visit_count']

            lines.append(
                f"- **{domain}:** {visit_analyzer.format_duration(domain_duration)} "
                f"({visit_count} visit{'s' if visit_count != 1 else ''})"
            )

    return '\n'.join(lines)


def format_video_section(domain_data: Dict[str, Dict], categories: Dict[str, str]) -> str:
    """Generate video watching section if applicable."""
    # Find video domains
    video_domains = []
    for domain, cat in categories.items():
        if cat == 'video' and domain in domain_data:
            video_domains.append(domain)

    if not video_domains:
        return ''

    lines = ["## Videos Watched"]

    for domain in video_domains:
        data = domain_data[domain]
        titles = data.get('titles', [])

        if not titles:
            continue

        lines.append(f"\n### {domain}")
        lines.append(f"Time spent: {visit_analyzer.format_duration(data['total_duration'])}")
        lines.append("\nVideos/content:")

        # Extract video titles (YouTube specific logic)
        for title in titles[:10]:  # Show top 10
            # Clean up YouTube titles (remove " - YouTube" suffix)
            clean_title = title.replace(' - YouTube', '').replace(' - Vimeo', '').strip()
            if clean_title:
                lines.append(f"- {clean_title}")

    return '\n'.join(lines)


def format_insights(domain_data: Dict[str, Dict], category_data: Dict[str, Dict]) -> str:
    """Generate insights section."""
    lines = ["## Insights"]

    # Most visited site
    if domain_data:
        most_visited = max(domain_data.values(), key=lambda d: d['visit_count'])
        lines.append(
            f"- **Most visited:** {most_visited['domain']} "
            f"({most_visited['visit_count']} visits)"
        )

    # Longest time on single site
    if domain_data:
        longest_site = max(domain_data.values(), key=lambda d: d['total_duration'])
        if longest_site['total_duration'] > 0:
            lines.append(
                f"- **Most time spent:** {longest_site['domain']} "
                f"({visit_analyzer.format_duration(longest_site['total_duration'])})"
            )

    # Dominant category
    if category_data:
        dominant_cat = max(category_data.values(), key=lambda c: c['total_duration'])
        if dominant_cat['total_duration'] > 0:
            category_name = dominant_cat['category'].replace('_', ' ').title()
            lines.append(
                f"- **Primary focus:** {category_name} "
                f"({visit_analyzer.format_duration(dominant_cat['total_duration'])})"
            )

    # Browsing patterns
    if domain_data:
        total_duration = sum(d['total_duration'] for d in domain_data.values())
        total_visits = sum(d['visit_count'] for d in domain_data.values())
        avg_duration_per_visit = total_duration / total_visits if total_visits > 0 else 0

        lines.append(
            f"- **Average time per page:** {visit_analyzer.format_duration(int(avg_duration_per_visit))}"
        )

    # Note about time estimation
    lines.append("\n*Note: Time estimates are calculated from visit sequences and may not reflect exact browsing time.*")

    return '\n'.join(lines)
