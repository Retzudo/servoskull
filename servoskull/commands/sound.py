"""Commands that are actively triggered by a user and require the bot to be connected to a voice channel."""
import discord
import youtube_dl

from servoskull.commands import registry
from servoskull.commands.regular import Command
from servoskull.settings import USE_AVCONV


_current_volume = 1.0


class SoundCommand(Command):
    """Base class for commands that require the bot
    to be connected to a voice channel."""
    async def execute_sound(self):
        """Should be implemented by SoundCommand children instead of `execute`."""
        raise NotImplementedError()

    async def execute(self) -> str:
        """We override the `execute` method of `Command` and run a check before every execution
        if the bot is connected to a voice channel."""
        if not self.voice_client:
            return 'I am not connected to any voice channel. Use `summon` to have me connect to one.'
        else:
            return await self.execute_sound()

    @property
    def voice_client(self):
        """Return the currently connected voice client of the message's server."""
        voice_client = self.message.server.voice_client
        if voice_client and not hasattr(voice_client, 'current_player'):
            voice_client.current_player = None

        return voice_client

    @property
    def current_player(self):
        if self.voice_client:
            return self.voice_client.current_player

    @current_player.setter
    def current_player(self, value):
        if self.voice_client:
            self.voice_client.current_player = value

    def _unset_current_player(self):
        self.current_player = None


@registry.register('summon', sound=True)
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

        # Sometimes the client can't connect to voice channels due to
        # unknown network problems.
        try:
            if not self.voice_client:
                await self.client.join_voice_channel(voice_channel)
            else:
                await self.voice_client.move_to(voice_channel)
            user_name = connect_to_member.nick or connect_to_member.name
            return 'Connected to {}\'s voice channel "{}"'.format(user_name, voice_channel.name)

        except ConnectionResetError as e:
            if self.voice_client:
                self.voice_client.disconnect()
            return 'Could not connect to your voice channel: {}'.format(e)


@registry.register('disconnect', sound=True)
class CommandDisconnect(SoundCommand):
    help_text = 'Disconnects the bot from the current voice channel'

    async def execute_sound(self):
        """Disconnect from the current voice channel."""
        await self.voice_client.disconnect()


@registry.register('sound', sound=True)
class CommandSound(SoundCommand):
    help_text = 'Play a sound (`sounds` for a list)'
    required_arguments = ['sound']

    # List of available sounds
    sounds = {
        'horn': {
            'url': 'https://www.youtube.com/watch?v=9Jz1TjCphXE',
            'volume': 0.2,
        },
    }

    async def execute_sound(self) -> str:
        """Play a sound."""
        if not self.arguments or len(self.arguments) < 1:
            return 'Use `sounds` for a list of sounds.'

        sound_name = self.arguments[0]
        sound = CommandSound.sounds.get(sound_name)
        if not sound:
            return 'No such sound "{}". Use `sounds` for a list of sounds'.format(sound_name)

        if self.current_player:
            return 'Something is already playing.'

        try:
            player = await self.voice_client.create_ytdl_player(
                sound.get('url'),
                use_avconv=USE_AVCONV,
            )
            player.volume = sound.get('volume', 1.0)
            player.start()
            self.current_player = player
        except youtube_dl.utils.DownloadError as e:
            return str(e)


@registry.register('sounds', sound=True)
class CommandSounds(Command):
    help_text = 'Respond with a list of available sounds for voice channels'

    async def execute(self) -> str:
        """Respond with a list of available sounds for the `sound` command."""
        response = "Available sounds:"
        for key, value in CommandSound.sounds.items():
            response += "\n  **{}**: <{}>".format(key, value['url'])

        return response


@registry.register('play', sound=True)
class CommandPlay(SoundCommand):
    help_text = 'Plays the video from the provided YouTube link in a voice channel or continues a paused video'

    async def execute_sound(self):
        if not self.arguments or len(self.arguments) < 1:
            if self.current_player:
                self.current_player.resume()
                return 'Unpaused'
            else:
                return 'No video running and no link specified'

        if self.current_player:
            self.current_player.stop()

        url = self.arguments[0]
        try:
            player = await self.voice_client.create_ytdl_player(
                url,
                use_avconv=USE_AVCONV,
                after=self._unset_current_player,
            )
            player.volume = _current_volume
            player.start()
            self.current_player = player
        except youtube_dl.utils.DownloadError as e:
            return str(e)


@registry.register('pause', sound=True)
class CommandPause(SoundCommand):
    help_text = 'Pauses the current YouTube video'

    async def execute_sound(self):
        if not self.current_player:
            return 'No video playing'

        self.current_player.pause()

        return 'Paused'


@registry.register('stop', sound=True)
class CommandStop(SoundCommand):
    help_text = 'Stops the current YouTube video'

    async def execute_sound(self):
        if not self.current_player:
            return 'No video playing'

        self.current_player.stop()

        return 'Stopped'


@registry.register('volume', sound=True)
class CommandVolume(SoundCommand):
    help_text = 'Sets the volume for YouTube videos to x%. Default is 100%'
    required_arguments = ['volume in %']

    async def execute_sound(self):
        percent_str = self.arguments[0]

        try:
            percent = int(percent_str)
        except ValueError:
            return

        if 0 < percent > 100:
            return

        volume = percent / 100

        global _current_volume  # I'm sooo sorry...
        _current_volume = volume
        if self.current_player:
            self.current_player.volume = volume