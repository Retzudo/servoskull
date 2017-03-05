import aiohttp
import re

from servoskull.logging import logger


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


class RedditCommentCommand(PassiveCommand):
    """If a user posts a link to a Reddit comment, respond with the comment
    text and some info about the Reddit post."""
    def __init__(self, message):
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
            post = json[0]['data']['children'][0]['data']
            comment = json[1]['data']['children'][0]['data']
        except (IndexError, KeyError) as e:
            logger.warning('Could not compile message because {}'.format(e))
            return None
        else:
            return """↑*{post[ups]}* **{post[title]}**:

*/u/{comment[author]} said (↑{comment[ups]}):*
{comment[body]}""".format(post=post, comment=comment)

    async def execute(self) -> str:
        logger.info('Fetching Reddit data')
        async with aiohttp.ClientSession() as session:
            async with session.get(self._get_url()) as response:
                json = await response.json()

        logger.info('Size of response JSON: {}'.format(len(json)))

        if json:
            return self._compile_message(json)


passive_commands = [
    RedditCommentCommand
]
