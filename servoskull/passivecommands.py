import re

class PassiveCommand:
    """Base class for passive commands

    A passive command is a command that is not actively triggered by a user but
    is reacting to a message that contain's a special keyword.
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
        self.regex = re.compile('https?://(www\.)?reddit.com/r/\w+/comments')

    def is_triggered(self) -> bool:
        return self.regex.search(self.message.content) is not None

    def _get_url(self):
        for word in self.message.content.split():
            if self.regex.match(word):
                return word

    async def execute(self) -> str:
        return self._get_url()


passive_commands = [
    PassiveCommand
]
