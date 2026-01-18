"""
Command Parser

Parses and routes slash commands (e.g., /dailyreview, /help, etc.)
"""

from typing import Dict, Callable
from commands.daily_review import handle_daily_review


# Command metadata - maps command names to their handler and description
COMMANDS = {
    'dailyreview': {
        'handler': handle_daily_review,
        'description': 'Generate a report of your browsing history with categories and time spent',
        'usage': '/dailyreview [today|yesterday|last N days]',
        'examples': [
            '/dailyreview which sites did I visit today?',
            '/dailyreview yesterday',
            '/dailyreview last 3 days'
        ]
    },
    'help': {
        'handler': None,  # Will be handled inline
        'description': 'Show available commands and their usage',
        'usage': '/help [command]',
        'examples': [
            '/help',
            '/help dailyreview'
        ]
    }
}

# Legacy registry for backwards compatibility
COMMAND_REGISTRY = {name: cmd['handler'] for name, cmd in COMMANDS.items() if cmd['handler'] is not None}


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


def handle_help(args: str) -> str:
    """
    Generate help message for commands.

    Args:
        args: Optional command name to get specific help

    Returns:
        Formatted help text
    """
    args = args.strip().lower()

    # Specific command help
    if args:
        if args in COMMANDS:
            cmd = COMMANDS[args]
            help_text = [
                f"# Help: /{args}",
                "",
                f"**Description:** {cmd['description']}",
                "",
                f"**Usage:** `{cmd['usage']}`",
                "",
                "**Examples:**"
            ]
            for example in cmd['examples']:
                help_text.append(f"- `{example}`")
            return '\n'.join(help_text)
        else:
            return f"Unknown command: /{args}\n\nType `/help` to see all available commands."

    # General help - list all commands
    help_text = [
        "# Available Commands",
        "",
        "Here are the slash commands you can use:",
        ""
    ]

    for name, cmd in COMMANDS.items():
        help_text.append(f"### /{name}")
        help_text.append(f"{cmd['description']}")
        help_text.append(f"**Usage:** `{cmd['usage']}`")
        help_text.append("")

    help_text.extend([
        "---",
        "",
        "**Tip:** Type `/help <command>` to see detailed help for a specific command.",
        "",
        "**Example:** `/help dailyreview`"
    ])

    return '\n'.join(help_text)


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

    # Special handling for help command
    if command == 'help':
        return handle_help(args)

    # Look up handler in registry
    if command not in COMMANDS:
        available_commands = ', '.join(f'/{cmd}' for cmd in COMMANDS.keys())
        return (
            f"Unknown command: /{command}\n\n"
            f"Available commands: {available_commands}\n\n"
            f"Type `/help` for more information."
        )

    handler = COMMANDS[command]['handler']

    if handler is None:
        return f"Command /{command} is not yet implemented."

    # Call the handler
    try:
        return handler(args, conversation_id)
    except Exception as e:
        return f"Error executing command /{command}: {str(e)}"
