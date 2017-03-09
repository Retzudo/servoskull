"""Regular commands that need to know about all other commands."""
from servoskull.commands import Command
from servoskull.commands import commands as regular_commands
from servoskull.settings import CMD_PREFIX
from servoskull.soundcommands import commands as sound_commands
from servoskull.passivecommands import commands as passive_commands


class CommandHelp(Command):
    help_text = 'List all commands'

    async def execute(self) -> str:
        """Respond with a help message containing all available commands."""
        response = 'Available commands:'
        for command, class_ in regular_commands.items():
            arguments = ''
            for argument in class_.required_arguments:
                arguments += '**<{}>** '.format(argument)

            response += '\n  **{}{}** {}- {}'.format(CMD_PREFIX, command, arguments, class_.help_text)

        response += '\n\nAvailable sound commands:'
        for command, class_ in sound_commands.items():
            arguments = ''
            for argument in class_.required_arguments:
                arguments += '**<{}>** '.format(argument)

            response += '\n  **{}{}** {}- {}'.format(CMD_PREFIX, command, arguments, class_.help_text)

        response += ('\n\nAvailable passive commands '
                     '(these trigger automatically if a message fulfills certain conditions):')
        for text, class_ in passive_commands.items():
            response += '\n  **{}{}** - {}'.format(CMD_PREFIX, text, class_.help_text)

        response += '\nEither prepend your command with `{}` or mention the bot using `@`.'.format(CMD_PREFIX)

        return response


commands = {
    'help': CommandHelp
}
