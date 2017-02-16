from datetime import datetime
import os

ENV_TOKEN = 'SERVOSKULL_TOKEN'
ENV_PREFIX = 'SERVOSKULL_CMD_PREFIX'
ENV_USE_AVCONV = 'SERVOSKULL_AVCONV'

DISCORD_TOKEN = os.getenv(ENV_TOKEN, None)
CMD_PREFIX = os.getenv(ENV_PREFIX, '!')

# Most systems use ffmpeg versions of Debian <9 and Ubuntu <15.04
# use libav instead. This env variable needs to be set on those
# systems including the Docker image.
USE_AVCONV = True if os.getenv(ENV_USE_AVCONV) else False
