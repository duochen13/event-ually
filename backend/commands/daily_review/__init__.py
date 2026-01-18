"""
Daily Review Command Handler

Main orchestrator for the /dailyreview command that:
1. Reads Chrome browser history
2. Estimates time spent on websites
3. Categorizes sites using AI
4. Generates formatted reports
"""

from . import chrome_reader
from . import visit_analyzer
from . import categorizer
from . import report_generator


def handle_daily_review(args: str, conversation_id: int) -> str:
    """
    Handle the /dailyreview command.

    Args:
        args: Command arguments (e.g., "today", "yesterday", custom query)
        conversation_id: The current conversation ID

    Returns:
        Formatted markdown report string
    """
    try:
        # Parse time range from args (default: 24 hours)
        hours = _parse_time_range(args)

        # 1. Read Chrome history
        visits = chrome_reader.read_history(hours=hours)

        if not visits:
            return (
                "No browsing history found for the specified period.\n\n"
                "This could mean:\n"
                "- You haven't browsed any websites recently\n"
                "- Your browsing history has been cleared\n"
                "- You've been using incognito/private mode"
            )

        # 2. Estimate visit durations
        visits_with_duration = visit_analyzer.estimate_visit_duration(visits)

        # 3. Aggregate by domain
        domain_data = visit_analyzer.aggregate_by_domain(visits_with_duration)

        # 4. Categorize domains with AI
        categorized = categorizer.categorize_domains_with_ai(domain_data)

        # 5. Generate report
        report = report_generator.generate_report(
            visits=visits_with_duration,
            domain_data=domain_data,
            categories=categorized,
            user_question=args
        )

        return report

    except FileNotFoundError as e:
        return (
            f"Chrome history not found.\n\n"
            f"Error: {str(e)}\n\n"
            "Please ensure Google Chrome is installed and you've browsed some websites."
        )
    except PermissionError as e:
        return (
            f"Permission denied accessing Chrome history.\n\n"
            f"Error: {str(e)}\n\n"
            "Try closing Chrome and running the command again."
        )
    except Exception as e:
        return f"Error generating daily review: {str(e)}"


def _parse_time_range(args: str) -> int:
    """
    Parse time range from command arguments.

    Args:
        args: User input (e.g., "today", "yesterday", "last 3 days")

    Returns:
        Number of hours to look back
    """
    args_lower = args.lower()

    if 'yesterday' in args_lower:
        return 48  # Last 2 days
    elif 'week' in args_lower:
        return 168  # 7 days
    elif 'days' in args_lower:
        # Try to extract number (e.g., "last 3 days")
        import re
        match = re.search(r'(\d+)\s*days?', args_lower)
        if match:
            days = int(match.group(1))
            return days * 24

    # Default: today (last 24 hours)
    return 24
