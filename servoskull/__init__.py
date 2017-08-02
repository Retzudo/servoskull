from datetime import datetime

__version__ = 'v1.8.0'

start_time = datetime.now()


class ServoSkullError(Exception):
    pass

from servoskull.commands.meta import *
from servoskull.commands.regular import *
from servoskull.commands.sound import *
from servoskull.commands.passive import *