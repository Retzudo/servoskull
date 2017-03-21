import pytest

from servoskull.commands import passive


class DottedDict(dict):
    def __getattr__(self, item):
        return self.get(item)


@pytest.mark.asyncio
async def test_reddit_comment_command():
    command = passive.RedditCommentCommand(message=DottedDict(
        content='test'
    ))
    assert command.is_triggered() is False

    # Link to a self post
    command = passive.RedditCommentCommand(message=DottedDict(
        content='https://www.reddit.com/r/IAmA/comments/z1c9z/i_am_barack_obama_president_of_the_united_states/'
    ))
    assert command.is_triggered() is False

    # Perma-link to a comment in a post
    command = passive.RedditCommentCommand(message=DottedDict(
        content='https://www.reddit.com/r/IAmA/comments/z1c9z/i_am_barack_obama_president_of_the_united_states/c60o0iw/'
    ))
    assert command.is_triggered() is True

    url = 'https://www.reddit.com/r/IAmA/comments/z1c9z/i_am_barack_obama_president_of_the_united_states/c60o0iw'
    command = passive.RedditCommentCommand(message=DottedDict(content='asdf bla {} yada yada'.format(url)))
    assert command._get_url() == url + '.json'

    message = command._compile_message({})
    assert message is None

    response = await command.execute()
    assert 'Here is a collection of all the questions and answers' in response

    command._get_url = lambda: 'http://httpbin.org/get'
    response = await command.execute()
    assert response is None

    command._get_url = lambda: 'http://httpbin.org/status/404'
    response = await command.execute()
    assert response is None
