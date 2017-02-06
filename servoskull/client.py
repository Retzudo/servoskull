import discord
import logging
import os


client = discord.Client()
TOKEN_ENVIRON_VARIABLE = 'SERVOSKULL_TOKEN'
CMD_PREFIX = os.getenv('SERVOSKULL_CMD_PREFIX', '!')


def get_command(message_string):
    return message_string[len(CMD_PREFIX):]


async def execute_command(command, message):
    msg = 'No such command "{}"'.format(command)

    await client.send_message(message.channel, msg)
    logging.warn(msg)


@client.event
async def on_ready():
    logging.info('Logged in as {} ({})'.format(client.user.name, client.user.id))


@client.event
async def on_message(message):
    if message.content.startswith(CMD_PREFIX):
        command = get_command(message.content)
        await execute_command(command, message)


class ServoSkullError(Exception):
    pass


if __name__ == '__main__':
    token = os.getenv(TOKEN_ENVIRON_VARIABLE, None)
    if not CMD_PREFIX:
        client.close()
        raise ServoSkullError('Invalid command prefix')
    if not token:
        client.close()
        raise ServoSkullError(
            'Discord API token not set with the {} environment variable'.format(TOKEN_ENVIRON_VARIABLE)
        )

    client.run(token)
