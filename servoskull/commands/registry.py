from functools import wraps
from servoskull.commands.passive import PassiveCommand

commands = {}
passive_commands = {}


def register(trigger):
    """A decorator that registers commands

    trigger: the string prepended by the command prefix users have
             to enter to trigger the command.
    passive: Whether the command is a passive command."""
    def decorator(cls):
        is_passive = issubclass(cls, PassiveCommand)
        if is_passive:
            passive_commands[trigger] = cls
        else:
            commands[trigger] = cls

        @wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)

        return wrapper

    return decorator
