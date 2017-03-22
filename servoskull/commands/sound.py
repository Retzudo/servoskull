"""Commands that are actively triggered by a user and require the bot to be connected to a voice channel."""
import discord

from servoskull.commands.regular import Command
from servoskull.settings import USE_AVCONV


class SoundCommand(Command):
    """Base class for commands that require the bot
    to be connected to a voice channel."""
    async def execute_sound(self):
        """Should be implemented by SoundCommand children instead of `execute`."""
        raise NotImplementedError()

    async def execute(self) -> str:
        """We override the `execute` method of `Command` and run a check before every execution
        if the bot is connected to a voice channel."""
        if not self._get_voice_client():
            return 'I am not connected to any voice channel. Use `summon` to have me connect to one.'
        else:
            return await self.execute_sound()

    def _get_voice_client(self):
        """Return the currently connected voice client of the message's server."""
        return self.message.server.voice_client


class CommandSummon(SoundCommand):
    help_text = "Summons the bot to the user's voice channel or to the voice channel of the user you mention with `@`."
    required_arguments = ['user']

    async def execute(self) -> str:
        """Have the bot connect to the voice channel of the message's user.

        This class implements `execute` instead of `execute_sound` because the bot not being
        connected to a voice channel is a valid state for this command."""
        connect_to_member = self.message.author

        # If the message mentions exactly one user, connect to their channel instead
        mentions = self._get_mentions()
        if len(mentions) == 1:
            connect_to_member = mentions[0]

        if not isinstance(connect_to_member, discord.Member):
            # 1. Users can be Members of multiple Discord servers.
            # 2. This includes the bot
            # 3. The bot and the requesting User can share many servers.
            # Thus we cannot easily determine on which server the user is connected to a voice channel
            # unless we implement such a search ourselves.
            return 'Due to some Discord API limitation you need to issue this command in a channel.'

        voice_channel = connect_to_member.voice.voice_channel
        if not voice_channel:
            return 'You are not connected to any voice channel'

        voice_client = self._get_voice_client()

        # Sometimes the client can't connect to voice channels due to
        # unknown network problems.
        try:
            if not voice_client:
                await self.client.join_voice_channel(voice_channel)
            else:
                await voice_client.move_to(voice_channel)
            user_name = connect_to_member.nick or connect_to_member.name
            return 'Connected to {}\'s voice channel "{}"'.format(user_name, voice_channel.name)

        except ConnectionResetError as e:
            if voice_client:
                voice_client.disconnect()
            return 'Could not connect to your voice channel: {}'.format(e)


class CommandDisconnect(SoundCommand):
    help_text = 'Disconnects the bot from the current voice channel'

    async def execute_sound(self):
        """Disconnect from the current voice channel."""
        voice_client = self._get_voice_client()
        await voice_client.disconnect()


class CommandSound(SoundCommand):
    help_text = 'Play a sound (`sounds` for a list)'
    required_arguments = ['sound']

    # List of available sounds
    sounds = {
        'horn': {
            'url': 'https://www.youtube.com/watch?v=1ytCEuuW2_A',
            'volume': 0.1,
        },
    }

    async def execute_sound(self) -> str:
        """Play a sound."""
        voice_client = self._get_voice_client()

        if not self.arguments or len(self.arguments) < 1:
            return 'Use `sounds` for a list of sounds.'

        sound_name = self.arguments[0]
        sound = CommandSound.sounds.get(sound_name)
        if not sound:
            return 'No such sound "{}". Use `sounds` for a list of sounds'.format(sound)

        player = await voice_client.create_ytdl_player(
            sound.get('url'),
            use_avconv=USE_AVCONV,
            options='-af "volume={}"'.format(sound.get('volume', 1.0))
        )
        player.start()


class CommandSounds(Command):
    help_text = 'Respond with a list of available sounds for voice channels'

    async def execute(self) -> str:
        """Respond with a list of available sounds for the `sound` command."""
        response = "Available sounds:"
        for key, value in CommandSound.sounds.items():
            response += "\n  **{}**: {}".format(key, value['url'])

        return response


commands = {
    'summon': CommandSummon,
    'disconnect': CommandDisconnect,
    'sounds': CommandSounds,
    'sound': CommandSound,
}