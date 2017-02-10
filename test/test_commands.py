from servoskull import commands


def test_cmd_help():
    response = commands.cmd_help()

    assert response.startswith('Available commands:')


def test_cmd_yesno():
    response = commands.cmd_yesno()

    assert response in ['yes', 'no']


def test_cmd_gif():
    response = commands.cmd_gif()
    assert response.startswith('Find a gif')

    response = commands.cmd_gif('worf')
    assert response.startswith('https://')


def test_cmd_date():
    import re
    response = commands.cmd_date()

    assert re.match("^By the Emperor's grace it is 0 \d{3} \d{3}\.M\d$", response)


def test_cmd_identify():
    response = commands.cmd_identify()

    assert len(response) > 100
    assert response.startswith('A Servo-skull is a drone-like')


def test_cmd_next_holiday():
    import re
    response = commands.cmd_next_holiday()

    assert re.match('^The next holiday is "\w+" .* \(\d{4}-\d{2}-\d{2}\)$', response)


def test_cmd_roll():
    response = commands.cmd_roll()
    assert response == 'Please specify a valid integer >= 2'

    response = commands.cmd_roll([])
    assert response == 'Please specify a valid integer >= 2'

    response = commands.cmd_roll(['1'])
    assert response.startswith('Please specify a valid integer >= 2')

    response = commands.cmd_roll(['0'])
    assert response.startswith('Please specify a valid integer >= 2')

    response = commands.cmd_roll(['-23'])
    assert response.startswith('Please specify a valid integer >= 2')

    response = commands.cmd_roll(['bla'])
    assert response == 'Please specify a valid integer >= 2'

    response = commands.cmd_roll(['bla', 'bla', 'bla'])
    assert response == 'Please specify a valid integer >= 2'

    response = commands.cmd_roll(['6'])
    assert response.startswith('Rolled a 6-sided die:')

    response = commands.cmd_roll(['6', 'bla'])
    assert response.startswith('Rolled a 6-sided die:')

    response = commands.cmd_roll(['100'])
    assert response.startswith('Rolled a 100-sided die:')