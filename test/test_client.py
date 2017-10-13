def test_get_by_command_prefix():
    from servoskull import client

    string = '!test arg1 arg2 arg3 !asdf'

    command, arguments = client.get_command_by_prefix(string)

    assert command == 'test'
    assert arguments == ['arg1', 'arg2', 'arg3', '!asdf']

    string = '!test <@!278126797306986496> arg1 arg2 arg3 !asdf'

    command, arguments = client.get_command_by_prefix(string)

    assert command == 'test'
    assert arguments == ['<@!278126797306986496>', 'arg1', 'arg2', 'arg3', '!asdf']


def test_get_command_by_mention():
    from servoskull import client

    string = '<@!278126797306986496> test arg1 arg2 arg3 <@!278126797306986497>'

    command, arguments = client.get_command_by_mention(string, '278126797306986496')

    assert command == 'test'
    assert arguments == ['arg1', 'arg2', 'arg3', '<@!278126797306986497>']


def test_get_closest_command():
    from servoskull import client

    assert client.get_closest_command('yeno') == 'yesno'
    assert client.get_closest_command('blabla') is None