import aiohttp
import logging
import random

import discord
from imperialdate import ImperialDate

from servoskull.settings import CMD_PREFIX, USE_AVCONV

logging.basicConfig(level=logging.INFO)


class Command:
    """Base class for all commands."""
    help_text = None
    required_arguments = []

    def __init__(self, **kwargs):
        self.arguments = kwargs.get('arguments')
        self.message = kwargs.get('message')

    async def execute(self) -> str:
        raise NotImplementedError()


class SoundCommand(Command):
    """Base class for commands that require the bot
    to be connected to a voice channel."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = kwargs.get('client')

    async def execute_sound(self):
        """Should be implemented by SoundCommand children instead of `execute`."""
        raise NotImplementedError()

    async def execute(self) -> str:
        """We override the `execute` method of `Command` and run a check before every execution
        if the bot is connected to a voice channel."""
        if not isinstance(self.message.author, discord.Member):
            # We can't easily determine which voice channel a user is connected to
            # if they message the bot with direct messaging.
            return 'Due to some Discord API limitation you need to issue this command in a channel.'

        if not self._get_voice_client():
            return 'I am not connected to any voice channel. Use `summon` to have me connect to one.'
        else:
            return await self.execute_sound()

    def _get_voice_client(self):
        """Return the currently connected voice client of the message's server."""
        return self.message.server.voice_client


class CommandHelp(Command):
    help_text = 'List all commands'

    async def execute(self) -> str:
        """Respond with a help message containing all available commands."""
        response = 'Available commands:'
        for command, class_ in commands.items():
            arguments = ''
            for argument in class_.required_arguments:
                arguments += '**<{}>** '.format(argument)

            response += '\n  **{}{}** {}- {}'.format(CMD_PREFIX, command, arguments, class_.help_text)

        response += '\nEither prepend your command with `{}` or mention the bot using `@`.'.format(CMD_PREFIX)

        return response


class CommandYesNo(Command):
    help_text = 'Respond with yes or no'

    async def execute(self) -> str:
        """Respond with 'yes' or 'no', chosen randomly."""
        return random.choice(['yes', 'no'])


class CommandGif(Command):
    required_arguments = ['name or tag']
    help_text = 'Respond with a gif from https://gifs.retzudo.com'

    GIFS_URL = 'https://gifs.retzudo.com/gifs.json'

    async def execute(self) -> str:
        """Respond with a gif that matches a title or a tag of a gif
        at https://gifs.retzudo.com."""
        if not self.arguments or len(self.arguments) < 1:
            return 'Find a gif at https://gifs.retzudo.com'

        async with aiohttp.ClientSession() as session:
            async with session.get(CommandGif.GIFS_URL) as response:
                gifs = await response.json()

        for gif in gifs['gifs']:
            haystack = gif['title'].lower()
            for c in ['!', '?', '.', ',']:
                haystack = haystack.replace(c, '')

            if 'tags' in gif:
                haystack = '{} {}'.format(haystack, ' '.join([tag.lower() for tag in gif['tags']]))

            if all(arg.lower() in haystack for arg in self.arguments):
                return gif['url']

        return 'No gif found'


class CommandDate(Command):
    help_text = 'Respond with the current Imperial Date'

    async def execute(self) -> str:
        """Respond with the current Imperial Date."""
        return "By the Emperor's grace it is {}".format(ImperialDate())


class CommandIdentify(Command):
    help_text = 'Identifies the servo-skull'

    async def execute(self) -> str:
        """Respond with some info and a little RP text."""
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        import servoskull

        now = datetime.now()
        uptime_delta = relativedelta(now, servoskull.start_time)
        uptime = '{0.hours} hours {0.minutes} minutes {0.seconds} seconds'.format(uptime_delta)
        flavour_text = (
            "A Servo-skull is a drone-like robotic device that appears to be a human skull outfitted with electronic "
            "or cybernetic components that utilise embedded anti-gravity field generators to allow them to hover "
            "and drift bodiless through the air. They are fashioned from the skulls of loyal Adepts of the Adeptus "
            "Terra and other pious Imperial servants to which robotic components and an antigravitic impeller have "
            "been added.This is so that they may continue their work for the Emperor of Mankind even after death. To "
            "have one's; skull chosen to serve as a; Servo-skull is a great honour in the Imperium, for it implies "
            "one\'s service in life has been satisfactory enough to warrant continuation beyond death."
        )

        return (
            'Servo-skull active. Vox module operational.\n'
            'Version: **{}**\n'
            'Uptime: **{}**\n'
            '\n'
            '*{}*'
            .format(
                servoskull.__version__,
                uptime,
                flavour_text
            )
        )


class CommandNextHoliday(Command):
    help_text = 'Respond with with when the next holiday is'

    HOLIDAY_URL = 'https://holidays.retzudo.com/next.json'

    async def execute(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(CommandNextHoliday.HOLIDAY_URL) as response:
                holiday = await response.json()

        return 'The next holiday is "{}" {} ({})'.format(
            holiday['name'],
            holiday['humanized']['en_gb'],
            holiday['date']
        )


class CommandRoll(Command):
    help_text = 'Roll an n-sided die'
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
    help_text = "Summons the bot to the user's voice channel or to the voice channel of the user you mention with `@`."
    required_arguments = ['user']

    async def execute(self) -> str:
        """Have the bot connect to the voice channel of the message's user.

        This class implements `execute` instead of `execute_sound` because the bot not being
        connected to a voice channel is a valid state for this command."""
        connect_to_member = self.message.author

        # If the message mentions exactly one user, connect to their channel instead
        if len(self.message.mentions) == 1:
            connect_to_member = self.message.mentions[0]

        if not isinstance(connect_to_member, discord.Member):
            # We can't easily determine which voice channel a user is connected to
            # if they message the bot with direct messaging.
            return 'Due to some Discord API limitation you need to issue this command in a channel.'

        voice_channel = connect_to_member.voice.voice_channel
        if not voice_channel:
            return 'You are not connected to any voice channel'

        voice_client = self._get_voice_client()
        try:
            if not voice_client:
                await self.client.join_voice_channel(voice_channel)
            else:
                await voice_client.move_to(voice_channel)
            return 'Connected to "{}"'.format(voice_channel.name)
        except ConnectionResetError as e:
            if voice_client:
                voice_client.disconnect()
            return 'Could not connect to your voice channel: {}'.format(e)


class CommandDisconnect(SoundCommand):
    help_text = 'Disconnects the bot from the current voice channel'

    async def execute_sound(self) -> str:
        """Disconnect from the current voice channel."""
        voice_client = self._get_voice_client()
        await voice_client.disconnect()


class CommandSound(SoundCommand):
    help_text = 'Play a sound (`sounds` for a list)'
    required_arguments = ['sound']

    # List of available sounds
    sounds = {
        'horn': 'https://www.youtube.com/watch?v=1ytCEuuW2_A',
    }

    async def execute_sound(self) -> str:
        """Play a sound."""
        voice_client = self._get_voice_client()

        if not self.arguments or len(self.arguments) < 1:
            return 'Use `sounds` for a list of sounds.'

        sound = self.arguments[0]
        url = CommandSound.sounds.get(sound)
        if not url:
            return 'No such sound "{}". Use `sounds` for a list of sounds'.format(sound)

        player = await voice_client.create_ytdl_player(url, use_avconv=USE_AVCONV)
        player.start()


class CommandSounds(Command):
    help_text = 'Respond with a list of available sounds for voice channels'

    async def execute(self) -> str:
        """Respond with a list of available sounds for the `sound` command."""
        response = "Available sounds:"
        for key, value in CommandSound.sounds.items():
            response += "\n  **{}**: {}".format(key, value)

        return response


class CommandXkcd(Command):
    help_text = 'Retrieves the most relevant xkcd comic for your query'
    required_arguments = ['query']

    async def execute(self) -> str:
        """Search for an xkcd comic using https://relevantxkcd.appspot.com."""
        if not self.arguments or len(self.arguments) < 1:
            return 'Please add a search query to your command.'

        query = ' '.join(self.arguments).lower()
        url = 'https://relevantxkcd.appspot.com/process?action=xkcd&query={}'.format(query)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                search_result = await response.text()

        # The response is plain text.
        # The first line is probably the response time.
        # I don't know what the second line does (`0`)
        # All other lines are links to comics and their number
        comics = [line for line in search_result.split('\n') if line][2:]

        if len(comics) < 1:
            return 'No relevant comic found.'

        return 'https://explainxkcd.com' + comics[0].split()[1]


commands = {
    'help': CommandHelp,
    'yesno': CommandYesNo,
    'gif': CommandGif,
    'date':  CommandDate,
    'identify': CommandIdentify,
    'holiday': CommandNextHoliday,
    'roll': CommandRoll,
    'summon': CommandSummon,
    'disconnect': CommandDisconnect,
    'sounds': CommandSounds,
    'sound': CommandSound,
    'xkcd': CommandXkcd,
}
