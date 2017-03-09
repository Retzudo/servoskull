import pytest

from servoskull import metacommands


@pytest.mark.asyncio
async def test_cmd_help():
    command = metacommands.CommandHelp()
    response = await command.execute()

    assert response.startswith('Available commands:')