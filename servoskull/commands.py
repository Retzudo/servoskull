import logging
import random

import requests
from imperialdate import ImperialDate

from servoskull.settings import CMD_PREFIX

logging.basicConfig(level=logging.INFO)

sounds = {
    'horn': 'https://www.youtube.com/watch?v=1ytCEuuW2_A'
}


async def cmd_help(arguments: list=None, **kwargs) -> str:
    """Respond with a help message containing all available commands."""
    response = 'Available commands:'
    for key, value in commands.items():
        arguments = ""
        if 'arguments' in value:
            for argument in value['arguments']:
                arguments += '**<{}>** '.format(argument)

        response += '\n  **{}{}** {}- {}'.format(CMD_PREFIX, key, arguments, value['description'])

    response += '\nEither prepend your command with `{}` or mention the bot using `@`.'.format(CMD_PREFIX)

    return response


async def cmd_yesno(arguments: list=None, **kwargs) -> str:
    """Respond with 'yes' or 'no', chosen randomly."""
    return random.choice(['yes', 'no'])


async def cmd_gif(arguments: list=None, **kwargs) -> str:
    """Respond with a gif that matches a title or a tag of a gif
    at https://gifs.retzudo.com."""
    if not arguments:
        return 'Find a gif at https://gifs.retzudo.com'

    gifs = requests.get('https://gifs.retzudo.com/gifs.json').json()

    for gif in gifs['gifs']:
        haystack = gif['title'].lower()
        for c in ['!', '?', '.', ',']:
            haystack = haystack.replace(c, '')

        if 'tags' in gif:
            haystack = '{} {}'.format(haystack, ' '.join([tag.lower() for tag in gif['tags']]))

        if all([arg.lower() in haystack for arg in arguments]):
            return gif['url']

    return 'No gif found'


async def cmd_date(arguments: list=None, **kwargs) -> str:
    """Respond with the current Imperial Date."""
    return "By the Emperor's grace it is {}".format(ImperialDate())


async def cmd_identify(arguments: list=None, **kwargs) -> str:
    """Respond with a little RP text."""
    return """A Servo-skull is a drone-like robotic device that appears to be a human skull outfitted with electronic
    or cybernetic components that utilise embedded anti-gravity field generators to allow them to hover and drift
    bodiless through the air. They are fashioned from the skulls of loyal Adepts of the Adeptus Terra and other pious
    Imperial servants to which robotic components and an antigravitic impeller have been added. This is so that they
    may continue their work for the Emperor of Mankind even after death. To have one's skull chosen to serve as a
    Servo-skull is a great honour in the Imperium, for it implies one's service in life has been satisfactory enough
    to warrant continuation beyond death."""


async def cmd_next_holiday(arguments: list=None, **kwargs) -> str:
    """Respond with when the next holiday is according to holidays.retzudo.com."""
    holiday = requests.get('https://holidays.retzudo.com/next.json').json()

    return 'The next holiday is "{}" {} ({})'.format(
        holiday['name'],
        holiday['humanized']['en_gb'],
        holiday['date']
    )


async def cmd_roll(arguments: list=None, **kwargs) -> str:
    """Respond with a roll of a die."""
    try:
        if not arguments:
            raise ValueError()
        sides = int(arguments[0])
        if sides < 2:
            raise ValueError()
    except ValueError:
        return 'Please specify a valid integer >= 2'

    return 'Rolled a {}-sided die: {}'.format(sides, random.randint(1, sides))


async def cmd_summon(arguments: list=None, **kwargs) -> str:
    """Have the bot connect to the voice channel of the message's user."""
    message = kwargs['message']
    client = kwargs['client']
    voice_channel = message.author.voice.voice_channel
    if not voice_channel:
        return 'You are not connected to any voice channel'

    voice_client = client.voice_client_in(message.server)
    if not voice_client:
        await client.join_voice_channel(voice_channel)
    else:
        await voice_client.move_to(voice_channel)

    return 'Connected to "{}"'.format(voice_channel.name)


async def cmd_disconnect(arguments: list=None, **kwargs) -> str:
    """Disconnect from the current voice channel."""
    message = kwargs['message']
    client = kwargs['client']
    voice_client = client.voice_client_in(message.server)
    if not voice_client:
        return 'I am not connected to any voice channel'
    else:
        await voice_client.disconnect()


async def cmd_sounds(arguments: list=None, **kwargs) -> str:
    response = "Available sounds:"
    for key, value in sounds.items():
        response += "\n  **{}**: {}".format(key, value)

    return response


async def cmd_sound(arguments: list=None, **kwargs) -> str:
    """Play a sound."""
    message = kwargs['message']
    client = kwargs['client']

    voice_client = client.voice_client_in(message.server)
    if not voice_client:
        return 'I am not connected to any voice channel'

    sound = arguments[0]
    url = sounds.get(sound)
    if not url:
        return 'No such sound.'

    player = voice_client.create_ytdl_player(url)
    player.start()


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
        'arguments': ['name or tag'],
        'description': 'Respond with a gif from gifs.retzudo.com'
    },
    'date': {
        'fn': cmd_date,
        'description': 'Respond with the current Imperial Date'
    },
    'identify': {
        'fn': cmd_identify,
        'description': 'Identifies the servo-skull'
    },
    'holiday': {
        'fn': cmd_next_holiday,
        'description': 'Respond with with when the next holiday is'
    },
    'roll': {
        'fn': cmd_roll,
        'arguments': ['n'],
        'description': 'Roll an n-sided die'
    },
    'summon': {
        'fn': cmd_summon,
        'description': "Summons the bot to the user's voice channel"
    },
    'disconnect': {
        'fn': cmd_disconnect,
        'description': 'Disconnects the bot from the current voice channel'
    },
    'sounds': {
        'fn': cmd_sounds,
        'description': 'Respond with a list of available sounds for voice channels'
    },
    'sound': {
        'fn': cmd_sound,
        'arguments': ['sound'],
        'description': 'Play a sound (`sounds` for a list)'
    }
}
