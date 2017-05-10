[![Build Status](https://travis-ci.org/Retzudo/servoskull.svg?branch=master)](https://travis-ci.org/Retzudo/servoskull)

# Servo-skull

## What is it?

A custom Discord bot for my server.

## What does it do?

1. Respond to commands either by prefix or when mentioned like a regular user.
2. Play sounds in voice channels.
3. Passively respond to messages that contain certain keywords

## What does it *not* do?

1. User management like kicking and banning
1. Greet people when they come online
1. Other crap I don't need but 99% of other bots seem to do

## Running the bot

### Checking for ffmpeg

Debian systems prior to 9 (Stretch) and Ubuntu systems prior to 15.04
use *libav* instead of *ffmpeg*. Therefore you need to have the environment
variable `SERVOSKULL_AVCONV` with any value present on those systems
before running the bot. If it doesn't exist, the bot won't be able to
play sounds in voice channels because it assumes an `ffmpeg` executable
to be present in `$PATH`.

### Docker

1. Build the Docker image: `docker build -t servoskull .`
2. Run a Docker container: `docker run --name servoskull --restart=always -e SERVOSKULL_TOKEN=<YOUR_TOKEN> servoskull`
3. Open `https://discordapp.com/api/oauth2/authorize?scope=bot&permissions=0&client_id=<YOUR_CLIENT_ID>`.
   You can get your client ID from your Discord dev dashboard.

If you want to change the default command prefix `!` to something else, add another parameters
`-e SERVOSKULL_PREFIX=<PREFIX>` e. g. `-e SERVOSKULL_PREFIX=#`


## Extending the command list

All commands must either return `None`, a `str` or an `discord.Embed` object.

### Regular command

A regular command is a command that does *something* and optionally returns a string. Create a new class in `regular.py`, inherit from `Command` and override the `execute` method where you can do anything. If you want the bot respond with a message, just return a string. Finally add your new class to the dictionary at the bottom of the file.

### Sound command

A sound command is a command that requires the bot to be connected to a voice channel before running the command. E. g. a command that plays a sound. Create a new class in `regular.py`, inherit from `SoundCommand` and override the `execute_sound` method (*not* the `execute` method). Finally add your new class to the dictionary at the bottom of the file.

### Passive command

A passive command is a command that can be triggered by any message the bot can listen to. Create a new class in `passive.py`, inherit from `PassiveCommand` and override `is_triggered` as well as `execute`. If somebody writes a message in Discord, the bot listens to it and uses the `is_triggered` method to check if it should call the class's `execute` method. Finally add your new class to the list at the bottom of the file.