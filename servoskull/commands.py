import logging
import random

import discord
import requests
from imperialdate import ImperialDate

from servoskull.settings import CMD_PREFIX, USE_AVCONV

logging.basicConfig(level=logging.INFO)


class Command:
    """Base class for all commands."""
    required_arguments = []

    def __init__(self, **kwargs):
        self.arguments = kwargs.get('arguments')

    async def execute(self) -> str:
        raise NotImplementedError()


class SoundCommand(Command):
    """Base class for commands that require the bot
    to be connected to a voice channel."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = kwargs.get('message')
        self.client = kwargs.get('client')

    def _get_voice_client(self):
        """Return the currently connected voice client of the message's server."""
        return self.client.voice_client_in(self.message.server)


class CommandHelp(Command):
    async def execute(self) -> str:
        """Respond with a help message containing all available commands."""
        response = 'Available commands:'
        for key, value in commands.items():
            arguments = ""
            for argument in value['class'].required_arguments:
                arguments += '**<{}>** '.format(argument)

            response += '\n  **{}{}** {}- {}'.format(CMD_PREFIX, key, arguments, value['description'])

        response += '\nEither prepend your command with `{}` or mention the bot using `@`.'.format(CMD_PREFIX)

        return response


class CommandYesNo(Command):
    async def execute(self) -> str:
        """Respond with 'yes' or 'no', chosen randomly."""
        return random.choice(['yes', 'no'])


class CommandGif(Command):
    required_arguments = ['name or tag']

    async def execute(self) -> str:
        """Respond with a gif that matches a title or a tag of a gif
        at https://gifs.retzudo.com."""
        if not self.arguments or len(self.arguments) < 1:
            return 'Find a gif at https://gifs.retzudo.com'

        gifs = requests.get('https://gifs.retzudo.com/gifs.json').json()

        for gif in gifs['gifs']:
            haystack = gif['title'].lower()
            for c in ['!', '?', '.', ',']:
                haystack = haystack.replace(c, '')

            if 'tags' in gif:
                haystack = '{} {}'.format(haystack, ' '.join([tag.lower() for tag in gif['tags']]))

            if all([arg.lower() in haystack for arg in self.arguments]):
                return gif['url']

        return 'No gif found'


class CommandDate(Command):
    async def execute(self) -> str:
        """Respond with the current Imperial Date."""
        return "By the Emperor's grace it is {}".format(ImperialDate())


class CommandIdentify(Command):
    async def execute(self) -> str:
        """Respond with a little RP text."""
        return """A Servo-skull is a drone-like robotic device that appears to be a human skull outfitted with electronic
        or cybernetic components that utilise embedded anti-gravity field generators to allow them to hover and drift
        bodiless through the air. They are fashioned from the skulls of loyal Adepts of the Adeptus Terra and other pious
        Imperial servants to which robotic components and an antigravitic impeller have been added. This is so that they
        may continue their work for the Emperor of Mankind even after death. To have one's skull chosen to serve as a
        Servo-skull is a great honour in the Imperium, for it implies one's service in life has been satisfactory enough
        to warrant continuation beyond death."""


class CommandNextHoliday(Command):
    async def execute(self) -> str:
        holiday = requests.get('https://holidays.retzudo.com/next.json').json()

        return 'The next holiday is "{}" {} ({})'.format(
            holiday['name'],
            holiday['humanized']['en_gb'],
            holiday['date']
        )


class CommandRoll(Command):
    required_arguments = ['n']

    async def execute(self) -> str:
        """Respond with a roll of a die."""
        try:
            if not self.arguments or len(self.arguments) < 1:
                raise ValueError()
            sides = int(self.arguments[0])
            if sides < 2:
                raise ValueError()
        except ValueError:
            return 'Please specify a valid integer >= 2'

        return 'Rolled a {}-sided die: {}'.format(sides, random.randint(1, sides))


class CommandSummon(SoundCommand):
    async def execute(self) -> str:
        """Have the bot connect to the voice channel of the message's user."""
        if not isinstance(self.message.author, discord.Member):
            return 'Due to some Discord API limitation you need to issue this command in a channel.'

        voice_channel = self.message.author.voice.voice_channel
        if not voice_channel:
            return 'You are not connected to any voice channel'

        voice_client = self._get_voice_client()
        if not voice_client:
            await self.client.join_voice_channel(voice_channel)
        else:
            await voice_client.move_to(voice_channel)

        return 'Connected to "{}"'.format(voice_channel.name)


class CommandDisconnect(SoundCommand):
    async def execute(self) -> str:
        """Disconnect from the current voice channel."""
        voice_client = self._get_voice_client()
        if not voice_client:
            return 'I am not connected to any voice channel'
        else:
            await voice_client.disconnect()


class CommandSound(SoundCommand):
    sounds = {
        'horn': 'https://www.youtube.com/watch?v=1ytCEuuW2_A'
    }

    required_arguments = ['sound']

    async def execute(self) -> str:
        """Play a sound."""
        voice_client = self.client.voice_client_in(self.message.server)
        if not voice_client:
            return 'I am not connected to any voice channel'

        sound = self.arguments[0]
        url = CommandSound.sounds.get(sound)
        if not url:
            return 'No such sound "{}". Use `sounds` for a list of sounds'.format(sound)

        player = await voice_client.create_ytdl_player(url, use_avconv=USE_AVCONV)
        player.start()


class CommandSounds(Command):
    async def execute(self) -> str:
        """Respond with a list of available sounds for the `sound` command."""
        response = "Available sounds:"
        for key, value in CommandSound.sounds.items():
            response += "\n  **{}**: {}".format(key, value)

        return response


commands = {
    'help': {
        'class': CommandHelp,
        'description': 'List all commands',
    },
    'yesno': {
        'class': CommandYesNo,
        'description': 'Respond with yes or no'
    },
    'gif': {
        'class': CommandGif,
        'description': 'Respond with a gif from gifs.retzudo.com'
    },
    'date': {
        'class': CommandDate,
        'description': 'Respond with the current Imperial Date'
    },
    'identify': {
        'class': CommandIdentify,
        'description': 'Identifies the servo-skull'
    },
    'holiday': {
        'class': CommandNextHoliday,
        'description': 'Respond with with when the next holiday is'
    },
    'roll': {
        'class': CommandRoll,
        'description': 'Roll an n-sided die'
    },
    'summon': {
        'class': CommandSummon,
        'description': "Summons the bot to the user's voice channel"
    },
    'disconnect': {
        'class': CommandDisconnect,
        'description': 'Disconnects the bot from the current voice channel'
    },
    'sounds': {
        'class': CommandSounds,
        'description': 'Respond with a list of available sounds for voice channels'
    },
    'sound': {
        'class': CommandSound,
        'description': 'Play a sound (`sounds` for a list)'
    }
}
