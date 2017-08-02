"""Regular commands that are actively triggered by a user and need to know about all other commands."""
from servoskull.commands import registry
from servoskull.commands.regular import Command
from servoskull.settings import CMD_PREFIX


@registry.register('help')
class CommandHelp(Command):
    help_text = 'List all commands'

    async def execute(self) -> str:
        """Respond with a help message containing all available commands."""
        regular_commands = registry.get_regular_commands()
        sound_commands = registry.get_sound_commands()
        passive_commands = registry.get_passive_commands()

        response = 'Available commands:'
        for command, dct in regular_commands.items():
            class_ = dct.get('class')
            arguments = ''
            for argument in class_.required_arguments:
                arguments += '**<{}>** '.format(argument)

            response += '\n  **{}{}** {}- {}'.format(CMD_PREFIX, command, arguments, class_.help_text)

        response += '\n\nAvailable sound commands:'
        for command, dct in sound_commands.items():
            class_ = dct.get('class')
            arguments = ''
            for argument in class_.required_arguments:
                arguments += '**<{}>** '.format(argument)

            response += '\n  **{}{}** {}- {}'.format(CMD_PREFIX, command, arguments, class_.help_text)

        response += ('\n\nAvailable passive commands '
                     '(these trigger automatically if a message fulfills certain conditions):')
        for text, dct in passive_commands.items():
            class_ = dct.get('class')
            response += '\n  **{}** - {}'.format(text, class_.help_text)

        response += '\n\nEither prepend your command with `{}` or mention the bot using `@`.'.format(CMD_PREFIX)

        return response
