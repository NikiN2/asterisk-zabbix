# coding=utf-8
import sys
import os
from argparse import ArgumentParser
from importlib import import_module


def find_commands(command_dir):
    try:
        return [f[:-3] for f in os.listdir(command_dir)
            if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []


def get_commands(commands_path):
    commands = {}
    for command_dir in commands_path:
        module_name = os.path.basename(command_dir)
        commands.update({name: module_name + "." + name for name in find_commands(command_dir)})
    return commands


def load_command_class(name):
    module = import_module(name)
    return module.Command()


class CommandUtility(object):
    commands_path = []

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

    def register_path(self, path):
        self.commands_path.append(path)

    def main_help_text(self):
        usage = [
             "",
             "Type '%s help <command>' for help on a specific command." % self.prog_name,
             "",
             "Available commands:",
        ]
        for command in sorted(get_commands(self.commands_path).keys()):
            comm = self.fetch_command(command)
            if comm:
                usage.append(" %s - %s" % (command, comm.help.strip()))
            else:
                usage.append(" %s" % command)
        return '\n'.join(usage)

    def fetch_command(self, command_module):
        commands = get_commands(self.commands_path)
        try:
            module_name = commands[command_module]
        except KeyError:
            sys.stderr.write("Unknown command: %r\nType '%s help' for usage.\n" % (command_module, self.prog_name))
            sys.exit(1)

        return load_command_class(module_name)

    def execute(self, ami):
        try:
            command_module = self.argv[1]
        except IndexError:
            command_module = None

        parser = ArgumentParser(None, usage="%(prog)s [command] [args]", add_help=False)
        parser.add_argument('args', nargs='*')

        options, args = parser.parse_known_args(self.argv[2:])

        if command_module is None:
            sys.stdout.write(self.main_help_text() + '\n')
        elif command_module == 'help':
            if '--commands' in args:
                sys.stdout.write(self.main_help_text() + '\n')
            elif len(options.args) < 1:
                sys.stdout.write(self.main_help_text() + '\n')
            else:
                self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
        elif self.argv[1:] in (['--help'], ['-h']):
            sys.stdout.write(self.main_help_text() + '\n')
        else:
            self.fetch_command(command_module).run_from_argv(ami, self.argv)
