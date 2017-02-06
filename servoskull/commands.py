import logging
import random

logging.basicConfig(level=logging.INFO)


def cmd_help() -> str:
    CMD_PREFIX = '!'
    response = 'Available commands:\n'
    for key, value in commands.items():
        response += '  **{}{}** - {}\n'.format(CMD_PREFIX, key, value['description'])

    return response


def cmd_yesno() -> str:
    return random.choice(['yes', 'no'])


commands = {
    'help': {
        'fn': cmd_help,
        'description': 'List all commands',
    },
    'yesno': {
        'fn': cmd_yesno,
        'description': 'Returns yes or no'
    }
}


