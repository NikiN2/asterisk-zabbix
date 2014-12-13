# coding=utf-8
import os
import sys
import re
import json
from argparse import ArgumentParser
import posix_ipc

PATTERN_LINE = re.compile("(?P<key>\w+): (?P<value>.*)")


class BaseCommand:
    help = ''
    args = ''

    def __init__(self):
        self.semaphore = posix_ipc.Semaphore("/zasterisk_command", initial_value=1, flags=posix_ipc.O_CREAT)
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def usage(self, command):
        usage = '%%prog %s [options] %s' % (command, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage

    def create_parser(self, prog_name, command):
        parser = ArgumentParser(prog="%s %s" % (os.path.basename(prog_name), command), description=self.help or None)
        parser.add_argument('-v', '--verbosity', action='store_true', dest='verbosity')
        if self.args:
            parser.add_argument('args', nargs='*')
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        pass

    def run_from_argv(self, ami, argv):
        parser = self.create_parser(argv[0], argv[1])
        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        args = cmd_options.pop('args', ())
        try:
            self.execute(ami, *args, **cmd_options)
        except Exception as e:
            self.stderr.write(str(e))
            sys.exit(1)

    def print_help(self, prog_name, command):
        parser = self.create_parser(prog_name, command)
        parser.print_help()

    def execute(self, ami, *args, **options):
        try:
            self.semaphore.acquire()
            ami.init(self, options)
            ami.login()
            output = self.handle(ami, *args, **options)
            if output:
                self.stdout.write(output)
            ami.close()
        finally:
            self.semaphore.release()

    def handle(self, ami, *args, **options):
        raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')

    @staticmethod
    def parse_line(line):
        match = PATTERN_LINE.match(line)
        if match:
            return match.group("key"), match.group("value")
        return None

    def get_all(self, connect):
        while True:
            self.stdout.write(connect.readline())

    def parse_events(self, connect, event_name):
        is_event = False
        events = []
        current_event = {}
        while True:
            line = connect.readline().strip()
            if not len(line):
                if is_event:
                    events.append(current_event)
                    current_event = {}
                is_event = False
                continue
            if line == "EventList: Complete":
                break
            if line == "Event: %s" % event_name:
                is_event = True

            if is_event:
                pair = self.parse_line(line)
                if pair:
                    key, value = pair
                    current_event[key] = value
        return events

    @staticmethod
    def get_discovery(items, param_name, key_name):
        result = []
        for item in items:
            value = item.get(key_name)
            if value:
                result.append({param_name: value})
        return json.dumps({"data": result})

    @staticmethod
    def expect_field(connect, field_name, timeout):
        try:
            connect.expect("%s: (.*?)\r" % field_name, timeout=timeout)
            if connect.match:
                return connect.match.group(1)
            else:
                return "Field '%s' not found" % field_name
        except Exception:
            return "Field '%s' not found" % field_name
