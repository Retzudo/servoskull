"""Due to the nature of sound commands, we can't easily test them.

We would have to do *a lot* of mocking which is probably more work than
just quickly testing it on a real server yourself.
"""
import pytest

from servoskull import soundcommands


@pytest.mark.asyncio
async def test_cmd_sounds():
    command = soundcommands.CommandSounds()
    response = await command.execute()

    assert response.startswith('Available sounds:')
    assert len(response.split('\n')) == len(soundcommands.CommandSound.sounds) + 1