[![Build Status](https://travis-ci.org/Retzudo/servoskull.svg?branch=master)](https://travis-ci.org/Retzudo/servoskull)

# Servo-skull

## What is it?

A custom Discord bot for my server.

## What does it do?

Respond to commands either by prefix or when mentioned like a regular user. Can also play some
sounds in voice channels.

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
Create a new class in `commands.py` that inherits from `Command` or `SoundCommand` depending on what you need and
implement the `execute` method. Finally, add your new class to the `commands` dictionary. The class properties
`help_text` and `required_arguments` are optional it's highly recommended you add them.
