"""Due to the nature of sound commands, we can't easily test them.

We would have to do *a lot* of mocking which is probably more work and
probably more error-prone than just quickly testing it on a real server
ourselves.
"""
import pytest

from servoskull.commands import sound


@pytest.mark.asyncio
async def test_cmd_sounds():
    command = sound.CommandSounds()
    response = await command.execute()

    assert response.startswith('Available sounds:')
    assert len(response.split('\n')) == len(sound.CommandSound.sounds) + 1