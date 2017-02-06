import json
import logging
import random
import requests

logging.basicConfig(level=logging.INFO)


def cmd_help(arguments=None) -> str:
    CMD_PREFIX = '!'
    response = 'Available commands:\n'
    for key, value in commands.items():
        response += '  **{}{}** - {}\n'.format(CMD_PREFIX, key, value['description'])

    return response


def cmd_yesno(arguments=None) -> str:
    return random.choice(['yes', 'no'])


def cmd_gif(arguments=None) -> str:
    if not arguments:
        return 'No gif found'

    data = requests.get('https://gifs.retzudo.com/gifs.json')
    gifs = json.loads(data.content.decode('utf-8'))['gifs']

    for gif in gifs:
        haystack = gif['title'].lower()
        for c in ['!', '?', '.', ',']:
            haystack = haystack.replace(c, '')

        if 'tags' in gif:
            haystack = '{} {}'.format(haystack, ' '.join([tag.lower() for tag in gif['tags']]))

        if all([arg.lower() in haystack for arg in arguments]):
            return gif['url']

    return 'No gif found'


commands = {
    'help': {
        'fn': cmd_help,
        'description': 'List all commands',
    },
    'yesno': {
        'fn': cmd_yesno,
        'description': 'Returns yes or no'
    },
    'gif': {
        'fn': cmd_gif,
        'description': 'Respond with a gif from gifs.retzudo.com'
    }
}
