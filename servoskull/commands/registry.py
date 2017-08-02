from functools import wraps

commands = {}


def register(trigger, passive=False, sound=False):
    """A decorator that registers commands

    trigger: the string prepended by the command prefix users have
             to enter to trigger the command.
    passive: Whether the command is a passive command."""
    def decorator(cls):
        commands[trigger] = {
            'passive': passive,
            'sound': sound,
            'class': cls,
        }

        @wraps(cls)
        def wrapper(*args, **kwargs):
            return cls(*args, **kwargs)

        return wrapper

    return decorator


def get_regular_commands():
    return {key: value for key, value in commands.items() if not value.get('passive') and not value.get('sound')}


def get_sound_commands():
    return {key: value for key, value in commands.items() if not value.get('passive') and value.get('sound')}


def get_passive_commands():
    return {key: value for key, value in commands.items() if value.get('passive') and not value.get('sound')}
