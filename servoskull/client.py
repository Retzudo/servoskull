from difflib import get_close_matches

import discord

from servoskull import ServoSkullError
from servoskull.settings import CMD_PREFIX, DISCORD_TOKEN, ENV_PREFIX, AUTOGIF
from servoskull.skulllogging import logger
from servoskull.commands import registry

client = discord.Client()


def get_command_by_prefix(message_string):
    """Extract the command an its arguments from a string
    starting with a command prefix.

    The command is the word prepended by the configured command prefix.
    The arguments are a list of words followed by the command.
    """
    command = message_string.split()[0][len(CMD_PREFIX):]
    arguments = message_string.split()[1:]

    return command, arguments


def get_command_by_mention(message_string, client_id):
    """Extract the command and its arguments from a string
    where the bot was mentioned in.

    The command is the first word in a list of words in the message without
    word the begins with `@` (mentions).
    The arguments are a list of words followed by the command.
    """
    words = [word for word in message_string.split() if client_id not in word]
    command = words[0]
    arguments = words[1:]

    return command, arguments


def get_closest_command(command):
    """Given a string, return the command that's most similar to it."""
    available_commands = {**registry.get_regular_commands(), **registry.get_sound_commands()}

    closest_commands = get_close_matches(command.lower(), available_commands, 1)
    if len(closest_commands) >= 1:
        return closest_commands[0]
    else:
        return None


@client.event
async def on_ready():
    logger.info('Logged in as {} ({})'.format(client.user.name, client.user.id))


@client.event
async def on_message(message):
    """Listen for messages."""
    if message.author.id == client.user.id:
        # Make it so that the bot can't trigger itself
        return

    if message.mention_everyone:
        # Don't trigger on @here etc.
        return

    command = None
    arguments = None

    await execute_passive_commands(message)

    logger.debug('Read message: "{}"'.format(message.content))
    if message.content.startswith(CMD_PREFIX):
        command, arguments = get_command_by_prefix(message.content)
        logger.debug('Read command by prefix - command: "{}"; arguments: {}'.format(command, arguments))
    elif client.user.mentioned_in(message):
        command, arguments = get_command_by_mention(message.content, client.user.id)
        logger.debug('Read command by mention - command: "{}"; arguments: {}'.format(command, arguments))

    if command:
        await execute_command(command, arguments, message)


async def execute_command(command, arguments, message):
    commands = {**registry.get_regular_commands(), **registry.get_sound_commands()}
    if command not in commands:
        logger.debug('User {} issued non-existing command "{}"'.format(message.author, command))
        response = 'No such command "{}".'.format(command, get_closest_command(command))
        closest_command = get_closest_command(command)
        if closest_command:
            response += ' Did you mean {}?'.format(closest_command)
        response += '\nTry `!help` for a list of commands'
        if AUTOGIF:
            # If AUTOGIF is enable with an env var, also respond with a GIF that matches
            # the command + arguments
            gif = await registry.commands['gif']['class'](arguments=[command] + arguments).execute()
            if 'no gif found' not in gif.lower():
                response += "\nAnyway, here's a GIF that matches your request:\n{}".format(gif)
        logger.info(response)
    else:
        class_ = registry.commands[command]['class']
        logger.debug('Executing command "{}"'.format(command))
        command = class_(arguments=arguments, message=message, client=client)
        response = await command.execute()

    if response:
        # Only respond if there's actually a response.
        # Some commands don't need to respond with text.
        if isinstance(response, str):
            await client.send_message(message.channel, content=response)
        if isinstance(response, discord.Embed):
            await client.send_message(message.channel, embed=response)
        logger.info(response)


async def execute_passive_commands(message):
    for command_class in registry.get_passive_commands().values():
        command = command_class['class'](message=message)
        response = None

        if command.is_triggered():
            logger.info('Message triggered passive command {}'.format(command_class))
            response = await command.execute()

        if response:
            await client.send_message(message.channel, response)
            logger.info(response)


if __name__ == '__main__':
    try:
        if not CMD_PREFIX:
            raise ServoSkullError('Invalid command prefix')
        if not DISCORD_TOKEN:
            raise ServoSkullError(
                'Discord API token not set with the {} environment variable'.format(ENV_PREFIX)
            )

        logger.debug('Starting Discord client with token {}...'.format(DISCORD_TOKEN[:5]))
        client.run(DISCORD_TOKEN)
    except ServoSkullError as error:
        logger.error(error, exc_info=True)
    finally:
        client.close()
