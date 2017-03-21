import pytest

from servoskull.commands import meta


@pytest.mark.asyncio
async def test_cmd_help():
    command = meta.CommandHelp()
    response = await command.execute()

    assert response.startswith('Available commands:')