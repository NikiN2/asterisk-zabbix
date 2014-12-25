# coding=utf-8
from zasterisk.base import DiscoveryCommand


class Command(DiscoveryCommand):
    help = '''
        CoreShowChannels
    '''

    def count(self, ami):
        def callback(connect, timeout):
            events = self.parse_events(connect)
            return len(events.get("CoreShowChannel"))
        return ami.execute("CoreShowChannels", {}, callback)

    def discovery(self, ami):
        return ""
