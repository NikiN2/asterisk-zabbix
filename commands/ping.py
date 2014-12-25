# coding=utf-8
from zasterisk.base import BaseCommand


class Command(BaseCommand):
    help = '''
        ping/pong.
    '''

    def handle(self, ami, *args, **options):
        def callback(connect, timeout):
            connect.expect("Timestamp: ([\d\.]*)\r", timeout=timeout)
            match = connect.match
            if match:
                return match.group(1)

        return ami.execute("Ping", {}, callback)
