import logging
from difflib import get_close_matches

import discord

from servoskull.commands import commands
from servoskull.settings import CMD_PREFIX, DISCORD_TOKEN, ENV_PREFIX

client = discord.Client()


class ServoSkullError(Exception):
    pass


def get_command_by_prefix(message_string):
    """Extract the command an its arguments from a string
    starting with a command prefix.

    The command is the word prepended by the configured command prefix.
    The arguments are a list of words followed by the command.
    """
    command = message_string.split()[0][len(CMD_PREFIX):]
    arguments = message_string.split()[1:]

    return command, arguments


def get_command_by_mention(message_string):
    """Extract the command and its arguments from a string
    where the bot was mentioned in.

    The command is the first word in a list of words in the message without
    word the begins with `@` (mentions).
    The arguments are a list of words followed by the command.
    """
    words = [word for word in message_string.split() if not word.startswith('<@!')]
    command = words[0]
    arguments = words[1:]

    return command, arguments


def get_closest_command(command):
    """Given a string, return the command that's most similar to it."""
    available_commands = commands.keys()

    closest_commands = get_close_matches(command.lower(), available_commands, 1)
    if len(closest_commands) >= 1:
        return closest_commands[0]
    else:
        return None


@client.event
async def on_ready():
    logging.info('Logged in as {} ({})'.format(client.user.name, client.user.id))


@client.event
async def on_message(message):
    """Listen for messages."""
    command = None
    arguments = None

    if message.content.startswith(CMD_PREFIX):
        command, arguments = get_command_by_prefix(message.content)
    elif client.user.mentioned_in(message):
        command, arguments = get_command_by_mention(message.content)

    if command:
        await execute_command(command, arguments, client, message)


async def execute_command(command, arguments, discord_client, message=None):
    if command not in commands:
        response = 'No such command "{}".'.format(command, get_closest_command(command))
        closest_command = get_closest_command(command)
        if closest_command:
            response += ' Did you mean {}?'.format(closest_command)
    else:
        class_ = commands[command]
        command = class_(arguments=arguments, message=message, client=client)
        response = await command.execute()

    if response:
        # Only response if there's actually a response.
        # Some commands don't need to respond with text.
        await discord_client.send_message(message.channel, response)
        logging.info(response)


if __name__ == '__main__':
    if not CMD_PREFIX:
        client.close()
        raise ServoSkullError('Invalid command prefix')
    if not DISCORD_TOKEN:
        client.close()
        raise ServoSkullError(
            'Discord API token not set with the {} environment variable'.format(ENV_PREFIX)
        )

    client.run(DISCORD_TOKEN)
