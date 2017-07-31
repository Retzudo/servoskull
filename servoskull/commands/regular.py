"""Commands that are actively triggered by a user."""
import random

import aiohttp
from discord import Embed
from imperialdate import ImperialDate

from servoskull.skulllogging import logger
from servoskull.commands import registry


class Command:
    """Base class for all commands."""
    help_text = None
    required_arguments = []

    def __init__(self, **kwargs):
        self.arguments = kwargs.get('arguments')
        self.message = kwargs.get('message')
        self.client = kwargs.get('client')

    async def execute(self):
        raise NotImplementedError()

    def _get_mentions(self):
        """Return Member/User objects for all mentioned users except the bot."""
        return [member for member in self.message.mentions if member.id != self.client.user.id]


@registry.register('yesno')
class CommandYesNo(Command):
    help_text = 'Respond with yes or no'

    async def execute(self) -> str:
        """Respond with 'yes' or 'no', chosen randomly."""
        return random.choice(['yes', 'no'])


@registry.register('gif')
class CommandGif(Command):
    required_arguments = ['name or tag']
    help_text = 'Respond with a gif from https://gifs.retzudo.com'

    GIFS_URL = 'https://gifs.retzudo.com/gifs.json'

    async def execute(self):
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
                response = Embed()
                response.set_image(url=gif['url'])
                return response

        return 'No gif found'


@registry.register('date')
class CommandDate(Command):
    help_text = 'Respond with the current Imperial Date'

    async def execute(self) -> str:
        """Respond with the current Imperial Date."""
        return "By the Emperor's grace it is {}".format(ImperialDate())


@registry.register('identify')
class CommandIdentify(Command):
    help_text = 'Identifies the servo-skull'

    async def execute(self) -> Embed:
        """Respond with some info and a little RP text."""
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        import servoskull

        now = datetime.now()
        uptime_delta = relativedelta(now, servoskull.start_time)
        uptime = '{0.days} days, {0.hours} hours, {0.minutes} minutes, {0.seconds} seconds'.format(uptime_delta)
        flavour_text = (
            "A Servo-skull is a drone-like robotic device that appears to be a human skull outfitted with electronic "
            "or cybernetic components that utilise embedded anti-gravity field generators to allow them to hover "
            "and drift bodiless through the air. They are fashioned from the skulls of loyal Adepts of the Adeptus "
            "Terra and other pious Imperial servants to which robotic components and an antigravitic impeller have "
            "been added. This is so that they may continue their work for the Emperor of Mankind even after death. To "
            "have one's skull chosen to serve as a Servo-skull is a great honour in the Imperium, for it implies "
            "one's service in life has been satisfactory enough to warrant continuation beyond death."
        )

        response = Embed()
        response.set_thumbnail(url='http://vignette3.wikia.nocookie.net/warhammer40k/images/c/c3/Servo-Skull-Front2.jpg/revision/latest?cb=20120711230906')
        response.title = 'Servo-skull active. Vox module operational.'
        response.add_field(name='Version', value=servoskull.__version__)
        response.add_field(name='Uptime', value=uptime)
        response.set_footer(text=flavour_text)

        return response


@registry.register('holiday')
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


@registry.register('roll')
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


@registry.register('xkcd')
class CommandXkcd(Command):
    help_text = 'Retrieves the most relevant xkcd comic for your query'
    required_arguments = ['query']

    async def execute(self) -> str:
        """Search for an xkcd comic using https://relevant-xkcd.github.io"""
        if not self.arguments or len(self.arguments) < 1:
            return 'Please add a search query to your command.'

        url = 'https://relevant-xkcd-backend.herokuapp.com/search'
        data = {
            'search': ' '.join(self.arguments).lower()
        }
        logger.info('Posting to URL {}: {}'.format(url, data))

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                data = await response.json()

        try:
            url = data['results'][0]['url']
        except (KeyError, TypeError) as e:
            logger.error(e, exc_info=True)
            return 'No relevant comic found.'

        logger.info('Returning xkcd {}'.format(url))
        if not url.startswith('https://') or not url.startswith('http://'):
            url = 'https://' + url
        return url
