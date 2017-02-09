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

    assert re.match("^By the Emperor's grace it is 0 \d{3} \d{3}\.M\d", response)


def test_cmd_identify():
    response = commands.cmd_identify()

    assert len(response) > 100
    assert response.startswith('A Servo-skull is a drone-like')
