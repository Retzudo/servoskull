from servoskull import passivecommands


class DottedDict(dict):
    def __getattr__(self, item):
        return self.get(item)


def test_reddit_comment_command():
    command = passivecommands.RedditCommentCommand(message=DottedDict(
        content='test'
    ))
    assert command.is_triggered() is False

    command = passivecommands.RedditCommentCommand(message=DottedDict(
        content='bla bla https://reddit.com/r/somesubreddit/comments yada yada'
    ))
    assert command.is_triggered() is True
