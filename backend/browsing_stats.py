"""
Browsing Statistics API

Provides endpoints for retrieving historical browsing statistics.
"""

from datetime import datetime, timedelta
from typing import List, Dict
from commands.daily_review import chrome_reader, visit_analyzer, categorizer


def get_daily_stats(days: int = 7) -> List[Dict]:
    """
    Get browsing statistics for the last N days.

    Args:
        days: Number of days to retrieve (default: 7)

    Returns:
        List of daily statistics dictionaries
    """
    daily_stats = []

    for day_offset in range(days):
        # Calculate the date range for this day
        target_date = datetime.now() - timedelta(days=day_offset)
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        try:
            # Read history for the entire period (we'll filter by day)
            visits = chrome_reader.read_history(hours=24 * (day_offset + 1))

            # Filter visits for this specific day
            day_visits = [
                v for v in visits
                if start_of_day <= v['visit_time'] <= end_of_day
            ]

            if not day_visits:
                # No data for this day
                daily_stats.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'day_name': target_date.strftime('%A'),
                    'total_time': 0,
                    'total_visits': 0,
                    'unique_sites': 0,
                    'top_category': None,
                    'categories': {}
                })
                continue

            # Estimate durations
            visits_with_duration = visit_analyzer.estimate_visit_duration(day_visits)

            # Aggregate by domain
            domain_data = visit_analyzer.aggregate_by_domain(visits_with_duration)

            # Categorize domains
            categories = categorizer.categorize_domains_with_ai(domain_data)

            # Aggregate by category
            category_data = categorizer.aggregate_by_category(domain_data, categories)

            # Calculate totals
            total_time = sum(d['total_duration'] for d in domain_data.values())
            total_visits = len(day_visits)
            unique_sites = len(domain_data)

            # Find top category
            top_category = None
            if category_data:
                sorted_categories = sorted(
                    category_data.items(),
                    key=lambda x: x[1]['total_duration'],
                    reverse=True
                )
                if sorted_categories:
                    top_cat_name = sorted_categories[0][0].replace('_', ' ').title()
                    top_cat_time = sorted_categories[0][1]['total_duration']
                    top_category = {
                        'name': top_cat_name,
                        'time': top_cat_time,
                        'percentage': int((top_cat_time / total_time * 100)) if total_time > 0 else 0
                    }

            # Format category breakdown
            category_breakdown = {}
            for cat_name, cat_info in category_data.items():
                category_breakdown[cat_name.replace('_', ' ').title()] = {
                    'time': cat_info['total_duration'],
                    'visits': cat_info['visit_count'],
                    'percentage': int((cat_info['total_duration'] / total_time * 100)) if total_time > 0 else 0
                }

            daily_stats.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'day_name': target_date.strftime('%A'),
                'total_time': total_time,
                'total_visits': total_visits,
                'unique_sites': unique_sites,
                'top_category': top_category,
                'categories': category_breakdown
            })

        except Exception as e:
            # If there's an error for this day, skip it
            print(f"Error processing day {day_offset}: {str(e)}")
            daily_stats.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'day_name': target_date.strftime('%A'),
                'total_time': 0,
                'total_visits': 0,
                'unique_sites': 0,
                'top_category': None,
                'categories': {},
                'error': str(e)
            })

    return daily_stats


def get_weekly_summary() -> Dict:
    """
    Get a summary of browsing for the past week.

    Returns:
        Dictionary with weekly aggregated statistics
    """
    try:
        # Get daily stats for last 7 days
        daily_stats = get_daily_stats(days=7)

        # Aggregate weekly totals
        total_time = sum(day['total_time'] for day in daily_stats)
        total_visits = sum(day['total_visits'] for day in daily_stats)
        avg_daily_time = total_time / 7 if daily_stats else 0

        # Aggregate categories across all days
        all_categories = {}
        for day in daily_stats:
            for cat_name, cat_info in day['categories'].items():
                if cat_name not in all_categories:
                    all_categories[cat_name] = {'time': 0, 'visits': 0}
                all_categories[cat_name]['time'] += cat_info['time']
                all_categories[cat_name]['visits'] += cat_info['visits']

        # Find top category for the week
        top_category = None
        if all_categories:
            sorted_cats = sorted(
                all_categories.items(),
                key=lambda x: x[1]['time'],
                reverse=True
            )
            if sorted_cats:
                top_cat_name = sorted_cats[0][0]
                top_cat_time = sorted_cats[0][1]['time']
                top_category = {
                    'name': top_cat_name,
                    'time': top_cat_time,
                    'percentage': int((top_cat_time / total_time * 100)) if total_time > 0 else 0
                }

        return {
            'period': 'Last 7 Days',
            'total_time': total_time,
            'total_visits': total_visits,
            'avg_daily_time': avg_daily_time,
            'days_with_data': len([d for d in daily_stats if d['total_visits'] > 0]),
            'top_category': top_category,
            'categories': all_categories,
            'daily_breakdown': daily_stats
        }

    except Exception as e:
        return {
            'period': 'Last 7 Days',
            'error': str(e),
            'total_time': 0,
            'total_visits': 0,
            'avg_daily_time': 0,
            'days_with_data': 0,
            'top_category': None,
            'categories': {},
            'daily_breakdown': []
        }
