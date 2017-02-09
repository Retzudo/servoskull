import json
import logging
import random
import requests

from imperialdate import ImperialDate
from servoskull.settings import CMD_PREFIX

logging.basicConfig(level=logging.INFO)


def cmd_help(arguments=None) -> str:
    """Respond with a help message containing all available commands."""
    response = 'Available commands:\n'
    for key, value in commands.items():
        response += '  **{}{}** - {}\n'.format(CMD_PREFIX, key, value['description'])

    return response


def cmd_yesno(arguments=None) -> str:
    """Respond with 'yes' or 'no', chosen randomly."""
    return random.choice(['yes', 'no'])


def cmd_gif(arguments=None) -> str:
    """Respond with a gif that matches a title or a tag of a gif
    at https://gifs.retzudo.com."""
    if not arguments:
        return 'Find a gif at https://gifs.retzudo.com'

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


def cmd_date(arguments=None) -> str:
    """Respond with the current Imperial Date."""
    return "By the Emperor's grace it is {}".format(ImperialDate())


def cmd_identify(arguments=None) -> str:
    """Respond with a little RP text."""
    return """A Servo-skull is a drone-like robotic device that appears to be a human skull outfitted with electronic
    or cybernetic components that utilise embedded anti-gravity field generators to allow them to hover and drift
    bodiless through the air. They are fashioned from the skulls of loyal Adepts of the Adeptus Terra and other pious
    Imperial servants to which robotic components and an antigravitic impeller have been added. This is so that they
    may continue their work for the Emperor of Mankind even after death. To have one's skull chosen to serve as a
    Servo-skull is a great honour in the Imperium, for it implies one's service in life has been satisfactory enough
    to warrant continuation beyond death."""


commands = {
    'help': {
        'fn': cmd_help,
        'description': 'List all commands',
    },
    'yesno': {
        'fn': cmd_yesno,
        'description': 'Respond with yes or no'
    },
    'gif': {
        'fn': cmd_gif,
        'description': 'Respond with a gif from gifs.retzudo.com'
    },
    'date': {
        'fn': cmd_date,
        'description': 'Respond with the current Imperial Date'
    },
    'identify': {
        'fn': cmd_identify,
        'description': 'Identifies the servo-skull'
    }
}
