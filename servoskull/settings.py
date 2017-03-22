import os

ENV_TOKEN = 'SERVOSKULL_TOKEN'
ENV_PREFIX = 'SERVOSKULL_CMD_PREFIX'
ENV_USE_AVCONV = 'SERVOSKULL_AVCONV'
ENV_LOGLEVEL = 'SERVOSKULL_LOGLEVEL'
ENV_AUTOGIF = 'SERVOSKULL_AUTOGIF'

DISCORD_TOKEN = os.getenv(ENV_TOKEN, None)
CMD_PREFIX = os.getenv(ENV_PREFIX, '!')

# Most systems use ffmpeg versions of Debian <9 and Ubuntu <15.04
# use libav instead. This env variable needs to be set on those
# systems including the Docker image.
USE_AVCONV = True if os.getenv(ENV_USE_AVCONV) else False

LOGGING_LEVEL = os.getenv(ENV_LOGLEVEL, 'DEBUG')

# If enabled, the bot also responds with a GIF as if called with the !gif command
# if it can't find the originally requested command in addition to the normal "couldn't
# find that command" response.
AUTOGIF = True if os.getenv(ENV_AUTOGIF) else False
