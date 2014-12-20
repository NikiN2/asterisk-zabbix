# coding=utf-8
from zasterisk.base import DiscoveryFieldCommand


class Command(DiscoveryFieldCommand):
    help = '''
        SIP peers
    '''

    def discovery(self, ami):
        def callback(connect, timeout):
            events = self.parse_events(connect, "PeerEntry")
            return self.create_discovery(events, "{#USERNAME}", "ObjectName")

        return ami.execute("SIPpeers", {}, callback)

    def get_field(self, ami, field_name, param):
        return ami.execute("SIPshowpeer", {"Peer": param},
                            lambda connect, timeout: self.expect_field(connect, field_name, timeout))
