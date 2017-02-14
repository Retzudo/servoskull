import pytest

from servoskull import commands


@pytest.mark.asyncio
async def test_cmd_help():
    command = commands.CommandHelp()
    response = await command.execute()

    assert response.startswith('Available commands:')
    assert len(response.split('\n')) == len(commands.commands.keys()) + 2


@pytest.mark.asyncio
async def test_cmd_yesno():
    command = commands.CommandYesNo()
    response = await command.execute()

    assert response in ['yes', 'no']


@pytest.mark.asyncio
async def test_cmd_gif():
    command = commands.CommandGif()
    response = await command.execute()
    assert response.startswith('Find a gif')

    command = commands.CommandGif(arguments=['worf'])
    response = await command.execute()
    assert response.startswith('https://')


@pytest.mark.asyncio
async def test_cmd_date():
    import re
    command = commands.CommandDate()
    response = await command.execute()

    assert re.match("^By the Emperor's grace it is 0 \d{3} \d{3}\.M\d$", response)


@pytest.mark.asyncio
async def test_cmd_identify():
    command = commands.CommandIdentify()
    response = await command.execute()

    assert len(response) > 100
    assert response.startswith('A Servo-skull is a drone-like')


@pytest.mark.asyncio
async def test_cmd_next_holiday():
    import re
    command = commands.CommandNextHoliday()
    response = await command.execute()

    assert re.match('^The next holiday is "\w+" .* \(\d{4}-\d{2}-\d{2}\)$', response)


@pytest.mark.asyncio
async def test_cmd_roll():
    command = commands.CommandRoll()
    response = await command.execute()
    assert response == 'Please specify a valid integer >= 2'

    command = commands.CommandRoll(arguments=[])
    response = await command.execute()
    assert response == 'Please specify a valid integer >= 2'

    command = commands.CommandRoll(arguments=['1'])
    response = await command.execute()
    assert response.startswith('Please specify a valid integer >= 2')

    command = commands.CommandRoll(arguments=['0'])
    response = await command.execute()
    assert response.startswith('Please specify a valid integer >= 2')

    command = commands.CommandRoll(arguments=['-23'])
    response = await command.execute()
    assert response.startswith('Please specify a valid integer >= 2')

    command = commands.CommandRoll(arguments=['bla'])
    response = await command.execute()
    assert response == 'Please specify a valid integer >= 2'

    command = commands.CommandRoll(arguments=['bla', 'bla', 'bla'])
    response = await command.execute()
    assert response == 'Please specify a valid integer >= 2'

    command = commands.CommandRoll(arguments=['6'])
    response = await command.execute()
    assert response.startswith('Rolled a 6-sided die:')

    command = commands.CommandRoll(arguments=['6', 'bla'])
    response = await command.execute()
    assert response.startswith('Rolled a 6-sided die:')

    command = commands.CommandRoll(arguments=['100'])
    response = await command.execute()
    assert response.startswith('Rolled a 100-sided die:')


@pytest.mark.asyncio
async def test_cmd_sounds():
    command = commands.CommandSounds()
    response = await command.execute()

    assert response.startswith('Available sounds:')
    assert len(response.split('\n')) == len(commands.CommandSound.sounds) + 1
