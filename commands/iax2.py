# coding=utf-8
from zasterisk.base import DiscoveryFieldCommand

class Command(DiscoveryFieldCommand):
    help = '''
        IAX2 peers
    '''

    def discovery(self, ami):
        def callback(connect, timeout):
            events = self.parse_events(connect)
            return self.create_discovery(events.get("PeerEntry"), "{#USERNAME}", "ObjectName")

        return ami.execute("IAXpeers", {}, callback)

    def get_field(self, ami, field_name, param):
        def callback(connect, timeout):
            events = self.parse_events(connect).get("PeerEntry")
            for event in events:
                if event.get("ObjectName") == param:
                    return event.get(field_name)
        result = ami.execute("IAXpeers", {}, callback)
        if not result:
            return "Field '%s' not found" % field_name
        return result

    def count(self, ami):
        return 0

