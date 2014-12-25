# coding=utf-8
import os
import sys
import re
import json
from argparse import ArgumentParser
import posix_ipc
from collections import defaultdict


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
            output = str(self.handle(ami, *args, **options))
            if output:
                self.stdout.write(output)
            ami.close()
        finally:
            self.semaphore.release()
            self.semaphore.unlink()

    def handle(self, ami, *args, **options):
        raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')

    def parse_events(self, connect, end_line="EventList: Complete"):
        result = defaultdict(list)
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
            if line == end_line:
                break
            if line.startswith("Event:"):
                is_event = True

            if is_event:
                pair = self.parse_field_line(line)
                if pair:
                    key, value = pair
                    current_event[key] = value

        for event in events:
            event_name = event.get("Event")
            result[event_name].append(event)

        return result

    @staticmethod
    def parse_field_line(line):
        match = PATTERN_LINE.match(line)
        if match:
            return match.group("key"), match.group("value")
        return None


class DiscoveryCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--all", "-a", dest='discovery', action='store_true', help="Discovery trunks.")
        parser.add_argument("--count", "-c", dest='count', action='store_true', help="Events count.")
        BaseCommand.add_arguments(self, parser)

    def discovery(self, ami):
        raise NotImplementedError('subclasses of DiscoveryCommand must provide a discovery() method')

    def count(self, ami):
        raise NotImplementedError('subclasses of DiscoveryCommand must provide a count() method')

    def handle(self, ami, *args, **options):
        discovery = options.get('discovery')
        if discovery:
            return self.discovery(ami)

        count = options.get('count')
        if count:
            return self.count(ami)

    def create_discovery(self, items, param_name, key_name):
        result = []
        for item in items:
            value = item.get(key_name)
            if value:
                result.append({param_name: value})
        return json.dumps({"data": result})


class FieldCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--field", "-f", dest='field', help="Return the name of the field")
        parser.add_argument("--param", "-p", dest='param', help="Filter parameter")
        parser.add_argument("--regex", "-r", dest='regex', help="Regular expression for field value. (Return group 1)")
        BaseCommand.add_arguments(self, parser)

    def handle(self, ami, *args, **options):
        field = options.get('field')
        param = options.get("param")
        regex = options.get("regex")

        if field and param:
            result = self.get_field(ami, field, param)
            if regex:
                match = re.search(regex, result)
                if match:
                    return match.group(1)
            return result

    def get_field(self, ami, field_name, param):
        raise NotImplementedError('subclasses of FieldCommand must provide a get_field() method')

    def expect_field(self, connect, field_name, timeout):
        try:
            connect.expect("%s: (.*?)\r" % field_name, timeout=timeout)
            if connect.match:
                return connect.match.group(1)
            else:
                return "Field '%s' not found" % field_name
        except Exception:
            return "Field '%s' not found" % field_name


class DiscoveryFieldCommand(DiscoveryCommand, FieldCommand):
    def add_arguments(self, parser):
        DiscoveryCommand.add_arguments(self, parser)
        FieldCommand.add_arguments(self, parser)

    def handle(self, ami, *args, **options):
        output = DiscoveryCommand.handle(self, ami, *args, **options)
        if not output:
            output = FieldCommand.handle(self, ami, *args, **options)
        return output
