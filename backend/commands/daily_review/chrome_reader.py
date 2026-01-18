"""
Chrome History Reader

Reads browsing history from Chrome's SQLite database.
"""

import sqlite3
import os
import platform
import shutil
import tempfile
from datetime import datetime, timedelta
from typing import List, Dict


def get_chrome_history_path() -> str:
    """
    Get the Chrome history database path for the current OS.

    Returns:
        Absolute path to Chrome History file

    Raises:
        FileNotFoundError: If Chrome history file doesn't exist
    """
    system = platform.system()
    home = os.path.expanduser('~')

    if system == 'Darwin':  # macOS
        path = os.path.join(home, 'Library', 'Application Support', 'Google', 'Chrome', 'Default', 'History')
    elif system == 'Windows':
        path = os.path.join(home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'History')
    elif system == 'Linux':
        path = os.path.join(home, '.config', 'google-chrome', 'Default', 'History')
    else:
        raise OSError(f'Unsupported operating system: {system}')

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Chrome history not found at: {path}\n"
            "Make sure Chrome is installed and you've browsed some websites."
        )

    return path


def copy_history_database(source_path: str) -> str:
    """
    Copy Chrome history database to a temporary location.

    Chrome locks the database while running, so we need to copy it first.

    Args:
        source_path: Path to Chrome History file

    Returns:
        Path to temporary copy

    Raises:
        PermissionError: If unable to copy the file
    """
    try:
        # Create a temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.db', prefix='chrome_history_')
        os.close(temp_fd)

        # Copy the database
        shutil.copy2(source_path, temp_path)

        return temp_path
    except (IOError, OSError) as e:
        raise PermissionError(
            f"Unable to access Chrome history: {str(e)}\n"
            "Try closing Chrome and running the command again."
        )


def convert_chrome_timestamp(chrome_time: int) -> datetime:
    """
    Convert Chrome's WebKit timestamp to Python datetime.

    Chrome uses microseconds since January 1, 1601 UTC.

    Args:
        chrome_time: Chrome timestamp (microseconds since 1601-01-01)

    Returns:
        Python datetime object
    """
    try:
        # Chrome epoch starts at 1601-01-01
        # Unix epoch starts at 1970-01-01
        # Difference: 11644473600 seconds
        unix_timestamp = (chrome_time / 1000000) - 11644473600
        return datetime.fromtimestamp(unix_timestamp)
    except (ValueError, TypeError, OSError):
        # If conversion fails, return current time as fallback
        return datetime.now()


def read_history(hours: int = 24) -> List[Dict]:
    """
    Read Chrome browsing history for the specified time period.

    Args:
        hours: Number of hours to look back (default: 24)

    Returns:
        List of visit dictionaries with keys:
        - url: The URL visited
        - title: Page title
        - visit_time: Visit timestamp (datetime object)
        - visit_time_chrome: Original Chrome timestamp
    """
    # Get Chrome history path
    history_path = get_chrome_history_path()

    # Copy to temporary location
    temp_db_path = copy_history_database(history_path)

    try:
        # Connect to the database
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Convert to Chrome timestamp format
        chrome_cutoff = int((cutoff_time.timestamp() + 11644473600) * 1000000)

        # Query visits with URLs
        query = """
        SELECT
            urls.url,
            urls.title,
            visits.visit_time,
            visits.id as visit_id
        FROM visits
        INNER JOIN urls ON visits.url = urls.id
        WHERE visits.visit_time >= ?
        ORDER BY visits.visit_time ASC
        """

        cursor.execute(query, (chrome_cutoff,))
        rows = cursor.fetchall()

        # Convert to list of dictionaries
        visits = []
        for row in rows:
            url, title, visit_time_chrome, visit_id = row

            # Skip invalid URLs
            if not url or url.startswith('chrome://') or url.startswith('chrome-extension://'):
                continue

            visit = {
                'url': url,
                'title': title or '',
                'visit_time': convert_chrome_timestamp(visit_time_chrome),
                'visit_time_chrome': visit_time_chrome,
                'visit_id': visit_id
            }
            visits.append(visit)

        conn.close()

        return visits

    finally:
        # Clean up temporary database file
        try:
            os.remove(temp_db_path)
        except OSError:
            pass  # Ignore cleanup errors
