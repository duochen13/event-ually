"""
Command Parser

Parses and routes slash commands (e.g., /dailyreview, /help, etc.)
"""

from typing import Dict
from commands.daily_review import handle_daily_review


# Command registry - maps command names to handler functions
COMMAND_REGISTRY = {
    'dailyreview': handle_daily_review,
}


def is_command(content: str) -> bool:
    """
    Check if a message is a slash command.

    Args:
        content: Message content

    Returns:
        True if message starts with '/', False otherwise
    """
    return content.strip().startswith('/')


def parse_command(content: str) -> Dict[str, str]:
    """
    Parse a command into its components.

    Args:
        content: Command string (e.g., "/dailyreview which site do I visit today?")

    Returns:
        Dictionary with 'command' and 'args' keys
    """
    content = content.strip()

    if not content.startswith('/'):
        return {'command': '', 'args': content}

    # Remove leading '/'
    content = content[1:]

    # Split into command and args
    parts = content.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''

    return {
        'command': command,
        'args': args
    }


def route_command(content: str, conversation_id: int) -> str:
    """
    Route a command to its handler.

    Args:
        content: Command string
        conversation_id: Current conversation ID

    Returns:
        Response string from command handler
    """
    parsed = parse_command(content)
    command = parsed['command']
    args = parsed['args']

    # Look up handler in registry
    handler = COMMAND_REGISTRY.get(command)

    if handler is None:
        available_commands = ', '.join(f'/{cmd}' for cmd in COMMAND_REGISTRY.keys())
        return (
            f"Unknown command: /{command}\n\n"
            f"Available commands: {available_commands}"
        )

    # Call the handler
    try:
        return handler(args, conversation_id)
    except Exception as e:
        return f"Error executing command /{command}: {str(e)}"
