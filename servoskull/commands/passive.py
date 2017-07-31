"""Commands that are triggered passively by messages in text channels that fulfill certain trigger conditions
(e. g. containing some special text or a link)."""
import aiohttp

from servoskull.commands import registry
from servoskull.skulllogging import logger


class PassiveCommand:
    """Base class for passive commands

    A passive command is a command that is not actively triggered by a user but
    reacts to a message that contains a special keyword.
    """
    def __init__(self, message):
        self.message = message

    async def execute(self) -> str:
        raise NotImplementedError()

    def is_triggered(self) -> bool:
        """Returns True if the message content triggers the command, else False."""
        raise NotImplementedError()


@registry.register('Reddit comment')
class RedditCommentCommand(PassiveCommand):
    """If a user posts a link to a Reddit comment, respond with the comment
    text and some info about the Reddit post."""
    help_text = 'Triggers when somebody posts a link to a Reddit comment'

    def __init__(self, message):
        import re

        super().__init__(message)
        self.regex = re.compile('https?://(www\.)?reddit.com/r/\w+/comments/[\w\d]+/[\w\d_]+/[\w\d]+')

    def is_triggered(self) -> bool:
        return self.regex.search(self.message.content) is not None

    def _get_url(self):
        for word in self.message.content.split():
            if self.regex.match(word):
                return word.rstrip('/') + '.json'

    @staticmethod
    def _compile_message(json):
        try:
            # Some digging around and hoping the json
            # structure is what we expect
            comment = json[1]['data']['children'][0]['data']
        except (IndexError, KeyError) as e:
            logger.warning('Could not compile message because {}'.format(e))
            return None
        else:
            return '/u/{comment[author]} said (↑{comment[ups]}):\n{comment[body]}'.format(comment=comment)

    async def execute(self) -> str:
        logger.info('Fetching Reddit data')
        async with aiohttp.ClientSession() as session:
            async with session.get(self._get_url()) as response:
                json = await response.json()

        if json:
            logger.info('Size of response JSON: {}'.format(len(json)))
            return self._compile_message(json)
